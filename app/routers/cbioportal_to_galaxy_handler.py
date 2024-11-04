from typing import Dict

from fastapi import APIRouter, HTTPException, Request, Depends
import logging
import time
from bioblend.galaxy import GalaxyInstance
from requests.exceptions import ConnectionError
from datetime import datetime
import tempfile
from urllib.parse import urlparse

from app.dependencies import get_env_vars


router = APIRouter()
logger = logging.getLogger(__name__)

def validate_and_fix_url(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.scheme:
        raise ValueError(f"Missing scheme in URL: {url}")
    if parsed.scheme not in ["http", "https"]:
        raise ValueError(f"Unsupported scheme in URL: {url}")
    return url


def get_galaxy_instance(url: str, key: str, max_retries: int = 5, delay: int = 5) -> GalaxyInstance:
    logger.info(f"Creating GalaxyInstance with URL: {url}")
    for attempt in range(max_retries):
        try:
            return GalaxyInstance(url, key)
        except ConnectionError as e:
            if attempt < max_retries - 1:
                logger.debug(f"Attempt {attempt + 1} failed, retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error(f"Failed to establish a new connection: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to establish a new connection: {e}")


def upload_data_string(galaxy_instance: GalaxyInstance, history_id: str, data_string: str, study_id: str, case_id: str,
                       file_suffix: str = 'data.txt') -> Dict[str, str]:
    current_time = datetime.now().strftime("%Y%m%dT%H%M")
    if case_id:
        file_name = f"{current_time}_{study_id}_{case_id}_{file_suffix}"
    else:
        file_name = f"{current_time}_{study_id}_{file_suffix}"

    with tempfile.NamedTemporaryFile(delete=True, mode='w', suffix=file_name) as tmp_file:
        tmp_file.write(data_string)
        tmp_file_path = tmp_file.name
        upload_info = galaxy_instance.tools.upload_file(tmp_file_path, history_id, file_name=file_name)
    return upload_info

@router.post("/export-to-galaxy/")
async def export_to_galaxy(request: Request, env_vars: dict = Depends(get_env_vars)) -> dict:
    try:
        data = await request.json()
        logger.debug(f"Received data: {data}")

        galaxy_token = data.get('galaxyToken')
        galaxy_history_name = data.get('galaxyHistoryName')
        cbioportal_study_id = data.get('studyId')
        cbioportal_case_id = data.get('caseId')
        galaxy_url = env_vars['galaxy_url']

        if not galaxy_token or not galaxy_history_name or 'data' not in data:
            logger.error("Missing required fields in the request.")
            raise ValueError("Missing required fields in the request.")

        gi = get_galaxy_instance(galaxy_url, galaxy_token)
        logger.info("Created GalaxyInstance successfully")

        histories = gi.histories.get_histories(name=galaxy_history_name)
        if histories:
            history_id = histories[0]['id']
        else:
            history = gi.histories.create_history(name=galaxy_history_name)
            history_id = history['id']

        logger.info(f"Working with history ID: {history_id}")

        data_modified = data.get('data')
        upload_info = upload_data_string(gi, history_id, data_modified, cbioportal_study_id, cbioportal_case_id)
        logger.info(f"Uploaded: {upload_info['outputs'][0]['name']}, ID: {upload_info['outputs'][0]['id']}")

        return {"message": "Data received successfully"}
    except ConnectionError as e:
        logger.error(f"Connection error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to establish a new connection: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))
