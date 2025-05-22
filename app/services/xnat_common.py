import os
from urllib.parse import urlparse
from fastapi import Depends
import requests
from app.dependencies import get_env_vars
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

def get_experiment_uid_from_url(viewer_url: str) -> str:
    """
    Extracts the experiment UID from the viewer URL.
    """
    path = urlparse(viewer_url).path
    return os.path.basename(path)

def get_experiment_label_from_json(subject_data: dict, experiment_uid: str) -> str:
    """
    Extracts the experiment label from the subject data.
    """
    for children in subject_data.get('items')[0].get('children'):
        for child in children.get('items'):
            if child.get('data_fields').get('UID') == experiment_uid:
                logger.debug(f"Experiment UID: {experiment_uid}")
                logger.debug(f"Experiment label: {child.get('data_fields').get('label')}")
                return child.get('data_fields').get('label')
    return None
    


def get_experiment_label_from_xnat(viewer_url: str, cbioportal_study_id: str, cbioportal_case_id: str,  env_vars: dict) -> str:
    
    experiment_uid = get_experiment_uid_from_url(viewer_url)
    xnat_url = env_vars['xnat_url']
    
    # Request the subject json from XNAT
    api_url = f"{xnat_url}/data/projects/{cbioportal_study_id}/subjects/{cbioportal_case_id}?format=json"
    response = requests.get(api_url)
    response.raise_for_status()
    
    subject_data = response.json()
    
    # Extract the experiment label from the subject data
    experiment_label = get_experiment_label_from_json(subject_data, experiment_uid)
    
    if not experiment_label:
        raise ValueError(f"Experiment label not found for UID: {experiment_uid} in study {cbioportal_study_id} and case {cbioportal_case_id}")
    
    return experiment_label

def get_project_label_from_json(project_data: dict, cbioportal_study_id: str) -> str:
    """
    Extracts the project label from the project data.
    """        
    return project_data.get('items')[0].get('data_fields').get('secondary_ID')
        
    
def get_project_label_from_xnat(cbioportal_study_id: str, env_vars: dict) -> str:
    """
    Extracts the project label from the viewer URL.
    """
    xnat_url = env_vars['xnat_url']
    
    # Request the subject json from XNAT
    api_url = f"{xnat_url}/data/projects/{cbioportal_study_id}?format=json"
    response = requests.get(api_url)
    response.raise_for_status()
    
    project_data = response.json()
    
    project_label = get_project_label_from_json(project_data, cbioportal_study_id)
    
    return project_label
    