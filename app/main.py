import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ipaddress import ip_network, ip_address
from routers import galaxy_image_handler, cbioportal_to_galaxy_handler, galaxy_to_cbioportal_handler
from dependencies import get_env_vars
from utils.logger import setup_logger
from app.middleware.https_redirect import CustomHTTPSRedirectMiddleware
import os

list_unrestricted_endpoints = ["/export-to-galaxy/"]

logger = setup_logger("uvicorn.error")
app = FastAPI()

# Define allowed IPs and subnet
ALLOWED_IPS = ["127.0.0.1"]
DOCKER_SUBNET = os.getenv("DOCKER_SUBNET")
if DOCKER_SUBNET:
    ALLOWED_SUBNET = ip_network(f"{DOCKER_SUBNET}.0/24")
else:
    ALLOWED_SUBNET = None

# Get the LIMIT_IP environment variable (default to false)
LIMIT_IP = os.getenv("LIMIT_IP", "false").lower() == "true"


@app.middleware("http")
async def ip_filter_middleware(request: Request, call_next):
    if LIMIT_IP:
        # Allow access to images and export-to-galaxy endpoint without restricting IP
        if not (request.url.path.startswith("/images/") and request.method == "GET") and request.url.path not in list_unrestricted_endpoints:
            client_ip = ip_address(request.client.host)
            if client_ip not in ALLOWED_IPS and (ALLOWED_SUBNET is None or client_ip not in ALLOWED_SUBNET):
                raise HTTPException(status_code=403, detail="Access forbidden: IP not allowed")
    response = await call_next(request)
    return response

# Configure CORS settings
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

# Get environment variables and display them
dict_env_vars = get_env_vars()

# logger.info(f"Using study directory: {dict_env_vars['study_directory_path']}")
# logger.info(f"Using Galaxy URL: {dict_env_vars['galaxy_url']}")
# logger.info(f"Using cBioPortal URL: {dict_env_vars['cbioportal_url']}")
