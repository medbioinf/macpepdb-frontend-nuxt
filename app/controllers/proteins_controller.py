import math
import textwrap

from flask import request, render_template, abort
from sqlalchemy import join, select, func
from sqlalchemy.orm import sessionmaker

from macpepdb.models.peptide import Peptide
from macpepdb.models.protein import Protein
from macpepdb.models.protein_peptide_association import ProteinPeptideAssociation
from macpepdb.models.taxonomy import Taxonomy

from app import app, get_database_connection
from .application_controller import ApplicationController


class ProteinsController(ApplicationController):
    PEPTIDES_PER_SEARCH_PAGE = 50

    @staticmethod
    @app.route("/proteins/<string:accession>", endpoint="protein_path")
    @app.route("/proteins/<string:accession>/<int:page>", endpoint="protein_page_path")
    def show(accession, page = 1):
        database_connection = get_database_connection()
        with database_connection.cursor() as database_cursor:

            protein = Protein.select(database_cursor, ("accession = %s", [accession]))
            if not protein:
                abort(404)

            database_cursor.execute(f"SELECT COUNT(*) FROM {ProteinPeptideAssociation.TABLE_NAME} WHERE protein_accession = %s;", (protein.accession,))
            peptide_count = database_cursor.fetchone()[0]

            page_count = max(math.ceil(peptide_count / float(ProteinsController.PEPTIDES_PER_SEARCH_PAGE)), 1)
            if page < 1:
                page = 1
            elif page > page_count:
                page = page_count
            
            peptides = protein.peptides(database_cursor, order_by = "mass", offset = ProteinsController.PEPTIDES_PER_SEARCH_PAGE * (page - 1), limit = ProteinsController.PEPTIDES_PER_SEARCH_PAGE)

            taxonomy = Taxonomy.select(database_cursor, ("id = %s", [protein.taxonomy_id]))

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
