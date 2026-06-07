from pathlib import Path

import yaml


def test_streamlit_waits_for_backend_health_before_starting():
    compose_path = Path(__file__).resolve().parents[2] / "deployment" / "compose.yaml"
    compose = yaml.safe_load(compose_path.read_text())

    backend = compose["services"]["backend"]
    streamlit = compose["services"]["streamlit"]

    assert backend["healthcheck"]["test"] == [
        "CMD",
        "python",
        "-c",
        "from urllib.request import urlopen; urlopen('http://127.0.0.1:8000/health', timeout=2).read()",
    ]
    assert streamlit["depends_on"]["backend"]["condition"] == "service_healthy"
    assert backend["restart"] == "unless-stopped"
    assert streamlit["restart"] == "unless-stopped"
