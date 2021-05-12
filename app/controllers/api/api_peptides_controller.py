import json

from flask import request, jsonify, url_for

from macpepdb.models.peptide import Peptide
from macpepdb.proteomics.mass.convert import to_float as mass_to_float

from app import app, get_database_connection
from ...models.convert import peptide_to_dict, protein_to_dict
from .api_abstract_peptide_controller import ApiAbstractPeptideController

class ApiPeptidesController(ApiAbstractPeptideController):

    @staticmethod
    @app.route("/api/peptides/search", endpoint="api_peptide_search_path", methods=["POST"])
    def search():
        return ApiAbstractPeptideController._search(request)

    @staticmethod
    @app.route("/api/peptides/<string:sequence>", endpoint="api_peptide_path", methods=["GET"])
    def show(sequence):
        requested_peptide = Peptide(sequence, 0)
        errors = []

        response_data = {}

        include_proteins = request.args.get("include_proteins", type=int, default=0)

        database_connection = get_database_connection()
        with database_connection.cursor() as database_cursor:

            peptide = Peptide.select(database_cursor, ("mass = %s AND sequence = %s", [requested_peptide.mass, requested_peptide.sequence]))

            if peptide:
                response_data["peptide"] = peptide_to_dict(peptide)
                response_data["url"] = url_for("peptide_path", sequence=peptide.sequence, _external=True)

                if include_proteins:
                    response_data["proteins"] = [protein_to_dict(protein) for protein in peptide.proteins(database_cursor)]
            else:            
                errors.append("no peptide for sequence '{}' found".format(sequence))

        if not len(errors):
            return jsonify(response_data)
        else:   
            return jsonify({
                "errors": errors
            }), 422

    @staticmethod
    @app.route("/api/peptides/mass/<string:sequence>", endpoint="api_peptide_mass_path", methods=["GET"])
    def sequence_mass(sequence):
        peptide = Peptide(sequence, 0)

        return jsonify({
            'mass': mass_to_float(peptide.mass)
        })