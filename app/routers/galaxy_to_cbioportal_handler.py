from fastapi import APIRouter, HTTPException, Request, Depends
import os
import logging
from io import StringIO
import pandas as pd
from services.importer_common import clear_cache_cbioportal, incremental_load_data_to_cbioportal
from dependencies import get_env_vars


router = APIRouter()
logger = logging.getLogger(__name__)


def merge_data_timeline(new_data: str, data_file_path: str) -> pd.DataFrame:
    df_input = pd.read_csv(StringIO(new_data), sep='\t', header=0)

    # If a file exists, read it and merge the new data with the previous data
    if os.path.exists(data_file_path):
        df_previous = pd.read_csv(data_file_path, sep="\t")
        try:
            df_previous = df_previous[~df_previous["PATIENT_ID"].isin(df_input["PATIENT_ID"])]
            df_combined = pd.concat([df_previous, df_input])
        # Exception handling for the case where there is no PATIENT_ID column have a warning log message that previous file will be overwritten
        except KeyError:
            logger.warning(
                f"Previous file {data_file_path} does not have a PATIENT_ID column. Previous file will be overwritten.")
            df_combined = df_input
    else:
        df_combined = df_input

    df_combined = df_combined.drop_duplicates()
    return df_combined


@router.post("/export-timeline-to-cbioportal")
async def export_timeline_to_cbioportal(request: Request, env_vars: dict = Depends(get_env_vars)) -> dict:
    try:
        data = await request.json()
        data_content = data.get('dataContent')
        meta_content = data.get('metaContent')
        study_id = data.get('studyId')
        case_id = data.get('caseId')
        suffix = data.get('suffix')

        if not data_content or not meta_content or not study_id or not case_id or not suffix:
            logger.error("Missing required fields: dataContent, metaContent, caseId, or studyId")
            raise HTTPException(status_code=400,
                                detail="Missing required fields: dataContent, metaContent, caseId, or studyId")

        study_id_directory_path = str(os.path.join(env_vars['study_directory_path'], 'incremental_import', study_id))
        meta_outfile_path = os.path.join(study_id_directory_path, f"meta_timeline_{suffix}.txt")
        data_outfile_path = os.path.join(study_id_directory_path, f"data_timeline_{suffix}.txt")

        df = merge_data_timeline(data_content, data_outfile_path)

        os.makedirs(study_id_directory_path, exist_ok=True)

        df.to_csv(data_outfile_path, sep='\t', index=False)
        with open(meta_outfile_path, 'w') as f:
            f.write(meta_content)

        load_message = incremental_load_data_to_cbioportal(study_id_directory_path, env_vars['cbioportal_url'])
        logger.debug(f"Load message: {load_message}")

        clear_cache_message = clear_cache_cbioportal(env_vars['cbioportal_url'], env_vars['api_key'])
        logger.debug(f"Clear cache message: {clear_cache_message}")

        return {"message": "Data successfully exported to cBioPortal."}
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))