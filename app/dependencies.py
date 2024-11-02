from fastapi import Depends, HTTPException
import os

def get_env_vars():
    study_directory_path = os.getenv('STUDY_DIRECTORY', '/study')
    cbioportal_url = os.getenv('CBIOPORTAL_URL')
    galaxy_url = os.getenv('GALAXY_URL')
    api_key = os.getenv('CBIOPORTAL_CACHE_API_KEY')


    missing_vars = []
    if not study_directory_path:
        missing_vars.append('STUDY_DIRECTORY')
    if not cbioportal_url:
        missing_vars.append('CBIOPORTAL_URL')
    if not galaxy_url:
        missing_vars.append('GALAXY_URL')
    if not api_key:
        missing_vars.append('CBIOPORTAL_CACHE_API_KEY')

    if missing_vars:
        raise HTTPException(status_code=500, detail=f"Missing environment variables: {', '.join(missing_vars)}")

    return {
        "study_directory_path": study_directory_path.strip(),
        "cbioportal_url": cbioportal_url.strip(),
        "api_key": api_key.strip()
    }