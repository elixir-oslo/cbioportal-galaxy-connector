import tempfile
from datetime import datetime
from io import StringIO
import time
import os
import pandas as pd
from fastapi import HTTPException
from bioblend.galaxy import GalaxyInstance
from requests.exceptions import ConnectionError
import logging
from urllib.parse import urlparse

logger = logging.getLogger("uvicorn.error")

def validate_and_fix_url(url):
    parsed = urlparse(url)
    if not parsed.scheme:
        raise ValueError(f"Missing scheme in URL: {url}")
    if parsed.scheme not in ["http", "https"]:
        raise ValueError(f"Unsupported scheme in URL: {url}")
    return url

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

    data = data.dropna(subset=['Variant Reads'])
    data['Variant Reads'] = data['Variant Reads'].astype(int)
    data = data.dropna(subset=['Ref Reads'])
    data['Ref Reads'] = data['Ref Reads'].astype(int)

    data = data.rename(columns={'Ref Reads': 'ref_counts'})
    data = data.rename(columns={'Variant Reads': 'alt_counts'})

    buffer = StringIO()
    data.to_csv(buffer, sep='\t', index=False, header=True)
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