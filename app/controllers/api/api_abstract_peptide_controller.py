import sys
import orjson

from flask import jsonify, Response
from sqlalchemy import func, distinct, and_, select
from sqlalchemy.orm import sessionmaker, aliased

from trypperdb.proteomics.mass.convert import to_int as mass_to_int, to_float as mass_to_float
from trypperdb.proteomics.modification import Modification, ModificationPosition
from trypperdb.proteomics.amino_acid import AminoAcid
from trypperdb.proteomics.modification_collection import ModificationCollection
from trypperdb.models.modified_peptide_where_clause_builder import ModifiedPeptideWhereClauseBuilder
from trypperdb.models.protein import Protein
from trypperdb.models.taxonomy import Taxonomy, TaxonomyRank
from trypperdb.models.peptide import Peptide
from trypperdb.models.associacions import proteins_peptides as proteins_peptides_table


from app import trypperdb
from ..application_controller import ApplicationController

class ApiAbstractPeptideController(ApplicationController):
    SUPPORTED_OUTPUTS = ['application/json', 'application/octet-stream', 'text/plain']

    @staticmethod
    def _search(request, peptide_class):
        errors = []
        data = request.get_json()

        include_count = False
        if 'include_count' in data and isinstance(data['include_count'], bool):
            include_count = data['include_count']

        order_results = False
        if 'order' in data and isinstance(data['order'], bool):
            order_results = data['order']

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
        
        if not len(errors):
            if "precursor" in data:
                if isinstance(data["precursor"], float) or isinstance(data["precursor"], int):

                    where_clause_builder = ModifiedPeptideWhereClauseBuilder(
                        modification_collection, 
                        mass_to_int(data["precursor"]),
                        data["lower_precursor_tolerance_ppm"],
                        data["upper_precursor_tolerance_ppm"],
                        data["variable_modification_maximum"]
                    )
                    where_clause = where_clause_builder.build(peptide_class)

                    count_query = select([func.count(distinct(peptide_class.id))]).where(where_clause).select_from(peptide_class.__table__)
                    peptides_query = None
                    if not output_style == ApiAbstractPeptideController.SUPPORTED_OUTPUTS[2]:
                        peptides_query = peptide_class.__table__.select(where_clause)
                    else:
                        peptides_query = select([peptide_class.id, peptide_class.sequence]).where(where_clause).distinct()


                    # The following filters only work for peptides because they contain a protein join
                    if peptide_class == Peptide:
                        protein_conditions = []

                        if "taxonomy_id" in data:
                            if isinstance(data["taxonomy_id"], int):
                                # Recursively select all taxonomies below the given one
                                recursive_query = select(Taxonomy.__table__.columns).where(Taxonomy.id == data["taxonomy_id"]).cte(recursive=True)
                                parent_taxonomies = recursive_query.alias()
                                child_taxonomies = Taxonomy.__table__.alias()
                                sub_taxonomies = recursive_query.union_all(select(child_taxonomies.columns).where(child_taxonomies.c.parent_id == parent_taxonomies.c.id))
                                sub_species_id_query = select([sub_taxonomies.c.id]).where(sub_taxonomies.c.rank == TaxonomyRank.SPECIES)

                                with trypperdb.connect() as connection:
                                    sub_species_ids = [row[0] for row in connection.execute(sub_species_id_query).fetchall()]
                                
                                if len(sub_species_ids) == 1:
                                    protein_conditions.append(Protein.taxonomy_id == sub_species_ids[0])
                                elif len(sub_species_ids) > 1:
                                    protein_conditions.append(Protein.taxonomy_id.in_(sub_species_ids))
                            else:
                                errors.append("taxonomy_id has to be of type int")

                        if "proteome_id" in data:
                            if isinstance(data["proteome_id"], str):
                                protein_conditions.append(Protein.proteome_id == data["proteome_id"])
                            else:
                                errors.append("proteome_id has to be of type string")

                        if "is_reviewed" in data:
                            if isinstance(data["is_reviewed"], int):
                                protein_conditions.append(Protein.is_reviewed == (data["is_reviewed"] > 0))
                            else:
                                errors.append("is_reviewed has to be of type int")

                        if len(protein_conditions):
                            # Concatenate conditions with and
                            protein_where_clause = and_(*protein_conditions)
                            # Rebuild count query
                            inner_count_query = select([peptide_class.id]).where(where_clause).select_from(peptide_class.__table__).alias('weight_specific_peptides')
                            protein_join = inner_count_query.join(proteins_peptides_table, proteins_peptides_table.c.peptide_id == inner_count_query.c.id)
                            protein_join = protein_join.join(Protein.__table__, Protein.id == proteins_peptides_table.c.protein_id)
                            count_query = select([func.count(distinct(inner_count_query.c.id))]).select_from(protein_join).where(protein_where_clause)

                            # Create alais for the inner query
                            inner_peptide_query = peptides_query.alias('weight_specific_peptides')
                            # Join innder query with proteins
                            protein_join = inner_peptide_query.join(proteins_peptides_table, proteins_peptides_table.c.peptide_id == inner_peptide_query.c.id)
                            protein_join = protein_join.join(Protein.__table__, Protein.id == proteins_peptides_table.c.protein_id)
                            # Create select around the inner query
                            peptides_query = select(inner_peptide_query.columns).distinct().select_from(protein_join).where(protein_where_clause)

                    # Sort by weight
                    if order_results and not output_style == ApiAbstractPeptideController.SUPPORTED_OUTPUTS[2]:
                        peptides_query = peptides_query.order_by(peptides_query.c.weight)
                    
                    if "limit" in data:
                        if isinstance(data["limit"], int):
                            peptides_query = peptides_query.limit(data["limit"])
                        else:
                            errors.append("limit has to be of type int")
                    if "offset" in data:
                        if isinstance(data["offset"], int):
                            peptides_query = peptides_query.offset(data["offset"])
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

        if output_style ==  ApiAbstractPeptideController.SUPPORTED_OUTPUTS[0]:
            def generate_json_stream(peptides_query, peptide_count_query, result_key: str, include_count: bool):
                """
                Serialize the given peptides as JSON objects, structure: {'result_key': [peptide_json, ...]}
                @param peptides_query The query for peptides
                @param peptide_count_query The query to count the peptides.
                @param result_key Name of the result key within the JSON-objecte, e.g. {'result_key': [peptide_json, ...]}
                @param include_count Boolean to include count in the results, e.g. {'count': 0, 'result_key': [peptide_json, ...]}
                """
                with trypperdb.connect() as db_connection:
                    # Open a JSON object
                    yield b"{"
                    # Check if there are pepritdes
                    # Add count to open object
                    if include_count:
                        peptide_count = db_connection.execute(peptide_count_query).fetchone()[0]
                        yield f"\"count\":{peptide_count},".encode()
                    # Add key `result_key` object with open array
                    yield f"\"{result_key}\":[".encode()
                    # Create cursor to stream results
                    peptides_cursor = db_connection.execution_options(stream_results=True).execute(peptides_query)
                    is_first_chunk = True
                    while True:
                        # Fetch 10000 results
                        peptides_chunk = peptides_cursor.fetchmany(10000)
                        # Stop loop if no results were fetched
                        if not peptides_chunk:
                            break
                        # If this is not the first chunk, append a ',', because the last peptide of the previous chunk does not has one appended
                        if not is_first_chunk:
                            yield b","
                        # Create iterator 
                        peptides_chunk_iter = peptides_chunk.__iter__()
                        # Get first result
                        previous_peptide_row = next(peptides_chunk_iter)
                        # Iterate over the remaining rows in this chunk
                        for peptide_row in peptides_chunk_iter:
                            # Write the previous peptide to stream ...
                            peptide_dict = {str(key): value for key, value in previous_peptide_row.items()}
                            peptide_dict["weight"] = mass_to_float(peptide_dict["weight"])
                            peptide_dict['peff_notation_of_modifications'] = ''
                            yield orjson.dumps(peptide_dict)
                            # ... and append 
                            yield b","
                            # Mark the current peptide as previous peptide for next iteration
                            previous_peptide_row = peptide_row
                        # Now write the last peptide without a ',' at the end
                        peptide_dict = {str(key): value for key, value in previous_peptide_row.items()}
                        peptide_dict["weight"] = mass_to_float(peptide_dict["weight"])
                        peptide_dict['peff_notation_of_modifications'] = ''
                        yield orjson.dumps(peptide_dict)
                        is_first_chunk = False
                    # Close array and object
                    yield b"]}"
            result_key = 'peptides' if peptide_class == Peptide else 'decoys'
            # Send stream
            return Response(generate_json_stream(peptides_query, count_query, result_key, include_count), content_type=f"{ApiAbstractPeptideController.SUPPORTED_OUTPUTS[0]}; charset=utf-8")
        elif output_style == ApiAbstractPeptideController.SUPPORTED_OUTPUTS[1]:
            def generate_octet_stream(peptides_query: list):
                """
                This will generate a stream of JSON-formatted peptides per line. Each JSON-string is bytestring.
                @param peptides_query The query for peptides
                """
                with trypperdb.connect() as db_connection:
                    # Create cursor
                    peptides_cursor = db_connection.execution_options(stream_results=True).execute(peptides_query)
                    is_first_chunk = True
                    while True:
                        # Fetch 10000 results
                        peptides_chunk = peptides_cursor.fetchmany(10000)
                        # Stop loop if no results were fetched
                        if not len(peptides_chunk):
                            break
                        # If this is not the first chunk, append a new line, because the last peptide of the previous chunk does not has one appended
                        if not is_first_chunk:
                            yield b"\n"
                        # Create iterator 
                        peptides_chunk_iter = peptides_chunk.__iter__()
                        # Get first result
                        previous_peptide_row = next(peptides_chunk_iter)
                        # Iterate over the remaining rows in this chunk
                        for peptide_row in peptides_chunk_iter:
                            # Write the previous peptide to stream ...
                            peptide_dict = {str(key): value for key, value in previous_peptide_row.items()}
                            peptide_dict["weight"] = mass_to_float(peptide_dict["weight"])
                            peptide_dict['peff_notation_of_modifications'] = ''
                            yield orjson.dumps(peptide_dict)
                            # ... and append 
                            yield b"\n"
                            # Mark the current peptide as previous peptide for next iteration
                            previous_peptide_row = peptide_row
                        # Now write the last peptide without a '\n' at the end
                        peptide_dict = {str(key): value for key, value in previous_peptide_row.items()}
                        peptide_dict["weight"] = mass_to_float(peptide_dict["weight"])
                        peptide_dict['peff_notation_of_modifications'] = ''
                        yield orjson.dumps(peptide_dict)
                        is_first_chunk = False
            return Response(generate_octet_stream(peptides_query), content_type=ApiAbstractPeptideController.SUPPORTED_OUTPUTS[1])
        elif output_style == ApiAbstractPeptideController.SUPPORTED_OUTPUTS[2]:
            def generate_txt_stream(peptide_query, peptide_class):
                """
                This will generate a stream of peptides in fasta format.
                @param peptides_query The query for peptides
                @params peptice_class Class of the peptides (Peptide/Decoy)
                """
                with trypperdb.connect() as db_connection:
                    # Create cursor
                    peptides_cursor = db_connection.execution_options(stream_results=True).execute(peptides_query)
                    is_first_chunk = True
                    while True:
                        # Fetch 10000 results
                        peptides_chunk = peptides_cursor.fetchmany(10000)
                        # Stop loop if no results were fetched
                        if not len(peptides_chunk):
                            break
                        # If this is not the first chunk, append a new line, because the last peptide of the previous chunk does not has one appended
                        if not is_first_chunk:
                            yield "\n"
                        # Create iterator 
                        peptides_chunk_iter = peptides_chunk.__iter__()
                        # Get first result
                        previous_peptide_row = next(peptides_chunk_iter)
                        # Iterate over the remaining rows in this chunk
                        for peptide_row in peptides_chunk_iter:
                            # Write the previous peptide to stream ...
                            yield f"{peptide_class.FASTA_HEADER_PREFIX}\n{previous_peptide_row['sequence']}"
                            # ... and append new line
                            yield "\n"
                            # Mark the current peptide as previous peptide for next iteration
                            previous_peptide_row = peptide_row
                        # Now write the last peptide without a new line at the end
                        yield f"{peptide_class.FASTA_HEADER_PREFIX}\n{previous_peptide_row['sequence']}"
                        is_first_chunk = False
            return Response(generate_txt_stream(peptides_query, peptide_class), content_type=ApiAbstractPeptideController.SUPPORTED_OUTPUTS[2])
        
