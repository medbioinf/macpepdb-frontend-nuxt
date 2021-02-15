import json
import sys
import math
import html

from flask import request, render_template

from sqlalchemy import between
from sqlalchemy.orm import sessionmaker

from macpepdb.proteomics.amino_acid import AminoAcid, AMINO_ACIDS_FOR_COUNTING
from macpepdb.proteomics.modification import Modification, ModificationPosition
from macpepdb.proteomics.modification_collection import ModificationCollection
from macpepdb.proteomics.mass.convert import to_int as mass_to_int
from macpepdb.models.peptide import Peptide
from macpepdb.models.protein import Protein
from macpepdb.proteomics.enzymes.digest_enzyme import DigestEnzyme
from macpepdb.proteomics.mass.precursor_range import PrecursorRange
from macpepdb.models.taxonomy import Taxonomy

from app import app, macpepdb
from .application_controller import ApplicationController

class PeptidesController(ApplicationController):
    PEPTIDES_PER_SEARCH_PAGE = 50
    PROTEIN_PEPTIDES_PER_SEARCH_PAGE = 20

    # @staticmethod
    # @app.route("/search", endpoint="search_path")
    # @app.route("/search/<str:search_type>", endpoint="search_for_path")
    # def show(search_type = "peptide"):
    #     return render_template("search/show.j2")

    @staticmethod
    @app.route("/peptides/search", endpoint="search_peptide_path", methods=["GET", "POST"])
    def search():
        errors = []

        amino_acids = [AminoAcid.get_by_one_letter_code(one_letter_code) for one_letter_code in AMINO_ACIDS_FOR_COUNTING ]
        # Need to change this as soon as MaCPepDB offer a reverse lookup or a list for the human readable positions and types
        modification_positions = sorted([str(position) for position in ModificationPosition])

        return render_template(
            "peptides/search.j2", 
            amino_acids = amino_acids,
            modification_positions = modification_positions,
            peptides_per_page = PeptidesController.PEPTIDES_PER_SEARCH_PAGE,
            digest_peptides_per_page = PeptidesController.PROTEIN_PEPTIDES_PER_SEARCH_PAGE
        )
        
    @app.route("/peptides/<string:sequence>", endpoint="peptide_path")
    def show(sequence):
        SessionClass = sessionmaker(bind = macpepdb)
        session = SessionClass()

        peptide = session.query(Peptide).filter(Peptide.sequence == sequence.upper()).one()
        proteins = peptide.proteins.all()
        taxonomies = session.query(Taxonomy).filter(Taxonomy.id.in_([protein.taxonomy_id for protein in proteins])).distinct().all()
        taxonomies = {taxonomy.id: taxonomy for taxonomy in taxonomies}

        session.close()

        return render_template(
            "peptides/show.j2",
            peptide = peptide,
            proteins = proteins,
            taxonomies = taxonomies
        )



