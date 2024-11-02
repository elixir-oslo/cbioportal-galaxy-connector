# galaxy_to_cbioportal_handler.py
import os
import subprocess
from io import StringIO

import pandas as pd
from fastapi import HTTPException, Request

def merge_data_timeline(new_data: str, path_data_file: str) -> pd.DataFrame:
    # Asign the data to a pandas dataframe
    df_input = pd.read_csv(StringIO(new_data), sep='\t', header=0)

    # If a file exists, read it and merge the new data with the previous data
    if os.path.exists(path_data_file):
        df_previous_data = pd.read_csv(path_data_file, sep="\t")
        try:
            df_previous_data = df_previous_data[~df_previous_data["PATIENT_ID"].isin(df_input["PATIENT_ID"])]
            df_combined = pd.concat([df_previous_data, df_input])
        # Exception handling for the case where there is no PATIENT_ID column have a warning log message that previous file will be overwritten
        except KeyError:
            print("Previous data file does not contain a PATIENT_ID column. Overwriting the previous data file.")
            df_combined = df_input
    else:
        df_combined = df_input

    # Remove duplicates rows
    df_combined = df_combined.drop_duplicates()

    return df_combined


def incremental_load_data_to_cbioportal(path_study_id_directory: str, cbioportal_url: str) -> list:
    try:
        # Construct the command
        command = ["python", "/scripts/importer/metaImport.py",
                   "-d", path_study_id_directory,
                   "-u", cbioportal_url,
                   "-o"]

        # Run the command
        result = subprocess.run(command, capture_output=True, text=True)

        # Check if the command was successful
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=result.stderr)

        return {"output": result.stdout}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def export_timeline_to_cbioportal(request: Request, path_study_directory: str, cbioportal_url: str) -> dict:
    try:
        data = await request.json()
        data_content = data.get('data_content')
        meta_content = data.get('meta_content')
        study_id = data.get('study_id')
        case_id = data.get('case_id')
        suffix = data.get('suffix')

        if not data_content or not meta_content or not study_id or not case_id or not suffix:
            raise HTTPException(status_code=400, detail="Missing required fields: data_content, meta_content, case_id, or study_id")

        path_study_id_directory = os.path.join(path_study_directory, 'incremental_import', study_id)
        path_meta_outfile = os.path.join(path_study_id_directory, f"meta_timeline_{suffix}.txt")
        path_data_outfile = os.path.join(path_study_id_directory, f"data_timeline_{suffix}.txt")

        df_dataframe = merge_data_timeline(data_content, path_data_outfile)

        # Create the output directory if it does not exist
        os.makedirs(path_study_id_directory, exist_ok=True)

        # Write the data and meta files
        df_dataframe.to_csv(path_data_outfile, sep='\t', index=False)
        with open(path_meta_outfile, 'w') as f:
            f.write(meta_content)

        load_message = incremental_load_data_to_cbioportal(path_study_id_directory, cbioportal_url)


        return {"message": "Data successfully exported to cBioPortal."}



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