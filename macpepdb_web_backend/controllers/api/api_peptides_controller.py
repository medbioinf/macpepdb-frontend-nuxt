import itertools

from flask import request, jsonify

from macpepdb.database.query_helpers.where_condition import WhereCondition
from macpepdb.models.peptide import Peptide
from macpepdb.models.protein import Protein
from macpepdb.models.protein_peptide_association import ProteinPeptideAssociation
from macpepdb.proteomics.mass.convert import to_float as mass_to_float
from macpepdb.proteomics.enzymes.digest_enzyme import DigestEnzyme

from macpepdb_web_backend import app, get_database_connection
from macpepdb_web_backend.models.convert import peptide_to_dict, protein_to_dict
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
        is_reviewed = request.args.get("is_reviewed", None)
        if is_reviewed is not None:
            is_reviewed = bool(is_reviewed)
        sequence = sequence.upper()
        database_connection = get_database_connection()
        with database_connection.cursor() as database_cursor:
            peptide = Peptide(sequence, 0, None)
            peptide = Peptide.select(
                database_cursor,
                WhereCondition(
                    ["partition = %s", "AND", "mass = %s", "AND", "sequence = %s"],
                    [peptide.partition, peptide.mass, peptide.sequence]
                ),
                include_metadata=True
            )
            if peptide is None:
                return jsonify({
                    "errors": {
                        "sequence": ["not found"]
                    }
                }), 404
            # Return peptide if is_reviewed is not requested (None),
            # or is_reviewed is requested and True and metadata is_swiss_prot is also True
            # or is_reviewed is requested and False and metadata is_trembl is True
            if is_reviewed is None \
                or is_reviewed and peptide.metadata.is_swiss_prot \
                or not is_reviewed and peptide.metadata.peptide.metadata.is_trembl:
                return jsonify(peptide_to_dict(peptide))

    @staticmethod
    @app.route("/api/peptides/<string:sequence>/proteins", endpoint="api_peptide_proteins_path", methods=["GET"])
    def proteins(sequence: str):
        peptide = Peptide(sequence.upper(), 0)
        database_connection = get_database_connection()
        with database_connection.cursor() as database_cursor:
            proteins = Protein.select(
                database_cursor,
                WhereCondition(
                    [
                        f"accession = ANY(SELECT protein_accession FROM {ProteinPeptideAssociation.TABLE_NAME} as ppa WHERE ppa.partition = %s AND ppa.peptide_mass = %s AND ppa.peptide_sequence = %s)"
                    ],
                    [
                        peptide.partition,
                        peptide.mass,
                        peptide.sequence
                    ]
                ),
                True
            )

            reviewed_proteins_rows = []
            unreviewed_proteins_rows = []

            for protein in proteins:
                if protein.is_reviewed:
                    reviewed_proteins_rows.append(
                        protein_to_dict(protein)
                    )
                else:
                    unreviewed_proteins_rows.append(
                        protein_to_dict(protein)
                    )

            return jsonify({
                "reviewed_proteins": reviewed_proteins_rows,
                "unreviewed_proteins": unreviewed_proteins_rows
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

    