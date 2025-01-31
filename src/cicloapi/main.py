# main.py

from fastapi import FastAPI
from cicloapi.core.config import settings
from cicloapi.core.routers import api_router
import uvicorn

# Mounts the API and include all routers onto it

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.DESCRIPTION,
    contact=settings.CONTACT,
)
app.include_router(api_router)

def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)
