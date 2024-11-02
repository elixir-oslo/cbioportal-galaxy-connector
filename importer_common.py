import subprocess
import logging
from fastapi import HTTPException, Request
from typing import Dict

logger = logging.getLogger(__name__)

def clear_cache_cbioportal(cbioportal_url: str, api_key: str) -> Dict[str, str]:
    try:
        # Clear cBioportal cache
        command = ["curl", "-X", "DELETE",
                   f"{cbioportal_url}/api/cache",
                   "-H", f"X-API-KEY: {api_key}"]

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"Failed to clear cache: {result.stderr}")
            raise HTTPException(status_code=500, detail=result.stderr)

        logger.info(f"Cache cleared: {result.stdout}")
        return {"output": result.stdout}
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def incremental_load_data_to_cbioportal(path_study_id_directory: str, cbioportal_url: str) -> Dict[str, str]:
    try:
        # Construct the load command
        command = ["python", "/scripts/importer/metaImport.py",
                   "-d", path_study_id_directory,
                   "-u", cbioportal_url,
                   "-o"]

        # Run the load command
        result = subprocess.run(command, capture_output=True, text=True)

        # Check if the command was successful
        if result.returncode != 0:
            logger.error(f"Failed to load data: {result.stderr}")
            raise HTTPException(status_code=500, detail=result.stderr)

        logger.info(f"Data loaded: {result.stdout}")
        return {"output": result.stdout}
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))