import json

from flask import request, jsonify, url_for

from macpepdb.models.peptide import Peptide
from macpepdb.models.protein import Protein
from macpepdb.models.protein_peptide_association import ProteinPeptideAssociation
from macpepdb.proteomics.mass.convert import to_float as mass_to_float

from macpepdb_web_backend import app, get_database_connection
from macpepdb_web_backend.models.convert import peptide_to_dict, protein_to_dict
from macpepdb_web_backend.controllers.api.api_abstract_peptide_controller import ApiAbstractPeptideController


class ApiPeptidesController(ApiAbstractPeptideController):

    @staticmethod
    @app.route("/api/peptides/search", endpoint="api_peptide_search_path", methods=["POST"])
    @app.route("/api/peptides/search.<string:file_extension>", endpoint="api_peptide_search_csv_path", methods=["POST"])
    def search(file_extension: str = None):
        return ApiAbstractPeptideController._search(request, file_extension)

    @staticmethod
    @app.route("/api/peptides/<string:sequence>", endpoint="api_peptide_path", methods=["GET"])
    def show(sequence: str):
        sequence = sequence.upper()
        database_connection = get_database_connection()
        with database_connection.cursor() as database_cursor:
            mass = Peptide.calculate_mass(sequence)
            peptide = Peptide.select(database_cursor, ("mass = %s AND sequence = %s", [mass, sequence]), False, True)
            if peptide:
                return jsonify(peptide_to_dict(peptide))
            else:
                return jsonify({
                    "errors": {
                        "sequence": ["not found"]
                    }
                }), 404

    @staticmethod
    @app.route("/api/peptides/<string:sequence>/proteins", endpoint="api_peptide_proteins_path", methods=["GET"])
    def proteins(sequence: str):
        sequence = sequence.upper()
        mass = Peptide.calculate_mass(sequence)
        database_connection = get_database_connection()
        with database_connection.cursor() as database_cursor:
            protein_query = (
                f"SELECT accession, secondary_accessions, entry_name, name, sequence, taxonomy_id, proteome_id, is_reviewed FROM {Protein.TABLE_NAME} "
                f"WHERE accession = ANY(SELECT protein_accession FROM {ProteinPeptideAssociation.TABLE_NAME} WHERE peptide_mass = %s AND peptide_sequence = %s);"
            )
            database_cursor.execute(protein_query, (mass, sequence))

            return jsonify({
                "proteins": [{
                    "accession": row[0],
                    "secondary_accessions": row[1],
                    "entry_name": row[2],
                    "name": row[3],
                    "sequence": row[4],
                    "taxonomy_id": row[5],
                    "proteome_id": row[6],
                    "is_reviewed": row[7]
                } for row in database_cursor.fetchall()]
            })

    @staticmethod
    @app.route("/api/peptides/mass/<string:sequence>", endpoint="api_peptide_mass_path", methods=["GET"])
    def sequence_mass(sequence):
        peptide = Peptide(sequence, 0)

        return jsonify({
            'mass': mass_to_float(peptide.mass)
        })

    