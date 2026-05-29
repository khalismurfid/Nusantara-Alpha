from app_streamlit.clients.api import APIClient


def test_api_client_stores_base_url():
    client = APIClient("http://localhost:8000")
    assert client.base_url == "http://localhost:8000"

