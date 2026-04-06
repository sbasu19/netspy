# 🕵️‍♂️ NETSPY: Comprehensive Technical Synopsis and Architecture Document

> **Project Name:** netspy  
> **Author/Lead Architect:** Shubhechchha Basu
> **Contributor:** Bratik Mukherjee ( Bimbok )
> **Version:** 1.1.0 (Enhanced)  
> **Python Version:** 3.12.8  
> **Primary Technologies:** `Python`, `Tkinter`, `Matplotlib`, `Scikit-learn`, `Psutil`, `Pandas`, `Numpy`  
> **Status:** Operational / Feature-Complete

---

## 📋 Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Project Philosophy & Objectives](#2-project-philosophy--objectives)
3. [System Architecture Overview](#3-system-architecture-overview)
4. [Deep Dive: The AI Core (`src/core/monitor.py`)](#4-deep-dive-the-ai-core)
    - 4.1 [The Isolation Forest Algorithm](#41-the-isolation-forest-algorithm)
    - 4.2 [Multi-Dimensional Feature Engineering](#42-multi-dimensional-feature-engineering)
    - 4.3 [Platform-Aware Model Caching](#43-platform-aware-model-caching)
    - 4.4 [Hardware Data Polling (Psutil)](#44-hardware-data-polling)
5. [Deep Dive: The Custom UI Engine (`src/ui/`)](#5-deep-dive-the-custom-ui-engine)
    - 5.1 [Theming and Cyberpunk Aesthetics](#51-theming-and-cyberpunk-aesthetics)
    - 5.2 [Geometric UI Hacks: The RoundedFrame](#52-geometric-ui-hacks-the-roundedframe)
    - 5.3 [Sidebar Navigation & State Management](#53-sidebar-navigation--state-management)
6. [Deep Dive: The View Controllers](#6-deep-dive-the-view-controllers)
    - 6.1 [The Base Monitor View Engine](#61-the-base-monitor-view-engine)
    - 6.2 [System Overview (Home View)](#62-system-overview)
    - 6.3 [Network Analyzer Intelligence](#63-network-analyzer-intelligence)
7. [Performance & Optimization Strategies](#7-performance--optimization-strategies)
8. [Data Flow Lifecycle](#8-data-flow-lifecycle)
9. [Future Roadmap & Expansion Potential](#9-future-roadmap--expansion-potential)
10. [Conclusion](#10-conclusion)

---

## 1. Executive Summary
**netspy** is an advanced, AI-driven system telemetry dashboard engineered to monitor computing resources (Network, CPU, RAM) in real-time. Moving beyond legacy system monitors that rely on static, hard-coded alert thresholds (e.g., "Alert if CPU > 90%"), **netspy** integrates an unsupervised Machine Learning model—specifically an **Isolation Forest**—to dynamically learn the user's specific hardware baseline and intelligently flag anomalous spikes.

Visually, the application abandons the standard, dated OS-native graphical interfaces in favor of a bespoke, high-performance **Tkinter/Matplotlib hybrid UI**. It employs a **"Cyberpunk Dark"** aesthetic with custom-rendered rounded geometries, neon accents, and smooth **25-30 FPS** data visualizations, making it functionally robust and visually striking for modern desktop environments (e.g., Linux window managers like Hyprland, as evidenced by the project's screenshots).

---

## 2. Project Philosophy & Objectives
The creation of **netspy** solves three distinct problems in modern system administration and power-user monitoring:

*   **The Context Problem:** A sudden 5MB/s network spike might be normal during a Steam game update, but highly suspicious if the system is supposed to be idle. Static thresholds cannot tell the difference. **netspy** aims to provide context-aware alerts through continuous ML retraining.
*   **The UI/UX Deficit:** Native Python GUI libraries (Tkinter) are notoriously ugly by default. Web-based wrappers (Electron) are visually pleasing but consume massive amounts of RAM—defeating the purpose of a system monitor. **netspy** aims to prove that native Tkinter can be beautiful and lightweight if mathematically manipulated (via Canvas polygons).
*   **The Telemetry Overload:** Users are often presented with too many raw numbers. **netspy** aims to distill raw bytes and packets into actionable intelligence (e.g., aggregating active remote endpoints and TCP/UDP distributions).

---

## 3. System Architecture Overview
The codebase is strictly modular, adhering to a paradigm similar to **Model-View-Controller (MVC)**. This separation ensures that the heavy mathematical processing does not block the UI rendering thread.

### Directory Structure Analysis:
```text
/netspy
├── main.py              # The lightweight entry point. Initializes the Tkinter root.
├── requirements.txt     # Dependency manifest.
├── src/
│   ├── core/            # Contains purely mathematical/OS-level logic. Unaware of UI.
│   │   └── monitor.py   # AIResourceMonitor implementation.
│   └── ui/              # All graphical elements.
│       ├── styles.py    # Design tokens & hex codes.
│       ├── dashboard.py # Main layout controller.
│       ├── components/  # Reusable widgets (RoundedFrame, Sidebar).
│       └── views/       # Domain-specific views (Home, CPU, Network, etc.).
```

### The Tech Stack Rationale:
| Technology | Role | Benefit |
| :--- | :--- | :--- |
| **Python 3.12.8** | Core Engine | Stability with pre-compiled C-extensions (Wheels). |
| **Scikit-Learn** | AI Engine | Provides the `IsolationForest` module; lightweight inference. |
| **Psutil** | Telemetry | Industry standard for cross-platform hardware polling. |
| **Tkinter** | UI Framework | Native, low-memory footprint, event-driven. |
| **Matplotlib** | Visualization | Embedded via `FigureCanvasTkAgg` for high-performance plotting. |

---

## 4. Deep Dive: The AI Core (`src/core/monitor.py`)
The `AIResourceMonitor` class is the absolute brain of the application. It is designed to be highly performant, instantiated once per resource type (Network, CPU, RAM), and polled continuously.

### 4.1. The Isolation Forest Algorithm
At the heart of the anomaly detection is `sklearn.ensemble.IsolationForest`.
*   **Configuration:** `n_estimators=100`, `contamination=0.02`, `random_state=42`.
*   **Why Isolation Forest?** Unlike standard algorithms that try to map "normal" data, an Isolation Forest explicitly isolates anomalies. It builds 100 random decision trees. Because anomalies are rare and statistically different, they end up closer to the root of the trees (shorter path lengths).
*   **Contamination Rate (0.02):** The model is mathematically tuned to expect that ~2% of the user's computing life will consist of anomalous spikes.

### 4.2. Multi-Dimensional Feature Engineering
The monitor does not simply feed raw values (e.g., 50% CPU) into the AI. In the `step()` function, it engineers a **3-dimensional feature vector** for every single tick:
1.  **Value (val):** The absolute current metric.
2.  **Velocity (delta):** `val - self.last_val`. Measures the rate of change. A sudden jump from 10% to 50% is treated differently than a slow creep from 40% to 50%.
3.  **Trend Deviance:** `val - moving_avg`. Measures how far the current value strays from the historical baseline of the current session.

By plotting these three dimensions in space, the Isolation Forest can detect complex anomalies, such as a process that is secretly pulsing data in small bursts, which might bypass a standard high-water-mark alert.

### 4.3. Platform-Aware Model Caching
Machine learning models suffer from the **"Cold Start"** problem. When **netspy** boots, it has no data to evaluate. To solve this, the core implements a highly sophisticated OS-aware caching mechanism (`_get_cache_dir`):
*   **Windows:** Saves to `AppData/Local/netspy/Cache`
*   **macOS:** Saves to `~/Library/Caches/netspy`
*   **Linux:** Saves to `~/.cache/netspy` (Respecting XDG Base Directory specs).

Models are serialized using Python's native `pickle` module. When the app is closed, it saves its learned brain; when opened, it reloads it, ensuring the AI retains its knowledge of the user's system across reboots.

### 4.4. Hardware Data Polling (Psutil)
The `get_current_value()` method normalizes all hardware into a single float.
*   **CPU / RAM:** Uses simple percentage getters.
*   **Network:** Acts as an odometer. It fetches total bytes since boot, compares it to the previous check, and divides by `time_elapsed`. This ensures accurate Bytes-Per-Second metrics regardless of thread lagging.

---

## 5. Deep Dive: The Custom UI Engine (`src/ui/`)
Building a modern UI in Tkinter requires overriding almost all of its default rendering behaviors. **netspy** achieves this through strict centralization of styles and custom drawing algorithms.

### 5.1. Theming and Cyberpunk Aesthetics
Defined in `styles.py`, the application uses a centralized design token system.
*   **Palette:** Deep space backgrounds (`#0b0e14`, `#161b22`) paired with high-contrast neon accents (Cyan `#00f2ff`, Matrix Green `#00ff41`, Alert Red `#ff3e3e`).
*   **Typography:** Heavily utilizes bolded sans-serif fonts for metrics, and `Courier New` for raw data (like IP addresses) to maintain a hacker/terminal motif.

### 5.2. Geometric UI Hacks: The RoundedFrame
Tkinter cannot draw rounded rectangles. The `RoundedFrame` component (`rounded_frame.py`) is a masterclass in GUI hacking.
1.  It inherits from `tk.Canvas` rather than `tk.Frame`.
2.  In `_draw_rounded_rect()`, it mathematically calculates a **20-point polygon** that simulates a rectangle with arcs at the corners.
3.  It smooths this polygon using `smooth=True` (Bezier curve interpolation).
4.  It spawns a standard `tk.Frame` inside this canvas, meticulously applying padding to ensure child widgets don't bleed over the rounded borders.
5.  It binds to `<Configure>` to dynamically redraw the polygon whenever the user resizes the window, applying a **1px inset** to prevent border clipping.

### 5.3. Sidebar Navigation & State Management
The Sidebar component (`sidebar.py`) implements a Single Page Application (SPA) feel.
*   It maintains a dictionary of buttons and their corresponding vertical indicator lines.
*   Hover effects are simulated manually using `<Enter>` and `<Leave>` event bindings.
*   When a navigation event occurs, it passes the target view name back up to the `Dashboard` controller via a callback (`self.on_navigate`), which handles the destruction of the old frame and rendering of the new one.

---

## 6. Deep Dive: The View Controllers
The UI is divided into modular "Views", each responsible for a specific domain of telemetry.

### 6.1. The Base Monitor View Engine (`monitor_view.py`)
To prevent code duplication across Network, CPU, and RAM screens, a `BaseMonitorView` was architected. This is the most complex UI component.
*   **The Loop:** It abandons standard `while` loops, utilizing `self.after(40, self.update_gui)` to create a native Tkinter game-loop running at approximately **25 FPS** (1000ms / 40ms = 25).
*   **Data Structures:** Uses `collections.deque(maxlen=120)` to maintain exactly 120 frames of historical data. Adding a new item automatically pops the oldest, operating in $O(1)$ time complexity without memory leaks.
*   **Matplotlib Integration:**
    *   Creates a `FigureCanvasTkAgg` embedded in the `RoundedFrame`.
    *   Instead of clearing and redrawing the graph (`ax.clear()`), which is computationally disastrous, it updates the Y-data of the existing line (`self.line.set_ydata()`).
*   **Dynamic Filling:** It removes and redraws the `fill_between` polygon every frame. Crucially, if the AI flags an anomaly, the fill and line color instantly snap from the accent color (e.g., Cyan) to `ANOMALY_RED`, providing immediate visual feedback.
*   **Statistics Compilation:** Tracks peak usage, calculates rolling averages, and aggregates total utilization over the session.

### 6.2. System Overview (Home View)
The `HomeView` serves as the command center.
*   **Mini-Graphs:** Renders stripped-down versions of the Matplotlib canvases (hiding axes and labels) for CPU and RAM simultaneously.
*   **Active Node Detection:** Implements a complex algorithm (`get_active_interface`) that iterates through all OS network interfaces, ignores loopbacks (`lo`), verifies the interface status (`isup`), and calculates the one with the highest traffic volume to dynamically determine if the user is on WLAN, Ethernet, or a VPN.

### 6.3. Network Analyzer Intelligence (`analyzer_view.py`)
This view provides deep packet/connection analysis.
*   **Protocol Distribution:** Renders a Matplotlib Bar Chart comparing active TCP vs. UDP connections.
*   **IP Resolution:** Interrogates the OS for all active `inet` connections. It parses the remote addresses, counts the frequency of connections per IP, and sorts them to display the top 8 remote endpoints the system is communicating with.

---

## 7. Performance & Optimization Strategies
A monitoring tool that consumes massive resources defeats its own purpose. **netspy** employs several high-level optimizations:

*   **Deque over Lists:** Native Python lists require memory reallocation when they grow or shrink from the front. `deque` from the `collections` module provides $O(1)$ append and pop operations, essential for high-frequency data streaming.
*   **Matplotlib `draw_idle()`:** Instead of forcing synchronous redraws with `.draw()`, the UI uses `.draw_idle()`, which tells the Tkinter mainloop to redraw the canvas only when it has free cycles, preventing GUI locking.
*   **Algorithmic Throttling:** Network connection polling (`psutil.net_connections`) is an expensive OS-level system call. The `get_connection_stats()` method includes a manual cache with a **2.0-second throttle**. If the GUI requests data faster than 2 seconds, it returns the cached data instead of blocking the CPU to ask the OS again.
*   **Decoupled AI Training:** The `IsolationForest.fit()` function is heavy. It is only called if `(now - self.last_retrain_time) > self.retrain_interval_sec` (60 seconds). Inference (`.predict()`), which is very fast, happens every frame using raw NumPy values to bypass Pandas overhead.
*   **Data Smoothing:** Raw hardware data is jittery. `BaseMonitorView` utilizes a secondary deque of size 10 to act as a **Simple Moving Average (SMA)** filter, smoothing out the graph lines for visual fluidity without hiding the actual anomalies.

---

## 8. Data Flow Lifecycle
To understand the system entirely, here is the chronological lifecycle of a single frame of data (occurring 25 times per second):

1.  **Trigger:** Tkinter's `after(40)` callback fires `update_gui()` in the active View.
2.  **Fetch:** The View calls `self.monitor.step()`.
3.  **Hardware Interrogation:** `AIResourceMonitor` calls `psutil` to get raw OS data.
4.  **Math/Vectorization:** Raw data is converted to `[val, delta, trend]`.
5.  **AI Inference:** The vector is passed to `IsolationForest.predict()`.
6.  **Return:** `step()` returns the smoothed value and a boolean `is_anomaly` flag.
7.  **State Update:** The View appends the value to its UI buffer (`deque`).
8.  **Color Resolution:** The View checks `is_anomaly`. If `True`, sets render hex to `#ff3e3e`.
9.  **Render:** Matplotlib geometry is updated, and `canvas.draw_idle()` is queued.
10. **Loop:** The cycle repeats.

---

## 9. Future Roadmap & Expansion Potential
Given the robust, modular architecture of **netspy**, the project is highly extensible. Recommended future enhancements include:

*   **Process-Level Blame:** Currently, **netspy** tracks global bandwidth. Using `psutil`, the core could be expanded to identify which specific **PID (Process ID)** is causing the anomaly (e.g., "Anomaly Detected: chrome.exe is downloading at 50MB/s").
*   **Deeper AI Models:** Replacing IsolationForest with an **LSTM (Long Short-Term Memory)** neural network via PyTorch could allow the system to predict future spikes based on sequential time-series patterns.
*   **Headless Daemon Mode:** Splitting the architecture so `monitor.py` runs as a background `systemd` service or Windows Service, allowing data collection even when the UI is closed. The UI would then connect to the daemon via local sockets.
*   **Packet Sniffing:** Integrating `scapy` into the `analyzer_view.py` to allow for deep packet inspection (DPI), showing HTTP hostnames instead of just raw IP addresses.

---

## 10. Conclusion
**netspy** is a highly sophisticated piece of software that elegantly bridges the gap between low-level system administration, machine learning, and custom graphical interface design. By rejecting heavy web-frameworks and static thresholds, it achieves a lightweight, mathematically intelligent, and visually striking footprint.

The codebase demonstrates advanced knowledge of Python's **GIL management** (via decoupling heavy training from the render loop), high-performance data structures, mathematical feature engineering, and GUI geometry manipulation. It stands as a premium example of modern desktop utility development.
