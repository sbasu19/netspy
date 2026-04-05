import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from collections import deque
import time
from src.core.monitor import SmartBandwidthMonitor
from src.ui.styles import (
    BG_DARK, BG_CARD, TEXT_MAIN, TEXT_DIM, ACCENT_CYAN, ANOMALY_RED, ACCENT_GREEN,
    FONT_SUBTITLE, FONT_NORMAL, FONT_BOLD, BORDER_RADIUS
)
from src.ui.components.rounded_frame import RoundedFrame


class MonitorView(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg=BG_DARK, **kwargs)

        self.monitor = SmartBandwidthMonitor(window_size=30, retrain_interval=15)
        self.graph_data = deque([0] * 60, maxlen=60)
        self.start_time = time.time()
        self.peak_speed = 0
        self.total_bytes = 0

        # --- Top Section: Header ---
        header_frame = tk.Frame(self, bg=BG_DARK)
        header_frame.pack(fill=tk.X, pady=(40, 10), padx=50)
        
        tk.Label(
            header_frame, text="LIVE TRAFFIC ANALYSIS", fg=ACCENT_CYAN, bg=BG_DARK, font=FONT_SUBTITLE
        ).pack(anchor="w")

        # --- Main Layout: Graph (Left) & Sidebar (Right) ---
        main_layout = tk.Frame(self, bg=BG_DARK)
        main_layout.pack(fill=tk.BOTH, expand=True, padx=40, pady=10)

        # Graph Container
        self.graph_rf = RoundedFrame(main_layout, bg=BG_DARK, border_color="#30363d", radius=BORDER_RADIUS)
        self.graph_rf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        self.setup_graph(self.graph_rf.get_container())

        # Stats Sidebar
        self.stats_rf = RoundedFrame(main_layout, bg=BG_CARD, border_color=ACCENT_CYAN, radius=BORDER_RADIUS, width=220)
        self.stats_rf.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        self.setup_stats(self.stats_rf.get_container())

        # Start loop
        self.update_gui()

    def setup_graph(self, container):
        self.fig, self.ax = plt.subplots(figsize=(5, 3), facecolor=BG_DARK)
        self.ax.set_facecolor(BG_DARK)
        self.ax.tick_params(colors=TEXT_DIM, labelsize=8)
        for spine in self.ax.spines.values():
            spine.set_color("#30363d")

        (self.line,) = self.ax.plot(self.graph_data, color=ACCENT_CYAN, linewidth=2)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=container)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def setup_stats(self, container):
        container.pack_propagate(False)
        tk.Label(container, text="SESSION STATS", fg=TEXT_DIM, bg=BG_CARD, font=FONT_BOLD).pack(pady=(20, 15))

        self.stat_labels = {}
        stats = [
            ("Peak", "0.0 KB/s", ACCENT_CYAN),
            ("Average", "0.0 KB/s", TEXT_MAIN),
            ("Total Data", "0.0 MB", ACCENT_GREEN),
            ("Uptime", "00:00:00", TEXT_DIM),
        ]

        for title, val, color in stats:
            tk.Label(container, text=title, fg=TEXT_DIM, bg=BG_CARD, font=FONT_NORMAL).pack(anchor="w", padx=20)
            lbl = tk.Label(container, text=val, fg=color, bg=BG_CARD, font=FONT_BOLD)
            lbl.pack(anchor="w", padx=20, pady=(2, 10))
            self.stat_labels[title] = lbl

        self.status_bar = tk.Label(container, text="GATHERING...", fg=ACCENT_CYAN, bg="#161b22", font=FONT_BOLD, pady=10)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_gui(self):
        current_speed, is_anomaly = self.monitor.step()
        speed_kb = current_speed / 1024
        
        self.total_bytes += current_speed
        if speed_kb > self.peak_speed: self.peak_speed = speed_kb

        # Update Graph
        self.graph_data.append(speed_kb)
        self.line.set_ydata(self.graph_data)
        self.ax.set_ylim(0, max(self.graph_data) * 1.2 + 5)
        self.canvas.draw_idle()

        # Update Stats
        uptime = time.strftime("%H:%M:%S", time.gmtime(time.time() - self.start_time))
        avg_speed = (self.total_bytes / (time.time() - self.start_time)) / 1024
        
        self.stat_labels["Peak"].config(text=f"{self.peak_speed:.1f} KB/s")
        self.stat_labels["Average"].config(text=f"{avg_speed:.1f} KB/s")
        self.stat_labels["Total Data"].config(text=f"{self.total_bytes / (1024**2):.2f} MB")
        self.stat_labels["Uptime"].config(text=uptime)

        if is_anomaly:
            self.line.set_color(ANOMALY_RED)
            self.status_bar.config(text="⚠️ ANOMALY", fg=ANOMALY_RED, bg="#2d1616")
        else:
            self.line.set_color(ACCENT_CYAN)
            if self.monitor.is_model_trained:
                self.status_bar.config(text="● NORMAL", fg=ACCENT_GREEN, bg="#16221a")
            else:
                self.status_label_text = f"BASELINE: {len(self.monitor.history)}/30"
                self.status_bar.config(text=self.status_label_text, fg=ACCENT_CYAN, bg="#161b22")

        self.after_id = self.after(1000, self.update_gui)

    def destroy(self):
        if hasattr(self, 'after_id'):
            self.after_cancel(self.after_id)
        super().destroy()
