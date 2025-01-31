import secrets
import logging
from pathlib import Path

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

BASE_DIR = Path.cwd()
ENV_PATH = BASE_DIR / ".env"

def generate_secret_key():
    """Generates a 32-character (16-bit) secret key."""
    return secrets.token_hex(16)

def generate_env_variable():
    """Generates a random SECRET_KEY and saves it if not already set."""
    if ENV_PATH.exists():
        with open(ENV_PATH, "r") as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("SECRET_KEY="):
                    logging.info(f"SECRET_KEY already exists in {ENV_PATH}, skipping.")
                    return

    secret_key = generate_secret_key()
    
    with open(ENV_PATH, "a") as f:  
        f.write(f"SECRET_KEY={secret_key}\n")
    
    logging.info(f"Generated SECRET_KEY and saved to {ENV_PATH}")

if __name__ == "__main__":
    generate_env_variable()