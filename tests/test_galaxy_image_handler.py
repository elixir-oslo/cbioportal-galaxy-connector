import os
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from galaxy_image_handler import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)


def test_upload_image_success(tmpdir):
    file_path = tmpdir.join("test_image.png")
    file_path.write("fake_image_data")

    with open(file_path, "rb") as file:
        response = client.post("/upload-image/", files={"file": ("test_image.png", file, "image/png")})

    assert response.status_code == 200
    assert response.json() == {"info": "file 'test_image.png' saved at './uploaded_images/test_image.png'"}


def test_get_image_success(tmpdir):
    upload_dir = "./uploaded_images"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, "test_image.png")
    with open(file_path, "wb") as file:
        file.write(b"fake_image_data")

    response = client.get("/images/test_image.png")
    assert response.status_code == 200
    assert response.content == b"fake_image_data"


def test_get_image_not_found():
    response = client.get("/images/non_existent_image.png")
    assert response.status_code == 404
    assert response.json() == {"detail": "Image not found"}