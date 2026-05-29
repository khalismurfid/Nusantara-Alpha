"""Paper-trading evidence display helpers."""


def format_paper_trading_evidence(evidence: dict) -> dict:
    summary = evidence.get("paper_trading_summary")
    return {
        "available": bool(summary and "No paper-trading evidence" not in summary),
        "summary": summary or "Paper-trading evidence is not available for this model.",
    }


def render_paper_trading_evidence(evidence: dict, st=None) -> dict:
    formatted = format_paper_trading_evidence(evidence)
    if st is not None:
        st.subheader("Paper-trading evidence")
        if formatted["available"]:
            st.write(formatted["summary"])
        else:
            st.caption(formatted["summary"])
    return formatted

