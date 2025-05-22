import os
from app.utils.logger import setup_logger
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request, Form
from fastapi.responses import FileResponse
from app.dependencies import get_env_vars

router = APIRouter()
logger = setup_logger(__name__)


# UPLOAD_DIRECTORY = "/uploaded_images"
# os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

def create_upload_directory(dir_path: str):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        logger.info(f"Created directory: {dir_path}")
    else:
        logger.info(f"Directory already exists: {dir_path}")

@router.post("/upload-image/")
async def upload_image(request: Request, file: UploadFile = File(...), overwrite: bool = Form(False), env_vars: dict = Depends(get_env_vars)):
    upload_directory = env_vars.get('image_upload_directory')
    
    image_name = os.path.basename(file.filename)
    file_location = os.path.join(upload_directory, image_name)

    if os.path.exists(file_location):
        if not overwrite:
            raise HTTPException(status_code=409,
                                detail=f"Image named '{image_name}' already exists. Set overwrite to true to replace it.")
        else:
            message = f"file '{file.filename}' overwritten at '{file_location}'"
            logger.info(message)

    else:
        message = f"file '{file.filename}' saved at '{file_location}'"
        logger.info(message)

    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    base_url = str(request.base_url)
    image_url = f"{base_url}images/{image_name}"

    return {"info": message, "url": image_url}


@router.get("/images/{image_name}")
async def get_image(image_name: str, env_vars: dict = Depends(get_env_vars)):
    upload_directory = env_vars.get('image_upload_directory')
    file_location = os.path.join(upload_directory, image_name)
    if not os.path.exists(file_location):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_location)


@router.delete("/images/{image_name}")
async def delete_image(image_name: str, env_vars: dict = Depends(get_env_vars)):
    upload_directory = env_vars.get('image_upload_directory')
    file_location = os.path.join(upload_directory, image_name)
    if not os.path.exists(file_location):
        raise HTTPException(status_code=404, detail="Image not found")
    os.remove(file_location)
    return {"detail": f"Image '{image_name}' deleted successfully"}
