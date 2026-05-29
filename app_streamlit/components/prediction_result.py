"""Prediction result presentation helpers."""


def format_prediction_result(output: dict) -> dict:
    return {
        "ticker": output["ticker"],
        "signal": output["model_signal"],
        "confidence": output["confidence_category"],
        "confidence_explanation": output["confidence_explanation"],
        "context": output["context_summary"],
        "limitations": output["limitation_summary"],
        "model": f"{output['model_name']} ({output['model_version']})",
        "data_as_of": output["data_as_of_timestamp"],
        "feature_generated_at": output["feature_generation_timestamp"],
        "prediction_generated_at": output["prediction_timestamp"],
        "evidence": output["evidence_reference"],
        "disclaimer": output["disclaimer_text"],
    }


def render_prediction_result(output: dict, st=None) -> dict:
    formatted = format_prediction_result(output)
    if st is not None:
        st.subheader(formatted["ticker"])
        st.write(f"Model signal: {formatted['signal']}")
        st.write(f"Confidence: {formatted['confidence']}")
        st.caption(formatted["confidence_explanation"])
        st.write(formatted["context"])
        st.warning(formatted["limitations"])
        st.caption(f"Data as of: {formatted['data_as_of']}")
        st.caption(f"Features generated: {formatted['feature_generated_at']}")
        st.caption(f"Prediction generated: {formatted['prediction_generated_at']}")
        st.info(formatted["disclaimer"])
    return formatted

