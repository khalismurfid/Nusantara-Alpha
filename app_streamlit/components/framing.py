"""Educational framing component."""

from app_streamlit.copy.disclaimers import EDUCATIONAL_DISCLAIMER


def framing_text() -> str:
    return EDUCATIONAL_DISCLAIMER


def render_framing(st=None) -> str:
    if st is not None:
        st.info(EDUCATIONAL_DISCLAIMER)
    return EDUCATIONAL_DISCLAIMER

