"""Customer-facing Nusantara Alpha Streamlit app."""

from __future__ import annotations

import os

from app_streamlit.clients.api import APIClient
from app_streamlit.components.demo_banner import render_demo_banner
from app_streamlit.components.evidence_panel import format_evidence, render_evidence_panel
from app_streamlit.components.framing import framing_text
from app_streamlit.components.paper_trading_evidence import render_paper_trading_evidence
from app_streamlit.components.prediction_result import render_prediction_result
from app_streamlit.components.ui_shell import inject_customer_styles, render_app_header, render_context_strip, render_section_heading
from app_streamlit.components.unavailable_state import render_unavailable_state
from app_streamlit.copy.product_language import format_signal, signal_badge

try:
    import streamlit as st  # type: ignore
except Exception:
    st = None


def configured_api_base_url() -> str:
    return os.getenv("NUSANTARA_API_BASE_URL", "http://localhost:8000")


def evidence_is_loaded(evidence: dict | None) -> bool:
    return bool(evidence) and evidence.get("evidence_load_status") == "loaded"


def supported_stock_options(stocks: list[dict]) -> list[str]:
    return [stock["ticker"] for stock in stocks if stock.get("support_status") == "supported"]


def prediction_is_ready(selected_model: dict | None, evidence: dict | None, selected_tickers: list[str]) -> bool:
    return bool(selected_model) and evidence_is_loaded(evidence) and bool(selected_tickers)


def split_stock_availability(stocks: list[dict]) -> tuple[list[dict], list[dict]]:
    supported = [stock for stock in stocks if stock.get("support_status") == "supported"]
    unavailable = [stock for stock in stocks if stock.get("support_status") != "supported"]
    return supported, unavailable


def public_prediction_is_available(demo_status: dict | None) -> bool:
    if not demo_status:
        return True
    return bool(demo_status.get("public_predictions_available", True))


def prediction_cache_key(selected_model: dict, evidence: dict, selected_tickers: list[str]) -> tuple:
    return (
        selected_model["model_id"],
        selected_model["model_version"],
        tuple(selected_tickers),
        evidence.get("evidence_id"),
        evidence.get("evidence_as_of"),
    )


def model_evaluation_period(model: dict) -> str:
    period = model.get("evaluation_period", {})
    if not period:
        return "Evaluation period unavailable"
    return f"{period.get('start')} to {period.get('end')}"


def stock_display_name(stock: dict) -> str:
    name = stock.get("name")
    return f"{stock['ticker']} - {name}" if name else stock["ticker"]


def selected_ticker_from_stock(stock: dict | None) -> list[str]:
    return [stock["ticker"]] if stock else []


def render_market_ranking(client: APIClient, selected_model: dict, selected_tickers: list[str], st=None) -> None:
    if st is None:
        return
    try:
        response = client.get_rankings(selected_model["model_id"], selected_model["model_version"])
    except Exception:
        return
    rows = response.get("rankings", [])
    if not rows:
        return
    selected = set(selected_tickers)
    selected_rows = [row for row in rows if row["ticker"] in selected]
    st.subheader("Market ranking")
    st.caption("Exploratory scores across reviewed stocks. Higher upside score means the model assigned more weight to the upward barrier outcome.")
    if selected_rows:
        selected_row = selected_rows[0]
        with st.container(border=True):
            rank_col, signal_col, score_col = st.columns([1, 1.2, 1])
            rank_col.metric("Selected stock rank", f"{selected_row['rank']} of {len(rows)}")
            signal_col.metric("Selected signal", signal_badge(selected_row["model_signal"]))
            score_col.metric("Upside score", f"{round(selected_row['ranking_score'] * 100)}%")
            if selected_row["model_signal"] == "up":
                st.success(format_signal(selected_row["model_signal"]))
            elif selected_row["model_signal"] == "down":
                st.error(format_signal(selected_row["model_signal"]))
            else:
                st.info(format_signal(selected_row["model_signal"]))

    top_rows = rows[:25]
    selected_outside_top = [row for row in selected_rows if row not in top_rows]
    display_rows = [_format_ranking_row(row, selected) for row in [*top_rows, *selected_outside_top]]
    column_config = None
    if hasattr(st, "column_config"):
        column_config = {
            "Upside score": st.column_config.ProgressColumn(
                "Upside score",
                min_value=0,
                max_value=100,
                format="%d%%",
            ),
        }
    st.dataframe(
        display_rows,
        hide_index=True,
        use_container_width=True,
        column_config=column_config,
    )


def _format_ranking_row(row: dict, selected_tickers: set[str]) -> dict:
    return {
        "Rank": row["rank"],
        "Stock": row["ticker"],
        "Name": row.get("name") or "",
        "Signal": format_signal(row["model_signal"]),
        "Confidence": row["confidence_category"],
        "Upside score": round(row["ranking_score"] * 100),
        "Selected": "Selected stock" if row["ticker"] in selected_tickers else "",
    }


def run_app() -> None:
    client = APIClient(configured_api_base_url())
    if st is None:
        return
    st.set_page_config(page_title="Nusantara Alpha", layout="wide")
    inject_customer_styles(st)
    render_app_header(
        "Nusantara Alpha",
        framing_text(),
        st,
    )
    demo_status = None
    try:
        demo_status = client.get_demo_status()
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

    render_section_heading(
        "Choose a model and stock",
        "Start with an approved model, then select one reviewed IDX stock.",
        st,
    )
    control_left, control_right = st.columns([1, 1])
    with control_left:
        selected_model = st.selectbox(
            "Prediction model",
            models,
            format_func=lambda model: f"{model['model_name']} ({model['model_version']})",
            help="Only approved customer-facing models appear here.",
        )
        st.caption(selected_model.get("description", ""))
    evidence = client.get_evidence(selected_model["model_id"])
    formatted_evidence = format_evidence(evidence)
    stocks = client.list_stocks(selected_model["model_id"]).get("stocks", [])
    supported, unavailable = split_stock_availability(stocks)
    with control_right:
        selected_stock = st.selectbox(
            "Stock",
            supported,
            index=0 if supported else None,
            format_func=stock_display_name,
            placeholder="No reviewed stocks available",
            help="Only stocks reviewed for the selected model are shown.",
        )
        selected_tickers = selected_ticker_from_stock(selected_stock)

    if prediction_is_ready(selected_model, evidence, selected_tickers):
        concise_evidence_summary = formatted_evidence["concise_summary"]
        if not public_prediction_is_available(demo_status):
            render_unavailable_state(
                "public_demo_release_gate_failed",
                (demo_status or {}).get("unavailable_reason")
                or "Signals are unavailable until an approved model and approved data are ready.",
                "Check the review notes below, or run locally with approved assets.",
                st,
            )
        else:
            cache_key = prediction_cache_key(selected_model, evidence, selected_tickers)
            cache = st.session_state.setdefault("prediction_response_cache", {})
            if cache_key not in cache:
                try:
                    cache[cache_key] = client.request_prediction(
                        selected_model["model_id"],
                        selected_model["model_version"],
                        selected_tickers,
                    )
                except Exception:
                    cache[cache_key] = {
                        "predictions": [],
                        "blocked": [
                            {
                                "reason": "invalid_prediction_response",
                                "user_message": "Prediction could not be generated right now.",
                                "next_step": "Check that the API is running, then try again.",
                            }
                        ],
                    }
            response = cache[cache_key]
            for blocked in response.get("blocked", []):
                render_unavailable_state(
                    blocked["reason"],
                    blocked["user_message"],
                    blocked.get("next_step"),
                    st,
                )
            for prediction in response.get("predictions", []):
                render_prediction_result(prediction, st, concise_evidence_summary)
            render_market_ranking(client, selected_model, selected_tickers, st)
    else:
        render_unavailable_state(
            "prediction_not_ready",
            "Choose a reviewed stock for a model with ready background data to see the signal.",
            "The signal appears after the selections pass the product checks.",
            st,
        )

    render_context_strip(
        [
            ("Model", selected_model["model_name"]),
            ("Stocks covered", str(len(evidence.get("supported_universe", [])))),
            ("Tested period", model_evaluation_period(selected_model)),
        ],
        st,
    )

    render_section_heading(
        "What this is based on",
        "Past performance, coverage, and limitations for the selected model.",
        st,
    )
    render_evidence_panel(evidence, st)
    render_paper_trading_evidence(evidence, st)
    if unavailable:
        with st.expander("Stocks not available yet", expanded=False):
            st.caption("These tickers need more review before they can appear in the stock selector.")
            for stock in unavailable:
                st.write(f"{stock['ticker']}: {stock.get('unavailable_reason') or 'Not available for this model yet.'}")
    if demo_status:
        render_demo_banner(demo_status, st)


if __name__ == "__main__":
    run_app()
