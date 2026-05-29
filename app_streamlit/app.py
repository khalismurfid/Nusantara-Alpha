"""Customer-facing Nusantara Alpha Streamlit app."""

from __future__ import annotations

from app_streamlit.clients.api import APIClient
from app_streamlit.components.demo_banner import render_demo_banner
from app_streamlit.components.evidence_panel import render_evidence_panel
from app_streamlit.components.framing import render_framing
from app_streamlit.components.paper_trading_evidence import render_paper_trading_evidence
from app_streamlit.components.prediction_result import render_prediction_result
from app_streamlit.components.unavailable_state import render_unavailable_state
from backend.config import get_settings

try:
    import streamlit as st  # type: ignore
except Exception:
    st = None


def run_app() -> None:
    settings = get_settings()
    client = APIClient(settings.api_base_url)
    if st is None:
        return
    st.set_page_config(page_title="Nusantara Alpha", layout="wide")
    st.title("Nusantara Alpha")
    render_framing(st)
    try:
        demo_status = client.get_demo_status()
        render_demo_banner(demo_status, st)
    except Exception:
        pass
    try:
        models = client.list_models().get("models", [])
    except Exception as exc:
        st.error(f"Model catalogue is unavailable: {exc}")
        return
    if not models:
        st.warning("Prediction is unavailable because no approved model is available.")
        return
    selected_model = st.selectbox("Curated model", models, format_func=lambda model: model["model_name"])
    evidence = client.get_evidence(selected_model["model_id"])
    render_evidence_panel(evidence, st)
    render_paper_trading_evidence(evidence, st)
    stock_query = st.text_input("IDX ticker", value="BBCA")
    stocks = client.list_stocks(selected_model["model_id"], stock_query).get("stocks", [])
    for stock in stocks:
        if stock["support_status"] != "supported":
            render_unavailable_state(
                stock["support_status"],
                stock.get("unavailable_reason") or "This stock is unavailable for the selected model.",
                "Remove or replace this ticker before requesting a prediction.",
                st,
            )
            client.record_unsupported_stock_interest(stock["ticker"], stock.get("unavailable_reason") or "unsupported", selected_model["model_id"])
    supported = [stock for stock in stocks if stock["support_status"] == "supported"]
    selected_tickers = st.multiselect("Supported IDX stocks", [stock["ticker"] for stock in supported], default=[supported[0]["ticker"]] if supported else [])
    if st.button("Request educational prediction"):
        response = client.request_prediction(selected_model["model_id"], selected_model["model_version"], selected_tickers)
        for blocked in response.get("blocked", []):
            st.error(blocked["user_message"])
        for prediction in response.get("predictions", []):
            render_prediction_result(prediction, st)


if __name__ == "__main__":
    run_app()
