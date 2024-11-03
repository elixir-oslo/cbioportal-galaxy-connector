import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_image():
    # Check if the image already exists
    response = client.get("/images/test_image.png")
    if response.status_code == 200:
        # Delete the image if it exists
        response = client.delete("/images/test_image.png")
        assert response.status_code in [200, 404, 405]  # 404 if the image does not exist

    # Upload the image
    with open("tests/test_data/test_image.png", "rb") as img:
        response = client.post("/upload-image/", files={"file": img})
    assert response.status_code == 200
    assert "url" in response.json()

def test_get_image():
    response = client.get("/images/test_image.png")
    assert response.status_code == 200

def test_delete_image():
    # Check if the image already exists
    response = client.get("/images/test_image.png")
    if response.status_code == 200:
        # Delete the image if it exists
        response = client.delete("/images/test_image.png")
        assert response.status_code == 200

    # Upload the image
    with open("tests/test_data/test_image.png", "rb") as img:
        response = client.post("/upload-image/", files={"file": img})
    assert response.status_code == 200

    # Delete the image
    response = client.delete("/images/test_image.png")
    assert response.status_code == 200
    assert response.json() == {"detail": "Image 'test_image.png' deleted successfully"}

    # Verify the image is deleted
    response = client.get("/images/test_image.png")
    assert response.status_code == 404


def test_upload_image_with_overwrite():
    # Ensure the image is uploaded first
    with open("tests/test_data/test_image.png", "rb") as img:
        response = client.post("/upload-image/", files={"file": img})


    assert response.status_code == 200

    # Upload the image again with overwrite
    with open("tests/test_data/test_image.png", "rb") as img:
        files = {"file": img}
        response = client.post(
            "/upload-image/",
            files=files,
            data={"overwrite": "true"}
        )

    # Debugging prints
    print("Response status code:", response.status_code)
    print("Response content:", response.json())
    print("Response headers:", response.headers)

    assert response.status_code == 200
    assert "url" in response.json()





