import json

from flask import request, jsonify, url_for

from macpepdb.models.peptide import Peptide
from macpepdb.proteomics.mass.convert import to_float as mass_to_float

from app import app, macpepdb_session
from .api_abstract_peptide_controller import ApiAbstractPeptideController

class ApiPeptidesController(ApiAbstractPeptideController):

    @staticmethod
    @app.route("/api/peptides/search", endpoint="api_peptide_search_path", methods=["POST"])
    def search():
        return ApiAbstractPeptideController._search(request)

    @staticmethod
    @app.route("/api/peptides/<string:sequence>", endpoint="api_peptide_path", methods=["GET"])
    def show(sequence):
        sequence = Peptide.generalize(sequence.upper())
        errors = []

        response_data = {}

        include_proteins = request.args.get("include_proteins", type=int, default=0)

        try:
            peptide = macpepdb_session.query(Peptide).filter(Peptide.sequence == sequence).one()
        except sqlalchemy_exceptions.NoResultFound as error:
            peptide = None

        if peptide:
            response_data["peptide"] = peptide.to_dict()
            response_data["peptide"]["weight"] = mass_to_float(response_data["peptide"]["weight"])
            response_data["url"] = url_for("peptide_path", sequence=peptide.sequence, _external=True)

            if include_proteins:
                proteins = peptide.proteins.all()
                response_data["proteins"] = []
                for protein in proteins:
                    response_data["proteins"].append(protein.to_dict())
        else:            
            errors.append("no peptide for sequence '{}' found".format(sequence))

        if not len(errors):
            return jsonify(response_data)
        else:   
            return jsonify({
                "errors": errors
            }), 422

    @staticmethod
    @app.route("/api/peptides/weight/<string:sequence>", endpoint="api_peptide_weight_path", methods=["GET"])
    def sequence_weight(sequence):
        sequence = Peptide.generalize(sequence.upper())
        peptide = Peptide(sequence, 0)

        return jsonify({
            'weight': mass_to_float(peptide.weight)
        })