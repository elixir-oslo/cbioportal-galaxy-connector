import tempfile
from datetime import datetime
from io import StringIO
import time
import os

import pandas as pd
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from bioblend.galaxy import GalaxyInstance
from requests.exceptions import ConnectionError
import logging
from urllib.parse import urlparse


logger = logging.getLogger("uvicorn.error")
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

def validate_and_fix_url(url):
    parsed = urlparse(url)
    if not parsed.scheme:
        raise ValueError(f"Missing scheme in URL: {url}")
    if parsed.scheme not in ["http", "https"]:
        raise ValueError(f"Unsupported scheme in URL: {url}")
    return url

# Configuration
# galaxy_url = 'http://localhost:8090'

# Configuration from environment variables
# galaxy_url = os.getenv('GALAXY_URL', 'http://localhost:8081')
# logger.info(f"Using Galaxy URL: {galaxy_url}")

# Configuration from environment variables
raw_galaxy_url = os.getenv('GALAXY_URL', 'http://localhost:8090').strip()
try:
    print(raw_galaxy_url)
    print(type(raw_galaxy_url))
    galaxy_url = validate_and_fix_url(raw_galaxy_url)
    logger.info(f"Using Galaxy URL: {galaxy_url}")
except ValueError as e:
    logger.error(f"Error in URL validation: {e}")
    raise




def get_galaxy_instance(url, key, max_retries=5, delay=5):
    logger.info(f"Creating GalaxyInstance with URL: {url}")
    for attempt in range(max_retries):
        try:
            return GalaxyInstance(url, key)
        except ConnectionError as e:
            if attempt < max_retries - 1:
                logger.info(f"Attempt {attempt + 1} failed, retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise HTTPException(status_code=500, detail=f"Failed to establish a new connection: {e}")


def prepare_data(tab_string):
    file_like_object = StringIO(tab_string)

    data = pd.read_csv(file_like_object, sep='\t', header=0)
    data[['patient_id', 'sample_id']] = data['Samples'].str.split('-', n=1, expand=True)
    data['mutation_id'] = data['patient_id'].astype(str) + ':' + data['Chromosome'].astype(str) + ':' + data[
        'Start Pos'].astype(str) + ':' + data['Ref'].astype(str)


    # Drop rows with NaN values in 'col1'
    data = data.dropna(subset=['Variant Reads'])
    data['Variant Reads'] = data['Variant Reads'].astype(int)

    data = data.dropna(subset=['Ref Reads'])
    data['Ref Reads'] = data['Ref Reads'].astype(int)

    # Rename column 'Ref Reads' to 'alt_counts'
    data = data.rename(columns={'Ref Reads': 'ref_counts'})
    data = data.rename(columns={'Variant Reads': 'alt_counts'})



    # Create a StringIO object to hold the output
    buffer = StringIO()

    # Write the DataFrame to the buffer as a CSV using tab as the separator with headers
    data.to_csv(buffer, sep='\t', index=False, header=True)

    # Get the string value from the buffer
    tab_delimited_string = buffer.getvalue()

    return tab_delimited_string


def upload_data_string(galaxy_instance, history_id, data_string, study_id, case_id, file_suffix='data.txt'):

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


@app.post("/export-to-galaxy")
async def export_to_galaxy(request: Request):
    try:
        data = await request.json()
        logger.debug(f"Received data: {data}")

        galaxy_token = data.get('galaxyToken')
        galaxy_history_name = data.get('galaxyHistoryName')
        cbioportal_study_id = data.get('studyId')
        cbioportal_case_id = data.get('caseId')

        if not galaxy_token or not galaxy_history_name or 'data' not in data:
            raise ValueError("Missing required fields in the request.")

        # Create a Galaxy instance with retry
        gi = get_galaxy_instance(galaxy_url, galaxy_token)
        logger.info("Created GalaxyInstance successfully")

        # Find or create the history with the provided name
        histories = gi.histories.get_histories(name=galaxy_history_name)
        if histories:
            history_id = histories[0]['id']
        else:
            history = gi.histories.create_history(name=galaxy_history_name)
            history_id = history['id']

        logger.info(f"Working with history ID: {history_id}")

        # data_modified = prepare_data(data['data'])
        # logger.info("Data prepared successfully")
        data_modified = data.get('data')

        # Upload the file to Galaxy
        upload_info = upload_data_string(gi, history_id, data_modified, cbioportal_study_id, cbioportal_case_id)
        logger.info(f"Uploaded: {upload_info['outputs'][0]['name']}, ID: {upload_info['outputs'][0]['id']}")

        return {"message": "Data received successfully"}
    except ConnectionError as e:
        logger.error(f"Connection error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to establish a new connection: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))
