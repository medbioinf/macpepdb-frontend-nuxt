import sys

from sqlalchemy.orm import sessionmaker, selectinload, exc as sqlalchemy_exceptions
from flask import request, jsonify, url_for

from macpepdb.models.taxonomy import Taxonomy
from macpepdb.models.taxonomy_merge import TaxonomyMerge

from app import app, macpepdb_session
from ..application_controller import ApplicationController

class ApiTaxonomiesController(ApplicationController):
    @staticmethod
    @app.route("/api/taxonomies/search", endpoint="api_taxonomy_search_path", methods=["POST"])
    def search():
        data = request.get_json()
        errors = []

        if not "query" in data:
            errors.append("attribute 'query' is not present")
            if not isinstance(data["query"], str) or not isinstance(data["query"], int):
                errors.append("attribute 'query' is not a string or int")
        
        if not len(errors):
            condition = None
            if isinstance(data["query"], str):
                query = data["query"].replace("*", "%")
                condition = Taxonomy.name.like(query)
            else: 
                condition = Taxonomy.id == data["query"]

            taxonomies = macpepdb_session.query(Taxonomy).filter(condition).all()

            if isinstance(data["query"], int) and not len(taxonomies):
                taxonomy_merge = macpepdb_session.query(TaxonomyMerge).filter(TaxonomyMerge.source_id == data["query"]).one_or_none()
                if taxonomy_merge:
                    taxonomies = macpepdb_session.query(Taxonomy).filter(Taxonomy.id == taxonomy_merge.target_id).all()

            response = []

            for taxonomy in taxonomies:
                response.append({
                    "id": taxonomy.id,
                    "name": taxonomy.name
                })
            return jsonify(response)
        else:
            return jsonify(errors), 422

    @staticmethod
    @app.route("/api/taxonomies/<string:id>", endpoint="api_taxonomy_path")
    def show(id):
        taxonomy = macpepdb_session.query(Taxonomy).filter(Taxonomy.id == id).one_or_none()

        if not taxonomy:
            taxonomy_merge = macpepdb_session.query(TaxonomyMerge).filter(TaxonomyMerge.source_id == id).one_or_none()
            if taxonomy_merge:
                taxonomy = macpepdb_session.query(Taxonomy).filter(Taxonomy.id == taxonomy_merge.target_id).one_or_none()

        response = None
        if taxonomy:
            response = {
                "id": taxonomy.id,
                "name": taxonomy.name,
                "parent": taxonomy.parent_id,
                "children": []
            }
        else:
            return jsonify(["not found"]), 422
        if taxonomy:
            children_id_rows = macpepdb_session.query(Taxonomy.id).filter(Taxonomy.parent_id == taxonomy.id).all()
            response["children"] = [row[0] for row in children_id_rows]
        return jsonify(response)