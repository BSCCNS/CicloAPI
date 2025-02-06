# main.py

from fastapi import FastAPI
from cicloapi.core.config import settings
from cicloapi.core.routers import api_router
import uvicorn
import argparse

# Mounts the API and include all routers onto it

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.DESCRIPTION,
    contact=settings.CONTACT,
)
app.include_router(api_router)


def main():
    parser = argparse.ArgumentParser(description="Input for the port address.")
    parser.add_argument("-P", type=int, default=8000, help="Port address.")
    args = parser.parse_args()

    uvicorn.run(app, host="0.0.0.0", port=args.P)
