# main.py

import os
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from galaxy_image_handler import router as image_router
from cbioportal_to_galaxy_handler import validate_and_fix_url, export_to_galaxy

logger = logging.getLogger("uvicorn.error")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(image_router)

raw_galaxy_url = os.getenv('GALAXY_URL', 'http://localhost:8081').strip()
try:
    galaxy_url = validate_and_fix_url(raw_galaxy_url)
    logger.info(f"Using Galaxy URL: {galaxy_url}")
except ValueError as e:
    logger.error(f"Error in URL validation: {e}")
    raise

@app.post("/export-to-galaxy")
async def export_to_galaxy_endpoint(request: Request):
    return await export_to_galaxy(request, galaxy_url)