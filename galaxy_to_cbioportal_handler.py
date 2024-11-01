# galaxy_to_cbioportal_handler.py
import os
import subprocess
from io import StringIO

import pandas as pd
from fastapi import HTTPException, Request

def merge_data_timeline(new_data: str, path_data_file: str):
    # Asign the data to a pandas dataframe
    df_input = pd.read_csv(StringIO(new_data), sep='\t', header=0)

    # If a file exists, read it and merge the new data with the previous data
    if os.path.exists(path_data_file):
        df_previous_data = pd.read_csv(path_data_file, sep="\t")
        # Overwrite rows with the same PATIENT_ID
        df_combined = pd.concat([df_previous_data, df_input]).drop_duplicates(subset=["PATIENT_ID"], keep='last')
    else:
        df_combined = df_input

    # Remove duplicates rows
    df_combined = df_combined.drop_duplicates()

    return df_combined



async def export_timeline_to_cbioportal(request: Request, path_study_directory: str):
    try:
        data = await request.json()
        data_content = data.get('data_content')
        meta_content = data.get('meta_content')
        study_id = data.get('study_id')
        case_id = data.get('case_id')

        if not data_content or not meta_content or not study_id or not case_id:
            raise HTTPException(status_code=400, detail="Missing required fields: data_content, meta_content, case_id, or study_id")

        path_study_id_directory = os.path.join(path_study_directory, 'incremental_import', study_id)
        path_meta_outfile = os.path.join(path_study_id_directory, 'meta_timeline.txt')

        df_dataframe = merge_data_timeline(data_content, path_meta_outfile)
        print(df_dataframe)



    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



    # try:
    #     # Construct the command
    #     command = ["python", "/scripts/importer/metaImport.py"] + args
    #
    #     print(command)
    #
    #     # Run the command
    #     result = subprocess.run(command, capture_output=True, text=True)
    #
    #     # Check if the command was successful
    #     if result.returncode != 0:
    #         raise HTTPException(status_code=500, detail=result.stderr)
    #
    #     return {"output": result.stdout}
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))