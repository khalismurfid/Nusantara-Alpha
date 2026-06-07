"""Native Streamlit rendering helpers for the customer-facing UI."""

from __future__ import annotations


def inject_customer_styles(st=None) -> None:
    """Reserved for future theme hooks.

    The app intentionally avoids raw HTML/CSS rendering so markup cannot leak
    into the customer-facing page.
    """
    return None


def render_app_header(title: str, subtitle: str, st=None) -> None:
    if st is None:
        return
    st.title(title)
    st.caption(subtitle)


def render_section_heading(title: str, caption: str | None = None, st=None) -> None:
    if st is None:
        return
    st.subheader(title)
    if caption:
        st.caption(caption)


def render_context_strip(items: list[tuple[str, str | None]], st=None) -> None:
    if st is None:
        return
    with st.container(border=True):
        columns = st.columns(len(items))
        for column, (label, value) in zip(columns, items, strict=False):
            column.caption(label)
            column.write(value or "Not available")


def render_primary_signal(
    ticker: str,
    signal: str,
    signal_badge: str,
    signal_summary: str,
    confidence: str,
    target: str,
    confidence_value: str,
    confidence_width: int,
    meta_items: list[tuple[str, str | None]],
    tone: str = "muted",
    st=None,
) -> None:
    if st is None:
        return
    clamped_width = max(0, min(confidence_width, 100))
    with st.container(border=True):
        signal_column, confidence_column = st.columns([1.6, 1])
        signal_column.caption(f"{ticker} | {target}")
        signal_column.metric("Model signal", signal_badge)
        if tone == "positive":
            signal_column.success(signal)
        elif tone == "negative":
            signal_column.error(signal)
        elif tone == "neutral":
            signal_column.info(signal)
        else:
            signal_column.warning(signal)
        signal_column.caption(signal_summary)

        confidence_column.metric("Confidence band", confidence, confidence_value)
        confidence_column.progress(clamped_width / 100)
        confidence_column.caption("Higher score means a stronger class probability, not certainty.")

        st.divider()
        meta_columns = st.columns(len(meta_items))
        for column, (label, value) in zip(meta_columns, meta_items, strict=False):
            column.caption(label)
            column.write(value or "Not available")


def render_guidance_items(items: list[str], st=None) -> None:
    if st is None:
        return
    for item in items:
        st.write(f"- {item}")


def render_insight_grid(items: list[tuple[str, str]], st=None) -> None:
    if st is None:
        return
    columns = st.columns(len(items))
    for column, (title, body) in zip(columns, items, strict=False):
        with column.container(border=True):
            st.markdown(f"**{title}**")
            st.write(body)


def render_metric_grid(metrics: list[dict], st=None) -> None:
    if st is None:
        return
    if not metrics:
        st.caption("No metric summary is available.")
        return
    columns = st.columns(min(3, len(metrics)))
    for index, metric in enumerate(metrics):
        column = columns[index % len(columns)]
        column.metric(metric.get("name", "Metric"), metric.get("value", "Not available"))
        interpretation = metric.get("interpretation")
        if interpretation:
            column.caption(interpretation)


def render_evidence_band(summary: dict, st=None) -> None:
    if st is None:
        return
    with st.container(border=True):
        st.caption(summary.get("section_title", "Past performance snapshot"))
        st.write(f"**{summary.get('headline', 'Evidence is loaded for this model.')}**")
        caveat = summary.get("caveat")
        if caveat:
            st.caption(caveat)
        render_metric_grid(summary.get("metrics", []), st)


def render_secondary_details(label: str, expanded: bool = False, st=None):
    if st is None:
        return None
    return st.expander(label, expanded=expanded)
