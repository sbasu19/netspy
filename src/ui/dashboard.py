import tkinter as tk
from src.ui.components.sidebar import Sidebar
from src.ui.views.home_view import HomeView
from src.ui.views.monitor_view import MonitorView
from src.ui.views.cpu_view import CPUView
from src.ui.views.ram_view import RAMView
from src.ui.views.analyzer_view import AnalyzerView
from src.ui.styles import BG_DARK


class Dashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NETSPY - Advanced AI Dashboard")
        self.geometry("1150x750")
        self.configure(bg=BG_DARK)

        # Navigation configuration
        self.nav_items = [
            {"name": "home", "label": "Overview", "icon": "🏠"},
            {"name": "network", "label": "Net Monitor", "icon": "🌐"},
            {"name": "analyzer", "label": "Net Analyzer", "icon": "🔍"},
            {"name": "cpu", "label": "CPU Monitor", "icon": "⚡"},
            {"name": "ram", "label": "RAM Monitor", "icon": "💾"},
        ]

        # Layout Setup
        self.sidebar = Sidebar(self, self.nav_items, self.navigate)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.content_area = tk.Frame(self, bg=BG_DARK)
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.current_view = None
        self.navigate("home")

    def navigate(self, name):
        """Switch between different views."""
        if self.current_view:
            self.current_view.destroy()

        if name == "home":
            self.current_view = HomeView(self.content_area)
        elif name == "network":
            self.current_view = MonitorView(self.content_area)
        elif name == "analyzer":
            self.current_view = AnalyzerView(self.content_area)
        elif name == "cpu":
            self.current_view = CPUView(self.content_area)
        elif name == "ram":
            self.current_view = RAMView(self.content_area)

        if self.current_view:
            self.current_view.pack(fill=tk.BOTH, expand=True)
            self.sidebar.set_active(name)
