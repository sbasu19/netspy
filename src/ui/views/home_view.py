import tkinter as tk
import psutil
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from collections import deque
import numpy as np
from src.ui.styles import (
    BG_DARK, BG_CARD, TEXT_MAIN, TEXT_DIM, ACCENT_CYAN, ACCENT_GREEN, ACCENT_BLUE, ACCENT_PURPLE,
    FONT_TITLE, FONT_SUBTITLE, FONT_NORMAL, FONT_BOLD, BORDER_RADIUS
)
from src.ui.components.rounded_frame import RoundedFrame

class HomeView(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg=BG_DARK, **kwargs)

        self.buffer_size = 50
        self.cpu_history = deque([0.0] * self.buffer_size, maxlen=self.buffer_size)
        self.ram_history = deque([0.0] * self.buffer_size, maxlen=self.buffer_size)

        # Header Section
        header_frame = tk.Frame(self, bg=BG_DARK)
        header_frame.pack(fill=tk.X, pady=(30, 10), padx=50)

        tk.Label(
            header_frame, text="SYSTEM OVERVIEW", fg=ACCENT_CYAN, bg=BG_DARK, font=FONT_TITLE
        ).pack(anchor="w")
        
        tk.Label(
            header_frame, text="Real-time performance and intelligence metrics", 
            fg=TEXT_DIM, bg=BG_DARK, font=FONT_NORMAL
        ).pack(anchor="w")

        # --- Main Dashboard Grid ---
        self.grid_frame = tk.Frame(self, bg=BG_DARK)
        self.grid_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 40))

        # Top Row: Network & System Status
        status_row = tk.Frame(self.grid_frame, bg=BG_DARK)
        status_row.pack(fill=tk.X, pady=5)

        self.sys_status_card = self.create_stat_card(status_row, "System Status", "OPERATIONAL", "Healthy", ACCENT_GREEN, side=tk.LEFT)
        self.net_node_card = self.create_stat_card(status_row, "Network Node", "Detecting...", "Scanning...", ACCENT_CYAN, side=tk.RIGHT)

        # Middle Row: Resource Graphs
        graph_row = tk.Frame(self.grid_frame, bg=BG_DARK)
        graph_row.pack(fill=tk.BOTH, expand=True, pady=10)

        # CPU Graph Card
        self.cpu_graph_rf = RoundedFrame(graph_row, bg=BG_CARD, border_color=ACCENT_BLUE, radius=BORDER_RADIUS)
        self.cpu_graph_rf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        self.setup_mini_graph(self.cpu_graph_rf.get_container(), "CPU LOAD (%)", ACCENT_BLUE, "cpu")

        # RAM Graph Card
        self.ram_graph_rf = RoundedFrame(graph_row, bg=BG_CARD, border_color=ACCENT_PURPLE, radius=BORDER_RADIUS)
        self.ram_graph_rf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        self.setup_mini_graph(self.ram_graph_rf.get_container(), "MEMORY USE (%)", ACCENT_PURPLE, "ram")

        # Start background updates
        self.update_loop()

    def setup_mini_graph(self, container, title, color, attr_prefix):
        tk.Label(container, text=title, fg=TEXT_DIM, bg=BG_CARD, font=FONT_BOLD).pack(pady=(10, 0))
        
        fig, ax = plt.subplots(figsize=(4, 2), facecolor=BG_CARD)
        ax.set_facecolor(BG_CARD)
        ax.set_ylim(0, 100)
        ax.axis('off') # Cleaner look for mini graphs

        x_vals = np.arange(self.buffer_size)
        line, = ax.plot(x_vals, [0]*self.buffer_size, color=color, linewidth=2)
        fill = ax.fill_between(x_vals, [0]*self.buffer_size, color=color, alpha=0.1)
        
        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        setattr(self, f"{attr_prefix}_fig", fig)
        setattr(self, f"{attr_prefix}_ax", ax)
        setattr(self, f"{attr_prefix}_line", line)
        setattr(self, f"{attr_prefix}_fill", fill)
        setattr(self, f"{attr_prefix}_canvas", canvas)

    def create_stat_card(self, parent, title, value, subtitle, color, side):
        rf = RoundedFrame(parent, bg=BG_CARD, border_color=color, radius=BORDER_RADIUS, width=380, height=100)
        rf.pack(side=side, expand=True, fill=tk.BOTH, padx=10)
        
        container = rf.get_container()
        container.pack_propagate(False)
        
        tk.Label(container, text=title, fg=TEXT_DIM, bg=BG_CARD, font=FONT_BOLD).pack(anchor="w", padx=20, pady=(15, 0))
        val_label = tk.Label(container, text=value, fg=color, bg=BG_CARD, font=FONT_SUBTITLE)
        val_label.pack(anchor="w", padx=20, pady=(2, 0))
        sub_label = tk.Label(container, text=subtitle, fg=TEXT_DIM, bg=BG_CARD, font=FONT_NORMAL)
        sub_label.pack(anchor="w", padx=20, pady=(0, 10))
        
        return {"val": val_label, "sub": sub_label}

    def get_active_interface(self):
        """Identify the primary network interface."""
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        io_counters = psutil.net_io_counters(pernic=True)
        
        best_iface = "N/A"
        max_traffic = -1
        
        for iface, addr_list in addrs.items():
            # Skip loopback
            if iface == 'lo' or 'loopback' in iface.lower(): continue
            
            # Check if up
            if iface in stats and not stats[iface].isup: continue
            
            # Use the one with most traffic as "active"
            if iface in io_counters:
                traffic = io_counters[iface].bytes_sent + io_counters[iface].bytes_recv
                if traffic > max_traffic:
                    max_traffic = traffic
                    best_iface = iface
                    
        return best_iface

    def update_loop(self):
        # 1. Update Resource Data
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        
        self.cpu_history.append(cpu_usage)
        self.ram_history.append(ram_usage)

        # 2. Update Graphs
        for prefix, history in [("cpu", self.cpu_history), ("ram", self.ram_history)]:
            line = getattr(self, f"{prefix}_line")
            fill = getattr(self, f"{prefix}_fill")
            ax = getattr(self, f"{prefix}_ax")
            canvas = getattr(self, f"{prefix}_canvas")
            
            y_data = list(history)
            line.set_ydata(y_data)
            
            # Update fill
            fill.remove()
            color = line.get_color()
            setattr(self, f"{prefix}_fill", ax.fill_between(np.arange(self.buffer_size), y_data, color=color, alpha=0.1))
            
            canvas.draw_idle()

        # 3. Update Network Info
        active_iface = self.get_active_interface()
        self.net_node_card["val"].config(text=active_iface.upper())
        self.net_node_card["sub"].config(text="ACTIVE NODE")

        self.after_id = self.after(500, self.update_loop)

    def destroy(self):
        if hasattr(self, 'after_id'):
            self.after_cancel(self.after_id)
        super().destroy()
