"""Model evidence presentation helpers."""

from __future__ import annotations

from app_streamlit.components.ui_shell import (
    render_evidence_band,
    render_guidance_items,
    render_secondary_details,
    render_section_heading,
)
from app_streamlit.copy.product_language import SECTION_TITLES, has_raw_limitation_fragment


def format_evidence(evidence: dict) -> dict:
    metrics = evidence.get("key_metrics", [])
    supported_universe = evidence.get("supported_universe", [])
    limitations = [_readable_limitation(item) for item in evidence.get("limitations", [])]
    evaluation_period = evidence["evaluation_period"]
    metric_highlights = [
        {
            "name": metric["name"],
            "value": metric["value"],
            "interpretation": metric["interpretation"],
        }
        for metric in metrics
    ]
    stocks_covered = _coverage_summary(supported_universe)
    concise_summary = {
        "section_title": SECTION_TITLES["evidence_snapshot"],
        "headline": f"Historical test period: {evaluation_period['start']} to {evaluation_period['end']}",
        "evaluation_period": f"{evaluation_period['start']} to {evaluation_period['end']}",
        "metric_highlights": metric_highlights,
        "metrics": metric_highlights[:3],
        "stocks_covered": stocks_covered,
        "caveat": evidence.get("historical_performance_caveat", ""),
        "barrier_config": evidence.get("barrier_config", {}),
    }
    return {
        "evidence_id": evidence["evidence_id"],
        "evaluation_period": evaluation_period,
        "metrics": metrics,
        "supported_universe": supported_universe,
        "limitations": limitations,
        "data_quality_notes": evidence.get("data_quality_notes", []),
        "historical_performance_caveat": evidence.get("historical_performance_caveat", ""),
        "evidence_status": evidence.get("evidence_status"),
        "evidence_load_status": evidence.get("evidence_load_status"),
        "evidence_as_of": evidence.get("evidence_as_of"),
        "barrier_config": evidence.get("barrier_config", {}),
        "concise_summary": concise_summary,
        "details_title": "More model details",
    }


def _coverage_summary(supported_universe: list[str]) -> str:
    if not supported_universe:
        return "Reviewed stock list is unavailable."
    if len(supported_universe) <= 12:
        return f"{len(supported_universe)} reviewed IDX tickers: {', '.join(supported_universe)}"
    return f"{len(supported_universe)} reviewed IDX tickers loaded for this model."


def _readable_limitation(limitation: str) -> str:
    if not has_raw_limitation_fragment(limitation):
        return limitation
    normalized = " ".join(limitation.lower().split())
    if "limited universe" in normalized or "small supported universe" in normalized:
        return "Coverage depends on the approved IDX universe and market data loaded for this model."
    if "no guarantee" in normalized:
        return "Future market sessions can behave differently from the historical test period."
    return limitation


def render_concise_evidence_summary(summary: dict, st=None) -> None:
    if st is None:
        return
    render_evidence_band(summary, st)


def render_evidence_panel(evidence: dict, st=None) -> dict:
    formatted = format_evidence(evidence)
    if st is not None:
        render_section_heading(
            SECTION_TITLES["model_evidence"],
            "Historical results and coverage for the selected model.",
            st,
        )
        render_concise_evidence_summary(formatted["concise_summary"], st)
        with render_secondary_details(formatted["details_title"], st=st):
            st.write(f"Review status: {formatted['evidence_status']}")
            st.write(f"Background data: {formatted['evidence_load_status']}")
            st.write(f"Last reviewed: {formatted['evidence_as_of']}")
            st.write("Data notes")
            for note in formatted["data_quality_notes"]:
                st.caption(note)
            barrier_config = formatted.get("barrier_config") or {}
            if barrier_config:
                st.write("How the near-term signal is defined")
                for label, key in [
                    ("Time window", "horizon"),
                    ("Entry assumption", "entry"),
                    ("Volatility measure", "volatility_measure"),
                    ("Upward barrier", "profit_barrier"),
                    ("Downward barrier", "stop_barrier"),
                    ("Neutral signal", "neutral_policy"),
                ]:
                    value = barrier_config.get(key)
                    if value:
                        st.caption(f"{label}: {value}")
            st.write("Limitations")
            render_guidance_items(formatted["limitations"], st)
    return formatted
