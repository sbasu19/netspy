import tkinter as tk
import psutil
from src.ui.styles import (
    BG_DARK, BG_CARD, TEXT_MAIN, TEXT_DIM, ACCENT_CYAN, ACCENT_GREEN, ACCENT_BLUE, ACCENT_PURPLE,
    FONT_TITLE, FONT_SUBTITLE, FONT_NORMAL, FONT_BOLD, BORDER_RADIUS
)
from src.ui.components.rounded_frame import RoundedFrame

class HomeView(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg=BG_DARK, **kwargs)

        # Header Section
        header_frame = tk.Frame(self, bg=BG_DARK)
        header_frame.pack(fill=tk.X, pady=(40, 20), padx=50)

        tk.Label(
            header_frame, text="SYSTEM OVERVIEW", fg=ACCENT_CYAN, bg=BG_DARK, font=FONT_TITLE
        ).pack(anchor="w")
        
        tk.Label(
            header_frame, text="Real-time performance and intelligence metrics", 
            fg=TEXT_DIM, bg=BG_DARK, font=FONT_NORMAL
        ).pack(anchor="w")

        # --- Main Dashboard Grid ---
        grid_frame = tk.Frame(self, bg=BG_DARK)
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=40)

        # Top Row: Network Status
        status_row = tk.Frame(grid_frame, bg=BG_DARK)
        status_row.pack(fill=tk.X, pady=10)

        self.create_stat_card(status_row, "System Status", "OPERATIONAL", "Healthy", ACCENT_GREEN, side=tk.LEFT)
        self.create_stat_card(status_row, "Network Node", "ETH-0", "Connected", ACCENT_CYAN, side=tk.RIGHT)

        # Middle Row: Resources
        resource_row = tk.Frame(grid_frame, bg=BG_DARK)
        resource_row.pack(fill=tk.X, pady=10)

        self.cpu_card = self.create_stat_card(resource_row, "CPU Load", "0%", "Calculating...", ACCENT_BLUE, side=tk.LEFT)
        self.ram_card = self.create_stat_card(resource_row, "Memory Use", "0%", "Calculating...", ACCENT_PURPLE, side=tk.RIGHT)

        # Start background update for resources
        self.update_resources()

    def create_stat_card(self, parent, title, value, subtitle, color, side):
        rf = RoundedFrame(parent, bg=BG_CARD, border_color=color, radius=BORDER_RADIUS, width=380, height=120)
        rf.pack(side=side, expand=True, fill=tk.BOTH, padx=10)
        
        container = rf.get_container()
        container.pack_propagate(False)
        
        tk.Label(container, text=title, fg=TEXT_DIM, bg=BG_CARD, font=FONT_BOLD).pack(anchor="w", padx=20, pady=(15, 0))
        
        val_label = tk.Label(container, text=value, fg=color, bg=BG_CARD, font=FONT_SUBTITLE)
        val_label.pack(anchor="w", padx=20, pady=(5, 0))
        
        sub_label = tk.Label(container, text=subtitle, fg=TEXT_DIM, bg=BG_CARD, font=FONT_NORMAL)
        sub_label.pack(anchor="w", padx=20, pady=(0, 15))
        
        return {"val": val_label, "sub": sub_label}

    def update_resources(self):
        cpu_usage = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        
        self.cpu_card["val"].config(text=f"{cpu_usage}%")
        self.cpu_card["sub"].config(text=f"Processors active")
        
        self.ram_card["val"].config(text=f"{ram.percent}%")
        self.ram_card["sub"].config(text=f"{ram.used // (1024**2)} MB / {ram.total // (1024**2)} MB")
        
        self.after_id = self.after(2000, self.update_resources)

    def destroy(self):
        if hasattr(self, 'after_id'):
            self.after_cancel(self.after_id)
        super().destroy()
