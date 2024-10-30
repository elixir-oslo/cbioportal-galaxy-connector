import os
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_export_to_galaxy_success(monkeypatch):
    def mock_get_galaxy_instance(url, key, max_retries=5, delay=5):
        class MockGalaxyInstance:
            def __init__(self):
                self.histories = self.Histories()
                self.tools = self.Tools()
            class Histories:
                def get_histories(self, name):
                    return [{'id': 'fake_history_id'}]
                def create_history(self, name):
                    return {'id': 'fake_history_id'}
            class Tools:
                def upload_file(self, file_path, history_id, file_name):
                    return {'outputs': [{'name': file_name, 'id': 'fake_file_id'}]}
        return MockGalaxyInstance()

    monkeypatch.setattr('cbioportal_to_galaxy_handler', 'get_galaxy_instance', mock_get_galaxy_instance)
    monkeypatch.setenv('GALAXY_URL', 'http://localhost:8080')  # Mock the environment variable

    response = client.post("/export-to-galaxy", json={
        "galaxyToken": "fake_token",
        "galaxyHistoryName": "fake_history",
        "studyId": "fake_study",
        "caseId": "fake_case",
        "data": "fake_data"
    })

    print(response.json())  # Add this line to print the response content
    assert response.status_code == 200
    assert response.json() == {"message": "Data received successfully"}

def test_export_to_galaxy_missing_fields():
    response = client.post("/export-to-galaxy", json={})
    assert response.status_code == 500
    assert response.json() == {"detail": "Missing required fields in the request."}