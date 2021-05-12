import pathlib

from flask import Flask, g as request_store
from psycopg2.pool import ThreadedConnectionPool


from macpepdb.proteomics.mass.convert import to_float as mass_to_float

from .utility.configuration import Configuration, Environment

config, env = Configuration.get_config_and_env()

# File which contains the asset build time created by Webpack
ASSET_BUILDTIME_FILE = pathlib.Path(__file__).parent.resolve().joinpath("static").joinpath("bundle").joinpath("buildtime.txt")

app = Flask('app')
# Default Flask parameter
app.config.update(
    ENV = env.name,
    DEBUG = config['debug'],
    SECRET_KEY = bytes(config['secret'], "ascii"),
    PREFERRED_URL_SCHEME = 'https' if config['use_https'] else 'http'
)

# Read asset build time. It will be appended to all asset urls as version to invalidate old assetes on new builds.
asset_buildtime = ASSET_BUILDTIME_FILE.open("r").read()
get_asset_buildtime = lambda: asset_buildtime

# In development mode read the asset hash on every request to ensure always up to date asset builds
if env == Environment.development:
    get_asset_buildtime = lambda: ASSET_BUILDTIME_FILE.open("r").read()

# Global variables and functions for templates
@app.context_processor
def inject_global_variables():
    return dict(
        get_asset_buildtime = get_asset_buildtime,
        mass_to_float = mass_to_float
    )

# Initialize connection pool for MaCPepDB database
__macpepdb_pool = ThreadedConnectionPool(1, config['macpepdb']['pool_size'], config['macpepdb']['url'])

def get_database_connection():
    """
    Takes a database connection from the pool, stores it in the request_store and returns it.
    It is automatically returned to the database pool after the requests is finished.
    """
    if "database_connection" not in request_store:
        request_store.database_connection = __macpepdb_pool.getconn() # pylint: disable=assigning-non-slot
    return request_store.database_connection

@app.teardown_appcontext
def return_database_connection_to_pool(exception=None):
    """
    Returns the database connection to the pool
    """
    database_connection = request_store.pop("database_connection", None)
    if database_connection:
        __macpepdb_pool.putconn(database_connection)

# Import controllers.
# Do not move this import to the top of the files. Each controller uses 'app' to build the routes.
# Some controllers also import the connection pools.
from .controllers import *