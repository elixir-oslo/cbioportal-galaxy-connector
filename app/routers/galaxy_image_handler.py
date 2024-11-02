import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Form
from fastapi.responses import FileResponse

router = APIRouter()

UPLOAD_DIRECTORY = "./uploaded_images"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


@router.post("/upload-image/")
async def upload_image(request: Request, file: UploadFile = File(...), overwrite: bool = Form(False)):
    file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)
    image_name = os.path.basename(file_location)

    if os.path.exists(file_location):
        if not overwrite:
            raise HTTPException(status_code=409,
                                detail=f"Image named '{image_name}' already exists. Set overwrite to true to replace it.")
        else:
            message = f"file '{file.filename}' overwritten at '{file_location}'"
    else:
        message = f"file '{file.filename}' saved at '{file_location}'"

    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    base_url = str(request.base_url)
    image_url = f"{base_url}images/{image_name}"

    return {"info": message, "url": image_url}


@router.get("/images/{image_name}")
async def get_image(image_name: str):
    file_location = os.path.join(UPLOAD_DIRECTORY, image_name)
    if not os.path.exists(file_location):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_location)
