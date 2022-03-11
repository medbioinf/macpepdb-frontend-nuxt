import os

import bjoern

from macpepdb_web_backend import app, env, config
from macpepdb_web_backend.utility.configuration import Environment

if __name__ == '__main__':
    print(f"Start MaCPepDB webinterface in {env.name} mode on {config['interface']}:{config['port']}")

    if env == Environment.production or os.getenv("USE_BJOERN", "false") == "true":
        bjoern.run(app, config['interface'], config['port'])
    else:
        app.run(config['interface'], config['port'])
