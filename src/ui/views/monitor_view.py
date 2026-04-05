import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from collections import deque
import time
import numpy as np
from src.core.monitor import AIResourceMonitor
from src.ui.styles import (
    BG_DARK, BG_CARD, TEXT_MAIN, TEXT_DIM, ACCENT_CYAN, ANOMALY_RED, ACCENT_GREEN,
    FONT_SUBTITLE, FONT_NORMAL, FONT_BOLD, BORDER_RADIUS
)
from src.ui.components.rounded_frame import RoundedFrame

class BaseMonitorView(tk.Frame):
    """Base class for live resource monitors (Network, CPU, RAM)."""
    def __init__(self, master, resource_type, title, unit, color, **kwargs):
        super().__init__(master, bg=BG_DARK, **kwargs)
        
        self.resource_type = resource_type
        self.unit = unit
        self.accent_color = color
        
        self.monitor = AIResourceMonitor(resource_type=resource_type)
        self.buffer_size = 120
        self.graph_data = deque([0.0] * self.buffer_size, maxlen=self.buffer_size)
        self.raw_data = deque([0.0] * 10, maxlen=10)

        self.start_time = time.time()
        self.peak_val = 0
        self.total_val = 0
        self.frame_count = 0

        # UI Setup
        header_frame = tk.Frame(self, bg=BG_DARK)
        header_frame.pack(fill=tk.X, pady=(40, 10), padx=50)
        tk.Label(header_frame, text=title, fg=self.accent_color, bg=BG_DARK, font=FONT_SUBTITLE).pack(anchor="w")

        main_layout = tk.Frame(self, bg=BG_DARK)
        main_layout.pack(fill=tk.BOTH, expand=True, padx=40, pady=10)

        self.graph_rf = RoundedFrame(main_layout, bg=BG_DARK, border_color="#30363d", radius=BORDER_RADIUS)
        self.graph_rf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        self.setup_graph(self.graph_rf.get_container())

        self.stats_rf = RoundedFrame(main_layout, bg=BG_CARD, border_color=self.accent_color, radius=BORDER_RADIUS, width=220)
        self.stats_rf.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        self.setup_stats(self.stats_rf.get_container())

        self.update_gui()

    def setup_graph(self, container):
        self.fig, self.ax = plt.subplots(figsize=(5, 3), facecolor=BG_DARK)
        self.ax.set_facecolor(BG_DARK)
        self.ax.tick_params(colors=TEXT_DIM, labelsize=8)
        for spine in self.ax.spines.values(): spine.set_color("#30363d")

        self.x_vals = np.arange(self.buffer_size)
        self.line, = self.ax.plot(self.x_vals, list(self.graph_data), color=self.accent_color, linewidth=2, alpha=0.9)
        self.fill = self.ax.fill_between(self.x_vals, list(self.graph_data), color=self.accent_color, alpha=0.15)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=container)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def setup_stats(self, container):
        container.pack_propagate(False)
        tk.Label(container, text="METRIC STATS", fg=TEXT_DIM, bg=BG_CARD, font=FONT_BOLD).pack(pady=(20, 15))

        self.stat_labels = {}
        stats = [
            ("Peak", f"0.0 {self.unit}", self.accent_color),
            ("Average", f"0.0 {self.unit}", TEXT_MAIN),
            ("Total Used", f"0.0 {self.unit}*s", ACCENT_GREEN),
            ("Uptime", "00:00:00", TEXT_DIM),
        ]

        for title, val, color in stats:
            tk.Label(container, text=title, fg=TEXT_DIM, bg=BG_CARD, font=FONT_NORMAL).pack(anchor="w", padx=20)
            lbl = tk.Label(container, text=val, fg=color, bg=BG_CARD, font=FONT_BOLD)
            lbl.pack(anchor="w", padx=20, pady=(2, 10))
            self.stat_labels[title] = lbl

        self.status_bar = tk.Label(container, text="GATHERING...", fg=self.accent_color, bg="#161b22", font=FONT_BOLD, pady=10)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def format_value(self, val):
        if self.resource_type == "network": return f"{val/1024:.1f} KB/s"
        return f"{val:.1f} %"

    def update_gui(self):
        val, is_anomaly = self.monitor.step()
        self.raw_data.append(val)
        smoothed_val = sum(self.raw_data) / len(self.raw_data)
        self.graph_data.append(smoothed_val)
        
        self.total_val += val * 0.04
        if val > self.peak_val: self.peak_val = val

        # Update Graph
        y_data = list(self.graph_data)
        self.line.set_ydata(y_data)
        self.fill.remove()
        color = ANOMALY_RED if is_anomaly else self.accent_color
        self.fill = self.ax.fill_between(self.x_vals, y_data, color=color, alpha=0.15)
        self.line.set_color(color)

        self.ax.set_ylim(0, max(max(y_data) * 1.3, 10 if self.resource_type != "network" else 20))
        self.canvas.draw_idle()

        # Update Stats
        self.frame_count += 1
        if self.frame_count % 15 == 0:
            uptime = time.strftime("%H:%M:%S", time.gmtime(time.time() - self.start_time))
            avg = (self.total_val / (time.time() - self.start_time))
            
            self.stat_labels["Peak"].config(text=self.format_value(self.peak_val))
            self.stat_labels["Average"].config(text=self.format_value(avg))
            self.stat_labels["Uptime"].config(text=uptime)

            if is_anomaly:
                self.status_bar.config(text="⚠️ ANOMALY DETECTED", fg=ANOMALY_RED, bg="#2d1616")
            elif self.monitor.is_model_trained:
                self.status_bar.config(text="● SYSTEM NORMAL", fg=ACCENT_GREEN, bg="#16221a")

        self.after_id = self.after(40, self.update_gui)

    def destroy(self):
        if hasattr(self, 'after_id'): self.after_cancel(self.after_id)
        super().destroy()

class MonitorView(BaseMonitorView):
    def __init__(self, master, **kwargs):
        super().__init__(master, "network", "LIVE TRAFFIC ANALYSIS", "KB/s", ACCENT_CYAN, **kwargs)

    def format_value(self, val):
        return f"{val/1024:.1f} KB/s"
