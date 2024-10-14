import tempfile
from io import StringIO

import pandas as pd
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from bioblend.galaxy import GalaxyInstance


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Configuration
galaxy_url = 'http://localhost:8090'


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


def upload_data_string(galaxy_instance, history_id, data_string, file_name='data.txt'):
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix=file_name) as tmp_file:
        tmp_file.write(data_string)
        tmp_file_path = tmp_file.name

    upload_info = galaxy_instance.tools.upload_file(tmp_file_path, history_id)
    return upload_info

@app.post("/run-script")
async def run_script(request: Request):
    data = await request.json()
    galaxy_token = data.get('galaxyToken')
    galaxy_history_name = data.get('galaxyHistoryName')

    # print(galaxy_token)
    # print(galaxy_history_name)
    # print(data)

    # Create a Galaxy instance
    gi = GalaxyInstance(galaxy_url, key=galaxy_token)

    # Find or create the history with the provided name
    histories = gi.histories.get_histories(name=galaxy_history_name)  # Modification/ added
    if histories:
        history_id = histories[0]['id']  # Modification/ added
    else:
        history = gi.histories.create_history(name=galaxy_history_name)  # Modification/ added
        history_id = history['id']  # Modification/ added


    data_modified = prepare_data(data['data'])


    # Create a temporary file and write data['data'] to it
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as temp_file:
        temp_file.write(data_modified)

        temp_file_path = temp_file.name

    # Upload the file to Galaxy
    upload_info = upload_data_string(gi, history_id, data_modified)
    print(f"Uploaded: {upload_info['outputs'][0]['name']}, ID: {upload_info['outputs'][0]['id']}")


    return {"message": "Data received successfully", "temp_file_path": temp_file_path}