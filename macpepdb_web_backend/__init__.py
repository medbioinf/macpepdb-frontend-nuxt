import json
import traceback
from logging import error

from flask import Flask, g as request_store, request
from flask.json import jsonify
from threading import Thread
from werkzeug.exceptions import HTTPException


from macpepdb.proteomics.mass.convert import to_float as mass_to_float

from macpepdb_web_backend.database.connection_pool import ConnectionPool
from macpepdb_web_backend.utility.configuration import Configuration
from macpepdb_web_backend.utility.headers.cross_origin_resource_sharing import add_allow_cors_headers
from macpepdb_web_backend.utility.matomo import track_request as matomo_track_request

config, env = Configuration.get_config_and_env()

app = Flask('app')
# Default Flask parameter
app.config.update(
    ENV = env.name,
    DEBUG = config['debug'],
    SECRET_KEY = bytes(config['secret'], "ascii"),
    PREFERRED_URL_SCHEME = 'https' if config['use_https'] else 'http'
)

# Global variables and functions for templates
@app.context_processor
def inject_global_variables():
    return dict(
        mass_to_float = mass_to_float
    )


macpepdb_pool = ConnectionPool(1, config['macpepdb']['pool_size'], config['macpepdb']['url'])
"""Connection pool for MaCPepDB database.
Use `get_database_connection` to get a database connection which is valid during a request request.
It will be put back automatically.
However, if you want to use a database connection in a generator for streaming,
you have to manually get and put back the connection.
The best way to deal with it in a generator, is to use a try/catch-block
and put the connection back when GeneratorExit is thrown or in the finally-block.
"""

def get_database_connection():
    """
    Takes a database connection from the pool, stores it in the request_store and returns it.
    It is automatically returned to the database pool after the requests is finished.
    """
    if "database_connection" not in request_store:
        request_store.database_connection = macpepdb_pool.getconn() # pylint: disable=assigning-non-slot
    return request_store.database_connection

@app.before_request
def track_request():
    if config["matomo"]["enabled"]:
        track_thread = Thread(target=matomo_track_request, args=(
            request.headers.get("User-Agent", ""),
            request.remote_addr,
            request.headers.get("Referer", ""),
            request.headers.get("Accept-Language", ""),
            request.headers.get("Host", ""),
            request.full_path,
            request.query_string,
            request.url.startswith("https"),
            config["matomo"]["url"],
            config["matomo"]["site_id"],
            config["matomo"]["auth_token"], 
            app,
            config["debug"]
        ))
        track_thread.start()
        request_store.track_thread = track_thread 

@app.teardown_appcontext
def return_database_connection_to_pool(exception=None):
    """
    Returns the database connection to the pool
    """
    database_connection = request_store.pop("database_connection", None)
    if database_connection:
        macpepdb_pool.putconn(database_connection)

@app.teardown_appcontext
def wait_for_track_request(exception=None):
    track_thread = request_store.pop("track_thread", None)
    if track_thread:
        track_thread.join()

@app.errorhandler(Exception)
def handle_exception(e):
    response = None
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        # Return JSON instead of HTML for HTTP errors
        # start with the correct headers and status code from the error
        response = e.get_response()
        # replace the body with JSON
        response.data = json.dumps({
            "errors": {
                "general": e.description
            }
        })
        response.content_type = "application/json"
    else:
        response = app.response_class(
            response=json.dumps({
                "errors": {
                    "general": str(e)
                }
            }),
            status=500,
            mimetype='application/json'
        )
    if config['debug']:
        app.logger.error(traceback.format_exc())
        response = add_allow_cors_headers(response)
    return response

if config['debug']:
    @app.after_request
    def add_cors_header_in_development_mode(response):
        return add_allow_cors_headers(response)


# Import controllers.
# Do not move this import to the top of the files. Each controller uses 'app' to build the routes.
# Some controllers also import the connection pools.
from .controllers import *