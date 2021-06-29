from flask import jsonify

from macpepdb.proteomics.modification import ModificationPosition

from macpepdb_web_backend import app
from macpepdb_web_backend.controllers.application_controller import ApplicationController

class ApiTaxonomiesController(ApplicationController):
    @staticmethod
    @app.route("/api/modifications/positions", endpoint="api_modification_position_path")
    def modification_positions():
        return jsonify({
            "modification_positions": sorted([str(position) for position in ModificationPosition])
        })