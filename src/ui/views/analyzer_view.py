import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from src.core.monitor import AIResourceMonitor
from src.ui.styles import (
    BG_DARK, BG_CARD, TEXT_MAIN, TEXT_DIM, ACCENT_CYAN, ACCENT_GREEN, ACCENT_BLUE, ACCENT_PURPLE,
    FONT_TITLE, FONT_SUBTITLE, FONT_NORMAL, FONT_BOLD, BORDER_RADIUS, FONT_MONO
)
from src.ui.components.rounded_frame import RoundedFrame

class AnalyzerView(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg=BG_DARK, **kwargs)
        
        self.monitor = AIResourceMonitor(resource_type="network") # Use generic monitor core

        # Header
        header_frame = tk.Frame(self, bg=BG_DARK)
        header_frame.pack(fill=tk.X, pady=(40, 10), padx=50)
        tk.Label(header_frame, text="NETWORK ANALYZER", fg=ACCENT_CYAN, bg=BG_DARK, font=FONT_TITLE).pack(anchor="w")
        tk.Label(header_frame, text="Real-time Protocol & IP Traffic Intelligence", fg=TEXT_DIM, bg=BG_DARK, font=FONT_NORMAL).pack(anchor="w")

        # Main Layout
        main_layout = tk.Frame(self, bg=BG_DARK)
        main_layout.pack(fill=tk.BOTH, expand=True, padx=40, pady=10)

        # Left Column: Protocol Distribution (Bar Chart)
        self.proto_rf = RoundedFrame(main_layout, bg=BG_CARD, border_color=ACCENT_BLUE, radius=BORDER_RADIUS)
        self.proto_rf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        self.setup_proto_chart(self.proto_rf.get_container())

        # Right Column: Top IP Addresses (List)
        self.ip_rf = RoundedFrame(main_layout, bg=BG_CARD, border_color=ACCENT_PURPLE, radius=BORDER_RADIUS, width=350)
        self.ip_rf.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        self.setup_ip_list(self.ip_rf.get_container())

        self.update_loop()

    def setup_proto_chart(self, container):
        tk.Label(container, text="PROTOCOL DISTRIBUTION", fg=TEXT_DIM, bg=BG_CARD, font=FONT_BOLD).pack(pady=(20, 10))
        
        self.fig, self.ax = plt.subplots(figsize=(5, 4), facecolor=BG_CARD)
        self.ax.set_facecolor(BG_CARD)
        self.ax.tick_params(colors=TEXT_DIM, labelsize=9)
        for spine in self.ax.spines.values(): spine.set_color("#30363d")

        self.bars = self.ax.bar(["TCP", "UDP"], [0, 0], color=[ACCENT_BLUE, ACCENT_PURPLE], alpha=0.8)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=container)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    def setup_ip_list(self, container):
        container.pack_propagate(False)
        tk.Label(container, text="TOP REMOTE ENDPOINTS", fg=TEXT_DIM, bg=BG_CARD, font=FONT_BOLD).pack(pady=(20, 10))
        
        self.ip_list_frame = tk.Frame(container, bg=BG_CARD)
        self.ip_list_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        self.ip_labels = []
        for i in range(8):
            lbl = tk.Label(self.ip_list_frame, text="", fg=TEXT_MAIN, bg=BG_CARD, font=FONT_MONO, anchor="w")
            lbl.pack(fill=tk.X, pady=4)
            self.ip_labels.append(lbl)

    def update_loop(self):
        # 1. Fetch connection stats from core
        top_ips, proto_counts = self.monitor.get_connection_stats()

        # 2. Update Bar Chart
        for bar, h in zip(self.bars, [proto_counts["TCP"], proto_counts["UDP"]]):
            bar.set_height(h)
        
        self.ax.set_ylim(0, max(list(proto_counts.values()) + [10]) * 1.2)
        self.canvas.draw_idle()

        # 3. Update IP List
        for i, (ip, count) in enumerate(top_ips):
            if i < len(self.ip_labels):
                self.ip_labels[i].config(text=f"{i+1}. {ip:<18} [{count} conn]")
        
        # Clear remaining labels if fewer than 8 IPs
        for i in range(len(top_ips), 8):
            self.ip_labels[i].config(text="")

        self.after_id = self.after(2000, self.update_loop)

    def destroy(self):
        if hasattr(self, 'after_id'): self.after_cancel(self.after_id)
        super().destroy()
