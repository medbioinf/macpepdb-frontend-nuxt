import math
import operator

from typing import List, Iterable
from flask import jsonify, Response

from macpepdb.proteomics.mass.convert import to_int as mass_to_int, to_float as mass_to_float
from macpepdb.proteomics.modification import Modification
from macpepdb.proteomics.modification_collection import ModificationCollection
from macpepdb.models.column_conditions_list import ColumnConditionsList
from macpepdb.models.modification_combination_list import ModificationCombinationList, ModificationCombination
from macpepdb.models.taxonomy import Taxonomy, TaxonomyRank
from macpepdb.models.peptide import Peptide
from macpepdb.models.row_stream import RowStream


from app import get_database_connection, macpepdb_pool
from ..application_controller import ApplicationController

class ApiAbstractPeptideController(ApplicationController):
    SUPPORTED_OUTPUTS = ['application/json', 'application/octet-stream', 'text/plain']
    SUPPORTED_ORDER_COLUMNS = ['mass', 'length', 'sequence', 'number_of_missed_cleavages']
    SUPPORTED_ORDER_DIRECTIONS = ['asc', 'desc']
    FASTA_SEQUENCE_LEN = 60

    PEPTIDE_QUERY_DEFAULT_COLUMNS = ["mass", "sequence", "number_of_missed_cleavages", "length", "is_swiss_prot", "is_trembl", "taxonomy_ids", "unique_taxonomy_ids", "proteome_ids"]

    @staticmethod
    def _search(request):
        errors = []
        data = request.get_json()

        include_count = False
        if 'include_count' in data and isinstance(data['include_count'], bool):
            include_count = data['include_count']

        order_by = None
        if 'order_by' in data:
            if isinstance(data['order_by'], str) and data['order_by'] in ApiAbstractPeptideController.SUPPORTED_ORDER_COLUMNS:
                order_by = data['order_by']
            else:
                errors.append(f"'order_by' must be a string with one of following values: {', '.join(ApiAbstractPeptideController.SUPPORTED_ORDER_COLUMNS)}")
        

        if 'order_direction' in data:
            if not isinstance(data['order_direction'], str) or not data['order_direction'] in ApiAbstractPeptideController.SUPPORTED_ORDER_DIRECTIONS:
                errors.append(f"'order_direction' must be a string with one of following values: {', '.join(ApiAbstractPeptideController.SUPPORTED_ORDER_DIRECTIONS)}")

        # Get accept header (default 'application/json'), split by ',' in case multiple mime types where supported and take the first one
        output_style = request.headers.get('accept', default=ApiAbstractPeptideController.SUPPORTED_OUTPUTS[0]).split(',')[0].strip()
        # If the mime type is not supported set default one
        if not output_style in ApiAbstractPeptideController.SUPPORTED_OUTPUTS:
            output_style = ApiAbstractPeptideController.SUPPORTED_OUTPUTS[0]

        # validate int attributes
        for attribute in  ["lower_precursor_tolerance_ppm", "upper_precursor_tolerance_ppm", "variable_modification_maximum"]:
            if not attribute in data or data[attribute] == None:
                errors.append("you have to specify {}".format(attribute))
                continue
            if not isinstance(data[attribute], int):
                errors.append("'{}' has to be int".format(attribute))
                continue
            if data[attribute] < 0:
                errors.append("'{}' must be greater or equals 0".format(attribute))

        modifications = []
        if "modifications" in data:
            if isinstance(data["modifications"], list):
                for idx, modification_attributes in enumerate(data["modifications"]):
                    if isinstance(modification_attributes, dict):
                        accession_and_name = "onlinemod:{}".format(idx)
                        try:
                            modification_attributes['accession'] = accession_and_name
                            modification_attributes['name'] = accession_and_name
                            modification_attributes['delta'] = mass_to_int(modification_attributes['delta'])
                            modifications.append(Modification.from_dict(modification_attributes))
                        except Exception as e:
                            errors.append("modification {} is not valid: {}".format(modification_attributes, e))
                    else:
                        errors.append("modifications {} has to be of type dict".format(modification_attributes))
            else:
                errors.append("modifications has to be of type list")
        
        try:
            modification_collection = ModificationCollection(modifications)
        except Exception as e:
            errors.append("{}".format(e))

        database_connection = get_database_connection()
        if not len(errors):
            if "precursor" in data:
                if isinstance(data["precursor"], float) or isinstance(data["precursor"], int):

                    modification_combination_list = ModificationCombinationList(
                        modification_collection, 
                        mass_to_int(data["precursor"]),
                        data["lower_precursor_tolerance_ppm"],
                        data["upper_precursor_tolerance_ppm"],
                        data["variable_modification_maximum"]
                    )

                    peptides_query = f"SELECT DISTINCT <COLUMNS> FROM {Peptide.TABLE_NAME} WHERE mass BETWEEN %s AND %s"

                    # List of metadata conditions
                    metadata_conditions = ColumnConditionsList()
                    if "taxonomy_id" in data:
                        if isinstance(data["taxonomy_id"], int):
                            # Recursively select all taxonomies below the given one
                            recursive_subspecies_id_query = (
                                "WITH RECURSIVE subtaxonomies AS ("
                                    "SELECT id, parent_id, rank "
                                    f"FROM {Taxonomy.TABLE_NAME} "
                                    "WHERE id = %s "
                                    "UNION " 
                                        "SELECT t.id, t.parent_id, t.rank "
                                        f"FROM {Taxonomy.TABLE_NAME} t "
                                        "INNER JOIN subtaxonomies s ON s.id = t.parent_id "
                                f") SELECT id FROM subtaxonomies WHERE rank = %s;"
                            )

                            with database_connection.cursor() as db_cursor:
                                db_cursor.execute(recursive_subspecies_id_query, (data["taxonomy_id"], TaxonomyRank.SPECIES.value))
                                metadata_conditions.append("taxonomy_ids", "&& %s::int[]", ApiAbstractPeptideController.is_intersecting, [row[0] for row in db_cursor.fetchall()])

                        else:
                            errors.append("taxonomy_id has to be of type int")

                    if "proteome_id" in data:
                        if isinstance(data["proteome_id"], str):
                            metadata_conditions.append("proteome_ids", "&& %s::int[]", lambda peptide_proteom_ids, proteome_id: proteome_id in peptide_proteom_ids, data["proteome_id"])
                        else:
                            errors.append("proteome_id has to be of type string")

                    if "is_reviewed" in data:
                        if isinstance(data["is_reviewed"], bool):
                            if data["is_reviewed"]:
                                metadata_conditions.append("is_swiss_prot", "= %s", operator.eq, True)
                            else:
                                metadata_conditions.append("is_trembl", "= %s", operator.eq, True)
                        else:
                            errors.append("is_reviewed has to be of type boolean")

                    # Sort by `order_by`
                    if order_by and not output_style == ApiAbstractPeptideController.SUPPORTED_OUTPUTS[2]:
                        peptides_query += f" ORDER BY {order_by} {data['order_direction']}"
                    peptides_query += ";"

                    # Note about offset and limit: It is much faster to fetch data from server and discard rows below the offset and stop the fetching when the limit is reached, instead of applying LIMIT and OFFSET directly to the query.
                    # Even on high offsets, which discards a lot of rows, this approach is faster.
                    # Curl shows the diffences: curl -o foo.json --header "Content-Type: application/json" --request POST --data '{"include_count":true,"offset":0,"limit":50,"modifications":[{"amino_acid":"C","position":"anywhere","is_static":true,"delta":57.021464}],"lower_precursor_tolerance_ppm":5,"upper_precursor_tolerance_ppm":5,"variable_modification_maximum":0,"order":true,"precursor":859.49506802369}' http://localhost:3000/api/peptides/search
                    # Applying OFFSET and LIMIT to query: 49 - 52 seconds
                    # Discarding rows which are below the offset and stop the fetching early: a few hundred miliseconds (not printed by curl).
                    offset = 0
                    limit = math.inf
                    if "limit" in data:
                        if isinstance(data["limit"], int):
                            limit = data["limit"]
                        else:
                            errors.append("limit has to be of type int")
                    if "offset" in data:
                        if isinstance(data["offset"], int):
                            offset = data["offset"]
                        else:
                            errors.append("offset has to be of type int")

                else:
                    errors.append("precursor has to be a int/float")
            else:
                errors.append("you have to specify a precursor")

        if len(errors):
            return jsonify({
                "errors": errors
            }), 422


        modification_combination_list = modification_combination_list if len(modification_combination_list) else [ModificationCombination([], mass_to_int(data["precursor"]), data["lower_precursor_tolerance_ppm"], data["upper_precursor_tolerance_ppm"])] 

        if output_style ==  ApiAbstractPeptideController.SUPPORTED_OUTPUTS[0]:
            return ApiAbstractPeptideController.generate_json_respond(peptides_query, modification_combination_list, metadata_conditions, include_count, offset, limit)
        elif output_style == ApiAbstractPeptideController.SUPPORTED_OUTPUTS[1]:
            return ApiAbstractPeptideController.generate_octet_response(peptides_query, modification_combination_list, metadata_conditions, offset, limit)
        elif output_style == ApiAbstractPeptideController.SUPPORTED_OUTPUTS[2]:
            return ApiAbstractPeptideController.generate_txt_response(peptides_query, modification_combination_list, metadata_conditions, offset, limit)

    @staticmethod
    def generate_json_respond(peptides_query: str, modification_combination_list: ModificationCombinationList, metadata_conditions: ColumnConditionsList, include_count: bool, offset: int, limit: int):
        """
        Serialize the given peptides as JSON objects, structure: {'result_key': [peptide_json, ...]}
        @param peptides_query The query for peptides
        @param modification_combination_list List of modification combinations to match
        @param metadata_conditions Conditions for metadata
        @param include_count Boolean to include count in the results, e.g. {'count': 0, 'peptides': [{'sequence': 'PEPTIDER', ...}, ...]}
        @param offset Result offset
        @param limit Result limit
        """
        def generate_json_stream():  
            # In a generator the reponse is already returned and the app context is teared down. So we can not use a database connection from the actual request handling.
            # Get a new one from the pool and return it when the generator ist stopped (GeneratorExit is thrown).
            database_connection = macpepdb_pool.getconn()
            try:
                with database_connection.cursor() as database_cursor:
                    # Counter for peptides which matches the given filters
                    matching_peptide_counter = 0
                    # Counter for written peptdes
                    written_peptide_counter = 0
                    # Open a JSON object and peptide array
                    yield b"{\"peptides\":["
                    for modification_combination in modification_combination_list:
                        query_columns = ApiAbstractPeptideController.PEPTIDE_QUERY_DEFAULT_COLUMNS + list(modification_combination.column_conditions_list.column_names)
                        finished_query = peptides_query.replace("<COLUMNS>", ", ".join(query_columns))
                        column_conditions_list = metadata_conditions + modification_combination.column_conditions_list

                        row_stream = RowStream(database_cursor, finished_query, [modification_combination.precursor_range.lower_limit, modification_combination.precursor_range.upper_limit], query_columns, column_conditions_list)
                    
                        for peptide_row in row_stream:
                            matching_peptide_counter += 1
                            # Write peptide to stream if matching_peptide_counter is larger than offset and written_peptide_counter is below the limit
                            if matching_peptide_counter > offset and written_peptide_counter < limit:
                                # Prepend comma if this is not the first returned peptide
                                if written_peptide_counter > 0 :
                                    yield b","
                                for json_chunk in ApiAbstractPeptideController.peptide_row_to_json_generator(peptide_row):
                                    yield json_chunk
                                # Increase written peptides
                                written_peptide_counter += 1
                            # Break for-loop if written_peptide_counter reaches the limit and include_count is false. If include_count is true we iterate over all peptide in mass range to count the matching peptides.
                            if written_peptide_counter == limit and not include_count:
                                break
                        if not include_count:
                            # Close array and object
                            yield b"]}"
                        else:
                            # Close array, add key for count
                            yield b"],\"count\":"
                            # Add count
                            yield str(matching_peptide_counter).encode()
                            # Close object
                            yield b"}"
                        break
            finally:
                macpepdb_pool.putconn(database_connection)
        # Send stream
        return Response(generate_json_stream(), content_type=f"{ApiAbstractPeptideController.SUPPORTED_OUTPUTS[0]}; charset=utf-8")

    @staticmethod
    def generate_octet_response(peptides_query: str, modification_combination_list: ModificationCombinationList, metadata_conditions: ColumnConditionsList, offset: int, limit: int):
        """
        This will generate a stream of JSON-formatted peptides per line. Each JSON-string is bytestring.
        @param peptides_query The query for peptides
        @param modification_combination_list List of modification combinations to match
        @param metadata_conditions Conditions for metadata
        @param include_count Boolean to include count in the results, e.g. {'count': 0, 'peptides': [{'sequence': 'PEPTIDER', ...}, ...]}
        @param offset Result offset
        @param limit Result limit
        """
        def generate_octet_stream():
            # In a generator the reponse is already returned and the app context is teared down. So we can not use a database connection from the actual request handling.
            # Get a new one from the pool and return it when the generator ist stopped (GeneratorExit is thrown).
            database_connection = macpepdb_pool.getconn()
            try:
                with database_connection.cursor() as database_cursor:
                    # Counter for peptides which matches the given filters
                    matching_peptide_counter = 0
                    # Counter for written peptdes
                    written_peptide_counter = 0

                    for modification_combination in modification_combination_list:
                        query_columns = ApiAbstractPeptideController.PEPTIDE_QUERY_DEFAULT_COLUMNS + list(modification_combination.column_conditions_list.column_names)
                        finished_query = peptides_query.replace("<COLUMNS>", ", ".join(query_columns))
                        column_conditions_list = metadata_conditions + modification_combination.column_conditions_list

                        row_stream = RowStream(database_cursor, finished_query, [modification_combination.precursor_range.lower_limit, modification_combination.precursor_range.upper_limit], query_columns, column_conditions_list)

                        for peptide_row in row_stream:
                            matching_peptide_counter += 1
                            # Write peptide to stream if matching_peptide_counter is larger than offset and written_peptide_counter is below the limit
                            if matching_peptide_counter > offset and written_peptide_counter < limit:
                                # Prepend newline if this is not the first returned peptide
                                if written_peptide_counter > 0 :
                                    yield b"\n"
                                for json_chunk in ApiAbstractPeptideController.peptide_row_to_json_generator(peptide_row):
                                    yield json_chunk
                                # Increase written peptides
                                written_peptide_counter += 1
                            # Break for-loop if written_peptide_counter reaches the limit.
                            if written_peptide_counter == limit:
                                break
            finally:
                macpepdb_pool.putconn(database_connection)
        return Response(generate_octet_stream(), content_type=ApiAbstractPeptideController.SUPPORTED_OUTPUTS[1])


    @staticmethod
    def generate_txt_response(peptides_query: str, modification_combination_list: ModificationCombinationList, metadata_conditions: ColumnConditionsList, offset: int, limit: int):
        """
        This will generate a stream of peptides in fasta format.
        @param peptides_query The query for peptides
        @param modification_combination_list List of modification combinations to match
        @param metadata_conditions Conditions for metadata
        @param include_count Boolean to include count in the results, e.g. {'count': 0, 'peptides': [{'sequence': 'PEPTIDER', ...}, ...]}
        @param offset Result offset
        @param limit Result limit
            """
        def generate_txt_stream():
            # In a generator the reponse is already returned and the app context is teared down. So we can not use a database connection from the actual request handling.
            # Get a new one from the pool and return it when the generator ist stopped (GeneratorExit is thrown).
            database_connection = macpepdb_pool.getconn()
            try:
                with database_connection.cursor() as database_cursor:
                    # Counter for peptides which matches the given filters
                    matching_peptide_counter = 0
                    # Counter for written peptdes
                    written_peptide_counter = 0

                    for modification_combination in modification_combination_list:
                        query_columns = ApiAbstractPeptideController.PEPTIDE_QUERY_DEFAULT_COLUMNS + list(modification_combination.column_conditions_list.column_names)
                        finished_query = peptides_query.replace("<COLUMNS>", ", ".join(query_columns))
                        column_conditions_list = metadata_conditions + modification_combination.column_conditions_list

                        row_stream = RowStream(database_cursor, finished_query, [modification_combination.precursor_range.lower_limit, modification_combination.precursor_range.upper_limit], query_columns, column_conditions_list)
                        for peptide_row in row_stream:
                            matching_peptide_counter += 1
                            # Write peptide to stream if matching_peptide_counter is larger than offset and written_peptide_counter is below the limit
                            if matching_peptide_counter > offset and written_peptide_counter < limit:
                                # Prepend semicolon if this is not the first returned peptide
                                if written_peptide_counter > 0 :
                                    yield b"\n"
                                # Begin FASTA entry with '>lcl|' ...
                                yield b">lcl|"
                                # ... add mass ...
                                yield str(peptide_row[0]).encode()
                                # ... add a underscore ...
                                yield b"_"
                                # ... add the sequence to create a unique fasta accession ...
                                yield peptide_row[1].encode()
                                # ... add the sequence in chunks of 60 amino acids ...
                                for chunk_start in range(0, len(peptide_row[1]), 60):
                                    yield b"\n"
                                    yield peptide_row[1][chunk_start : chunk_start+60].encode()
                                # Increase written peptides
                                written_peptide_counter += 1
                            # Break for-loop if written_peptide_counter reaches the limit.
                            if written_peptide_counter == limit:
                                break
            finally:
                macpepdb_pool.putconn(database_connection)
        return Response(generate_txt_stream(), content_type=ApiAbstractPeptideController.SUPPORTED_OUTPUTS[2])
        

    @staticmethod
    def peptide_row_to_json_generator(peptide_row: tuple):
        """
        Generate a JSON-formatted string from am peptide row.
        @param peptide_row Should contain the ApiAbstractPeptideController.PEPTIDE_QUERY_DEFAULT_COLUMNS as first elements.
        """
        # Open peptide object with 'mass' key ...
        yield b"{\"mass\":"
        # ... add mass as float as utf-8 encoded bytes ... 
        yield str(mass_to_float(peptide_row[0])).encode()
        # ... add comma and add new key for sequence with open string ...
        yield b",\"sequence\":\""
        # ... add sequence as bytes ...
        yield peptide_row[1].encode()
        # ... close sequence string, add comma and add key for review status ...
        yield b"\",\"is_swiss_prot\":"
        # ... write true or false to stream ...
        yield b"true" if peptide_row[4] else b"false"
        # ... add comma and add key for second review status ...
        yield b",\"is_trembl\":"
        # ... write true or false to stream ...
        yield b"true" if peptide_row[5] else b"false"
        # ... add comma, add key for taxonomy IDs and open array ...
        yield b",\"taxonomy_ids\":["
        # ... add commaseparated list of taxonomy IDs ...
        yield ",".join([str(taxonomy_id) for taxonomy_id in peptide_row[6]]).encode()
        # ... close array, add comma, add key for unique taxonomy IDs and add open array ...
        yield b"],\"unique_taxonomy_ids\":["
        # ... add commaseparated list of taxonomy IDs ...
        yield ",".join([str(taxonomy_id) for taxonomy_id in peptide_row[7]]).encode()
        # ... close array, add comma, add key for protoeme IDs and open array ...
        yield b"],\"proteome_ids\":["
        # ... add commaseparated list of proteome IDs (proteome IDs are strings, so they have to wrapped in quotation marks) ...
        yield ",".join([f"\"{proteome_id}\"" for proteome_id in peptide_row[8]]).encode()
        # ... close array and peptide object
        yield b"]}"

    @staticmethod
    def is_intersecting(iterable_x: Iterable, iterable_y: Iterable) -> bool:
        """Checks if two iterable are intersecting by checking if one element of iterable x is contained by iterable y.

        Arguments:
        iterable_x -- List with elements
        iterable_y -- List with elements
        """
        for x_element in iterable_x:
            if x_element in iterable_y:
                return True
        return False