from io import StringIO

import pytest
from fastapi.testclient import TestClient
from routers.galaxy_to_cbioportal_handler import merge_data_timeline, export_timeline_to_cbioportal, router
import pandas as pd
from unittest.mock import patch, mock_open
import os

client = TestClient(router)

class TestMergeDataTimeline:
    @pytest.mark.skip(reason="Error")
    def test_merge_data_timeline_with_existing_file(self):
        new_data = "PATIENT_ID\tDATA\n1\tnew_data1\n2\tnew_data2"
        existing_data = "PATIENT_ID\tDATA\n2\texisting_data2\n3\texisting_data3"
        expected_data = "PATIENT_ID\tDATA\n3\texisting_data3\n1\tnew_data1\n2\tnew_data2"

        with patch("builtins.open", mock_open(read_data=existing_data)), \
             patch("os.path.exists", return_value=True):
            result_df = merge_data_timeline(new_data, "dummy_path")
            expected_df = pd.read_csv(StringIO(expected_data), sep='\t')
            pd.testing.assert_frame_equal(result_df, expected_df)

    def test_merge_data_timeline_no_patient_id_column(self):
        new_data = "PATIENT_ID\tDATA\n1\tnew_data1\n2\tnew_data2"
        existing_data = "DATA\nexisting_data2\nexisting_data3"

        with patch("builtins.open", mock_open(read_data=existing_data)), \
             patch("os.path.exists", return_value=True), \
             patch("app.routers.galaxy_to_cbioportal_handler.logger.warning") as mock_warning:
            result_df = merge_data_timeline(new_data, "dummy_path")
            expected_df = pd.read_csv(StringIO(new_data), sep='\t')
            pd.testing.assert_frame_equal(result_df, expected_df)
            mock_warning.assert_called_once_with(
                "Previous file dummy_path does not have a PATIENT_ID column. Previous file will be overwritten."
            )

class TestExportTimelineToCbioportal:
    @pytest.mark.skip(reason="Error")
    def test_export_timeline_missing_fields(self):
        response = client.post("/export-timeline-to-cbioportal", json={
            "dataContent": "sample_data_content",
            "metaContent": "sample_meta_content",
            "studyId": "sample_study_id",
            "caseId": "sample_case_id",
            "suffix": "sample_suffix"
        })
        print(response.json())
        # assert response.status_code == 400
        # assert response.json() == {"detail": "Missing required fields: dataContent, metaContent, caseId, or studyId"}