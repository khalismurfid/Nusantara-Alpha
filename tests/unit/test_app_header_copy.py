from app_streamlit.components.framing import framing_text


class _ElementRecorder:
    def __init__(self):
        self.values = []

    def metric(self, label, value):
        self.values.append(("metric", label, value))

    def write(self, value):
        self.values.append(("write", value))

    def caption(self, value):
        self.values.append(("caption", value))


class _StreamlitRecorder:
    def __init__(self):
        self.values = []

    def title(self, value):
        self.values.append(("title", value))

    def caption(self, value):
        self.values.append(("caption", value))

    def subheader(self, value):
        self.values.append(("subheader", value))

    def info(self, value):
        self.values.append(("info", value))

    def columns(self, count):
        assert count == 3
        return self._columns


def test_app_header_puts_plain_explanation_before_workflow_steps():
    from app_streamlit.components.ui_shell import render_app_header

    recorder = _StreamlitRecorder()

    render_app_header("Nusantara Alpha", framing_text(), recorder)

    assert recorder.values[0] == ("title", "Nusantara Alpha")
    assert recorder.values[1][0] == "caption"
    assert "quick outlook" in recorder.values[1][1].lower()
    assert len(recorder.values) == 2
