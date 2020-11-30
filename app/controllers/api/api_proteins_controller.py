import sys

from sqlalchemy import between, and_
from sqlalchemy.orm import selectinload, exc as sqlalchemy_exceptions
from flask import request, jsonify, url_for

from trypperdb.proteomics.mass.convert import to_float as mass_to_float
from trypperdb.proteomics.enzymes.digest_enzyme import DigestEnzyme
from trypperdb.models.protein import Protein
from trypperdb.models.peptide import Peptide

from app import app, trypperdb_session
from ..application_controller import ApplicationController

class ApiProteinsController(ApplicationController):
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
                    peptides = enzyme.digest(Protein('>tmp', 'trypperdb_temporary', 'TrypperDB Temporary', data["sequence"], 0, "temporary", False))
                    peptides.sort(key = lambda peptide: peptide.weight)
            elif "accession" in data:
                try:
                    protein = trypperdb_session.query(Protein).filter(Protein.accession == data["accession"]).one()
                except sqlalchemy_exceptions.NoResultFound as error:
                    protein = None

                if protein:                    
                    peptides = protein.peptides.order_by(Peptide.weight).filter(
                        Peptide.number_of_missed_cleavages <= data["maximum_number_of_missed_cleavages"],
                        between(Peptide.length, data["minimum_peptide_length"], data["maximum_peptide_length"])
                    ).all()
                else:
                    errors.append("no protein for accession '{}' found".format(data["accession"]))
            else:
                errors.append("you have to specify sequence or accession")

        if not len(errors):
            peptide_dicts = []
            for peptide in peptides:
                peptide_dict = peptide.to_dict()
                peptide_dict["weight"] = mass_to_float(peptide_dict["weight"])
                peptide_dicts.append(peptide_dict)
            return jsonify({
                "peptides": peptide_dicts,
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
        errors = []

        include_peptides = request.args.get("include_peptides", type=int, default=0)

        response_data = {}

        try:
            protein = trypperdb_session.query(Protein).filter(Protein.accession == accession).one()
        except sqlalchemy_exceptions.NoResultFound as error:
            protein = None

        if protein:
            response_data["protein"] = protein.to_dict()
            response_data["url"] = url_for("protein_path", accession=protein.accession, _external=True)

            if include_peptides:
                peptides = protein.peptides.all()
                peptide_dicts = []
                for peptide in peptides:
                    peptide_dict = peptide.to_dict()
                    peptide_dict["weight"] = mass_to_float(peptide_dict["weight"])
                    peptide_dicts.append(peptide_dict)
                response_data["peptides"] = peptide_dicts
        else:            
            errors.append("no protein for accession '{}' found".format(accession))

        if not len(errors):
            return jsonify(response_data)
        else:   
            return jsonify({
                "errors": errors
            }), 422

