# CicloAPI 1.0
**API for the ciclovias project**

## Instructions

### Docker

1. Build the docker container by running `docker build -t cicloapi .`.
2. Run the docker container by `docker run -p 8000:8000 cicloapi`.
3. The API runs by default in `localhost:8000`.

We also provide a `cicloapi.sh` bash file which builds the docker from scratch and runs it. It allow for a flag `-p`to configure the port in the external machine (within the docker it is 8000 by default).


### Editable instalation

1. Clone the repository.
2. If not installed, install uv `pipx install uv`.
3. Build the package with `uv build`, this will generate the files inside the `dist` folder.
4. Run `pip install -e .` for local installation with editable properties. 
6. Run the server with `cicloapi`.
7. The API runs by default in `localhost:8000`.

### System-wide installation

1. Clone the repository.
2. If not installed, install uv `pipx install uv`.
3. Build the package with `uv build`, this will generate the files inside the `dist` folder.
4. Run `pip install dist/*.whl` to install the whl file. 
5. Run the server with `cicloapi`.
6. The API runs by default in `localhost:8000`.


## Overview

```bash
├── src/cicloapi
│   │   ├── backend/
│   │   │   ├── jobs/scripts
│   │   │   │   ├── downloadloop.py
│   │   │   ├── parameters
│   │   │   │   ├── parameters.py
│   │   │   │   ├── cities.csv
│   │   │   ├── scripts
│   │   │   │   ├── analyze_results.py
│   │   │   │   ├── cluster_pois.py
│   │   │   │   ├── functions.py
│   │   │   │   ├── initialize.py
│   │   │   │   ├── path.py
│   │   │   │   ├── poi_based_generation.py
│   │   │   │   ├── prepare_networks.py
│   │   │   │   ├── prepare_pois.py
│   │   │   │   ├── real_city_metrics.py
│   │   ├── core/
│   │   ├── config.py
│   │   ├── endpoints.py 
│   │   ├── routers.py    
│   ├── data/endpoints
│   ├── schemas/
│   │   ├── schemas.py
│   ├── __init__.py
├── requirements.txt
├── pyproject.toml
├── Dockerfile
├── cicloapi.sh
```

The model runs from within the folder `backend`. The list of cities and the input parameters are in `backend/parameters`. Endpoints are described in `core/endpoints.py`. 