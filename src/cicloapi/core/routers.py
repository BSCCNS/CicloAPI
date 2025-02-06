# routers.py

from fastapi import APIRouter, Security
from cicloapi.core import endpoints

# We define a router that collects everything together
api_router = APIRouter()
api_router.include_router(endpoints.router, prefix="/tasks")  # API endpoints
