import pytest
from fastapi import HTTPException
from cbioportal_to_galaxy_handler import validate_and_fix_url, get_galaxy_instance

def test_validate_and_fix_url_success():
    url = "http://example.com"
    assert validate_and_fix_url(url) == url

def test_validate_and_fix_url_missing_scheme():
    with pytest.raises(ValueError, match="Missing scheme in URL: example.com"):
        validate_and_fix_url("example.com")

def test_validate_and_fix_url_unsupported_scheme():
    with pytest.raises(ValueError, match="Unsupported scheme in URL: ftp://example.com"):
        validate_and_fix_url("ftp://example.com")

# def test_get_galaxy_instance_success(monkeypatch):
#     class MockGalaxyInstance:
#         def __init__(self, url, key):
#             self.url = url
#             self.key = key
#             self.histories = self.Histories()
#             self.tools = self.Tools()
#
#         class Histories:
#             def get_histories(self, name):
#                 return [{'id': 'fake_history_id'}]
#
#             def create_history(self, name):
#                 return {'id': 'fake_history_id'}
#
#         class Tools:
#             def upload_file(self, file_path, history_id, file_name):
#                 return {'outputs': [{'name': file_name, 'id': 'fake_file_id'}]}
#
#     monkeypatch.setattr('bioblend.galaxy.GalaxyInstance', MockGalaxyInstance)
#
#     instance = get_galaxy_instance("http://example.com", "fake_key")
#     assert isinstance(instance, MockGalaxyInstance)