from src.ui.views.monitor_view import BaseMonitorView
from src.ui.styles import ACCENT_PURPLE

class RAMView(BaseMonitorView):
    def __init__(self, master, **kwargs):
        super().__init__(master, "ram", "MEMORY ALLOCATION UNIT", "%", ACCENT_PURPLE, **kwargs)
