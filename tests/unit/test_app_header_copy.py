from app_streamlit.components.framing import framing_text


class _ElementRecorder:
    def __init__(self):
        self.values = []

    def write(self, value):
        self.values.append(("write", value))

    def caption(self, value):
        self.values.append(("caption", value))


class _StreamlitRecorder:
    def __init__(self):
        self.values = []
        self._columns = [_ElementRecorder(), _ElementRecorder(), _ElementRecorder()]

    def title(self, value):
        self.values.append(("title", value))

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
    assert recorder.values[1] == ("subheader", "What this does")
    assert recorder.values[2][0] == "info"
    assert "quick outlook" in recorder.values[2][1].lower()
    assert recorder._columns[0].values[0] == ("write", "**1. Pick a stock**")
