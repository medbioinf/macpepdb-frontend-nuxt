import itertools
import json

from collections import defaultdict
from flask import request, jsonify

from macpepdb.models.peptide import Peptide
from macpepdb.models.protein import Protein
from macpepdb.models.protein_peptide_association import ProteinPeptideAssociation
from macpepdb.proteomics.mass.convert import to_float as mass_to_float
from macpepdb.proteomics.enzymes.digest_enzyme import DigestEnzyme

from macpepdb_web_backend import app, get_database_connection
from macpepdb_web_backend.models.convert import peptide_to_dict
from macpepdb_web_backend.controllers.api.api_abstract_peptide_controller import ApiAbstractPeptideController
from macpepdb_web_backend.controllers.api.api_digestion_controller import ApiDigestionController


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


    @staticmethod
    @app.route("/api/peptides/digest", endpoint="api_peptide_digest_search", methods=["POST"])
    def digest():
        """
        Digest a given peptide/sequence, search the resulting peptides in the database and return matching and not matching peptides in separate array.
        """
        data = request.get_json()
        errors = ApiDigestionController.check_digestion_parameters(data)

        if not "sequence" in data:
            errors["sequence"].append("cannot be empty")

        digestion_peptides = []
        database_peptides = []
        if len(errors) == 0:
            EnzymeClass = DigestEnzyme.get_enzyme_by_name("trypsin")
            enzyme = EnzymeClass(data["maximum_number_of_missed_cleavages"], data["minimum_peptide_length"], data["maximum_peptide_length"])
            digestion_peptides = enzyme.digest(Protein("TMP", [], "TMP", "TMP", data["sequence"], [], [], False, 0))

            where_clause = " OR ".join(["mass = %s AND sequence = %s"] * len(digestion_peptides))
            where_values = list(itertools.chain.from_iterable([[peptide.mass, peptide.sequence] for peptide in digestion_peptides]))

            if "do_database_search" in data and isinstance(data["do_database_search"], bool) and data["do_database_search"]:
                database_connection = get_database_connection()           
                with database_connection.cursor() as database_cursor:
                    database_peptides = Peptide.select(database_cursor, (where_clause, where_values), fetchall=True)
                database_peptides.sort(key = lambda peptide: peptide.mass)
                digestion_peptides = [peptide for peptide in digestion_peptides if peptide not in database_peptides]


            digestion_peptides.sort(key = lambda peptide: peptide.mass)

        if len(errors) == 0:
            return jsonify({
                "database": [peptide_to_dict(peptide) for peptide in database_peptides],
                "digestion": [peptide_to_dict(peptide) for peptide in digestion_peptides],
                "count": len(database_peptides) +  len(digestion_peptides)
            })
        else:
            return jsonify({
                "errors": errors
            }), 422

    