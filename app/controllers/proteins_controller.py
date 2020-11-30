import math
import textwrap

from flask import request, render_template
from sqlalchemy import join, select, func
from sqlalchemy.orm import sessionmaker

from trypperdb.models.peptide import Peptide
from trypperdb.models.protein import Protein
from trypperdb.models.associacions import proteins_peptides
from trypperdb.models.taxonomy import Taxonomy

from app import app, trypperdb
from .application_controller import ApplicationController


class ProteinsController(ApplicationController):
    PEPTIDES_PER_SEARCH_PAGE = 50

    @staticmethod
    @app.route("/proteins/<string:accession>", endpoint="protein_path")
    @app.route("/proteins/<string:accession>/<int:page>", endpoint="protein_page_path")
    def show(accession, page = 1):
        SessionClass = sessionmaker(bind = trypperdb)
        session = SessionClass()

        protein = session.query(Protein).filter(Protein.accession == accession).one()

        peptide_count = session.execute(select([func.count()]).where(proteins_peptides.c.protein_id == protein.id).select_from(proteins_peptides)).scalar()

        page_count = max(math.ceil(peptide_count / float(ProteinsController.PEPTIDES_PER_SEARCH_PAGE)), 1)
        if page < 1:
            page = 1
        elif page > page_count:
            page = page_count
        
        peptides = protein.peptides.order_by(Peptide.weight).limit(ProteinsController.PEPTIDES_PER_SEARCH_PAGE).offset(ProteinsController.PEPTIDES_PER_SEARCH_PAGE * (page - 1)).all()

        taxonomy = session.query(Taxonomy).filter(Taxonomy.id == protein.taxonomy_id).one()

        session.close()

        return render_template(
            "proteins/show.j2",
            protein = protein,
            peptides = peptides,
            page_count = page_count,
            current_page = page - 1,
            taxonomy = taxonomy
        )

    @staticmethod
    @app.route("/proteins", endpoint="proteins_path")
    def index():
        return render_template("proteins/index.j2")
