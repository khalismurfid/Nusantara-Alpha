"""Guardrails for native Streamlit rendering."""

from __future__ import annotations

import inspect

from app_streamlit.components import ui_shell


def test_customer_ui_does_not_render_raw_html():
    source = inspect.getsource(ui_shell)

    assert "unsafe_allow_html" not in source
    assert "<div" not in source
    assert "<style" not in source
