"""Model evidence presentation helpers."""


def format_evidence(evidence: dict) -> dict:
    return {
        "evidence_id": evidence["evidence_id"],
        "evaluation_period": evidence["evaluation_period"],
        "metrics": evidence.get("key_metrics", []),
        "supported_universe": evidence.get("supported_universe", []),
        "limitations": evidence.get("limitations", []),
        "data_quality_notes": evidence.get("data_quality_notes", []),
        "historical_performance_caveat": evidence.get("historical_performance_caveat", ""),
        "evidence_status": evidence.get("evidence_status"),
        "evidence_load_status": evidence.get("evidence_load_status"),
        "evidence_as_of": evidence.get("evidence_as_of"),
    }


def render_evidence_panel(evidence: dict, st=None) -> dict:
    formatted = format_evidence(evidence)
    if st is not None:
        st.subheader("Historical evidence")
        st.caption(f"Evaluation period: {formatted['evaluation_period']['start']} to {formatted['evaluation_period']['end']}")
        for metric in formatted["metrics"]:
            st.write(f"{metric['name']}: {metric['value']} - {metric['interpretation']}")
        st.write("Supported universe: " + ", ".join(formatted["supported_universe"]))
        for note in formatted["data_quality_notes"]:
            st.caption(note)
        for limitation in formatted["limitations"]:
            st.warning(limitation)
        st.info(formatted["historical_performance_caveat"])
    return formatted

