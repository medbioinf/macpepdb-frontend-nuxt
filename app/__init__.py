import pathlib
import gc

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

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
macpepdb = create_engine(config['macpepdb']['url'], pool_size = config['macpepdb']['pool_size'], max_overflow = 0, pool_timeout=None)
macpepdb_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=macpepdb))
# Remove session for macpepdb after request is done
@app.teardown_appcontext
def shutdown_session(exception=None):
    macpepdb_session.remove()
    # Run garbage collection to make sure unnecessary resource from session are freed up.
    gc.collect()

# Import controllers.
# Do not move this import to the top of the files. Each controller uses 'app' to build the routes.
# Some controllers also import the connection pools.
from .controllers import *