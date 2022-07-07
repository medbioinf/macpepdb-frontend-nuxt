from flask import jsonify

from macpepdb.proteomics.modification import ModificationPosition

from macpepdb_web_backend.server import app
from macpepdb_web_backend.controllers.application_controller import ApplicationController

class ApiModificationsController(ApplicationController):
    @staticmethod
    def modification_positions():
        return jsonify({
            "modification_positions": sorted([str(position) for position in ModificationPosition])
        })