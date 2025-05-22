import json
from pathlib import Path
from .xnat_common import get_experiment_label_from_json

def test_get_experiment_label_from_json_real_data():
    # Load subject_data from the test_xnat.json file
    json_path = Path(__file__).parent.parent / "test_data" / "test_xnat.json"
    with open(json_path, "r") as f:
        subject_data = json.load(f)
    experiment_uid = "1.3.6.1.4.1.14519.5.2.1.8421.4017.143112626223669848047982968345"

    label = get_experiment_label_from_json(subject_data, experiment_uid)
    assert label == "10-31-2002-NA-CT-ABDOMEN-PELVIS-W-CONT-2-68345"