from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum, unique
from importlib.metadata import metadata
import json
import math
from typing import List, Iterable, Optional, Any

from flask import jsonify, Response
from macpepdb.database.query_helpers.where_condition import WhereCondition
from macpepdb.proteomics.mass.convert import to_int as mass_to_int, to_float as mass_to_float
from macpepdb.proteomics.modification import Modification
from macpepdb.proteomics.modification_collection import ModificationCollection
from macpepdb.models.modification_combination_list import ModificationCombinationList, ModificationCombination
from macpepdb.models.taxonomy import Taxonomy, TaxonomyRank
from macpepdb.models.peptide import Peptide
from macpepdb.models.peptide_metadata import PeptideMetadata


from macpepdb_web_backend import get_database_connection, macpepdb_pool, app
from macpepdb_web_backend.controllers.application_controller import ApplicationController

@unique
class OutputFormat(Enum):
    json = "application/json"
    stream = "application/octet-stream"
    text = "text/plain"
    csv = "text/csv"
    fasta = "text/fasta"

    def __str__(self) -> str:
        return f"{self.value}"

    @classmethod
    def from_name(cls, name: str) -> OutputFormat:
        return cls[name.lower()]

    @classmethod
    def from_value(cls, value: str) -> OutputFormat:
        lower_value = value.lower()
        for format in cls:
            if format.value == lower_value:
                return format
        raise KeyError(f"f{value} not found")

@dataclass
class MetadataCondition:
    __slots__ = [
        "__is_swiss_prot",
        "__is_trembl",
        "__taxonomy_ids",
        "__unique_taxonomy_ids",
        "__proteome_id"
    ]

    __is_swiss_prot: Optional[bool]
    __is_trembl: Optional[bool]
    __taxonomy_ids: Optional[List[int]]
    __unique_taxonomy_ids: Optional[List[int]]
    __proteome_id: Optional[str]

    def __init__(self):
        self.__is_swiss_prot = None
        self.__is_trembl = None
        self.__taxonomy_ids = None
        self.__unique_taxonomy_ids = None
        self.__proteome_id = None

    @property
    def is_swiss_prot(self) -> Optional[bool]:
        return self.__is_swiss_prot

    @property
    def is_trembl(self) -> Optional[bool]:
        return self.__is_trembl

    @property
    def taxonomy_ids(self) -> Optional[List[int]]:
        return self.__taxonomy_ids

    @property
    def unique_taxonomy_ids(self) -> Optional[List[int]]:
        return self.__unique_taxonomy_ids

    @property
    def proteome_id(self) -> Optional[str]:
        return self.__proteome_id

    @is_swiss_prot.setter
    def is_swiss_prot(self, value: Optional[bool]):
        self.__is_swiss_prot = value

    @is_trembl.setter
    def is_trembl(self, value: Optional[bool]):
        self.__is_trembl = value

    @taxonomy_ids.setter
    def taxonomy_ids(self, value: Optional[List[int]]):
        self.__taxonomy_ids = value

    @unique_taxonomy_ids.setter
    def unique_taxonomy_ids(self, value: Optional[List[int]]):
        self.__unique_taxonomy_ids = value

    @proteome_id.setter
    def proteome_id(self, value: Optional[str]):
        self.__proteome_id = value


    def validate(self, metadata: PeptideMetadata) -> bool:
        if self.__is_swiss_prot is not None and metadata.is_swiss_prot != self.__is_swiss_prot:
            return False
        if self.__is_trembl is not None and metadata.is_trembl != self.__is_trembl:
            return False
        if self.__taxonomy_ids is not None and not self.__class__.is_intersecting(self.__taxonomy_ids, metadata.taxonomy_ids):
            return False
        if self.__unique_taxonomy_ids is not None and not self.__class__.is_intersecting(self.__unique_taxonomy_ids, metadata.unique_taxonomy_ids):
            return False
        if self.__proteome_id is not None and self.__proteome_id not in metadata.proteome_ids:
            return False
        return True

    def has_conditions(self) -> bool:
        """
        Checks if metadata conditions exists

        Returns
        -------
        bool
            False if no check is needed (not metadata condition)
        """
        return self.__is_swiss_prot is not None \
            or self.__is_trembl is not None \
            or self.__taxonomy_ids is not None \
            or self.__unique_taxonomy_ids is not None \
            or self.__proteome_id is not None \
        
    @classmethod
    def is_intersecting(cls, iterable_x: Iterable[Any], iterable_y: Iterable[Any]) -> bool:
        """
        Checks if two iterables are intersecting by checking if one element of iterable x is contained by iterable y.

        Arguments
        ---------
        iterable_x: Iterable[Any]
            List with elements
        iterable_y: Iterable[Any]
            List with elements
        
        Returns
        -------
        Ture if intersect
        """
        for x_element in iterable_x:
            if x_element in iterable_y:
                return True
        return False


class ApiAbstractPeptideController(ApplicationController):
    SUPPORTED_ORDER_COLUMNS = ['mass', 'length', 'sequence', 'number_of_missed_cleavages']
    SUPPORTED_ORDER_DIRECTIONS = ['asc', 'desc']
    FASTA_SEQUENCE_LEN = 60

    PEPTIDE_QUERY_DEFAULT_COLUMNS = ["mass", "sequence", "number_of_missed_cleavages", "length", "is_swiss_prot", "is_trembl", "taxonomy_ids", "unique_taxonomy_ids", "proteome_ids"]

    @staticmethod
    def _search(request, file_extension: str):
        errors = defaultdict(list)
        data = None
        if request.headers.get("Content-Type", "") == "application/json":
            data = request.get_json()
        elif request.headers.get("Content-Type", "") == "application/x-www-form-urlencoded":
            # For use with classical form-tag. The JSON-formatted search parameters should be provided in the form parameter "search_params"
            data = json.loads(request.form.get("search_params", "{}"))

        include_count = False
        if 'include_count' in data and isinstance(data['include_count'], bool):
            include_count = data['include_count']

        order_by = None
        if 'order_by' in data:
            if isinstance(data['order_by'], str) and data['order_by'] in ApiAbstractPeptideController.SUPPORTED_ORDER_COLUMNS:
                order_by = data['order_by']
            else:
                errors["order_by"].append(f"must be a string with one of following values: {', '.join(ApiAbstractPeptideController.SUPPORTED_ORDER_COLUMNS)}")
        

        if 'order_direction' in data:
            if not isinstance(data['order_direction'], str) or not data['order_direction'] in ApiAbstractPeptideController.SUPPORTED_ORDER_DIRECTIONS:
                errors["order_direction"].append(f"'order_direction' must be a string with one of following values: {', '.join(ApiAbstractPeptideController.SUPPORTED_ORDER_DIRECTIONS)}")
            

        output_style = None
        if file_extension is not None:
            try:
                output_style = OutputFormat.from_name(file_extension)
            except KeyError:
                pass
        else:
            try:
                output_style = OutputFormat.from_value(request.headers.get("accept", default=""))
            except KeyError:
                output_style = OutputFormat.json

        # validate int attributes
        for attribute in  ["lower_precursor_tolerance_ppm", "upper_precursor_tolerance_ppm", "variable_modification_maximum"]:
            if attribute in data:
                if isinstance(data[attribute], int):
                    if data[attribute] < 0:
                        errors[attribute].append("not greater or equals 0")
                else:
                    errors[attribute].append("not an integer")
            else:    
                errors[attribute].append("cannot be empty")

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
                            errors[f"modifications[{idx}]"].append("is invalid")
                    else:
                        errors[f"modifications[{idx}]"].append("not a dictionary")
            else:
                errors["modifications"].append("modifications has to be of type list")
        
        try:
            modification_collection = ModificationCollection(modifications)
        except Exception as e:
            errors["modifications"].append(f"{e}")

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

                    metadata_condition = MetadataCondition()

                    # List of metadata conditions
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
                                metadata_condition.taxonomy_ids = [row[0] for row in db_cursor.fetchall()]

                        else:
                            errors["taxonomy_id"].append("must be an integer")

                    if "proteome_id" in data:
                        if isinstance(data["proteome_id"], str):
                            metadata_condition.proteome_id = data["proteome_id"]
                        else:
                            errors["proteome_id"].append("must be a string")

                    if "is_reviewed" in data:
                        if isinstance(data["is_reviewed"], bool):
                            if data["is_reviewed"]:
                                metadata_condition.is_swiss_prot = True
                            else:
                                metadata_condition.is_trembl = True
                        else:
                            errors["is_reviewed"].append("must be a boolean")

                    # Sort by `order_by`
                    order_by_instruction = None
                    if order_by and not output_style == OutputFormat.text:
                        order_by_instruction = f"{order_by} {data['order_direction']}"

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
                            errors["limit"].append("must be an integer")
                    if "offset" in data:
                        if isinstance(data["offset"], int):
                            offset = data["offset"]
                        else:
                            errors["offset"].append("must be an integer")

                else:
                    errors["precursor"] = ["must be an integer or float"]
            else:
                errors["precursor"] = ["cannot be missing"]

        if len(errors):
            return jsonify({
                "errors": errors
            }), 422

        if output_style == OutputFormat.json:
            return ApiAbstractPeptideController.generate_json_respond(
                modification_combination_list.to_where_condition(),
                order_by_instruction,
                offset,
                limit,
                include_count,
                metadata_condition
            )
        elif output_style == OutputFormat.stream:
            return ApiAbstractPeptideController.generate_octet_response(
                modification_combination_list.to_where_condition(),
                order_by_instruction,
                offset, 
                limit,
                metadata_condition
            )
        elif output_style == OutputFormat.fasta:
            return ApiAbstractPeptideController.generate_fasta_response(
                modification_combination_list.to_where_condition(),
                order_by_instruction,
                offset, 
                limit,
                metadata_condition
            )
        elif output_style == OutputFormat.csv:
            return ApiAbstractPeptideController.generate_csv_response(
                modification_combination_list.to_where_condition(),
                order_by_instruction,
                offset, 
                limit,
                metadata_condition
            )
        elif output_style == OutputFormat.text:
            return ApiAbstractPeptideController.generate_text_response(
                modification_combination_list.to_where_condition(),
                order_by_instruction,
                offset, 
                limit,
                metadata_condition
            )

    @staticmethod
    def generate_json_respond(where_condition: WhereCondition, order_by_instruction: str, offset: int, limit: int, include_count: bool, metadata_condition: MetadataCondition):
        """
        Serialize the given peptides as JSON objects, structure: {'result_key': [peptide_json, ...]}
        @param peptides_query The query for peptides
        @param modification_combination_list List of modification combinations to match
        @param include_count Boolean to include count in the results, e.g. {'count': 0, 'peptides': [{'sequence': 'PEPTIDER', ...}, ...]}
        @param offset Result offset
        @param limit Result limit
        """
        def generate_json_stream():
            # In a generator the reponse is already returned and the app context is teared down. So we can not use a database connection from the actual request handling.
            # Get a new one from the pool and return it when the generator ist stopped (GeneratorExit is thrown).
            database_connection = macpepdb_pool.getconn()
            do_metadata_checks = metadata_condition.has_conditions()
            try:
                with database_connection.cursor() as database_cursor:
                    # Counter for written peptides necessary of manual limit offset handling
                    written_peptides = 0
                    # Open a JSON object and peptide array
                    yield b"{\"peptides\":["
                    for peptide_idx, peptide in enumerate(Peptide.select(database_cursor, where_condition, order_by=order_by_instruction, include_metadata=True, stream=True)):
                        if peptide_idx >= offset - 1 and (not do_metadata_checks or metadata_condition.validate(peptide.metadata)):
                            if written_peptides > 0:
                                yield b","
                            for json_chunk in ApiAbstractPeptideController.peptide_to_json(peptide):
                                yield json_chunk
                            written_peptides += 1
                        # Break peptide cursor loop if limit is hit
                        if written_peptides == limit:
                            break
                    if not include_count:
                        yield b"]}"
                    else:
                        # Close array, add key for count
                        yield b"],\"count\":"
                        # Add count
                        yield str(Peptide.count(database_cursor, where_condition)).encode()
                        # Close object
                        yield b"}"

            finally:
                macpepdb_pool.putconn(database_connection)
        # Send stream
        return Response(generate_json_stream(), content_type=f"{OutputFormat.json}; charset=utf-8")

    @staticmethod
    def generate_octet_response(where_condition: WhereCondition, order_by_instruction: str, offset: int, limit: int, metadata_condition: MetadataCondition):
        """
        This will generate a stream of JSON-formatted peptides per line. Each JSON-string is bytestring.
        @param peptides_query The query for peptides
        @param modification_combination_list List of modification combinations to match
        @param include_count Boolean to include count in the results, e.g. {'count': 0, 'peptides': [{'sequence': 'PEPTIDER', ...}, ...]}
        @param offset Result offset
        @param limit Result limit
        """
        def generate_octet_stream():
            # In a generator the reponse is already returned and the app context is teared down. So we can not use a database connection from the actual request handling.
            # Get a new one from the pool and return it when the generator ist stopped (GeneratorExit is thrown).
            database_connection = macpepdb_pool.getconn()
            do_metadata_checks = metadata_condition.has_conditions()
            try:
                with database_connection.cursor() as database_cursor:
                    # Counter for written peptdes
                    written_peptide_counter = 0
                
                    for peptide_idx, peptide in enumerate(Peptide.select(database_cursor, where_condition, order_by=order_by_instruction, include_metadata=True, stream=True)):
                        if peptide_idx > offset - 1 and (not do_metadata_checks or metadata_condition.validate(peptide.metadata)):
                            # Prepend newline if this is not the first returned peptide
                            if written_peptide_counter > 0 :
                                yield b"\n"
                            for json_chunk in ApiAbstractPeptideController.peptide_to_json(peptide):
                                yield json_chunk
                            # Increase written peptides
                            written_peptide_counter += 1
                        # Break for-loop if written_peptide_counter reaches the limit.
                        if written_peptide_counter == limit:
                            break
            finally:
                macpepdb_pool.putconn(database_connection)
        return Response(generate_octet_stream(), content_type=OutputFormat.stream)


    @staticmethod
    def generate_fasta_response(where_condition: WhereCondition, order_by_instruction: str, offset: int, limit: int, metadata_condition: MetadataCondition):
        """
        Generates a FASAT stream. Fasta header contains only database identifier and the accession, which is the ongoing peptide index.

        Parameters
        ----------
        where_condition : WhereCondition
            Select conditions
        order_by_instruction : str
            SQL instruction for order by
        offset : int
            Offset
        limit : int
            limit
        metadata_condition : MetadataCondition
            Conditions for metadata
        """
        def generate_fasta_stream():
            # In a generator the reponse is already returned and the app context is teared down. So we can not use a database connection from the actual request handling.
            # Get a new one from the pool and return it when the generator ist stopped (GeneratorExit is thrown).
            database_connection = macpepdb_pool.getconn()
            do_metadata_checks = metadata_condition.has_conditions()
            try:
                with database_connection.cursor() as database_cursor:
                    # Counter for written peptdes
                    written_peptide_counter = 0
                
                    for peptide_idx, peptide in enumerate(Peptide.select(database_cursor, where_condition, order_by=order_by_instruction, include_metadata=True, stream=True)):
                        # Write peptide to stream if matching_peptide_counter is larger than offset and written_peptide_counter is below the limit
                        if peptide_idx > offset - 1 and (not do_metadata_checks or metadata_condition.validate(peptide.metadata)):
                            # Prepend semicolon if this is not the first returned peptide
                            if written_peptide_counter > 0 :
                                yield b"\n"
                            # Begin FASTA entry with '>macpepdb|' ...
                            yield b">macpepdb|"
                            # Use the peptide index as unique key
                            yield str(peptide_idx).encode("utf-8")
                            yield b"|"
                            # ... add the sequence in chunks of 60 amino acids ...
                            for chunk_start in range(0, len(peptide.sequence), 60):
                                yield b"\n"
                                yield peptide.sequence[chunk_start : chunk_start+60].encode()
                            # Increase written peptides
                            written_peptide_counter += 1
                        # Break for-loop if written_peptide_counter reaches the limit.
                        if written_peptide_counter == limit:
                            break
            finally:
                macpepdb_pool.putconn(database_connection)
        return Response(generate_fasta_stream(), content_type=OutputFormat.text)
        

    @staticmethod
    def generate_csv_response(where_condition: WhereCondition, order_by_instruction: str, offset: int, limit: int, metadata_condition: MetadataCondition):
        """
        This will generate a stream of peptides in fasta format.
        @param peptides_query The query for peptides
        @param modification_combination_list List of modification combinations to match
        @param include_count Boolean to include count in the results, e.g. {'count': 0, 'peptides': [{'sequence': 'PEPTIDER', ...}, ...]}
        @param offset Result offset
        @param limit Result limit
            """
        def generate_csv_stream():
            # In a generator the reponse is already returned and the app context is teared down. So we can not use a database connection from the actual request handling.
            # Get a new one from the pool and return it when the generator ist stopped (GeneratorExit is thrown).
            database_connection = macpepdb_pool.getconn()
            do_metadata_checks = metadata_condition.has_conditions()
            try:
                with database_connection.cursor() as database_cursor:
                    # Counter for written peptdes
                    written_peptide_counter = 0

                    # Write header to stream
                    yield b"\"mass\",\"sequence\",\"in_swiss_prot\",\"in_trembl\",\"taxonomy_ids\",\"unique_for_taxonomy_ids\",\"proteome_ids\""
                    # Counter for written peptdes
                    written_peptide_counter = 0
                
                    for peptide_idx, peptide in enumerate(Peptide.select(database_cursor, where_condition, order_by=order_by_instruction, include_metadata=True, stream=True)):
                            # Write peptide to stream if matching_peptide_counter is larger than offset and written_peptide_counter is below the limit
                            if peptide_idx > offset -1 and (not do_metadata_checks or metadata_condition.validate(peptide.metadata)):
                                yield b"\n"
                                yield str(mass_to_float(peptide.mass)).encode()
                                # At this point only string values are added to the cssv, so we quote them for better compatibility
                                yield b",\""
                                yield peptide.sequence.encode()
                                yield b"\",\""
                                yield b"true" if peptide.metadata.is_swiss_prot else b"false"
                                yield b"\",\""
                                yield b"true" if peptide.metadata.is_trembl else b"false"
                                yield b"\",\""
                                yield ",".join([str(taxonomy_id) for taxonomy_id in peptide.metadata.taxonomy_ids]).encode()
                                yield b"\",\""
                                yield ",".join([str(taxonomy_id) for taxonomy_id in peptide.metadata.unique_taxonomy_ids]).encode()
                                yield b"\",\""
                                yield ",".join([f"{proteome_id}" for proteome_id in peptide.metadata.proteome_ids]).encode()
                                yield b"\""
                                # Increase written peptides
                                written_peptide_counter += 1
                            # Break for-loop if written_peptide_counter reaches the limit.
                            if written_peptide_counter == limit:
                                break
            finally:
                macpepdb_pool.putconn(database_connection)
        return Response(generate_csv_stream(), mimetype=str(OutputFormat.csv), headers = {"Content-Disposition": "attachment; filename=macpepdb_peptide.csv"})
    

    @staticmethod
    def generate_text_response(where_condition: WhereCondition, order_by_instruction: str, offset: int, limit: int, metadata_condition: MetadataCondition):
        """
        Generates a plain text stream, where each line contains just the peptide sequence.

        Parameters
        ----------
        where_condition : WhereCondition
            Select conditions
        order_by_instruction : str
            SQL instruction for order by
        offset : int
            Offset
        limit : int
            limit
        metadata_condition : MetadataCondition
            Conditions for metadata
        """
        def generate_text_stream():
            # In a generator the reponse is already returned and the app context is teared down. So we can not use a database connection from the actual request handling.
            # Get a new one from the pool and return it when the generator ist stopped (GeneratorExit is thrown).
            database_connection = macpepdb_pool.getconn()
            do_metadata_checks = metadata_condition.has_conditions()
            try:
                with database_connection.cursor() as database_cursor:
                    # Counter for written peptdes
                    written_peptide_counter = 0
                
                    for peptide_idx, peptide in enumerate(Peptide.select(database_cursor, where_condition, order_by=order_by_instruction, include_metadata=True, stream=True)):
                            # Write peptide to stream if matching_peptide_counter is larger than offset and written_peptide_counter is below the limit
                            if peptide_idx > offset -1 and (not do_metadata_checks or metadata_condition.validate(peptide.metadata)):
                                if written_peptide_counter > 0:
                                    yield b"\n"
                                yield peptide.sequence.encode("utf-8")
                                # Increase written peptides
                                written_peptide_counter += 1
                            # Break for-loop if written_peptide_counter reaches the limit.
                            if written_peptide_counter == limit:
                                break
            finally:
                macpepdb_pool.putconn(database_connection)
        return Response(generate_text_stream(), mimetype=str(OutputFormat.csv), headers = {"Content-Disposition": "attachment; filename=macpepdb_peptide.csv"})

    @staticmethod
    def peptide_to_json(peptide: Peptide):
        """
        Generate a JSON-formatted string from am peptide row.
        @param peptide_row Should contain the ApiAbstractPeptideController.PEPTIDE_QUERY_DEFAULT_COLUMNS as first elements.
        """
        # Open peptide object with 'mass' key ...
        yield b"{\"mass\":"
        # ... add mass as float as utf-8 encoded bytes ... 
        yield str(mass_to_float(peptide.mass)).encode()
        # ... add comma and add new key for sequence with open string ...
        yield b",\"sequence\":\""
        # ... add sequence as bytes ...
        yield peptide.sequence
        # ... close sequence string, add comma and add key for review status ...
        yield b"\",\"is_swiss_prot\":"
        # ... write true or false to stream ...
        yield b"true" if peptide.metadata.is_swiss_prot else b"false"
        # ... add comma and add key for second review status ...
        yield b",\"is_trembl\":"
        # ... write true or false to stream ...
        yield b"true" if peptide.metadata.is_trembl else b"false"
        # ... add comma, add key for taxonomy IDs and open array ...
        yield b",\"taxonomy_ids\":["
        # ... add commaseparated list of taxonomy IDs ...
        yield ",".join([str(taxonomy_id) for taxonomy_id in peptide.metadata.taxonomy_ids]).encode()
        # ... close array, add comma, add key for unique taxonomy IDs and add open array ...
        yield b"],\"unique_taxonomy_ids\":["
        # ... add commaseparated list of taxonomy IDs ...
        yield ",".join([str(taxonomy_id) for taxonomy_id in peptide.metadata.unique_taxonomy_ids]).encode()
        # ... close array, add comma, add key for protoeme IDs and open array ...
        yield b"],\"proteome_ids\":["
        # ... add commaseparated list of proteome IDs (proteome IDs are strings, so they have to wrapped in quotation marks) ...
        yield ",".join([f"\"{proteome_id}\"" for proteome_id in peptide.metadata.proteome_ids]).encode()
        # ... close array and peptide object
        yield b"]}"
