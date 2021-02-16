# MaCPepDB Web
MaCPepDB is a web frontend for the database created with MaCPepDB.


## Development
### Prepare development environment
```bash
# Install necessary dependencies for your distro
sudo pacman -S python python-pip yarn nodejs npm libev

# It is recommended to use a pyenv to make sure the python version is matching
# Follow the instruction to install pyenv on https://github.com/pyenv/pyenv#installation

# Install the correct python version. You can find the needed python version in .python-version at the beginning of the string (.python-version contains the actual name of the python environment).
# The following command will extract the python version from .python-version for you and install it
pyenv install $(cat .python-version | awk 'BEGIN { FS = "/" } ; { print $1 }')

# Create an environment. The following command will extract the python version and environment name from .python-version for you and install it
pyenv virtualenv $(cat .python-version | awk 'BEGIN { FS = "/" } ; { print $1 }') $(cat .python-version | awk 'BEGIN { FS = "/" } ; { print $3 }')

# And activate the environment (later pyenv will do it for you if you enter a folder with a .python-version file)
pyenv activate

# Update pip (to make sure its the newest version)
pip install --upgrade pip

# Install needed python modules
pip install -r ./requirements.txt

# Install node requirements
yarn install
```
Create a `config.local.yaml` (see [Configuration](#Configuration)) and set a local MaCPepDB for developing.

### Start the app
```bash
honcho start
```

## Configuration
The Configuration is split into multiple files which for different environments:
file | read order | environment | purpose
- | - | - | -
`config.yaml` | 1 | all | config definition
`config.development.yaml` | 2 | development | contains all necessary information for the development environment
`config.production.yaml` | 2 | production | some minor adjustments for production
`config.local.yaml` | 4 | all | excluded from GIT, every user specific overwrite

The environment is set by the environment variable `MACPEPDB_ENV`. The default environment is `development`.

You can overwrite some configuration variables and the environment with CLI arguments. For more information run `python ./run.py --help`

## Production
First create a local configuration file by copying `config.yaml` to `config.local.yaml` and adjust it to your needs. You have then two options to run the app:
* [Native deployment](#native-deployment)
* [Docker deployment](#docker-deployment)

In both cases make sure PostgreSQL is running before you start the app.

It is also recommended to use a reverse proxy like NginX to apply encryption with SSL or network rules.

Note: Each app start will create exactly one process to handle incoming requests. To create a high available application start the app multiple times and use NginX as reverse proxy with its build in load balancer. It is important, that all processes have access to the same upload directory and database for consistent data. Take a look into the `docker-compose.yaml` and `nginx-high-available.conf` for more information.

### Native deployment
If you run the application on a bare metal machine, it is recommended to set up a virtual environment with all necessary dependencies. You can follow the development instruction to create one. Then run `python ./run.py --environment production` or `MACPEPDB_ENV=production python ./run.py`

### Docker deployment
First build an image of your configured application with: `docker build --tag="<YOUR_CONTAINER_TAG>" ./`   
Than you can start a container from the new image with:
```bash
    docker run -d --name="<SOME_NAME>" \
    -p <HOST_PORT>:80 \
    <YOUR_CONTAINER_TAG>
```
You can also prepend arguements for the CLI.

If you run this container with other containers like NginX, RabbitMQ or PostgreSQL on the same host, make sure they are accessible on the same, non-default docker network.

You can use [bind mounts](https://docs.docker.com/storage/bind-mounts/) persist the uploaded files and make them available to the host.   
With a bind mount it is also very easy to adjust the configuration without rebuilding the image by mounting a new `config.local.yaml` to `/usr/src/max-decoy-cloud-hq/config.local.yaml`.
