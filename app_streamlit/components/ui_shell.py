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
    st.subheader("What this does")
    st.info(subtitle)
    steps = st.columns(3)
    steps[0].write("**1. Pick a stock**")
    steps[0].caption("Choose one supported Indonesian stock.")
    steps[1].write("**2. See the signal**")
    steps[1].caption("View the model's near-term read.")
    steps[2].write("**3. Read the context**")
    steps[2].caption("Check confidence, reason, and limitations.")


def render_section_heading(title: str, caption: str | None = None, st=None) -> None:
    if st is None:
        return
    st.subheader(title)
    if caption:
        st.caption(caption)


def render_context_strip(items: list[tuple[str, str | None]], st=None) -> None:
    if st is None:
        return
    columns = st.columns(len(items))
    for column, (label, value) in zip(columns, items, strict=False):
        column.metric(label, value or "Not available")


def render_primary_signal(
    ticker: str,
    signal: str,
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
        signal_column, confidence_column = st.columns([2.3, 1])
        signal_column.caption(f"{ticker} | {target}")
        signal_column.header(signal)
        signal_column.caption("Model signal looking up to 5 trading days ahead.")

        confidence_column.metric("Confidence", confidence, confidence_value)
        confidence_column.progress(clamped_width / 100)
        confidence_column.caption("Confidence is uncertainty, not a guarantee.")

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
