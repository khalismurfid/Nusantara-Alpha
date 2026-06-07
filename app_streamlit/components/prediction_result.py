"""Prediction result presentation helpers."""

from __future__ import annotations

from app_streamlit.components.ui_shell import (
    render_guidance_items,
    render_insight_grid,
    render_primary_signal,
    render_secondary_details,
    render_section_heading,
)
from app_streamlit.copy.product_language import (
    SECTION_TITLES,
    format_confidence_value,
    format_signal,
    format_target,
    signal_tone,
)


def _as_list(value: str | list[str] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def format_prediction_result(output: dict, concise_evidence_summary: dict | None = None) -> dict:
    numeric_confidence = output.get("numeric_confidence")
    confidence_value = format_confidence_value(numeric_confidence)
    confidence_width = round(numeric_confidence * 100) if numeric_confidence is not None else 0
    target = format_target(output["prediction_target"])
    traceability = {
        "model": f"{output['model_name']} ({output['model_version']})",
        "model_id": output["model_id"],
        "data_as_of": output["data_as_of_timestamp"],
        "feature_generated_at": output["feature_generation_timestamp"],
        "prediction_generated_at": output["prediction_timestamp"],
        "evaluation_context": output["evaluation_context"],
        "evidence": output["evidence_reference"],
        "disclaimer": output["disclaimer_text"],
        "disclaimer_version": output.get("disclaimer_version"),
    }
    return {
        "primary": {
            "section_title": SECTION_TITLES["market_snapshot"],
            "ticker": output["ticker"],
            "signal": format_signal(output["model_signal"]),
            "raw_signal": output["model_signal"],
            "tone": signal_tone(output["model_signal"]),
            "target": target,
            "confidence": output["confidence_category"],
            "confidence_value": confidence_value,
            "confidence_width": confidence_width,
            "meta_items": [
                {"label": "Model", "value": output["model_name"]},
                {"label": "Target", "value": target},
                {"label": "Market data reviewed", "value": output["data_as_of_timestamp"]},
                {"label": "Signal generated", "value": output["prediction_timestamp"]},
                {
                    "label": "Universe rank",
                    "value": _format_rank(output.get("rank"), output.get("rank_universe_size")),
                },
            ],
        },
        "supporting": {
            "confidence_title": SECTION_TITLES["confidence"],
            "confidence_explanation": output["confidence_explanation"],
            "why_signal_title": SECTION_TITLES["why_signal"],
            "why_signal": output["context_summary"],
            "limitations_title": SECTION_TITLES["key_limitations"],
            "limitations": _as_list(output["limitation_summary"]),
            "evidence_title": SECTION_TITLES["model_evidence"],
            "concise_evidence": concise_evidence_summary,
            "insights": [
                {"title": SECTION_TITLES["confidence"], "body": output["confidence_explanation"]},
                {"title": SECTION_TITLES["why_signal"], "body": output["context_summary"]},
            ],
        },
        "secondary": {
            "traceability_title": SECTION_TITLES["traceability"],
            "traceability": traceability,
        },
        "disclaimer": output["disclaimer_text"],
    }


def render_prediction_result(output: dict, st=None, concise_evidence_summary: dict | None = None) -> dict:
    formatted = format_prediction_result(output, concise_evidence_summary)
    if st is not None:
        primary = formatted["primary"]
        supporting = formatted["supporting"]
        render_section_heading(
            primary["section_title"],
            "Near-term signal looking up to 5 trading days ahead, with confidence and context.",
            st,
        )
        render_primary_signal(
            primary["ticker"],
            primary["signal"],
            primary["confidence"],
            primary["target"],
            primary["confidence_value"],
            primary["confidence_width"],
            [(item["label"], item["value"]) for item in primary["meta_items"]],
            primary["tone"],
            st,
        )
        render_insight_grid([(item["title"], item["body"]) for item in supporting["insights"]], st)
        render_section_heading(supporting["limitations_title"], None, st)
        render_guidance_items(supporting["limitations"], st)
        if supporting["concise_evidence"]:
            summary = supporting["concise_evidence"]
            render_section_heading(supporting["evidence_title"], summary["headline"], st)
            for metric in summary["metric_highlights"]:
                st.caption(f"{metric['name']}: {metric['value']} - {metric['interpretation']}")
            st.caption(summary["stocks_covered"])
            if summary["caveat"]:
                st.caption(summary["caveat"])
        with render_secondary_details(formatted["secondary"]["traceability_title"], st=st):
            traceability = formatted["secondary"]["traceability"]
            st.write(f"Model used: {traceability['model']}")
            st.write(f"Model record: {traceability['model_id']}")
            st.write(f"Market data reviewed: {traceability['data_as_of']}")
            st.write(f"Features prepared: {traceability['feature_generated_at']}")
            st.write(f"Signal generated: {traceability['prediction_generated_at']}")
            st.write(f"Historical test window: {traceability['evaluation_context']}")
            st.write(f"Evidence record: {traceability['evidence']}")
        st.info(formatted["disclaimer"])
    return formatted


def _format_rank(rank: int | None, universe_size: int | None) -> str:
    if not rank or not universe_size:
        return "Not ranked"
    return f"{rank} of {universe_size}"
