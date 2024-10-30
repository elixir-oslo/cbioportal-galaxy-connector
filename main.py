import os
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from galaxy_image_handler import router as image_router
from cbioportal_to_galaxy_handler import validate_and_fix_url, get_galaxy_instance, upload_data_string

logger = logging.getLogger("uvicorn.error")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(image_router)

raw_galaxy_url = os.getenv('GALAXY_URL', 'http://localhost:8081').strip()
try:
    galaxy_url = validate_and_fix_url(raw_galaxy_url)
    logger.info(f"Using Galaxy URL: {galaxy_url}")
except ValueError as e:
    logger.error(f"Error in URL validation: {e}")
    raise

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

        gi = get_galaxy_instance(galaxy_url, galaxy_token)
        logger.info("Created GalaxyInstance successfully")

        histories = gi.histories.get_histories(name=galaxy_history_name)
        if histories:
            history_id = histories[0]['id']
        else:
            history = gi.histories.create_history(name=galaxy_history_name)
            history_id = history['id']

        logger.info(f"Working with history ID: {history_id}")

        data_modified = data.get('data')
        upload_info = upload_data_string(gi, history_id, data_modified, cbioportal_study_id, cbioportal_case_id)
        logger.info(f"Uploaded: {upload_info['outputs'][0]['name']}, ID: {upload_info['outputs'][0]['id']}")

        return {"message": "Data received successfully"}
    except ConnectionError as e:
        logger.error(f"Connection error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to establish a new connection: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))