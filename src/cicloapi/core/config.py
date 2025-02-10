# config.py

from dotenv import load_dotenv
from pathlib import Path

# Load the environment file
BASE_DIR = Path.cwd()
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

# Setting for the API


class Settings:
    PROJECT_NAME: str = "CicloAPI"
    DESCRIPTION: str = "API for the ciclovias project."
    CONTACT: dict[str] = {"name": "M. Herrero", "e-mail": "mherrero@bsc.es"}
    PROJECT_VERSION: str = "1.0"

class DB_settings:
    host="localhost"          # PostgreSQL server hostname
    port= 5433               # Port number (use 5432 or the one you exposed)
    database="CICLOAPI"       # Database name
    user="postgres"              # Username
    password="rogerbsc"        # Password



settings = Settings()
