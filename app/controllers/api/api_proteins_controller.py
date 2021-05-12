from os import access
import sys

from sqlalchemy import between, and_
from sqlalchemy.orm import selectinload, exc as sqlalchemy_exceptions
from flask import request, jsonify, url_for

from macpepdb.proteomics.mass.convert import to_float as mass_to_float
from macpepdb.proteomics.enzymes.digest_enzyme import DigestEnzyme
from macpepdb.models.protein import Protein

from app import app, get_database_connection
from ...models.convert import peptide_to_dict, protein_to_dict
from ..application_controller import ApplicationController

class ApiProteinsController(ApplicationController):
    @staticmethod
    @app.route("/api/proteins/digest", endpoint="api_protein_digest_path", methods=["POST"])
    def digest():
        errors = []
        data = request.get_json()

        for attribute in  ["maximum_number_of_missed_cleavages", "minimum_peptide_length", "maximum_peptide_length"]:
            if not attribute in data:
                errors.append("you have to specify {}".format(attribute))
                continue
            if not isinstance(data[attribute], int):
                errors.append("'{}' has to be int".format(attribute))
                continue

        if not len(errors):
            if data["maximum_number_of_missed_cleavages"] < 0:
                errors.append("'maximum_number_of_missed_cleavages' must be greater or equals 0")

            for attribute in  ["minimum_peptide_length", "maximum_peptide_length"]:
                if data[attribute] < 1:
                    errors.append("'{}' must be greater or equals 0".format(attribute))

            if data["maximum_peptide_length"] < data["minimum_peptide_length"]:
                errors.append("'maximum_peptide_length' must be greater or equals 'minimum_peptide_length'")

        peptides = []
        if not len(errors):
            if "sequence" in data:
                if not len(errors):
                    EnzymeClass = DigestEnzyme.get_enzyme_by_name("trypsin")
                    enzyme = EnzymeClass(data["maximum_number_of_missed_cleavages"], data["minimum_peptide_length"], data["maximum_peptide_length"])
                    peptides = enzyme.digest(Protein("TMP", [], "TMP", "TMP", data["sequence"], [], [], False))
            elif "accession" in data:
                database_connection = get_database_connection()
                with database_connection.cursor() as database_cursor:
                    protein = Protein.select(database_cursor, ("accession = %s", [data["accession"]]))
                    if protein:
                        peptides = list(filter(
                            lambda peptide: peptide.number_of_missed_cleavages <= data["maximum_number_of_missed_cleavages"] and data["minimum_peptide_length"] <= peptide.length <= data["maximum_peptide_length"],
                            protein.peptides(database_cursor)
                        ))
                    else:
                        errors.append("no protein for accession '{}' found".format(data["accession"]))
            else:
                errors.append("you have to specify sequence or accession")

        peptides.sort(key = lambda peptide: peptide.mass)
        if not len(errors):
            return jsonify({
                "peptides": [peptide_to_dict(peptide) for peptide in peptides],
                "count": len(peptides)
            })
        else:
            return jsonify({
                "errors": errors
            }), 422

    @staticmethod
    @app.route("/api/proteins/<string:accession>", endpoint="api_protein_path")
    def search(accession):
        accession = accession.upper()

        include_peptides = request.args.get("include_peptides", type=int, default=0)
        database_connection = get_database_connection()

        with database_connection.cursor() as database_cursor:
            protein = Protein.select(database_cursor, ("accession = %s", [accession]))

            if protein:
                response_data = {
                    "protein": protein_to_dict(protein),
                    "url": url_for("protein_path", accession=protein.accession, _external=True)
                }

                if include_peptides:
                    response_data["peptides"] = [peptide_to_dict(peptide) for peptide in protein.peptides(database_cursor)]

                    return jsonify(response_data)
            else:               
                return jsonify({
                    "errors": [f"no protein for accession '{accession}' found"]
                }), 422

