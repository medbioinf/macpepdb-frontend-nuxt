# MaCPepDB Web
MaCPepDB web is a web GUI for the MaCPepDB web API.

## Dependencies
* Docker
* NodeJS 14.x
* yarn
* MaCPepDB 2.x

### For development only
* GIT

## Development
MaCPepDB Web consists of two parts.
1. `macpepdb_web_backend` - A [Flask](https://flask.palletsprojects.com/en/2.0.x/) web application, providing the API endpoints.
2. `macpepdb_web_frontend` - A [NuxtJS](https://nuxtjs.org/) application, providing the web pages.
### Prepare development environment
Start the MaCPepDB web API, than start the GUI
```bash
# Install node requirements
yarn install

### Start the app
```bash
yarn dev
```
The frontend can than be accessed on port `http://localhost:5000`

## Configuration
### Backend configuration
The frontend is configured by 3 environment variables:
| variable | default | description |
| --- | --- | --- |
| MACPEPDB_BACKEND_BASE_URL | `http://localhost:3000` | Base URL for the backend (no trailing slash, must be accessible for the internet browser) |
| MACPEPDB_FRONTEND_INTERFACE | `127.0.0.1` | IP for the frontend |
| MACPEPDB_FRONTEND_PORT | `5000` | Port of the frontend |

## Production
You have two options to run the app:
* [Native deployment](#native-deployment)
* [Docker deployment](#docker-deployment)

### Native deployment
1. Clone the project
2. Prepare the frontend dependencies `yarn install`
3. Prepare the frontend `yarn build`
4. Start the frontend `yarn start`

### Docker deployment
1. Clone the project
3. Build the frontend image `docker build --tag="mpc/macpepdb-web-frontend:<some-version-tag>" -f .`
4. Start the frontend container `docker run -d -it --name="macpepdb-web-frontend" -p <host-port>:<container-port> mpc/macpepdb-web-frontend:<some-version-tag>`
    (Adjust the environments variables with `-e VAR=<VALUE>`)

### Make it available over a single domain and scale it up
For production and combination of backend and frontend into a single domain just merge the nginx.example.conf with the one of MaCPepDB web API.

## Citation and Publication
* **MaCPepDB: A Database to Quickly Access All Tryptic Peptides of the UniProtKB**   
    Julian Uszkoreit, Dirk Winkelhardt, Katalin Barkovits, Maximilian Wulf, Sascha Roocke, Katrin Marcus, and Martin Eisenacher   
    Journal of Proteome Research 2021 20 (4), 2145-2150   
    [DOI: 10.1021/acs.jproteome.0c00967](https://doi.org/10.1021/acs.jproteome.0c00967)