import sys

from sqlalchemy.orm import sessionmaker, selectinload, exc as sqlalchemy_exceptions
from flask import request, jsonify, url_for

from macpepdb.models.taxonomy import Taxonomy
from macpepdb.models.taxonomy_merge import TaxonomyMerge

from app import app, get_database_connection
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
                condition = ("name LIKE %s", [query])
            else: 
                condition = ("id = %s", [data["query"]])

            database_connection = get_database_connection()
            with database_connection.cursor() as database_cursor:
                taxonomies = Taxonomy.select(database_cursor, condition, fetchall=True)

                if isinstance(data["query"], int) and not len(taxonomies):
                    taxonomy_merge = TaxonomyMerge.select(database_cursor, ("source_id = %s", [data["query"]]))
                    if taxonomy_merge:
                        taxonomies = Taxonomy.select(database_cursor, ("id = %s", [taxonomy_merge.target_id]), fetchall=True)

                response = [{
                    "id": taxonomy.id,
                    "name": taxonomy.name
                } for taxonomy in taxonomies]

            return jsonify(response)
        else:
            return jsonify(errors), 422

    @staticmethod
    @app.route("/api/taxonomies/<int:id>", endpoint="api_taxonomy_path")
    def show(id):
        database_connection = get_database_connection()
        with database_connection.cursor() as database_cursor:
            taxonomy = Taxonomy.select(database_cursor, ("id = %s", [id]))

            if not taxonomy:
                taxonomy_merge = TaxonomyMerge.select(database_cursor, ("source_id = %s", [id]))
                if taxonomy_merge:
                    taxonomy = Taxonomy.select(database_cursor, ("id = %s", [taxonomy_merge.target_id]))


            response = None
            if taxonomy:
                response = {
                    "id": taxonomy.id,
                    "name": taxonomy.name,
                    "parent": taxonomy.parent_id,
                    "children": [taxonomy.id for taxonomy in taxonomy.children(database_cursor)]
                }

        if response:
            return jsonify(response)
        else:
            return jsonify(["not found"]), 422
        