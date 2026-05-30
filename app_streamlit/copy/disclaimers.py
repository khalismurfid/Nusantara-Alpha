"""Centralized educational framing and copy-safety constants."""

from app_streamlit.copy.product_language import (
    has_raw_limitation_fragment,
    is_awkward_action_label,
)

DISCLAIMER_VERSION = "2026-05-29.v1"

EDUCATIONAL_DISCLAIMER = (
    "Nusantara Alpha is an educational research and portfolio demonstration "
    "tool. Model outputs are exploratory signals, not financial advice, "
    "personalized investment guidance, trade instructions, position sizing, "
    "portfolio allocation advice, or guaranteed outcomes."
)

APPROVED_PREDICTION_TERMS = {
    "model signal",
    "predicted direction",
    "confidence",
    "historical evidence",
    "limitations",
    "uncertainty",
    "educational research",
}

FORBIDDEN_ADVICE_PHRASES = {
    "you should buy",
    "you should sell",
    "safe trade",
    "guaranteed profit",
    "recommended position size",
    "optimal allocation",
}


def contains_forbidden_advice(text: str) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in FORBIDDEN_ADVICE_PHRASES)


def assert_copy_safe(text: str) -> None:
    if contains_forbidden_advice(text):
        raise ValueError("User-facing copy contains forbidden financial-advice framing.")


def assert_action_label_safe(label: str) -> None:
    if is_awkward_action_label(label):
        raise ValueError("Prediction action label is awkward or too academic.")


def assert_limitation_copy_readable(text: str) -> None:
    if has_raw_limitation_fragment(text):
        raise ValueError("Limitation copy looks like raw metadata instead of product guidance.")
