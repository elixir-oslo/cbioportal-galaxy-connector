from fastapi import Depends, HTTPException
import os

def get_env_vars():
    study_directory_path = os.getenv('STUDY_DIRECTORY', '/study')
    cbioportal_url = os.getenv('CBIOPORTAL_URL')
    galaxy_url = os.getenv('GALAXY_URL')
    xnat_url = os.getenv('XNAT_URL', None)
    api_key = os.getenv('CBIOPORTAL_CACHE_API_KEY')
    galaxy_workflow_name = os.getenv('GALAXY_WORKFLOW_NAME', None)
    image_upload_directory = os.getenv('IMAGE_UPLOAD_DIRECTORY', '/uploaded_images')


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
        "api_key": api_key.strip(),
        "galaxy_url": galaxy_url.strip(),
        "galaxy_workflow_name": galaxy_workflow_name.strip() if galaxy_workflow_name else None,
        "image_upload_directory": image_upload_directory.strip(),
        "xnat_url": xnat_url.strip() if xnat_url else None
    }