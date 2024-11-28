from typing import Dict

from fastapi import APIRouter, HTTPException, Request, Depends
from app.utils.logger import setup_logger
import time
from bioblend.galaxy import GalaxyInstance
from requests.exceptions import ConnectionError
from datetime import datetime
import tempfile
from urllib.parse import urlparse

from app.dependencies import get_env_vars

router = APIRouter()
logger = setup_logger(__name__)


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


def get_galaxy_instance_from_request(data: dict, env_vars: dict) -> GalaxyInstance:
    galaxy_token = data.get('galaxyToken')
    galaxy_url = env_vars['galaxy_url']
    if not galaxy_token:
        logger.error("Missing Galaxy token in the request.")
        raise ValueError("Missing Galaxy token in the request.")
    return get_galaxy_instance(galaxy_url, galaxy_token)


def get_or_create_galaxy_history(gi: GalaxyInstance, galaxy_history_name: str) -> str:
    histories = gi.histories.get_histories(name=galaxy_history_name)
    if histories:
        return histories[0]['id']
    else:
        history = gi.histories.create_history(name=galaxy_history_name)
        return history['id']


def get_workflow_id(gi: GalaxyInstance, workflow_name: str) -> str:
    workflows = gi.workflows.get_workflows(name=workflow_name)
    if workflows:
        return workflows[0]['id']
    else:
        raise ValueError(f"Workflow with name {workflow_name} not found")


def upload_data_to_galaxy(gi: GalaxyInstance, history_id: str, data: str, cbioportal_study_id: str,
                          cbioportal_case_id: str) -> dict:
    if not data:
        logger.error("Missing data in the request.")
        raise ValueError("Missing data in the request.")
    return upload_data_string(gi, history_id, data, cbioportal_study_id, cbioportal_case_id)


@router.post("/export-to-galaxy/")
async def export_to_galaxy(request: Request, env_vars: dict = Depends(get_env_vars)) -> dict:
    try:
        data = await request.json()
        logger.debug(f"Received data: {data}")

        gi = get_galaxy_instance_from_request(data, env_vars)
        logger.info("Created GalaxyInstance successfully")

        history_id = get_or_create_galaxy_history(gi, data.get('galaxyHistoryName'))
        logger.info(f"Working with history ID: {history_id}")

        upload_info = upload_data_to_galaxy(gi, history_id, data.get('data'), data.get('studyId'), data.get('caseId'))
        logger.info(f"Uploaded: {upload_info['outputs'][0]['name']}, ID: {upload_info['outputs'][0]['id']}")

        return {"message": "Data received successfully"}
    except ConnectionError as e:
        logger.error(f"Connection error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to establish a new connection: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/galaxy-workflow/")
async def galaxy_workflow(request: Request, env_vars: dict = Depends(get_env_vars)) -> dict:
    try:
        data = await request.json()
        logger.debug(f"Received data: {data}")

        gi = get_galaxy_instance_from_request(data, env_vars)
        logger.info("Created GalaxyInstance successfully")

        history_id = get_or_create_galaxy_history(gi, data.get('galaxyHistoryName'))
        logger.info(f"Working with history ID: {history_id}")

        data_header, data_body = data.get('data').split('\n', 1)
        fixed_header = data_header.replace(' ', '_').lower()

        data_modified = f"{fixed_header}\n{data_body}"

        upload_info = upload_data_to_galaxy(gi, history_id, data_modified, data.get('studyId'), data.get('caseId'))
        logger.info(f"Uploaded: {upload_info['outputs'][0]['name']}, ID: {upload_info['outputs'][0]['id']}")
        logger.debug(f"Information: {upload_info}")

        # Bioblend, get workflow ID from name from environment variable
        workflow_id = get_workflow_id(gi, env_vars['galaxy_workflow_name'])

        # List files in history every 5 seconds for 2 minutes
        for _ in range(24):
            files = gi.histories.show_history(history_id, contents=True)
            for file in files:
                if file['name'] == upload_info['outputs'][0]['name'] and file['state'] == 'ok':
                    logger.info(f"File {file['name']} is ready")
                    logger.debug(f"File info: {file}")
                    break
            else:
                time.sleep(5)
                continue
            break
        else:
            raise ValueError("No files found in history after 2 minutes")



        inputs = {
            '0': {  # Step ID in the workflow
                'src': 'hda',  # Source type: hda (history dataset)
                'id': upload_info['outputs'][0]['id']  # Dataset ID
            }
        }

        # get file content from uploaded file
        file_content = gi.datasets.show_dataset(upload_info['outputs'][0]['id'])
        logger.info(f"File content: {file_content}")
        logger.info(f"File uploaded: {upload_info}")

        logger.info(f"inputs: {inputs}")

        # Fetch the workflow details
        workflow = gi.workflows.show_workflow(workflow_id)
        inputs = workflow['inputs']

        # Assuming the workflow has a single input we want to map to our uploaded dataset
        # input_id = list(inputs.keys())[0]
        logger.info(f"Input ID: {inputs}")



        # Bioblend, invoke workflow
        workflow_info = gi.workflows.invoke_workflow(workflow_id,
                                                     inputs=inputs,
                                                     history_id=history_id)
        logger.info(f"Workflow info: {workflow_info}")

        return {"message": "Data received successfully"}

        # workflow_id = data.get('workflowId')
        # if not workflow_id:
        #     logger.error("Missing workflow ID in the request.")
        #     raise ValueError("Missing workflow ID in the request.")
        #
        # inputs = data.get('inputs')
        # if not inputs:
        #     logger.error("Missing inputs in the request.")
        #     raise ValueError("Missing inputs in the request.")
        #
        # workflow_info = gi.workflows.invoke_workflow(workflow_id, inputs=inputs, history_id=history_id)
        # logger.info(f"Invoked workflow: {workflow_info['id']}")
        #
        # return {"message": "Workflow invoked successfully"}
    except ConnectionError as e:
        logger.error(f"Connection error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to establish a new connection: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))
