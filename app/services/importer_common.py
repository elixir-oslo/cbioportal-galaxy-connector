import os
import re
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


def load_data_to_cbioportal(study_id_directory_path: str, cbioportal_url: str, incremental: bool = False) -> Dict[str, str]:
    try:
        command = ["python", "/scripts/importer/metaImport.py",
                   "-d" if incremental else "-s", study_id_directory_path,
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


def get_study_directory(study_id: str, path_to_study: str) -> str:
    list_dir = []
    pattern = re.compile(rf"^cancer_study_identifier: {re.escape(study_id)}$")

    # Get list directories in the study directory
    for file in os.listdir(path_to_study):
        d = os.path.join(path_to_study, file)
        if os.path.isdir(d):
            # Only append if a file meta_study.txt is present with the correct study_id
            try:
                with open(os.path.join(d, "meta_study.txt")) as f:
                    for line in f:
                        if pattern.match(line.strip()):
                            list_dir.append(d)
                            break
            except FileNotFoundError:
                pass

    if len(list_dir) == 0:
        logger.error(f"No directory found for study {study_id} in {path_to_study}")
        raise FileNotFoundError(f"No directory found for study {study_id} in {path_to_study}")
    elif len(list_dir) > 1:
        logger.error(f"Multiple directories found for study {study_id} in {path_to_study}")
        raise ValueError(f"Multiple directories found for study {study_id} in {path_to_study}")

    logger.info(f"Study directory found: {list_dir[0]}")

    return list_dir[0]