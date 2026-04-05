import tkinter as tk
from src.ui.components.sidebar import Sidebar
from src.ui.views.home_view import HomeView
from src.ui.views.monitor_view import MonitorView
from src.ui.styles import BG_DARK


class Dashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NETSPY - Advanced AI Dashboard")
        self.geometry("1100x750")
        self.configure(bg=BG_DARK)

        # Navigation configuration
        self.nav_items = [
            {"name": "home", "label": "Overview", "icon": "🏠"},
            {"name": "monitor", "label": "Live Monitor", "icon": "📈"},
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
        elif name == "monitor":
            self.current_view = MonitorView(self.content_area)

        if self.current_view:
            self.current_view.pack(fill=tk.BOTH, expand=True)
            self.sidebar.set_active(name)
