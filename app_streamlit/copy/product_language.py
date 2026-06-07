"""Product-facing labels and wording rules for the Streamlit app."""

PRIMARY_ACTION_PREDICT = "Predict"

SECTION_TITLES = {
    "prediction": "Model signal",
    "confidence": "Confidence",
    "why_signal": "What influenced the signal",
    "key_limitations": "Important limitations",
    "model_evidence": "Past performance",
    "traceability": "Technical details",
    "market_snapshot": "Signal summary",
    "evidence_snapshot": "Past performance snapshot",
}

AWKWARD_ACTION_LABELS = {
    "request educational prediction",
    "request research prediction",
    "generate educational signal request",
}

RAW_LIMITATION_FRAGMENTS = {
    "limited universe",
    "small supported universe",
    "no guarantee of future",
    "no guarantee of future accuracy",
}

SIGNAL_LABELS = {
    "up": "UP - leans toward the upward barrier",
    "down": "DOWN - leans toward the downward barrier",
    "neutral": "NEUTRAL - mixed or range-bound read",
    "unavailable": "Unavailable",
}

SIGNAL_BADGES = {
    "up": "UP",
    "down": "DOWN",
    "neutral": "NEUTRAL",
    "unavailable": "N/A",
}

SIGNAL_SUMMARIES = {
    "up": "The model puts more weight on the upward barrier outcome.",
    "down": "The model puts more weight on the downward barrier outcome.",
    "neutral": "The model does not show a clear upward or downward lean.",
    "unavailable": "A signal is not available for this selection.",
}

TARGET_LABELS = {
    "near_term_barrier_signal": "Near-term signal",
    "next_market_session_direction": "Near-term signal",
}

SIGNAL_TONES = {
    "up": "positive",
    "down": "negative",
    "neutral": "neutral",
    "unavailable": "muted",
}


def normalize_copy(text: str) -> str:
    return " ".join(text.lower().split())


def is_awkward_action_label(label: str) -> bool:
    return normalize_copy(label) in AWKWARD_ACTION_LABELS


def has_raw_limitation_fragment(text: str) -> bool:
    normalized = normalize_copy(text)
    return any(fragment in normalized for fragment in RAW_LIMITATION_FRAGMENTS)


def format_signal(signal: str) -> str:
    return SIGNAL_LABELS.get(normalize_copy(signal), signal.replace("_", " ").title())


def signal_badge(signal: str) -> str:
    return SIGNAL_BADGES.get(normalize_copy(signal), signal.replace("_", " ").upper())


def signal_summary(signal: str) -> str:
    return SIGNAL_SUMMARIES.get(normalize_copy(signal), "The model signal needs review.")


def signal_tone(signal: str) -> str:
    return SIGNAL_TONES.get(normalize_copy(signal), "muted")


def format_target(target: str) -> str:
    return TARGET_LABELS.get(normalize_copy(target), target.replace("_", " ").title())


def format_confidence_value(value: float | None) -> str:
    if value is None:
        return "Not scored"
    return f"{round(value * 100)}%"
