"""Unavailable and error state presentation helpers."""


def format_unavailable_state(reason: str, message: str, next_step: str | None = None) -> dict:
    return {
        "reason": reason,
        "message": message,
        "next_step": next_step,
    }


def render_unavailable_state(reason: str, message: str, next_step: str | None = None, st=None) -> dict:
    formatted = format_unavailable_state(reason, message, next_step)
    if st is not None:
        st.error(message)
        if next_step:
            st.caption(next_step)
    return formatted

