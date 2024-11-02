import os
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routers import galaxy_image_handler, cbioportal_to_galaxy_handler, galaxy_to_cbioportal_handler
from utils.logger import setup_logger

logger = setup_logger("uvicorn.error")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(galaxy_image_handler.router)
app.include_router(cbioportal_to_galaxy_handler.router)
app.include_router(galaxy_to_cbioportal_handler.router)

# Environment variables and other setup code...

# Get environment variables
raw_galaxy_url = os.getenv('GALAXY_URL', 'http://localhost:8081').strip()


study_directory_path = os.getenv('STUDY_DIRECTORY', '/study').strip()
logger.info(f"Using study directory: {study_directory_path}")

cbioportal_url = os.getenv('CBIOPORTAL_URL', 'http://localhost:8080').strip()
logger.info(f"Using cBioPortal URL: {cbioportal_url}")
cbioportal_cache_api_key = os.getenv('CBIOPORTAL_CACHE_API_KEY', 'fd15f1ae-66f2-4b8a-8d54-fb899b03557e').strip()


