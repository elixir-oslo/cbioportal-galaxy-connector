# main.py
import os
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from galaxy_image_handler import router as image_router
from cbioportal_to_galaxy_handler import validate_and_fix_url, export_to_galaxy
from galaxy_to_cbioportal_handler import export_timeline_to_cbioportal

logger = logging.getLogger("uvicorn.error")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the image router
app.include_router(image_router)

# Get the Galaxy URL from the environment variables
raw_galaxy_url = os.getenv('GALAXY_URL', 'http://localhost:8081').strip()
try:
    galaxy_url = validate_and_fix_url(raw_galaxy_url)
    logger.info(f"Using Galaxy URL: {galaxy_url}")
except ValueError as e:
    logger.error(f"Error in URL validation: {e}")
    raise

# Get the study directory from the environment variables
path_study_directory = os.getenv('STUDY_DIRECTORY', '/study').strip()

# Get cBioPortal URL from the environment variables
cbioportal_url = os.getenv('CBIOPORTAL_URL', 'http://localhost:8080').strip()
cbioportal_cache_api_key = os.getenv('CBIOPORTAL_CACHE_API_KEY', 'fd15f1ae-66f2-4b8a-8d54-fb899b03557e').strip()


@app.post("/export-to-galaxy")
async def export_to_galaxy_endpoint(request: Request):
    return await export_to_galaxy(request, galaxy_url)

@app.post("/export-timeline-to-cbioportal")
async def export_timeline_to_cbioportal_endpoint(request: Request):
    return await export_timeline_to_cbioportal(request, path_study_directory, cbioportal_url, cbioportal_cache_api_key)
