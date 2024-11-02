import subprocess
import logging
from fastapi import HTTPException
from typing import Dict

logger = logging.getLogger(__name__)


def clear_cache_cbioportal(cbioportal_url: str, api_key: str) -> Dict[str, str]:
    try:
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


def incremental_load_data_to_cbioportal(study_id_directory_path: str, cbioportal_url: str) -> Dict[str, str]:
    try:
        command = ["python", "/scripts/importer/metaImport.py",
                   "-d", study_id_directory_path,
                   "-u", cbioportal_url,
                   "-o"]

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"Failed to load data: {result.stderr}")
            raise HTTPException(status_code=500, detail=result.stderr)

        logger.info(f"Data loaded: {result.stdout}")
        return {"output": result.stdout}
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))
