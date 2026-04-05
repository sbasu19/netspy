import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from collections import deque
from monitor import SmartBandwidthMonitor

# --- Theme Colors ---
BG_COLOR = "#282828"  # Dark background
FG_COLOR = "#ebdbb2"  # Light text
LINE_NORMAL = "#b8bb26"  # Green line
LINE_ANOMALY = "#cc241d"  # Red line


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("netspy - AI Bandwidth Monitor")
        self.root.geometry("600x400")
        self.root.configure(bg=BG_COLOR)

        # Initialize the AI Brain
        self.monitor = SmartBandwidthMonitor(window_size=30, retrain_interval=15)

        # Graph Data Storage (stores the last 60 seconds for the visual graph)
        self.graph_data = deque([0] * 60, maxlen=60)

        # --- Setup Matplotlib Figure ---
        self.fig, self.ax = plt.subplots(figsize=(6, 4), facecolor=BG_COLOR)
        self.ax.set_facecolor(BG_COLOR)
        self.ax.tick_params(colors=FG_COLOR)
        for spine in self.ax.spines.values():
            spine.set_color(FG_COLOR)

        self.ax.set_title("Live Network Traffic (KB/s)", color=FG_COLOR)

        # Create the initial empty line
        (self.line,) = self.ax.plot(self.graph_data, color=LINE_NORMAL, linewidth=2)

        # Embed the graph into Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Status Label for Anomalies
        self.status_label = tk.Label(
            self.root,
            text="Gathering Baseline...",
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=("Arial", 14, "bold"),
        )
        self.status_label.pack(pady=5)

        # Start the update loop
        self.update_gui()

    def update_gui(self):
        # 1. Ask the monitor for the latest speed and AI status
        current_speed, is_anomaly = self.monitor.step()
        speed_kb = current_speed / 1024

        # 2. Update the visual graph data
        self.graph_data.append(speed_kb)
        self.line.set_ydata(self.graph_data)

        # Adjust the graph's Y-axis dynamically based on current speeds
        self.ax.set_ylim(0, max(self.graph_data) * 1.2 + 10)

        # 3. Update Colors and Text based on AI prediction
        if is_anomaly:
            self.line.set_color(LINE_ANOMALY)
            self.status_label.config(
                text=f"⚠️ ANOMALY: {speed_kb:.2f} KB/s", fg=LINE_ANOMALY
            )
        else:
            self.line.set_color(LINE_NORMAL)
            if self.monitor.is_model_trained:
                self.status_label.config(
                    text=f"Normal: {speed_kb:.2f} KB/s", fg=LINE_NORMAL
                )

        self.canvas.draw()

        # 4. Tell Tkinter to run this function again in 1000ms (1 second)
        self.root.after(1000, self.update_gui)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
