# main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_redoc_html
from cicloapi.core.config import settings
from cicloapi.core.routers import api_router
import uvicorn
import argparse
from fastapi.openapi.utils import get_openapi
from pathlib import Path

# Mounts the API and include all routers onto it

app = FastAPI(redoc_url=None)
app.include_router(api_router)

####################################
####################################
# Endpoint for logos
path = Path(__file__).parent / "images"
app.mount("/images", StaticFiles(directory=path), name="images")

# Custom OpenAPI schema to include logo.
def custom_openapi():

    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        summary=settings.SUMMARY,
        description=settings.DESCRIPTION,
        routes=app.routes
    )

    openapi_schema["info"]["x-logo"] = {
        "url": "/images/Logo_blue.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


@app.get("/redoc", include_in_schema=False)
def overridden_redoc():
	return get_redoc_html(
        openapi_url="/openapi.json", 
        title="CicloAPI", 
        redoc_favicon_url="/images/favicon.png"
    )



#####################################
#####################################
def main():
    parser = argparse.ArgumentParser(description="Input for the port address.")
    parser.add_argument("-P", type=int, default=8000, help="Port address.")
    args = parser.parse_args()

    uvicorn.run(app, host="0.0.0.0", port=args.P)
