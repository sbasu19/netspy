from src.ui.views.monitor_view import BaseMonitorView
from src.ui.styles import ACCENT_BLUE

class CPUView(BaseMonitorView):
    def __init__(self, master, **kwargs):
        super().__init__(master, "cpu", "CPU PERFORMANCE CLUSTER", "%", ACCENT_BLUE, **kwargs)
