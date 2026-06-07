from app_streamlit.clients.api import APIClient


def test_api_client_stores_base_url():
    client = APIClient("http://localhost:8000")
    assert client.base_url == "http://localhost:8000"


def test_prediction_request_uses_api_post(monkeypatch):
    calls = []

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b'{"request_id":"req-1","predictions":[],"blocked":[],"disclaimer":"Educational research only."}'

    def fake_urlopen(request, timeout):
        calls.append((request.full_url, request.get_method(), request.data.decode("utf-8"), timeout))
        return Response()

    monkeypatch.setattr("app_streamlit.clients.api.urlopen", fake_urlopen)
    client = APIClient("http://api.local")

    response = client.request_prediction("idx-direction-baseline", "2026.05", ["BBCA"])

    assert response["request_id"] == "req-1"
    assert calls[0][0] == "http://api.local/predictions"
    assert calls[0][1] == "POST"
    assert '"model_id": "idx-direction-baseline"' in calls[0][2]
    assert '"tickers": ["BBCA"]' in calls[0][2]
    assert '"target": "near_term_barrier_signal"' in calls[0][2]


def test_ranking_request_uses_model_endpoint(monkeypatch):
    calls = []

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b'{"rankings":[]}'

    def fake_urlopen(url, timeout):
        calls.append((url, timeout))
        return Response()

    monkeypatch.setattr("app_streamlit.clients.api.urlopen", fake_urlopen)
    client = APIClient("http://api.local")

    response = client.get_rankings("idx-direction-baseline", "2026.05")

    assert response == {"rankings": []}
    assert calls == [("http://api.local/models/idx-direction-baseline/rankings?model_version=2026.05", 10)]
