import pytest
from fastapi import HTTPException
from requests.exceptions import ConnectionError
from unittest.mock import patch, MagicMock
from app.routers.cbioportal_to_galaxy_handler import validate_and_fix_url, get_galaxy_instance, export_to_galaxy

def test_validate_and_fix_url_missing_scheme():
    with pytest.raises(ValueError, match="Missing scheme in URL:"):
        validate_and_fix_url("www.example.com")

@patch('app.routers.cbioportal_to_galaxy_handler.GalaxyInstance')
def test_get_galaxy_instance_retries(mock_galaxy_instance):
    mock_galaxy_instance.side_effect = ConnectionError("Connection failed")
    with pytest.raises(HTTPException, match="Failed to establish a new connection: Connection failed"):
        get_galaxy_instance("http://example.com", "fake_key", max_retries=3, delay=0)

# @patch('app.routers.cbioportal_to_galaxy_handler.get_galaxy_instance')
# @pytest.mark.asyncio
# async def test_export_to_galaxy_connection_error(mock_get_galaxy_instance, async_client):
#     mock_get_galaxy_instance.side_effect = ConnectionError("Connection failed")
#     response = await async_client.post("/export-to-galaxy", json={
#         "galaxyToken": "fake_token",
#         "galaxyHistoryName": "fake_history",
#         "studyId": "fake_study",
#         "caseId": "fake_case",
#         "data": "fake_data"
#     }, params={"galaxy_url": "http://example.com"})
#     assert response.status_code == 500
#     assert "Failed to establish a new connection" in response.json()['detail']