"""Public demo status and review note helpers."""

from __future__ import annotations

from datetime import datetime


def _friendly_timestamp(value: str | None) -> str | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value
    formatted = parsed.strftime("%b %d, %Y %H:%M UTC")
    return formatted.replace(" 0", " ")


def _friendly_limitations(text: str) -> str:
    normalized = " ".join(text.lower().split())
    if normalized == "static approved non-sensitive data for reviewing the product flow.":
        return "This preview uses approved historical data. Live market feeds are not connected in this version."
    return text


def format_demo_banner(status: dict) -> dict:
    release_status = status.get("release_status", "unavailable")
    if release_status == "full":
        title = "Signal availability"
        message = "Signals are available for the reviewed stocks in this version."
    elif release_status == "degraded":
        title = "Signal availability"
        message = "Signals are paused until the model and data checks are complete."
    else:
        title = "Signal availability"
        message = "Signals are unavailable right now."
    return {
        "release_status": release_status,
        "title": title,
        "message": message,
        "limitations": _friendly_limitations(status.get("demo_limitations", "")),
        "data_as_of": _friendly_timestamp(status.get("data_as_of")),
        "public_predictions_available": bool(status.get("public_predictions_available")),
        "disclaimer": status.get("disclaimer", ""),
    }


def render_demo_banner(status: dict, st=None) -> dict:
    banner = format_demo_banner(status)
    if st is not None:
        with st.expander("Review notes", expanded=False):
            st.write(f"**{banner['title']}**")
            st.write(banner["message"])
            if banner["data_as_of"]:
                st.caption(f"Data last reviewed: {banner['data_as_of']}")
            if banner["limitations"]:
                st.caption(banner["limitations"])
            if banner["disclaimer"]:
                st.caption(banner["disclaimer"])
    return banner
