import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import galaxy_image_handler, cbioportal_to_galaxy_handler, galaxy_to_cbioportal_handler
from dependencies import get_env_vars
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

# Get environment variables and display then
dict_env_vars = get_env_vars()

# logger.info(f"Using study directory: {dict_env_vars['study_directory_path']}")
# logger.info(f"Using Galaxy URL: {dict_env_vars['galaxy_url']}")
# logger.info(f"Using cBioPortal URL: {dict_env_vars['cbioportal_url']}")
