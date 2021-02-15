from flask import render_template

from app import app
from .application_controller import ApplicationController

class ApplicationController(ApplicationController):
    @staticmethod
    @app.route("/documentations/api", endpoint="api_documentation_path")
    def api():
        return render_template('documentations/api.j2')
