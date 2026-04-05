import psutil
import time
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from collections import deque


class AIResourceMonitor:
    """Advanced AI Monitor using an ensemble of trees (Isolation Forest) for any system resource."""
    def __init__(self, resource_type="network", window_size=60, retrain_interval=30):
        self.resource_type = resource_type
        self.window_size = window_size
        self.retrain_interval = retrain_interval

        # Feature buffer: Stores [value, delta, rolling_mean]
        self.history = deque(maxlen=window_size)
        
        # Isolation Forest is the "Random Forest" for anomaly detection.
        # It's an ensemble of trees that isolates outliers.
        self.model = IsolationForest(
            n_estimators=100, 
            contamination=0.02, # 2% expected anomalies
            random_state=42
        )
        self.is_model_trained = False

        self.last_val = 0
        self.last_io = psutil.net_io_counters()
        self.last_time = time.time()
        self.seconds_running = 0

    def get_current_value(self):
        """Fetches the current raw value."""
        if self.resource_type == "cpu":
            return psutil.cpu_percent()
        elif self.resource_type == "ram":
            return psutil.virtual_memory().percent
        elif self.resource_type == "network":
            current_io = psutil.net_io_counters()
            current_time = time.time()
            time_elapsed = current_time - self.last_time
            if time_elapsed <= 0: return self.last_val
            
            sent = (current_io.bytes_sent - self.last_io.bytes_sent) / time_elapsed
            recv = (current_io.bytes_recv - self.last_io.bytes_recv) / time_elapsed
            
            self.last_io = current_io
            self.last_time = current_time
            return sent + recv
        return 0

    def step(self):
        """AI-powered step: Extracts features, trains, and predicts anomalies."""
        val = self.get_current_value()
        
        # --- Feature Engineering ---
        # Instead of just the raw value, we give the AI context:
        delta = val - self.last_val
        
        # Moving average of history for trend detection
        history_vals = [h[0] for h in self.history]
        moving_avg = np.mean(history_vals) if history_vals else val
        
        # Store features: [Value, Velocity, Trend-Deviance]
        features = [val, delta, val - moving_avg]
        self.history.append(features)
        
        self.last_val = val
        self.seconds_running += 1

        is_anomaly = False

        # --- Training (Every 'retrain_interval' steps) ---
        if len(self.history) == self.window_size:
            if not self.is_model_trained or self.seconds_running % self.retrain_interval == 0:
                data = pd.DataFrame(list(self.history), columns=["val", "delta", "trend"])
                self.model.fit(data)
                self.is_model_trained = True

        # --- Prediction ---
        if self.is_model_trained:
            # Wrap current features in a DataFrame
            df_predict = pd.DataFrame([features], columns=["val", "delta", "trend"])
            prediction = self.model.predict(df_predict)
            
            # -1 indicates an anomaly (the forest isolated this point easily)
            if prediction[0] == -1:
                is_anomaly = True

        return val, is_anomaly

    def get_connection_stats(self):
        """Returns top active IP addresses and protocol counts."""
        try:
            connections = psutil.net_connections(kind='inet')
            ip_counts = {}
            proto_counts = {"TCP": 0, "UDP": 0}
            
            for conn in connections:
                # Count Protocols
                if conn.type == 1: proto_counts["TCP"] += 1
                elif conn.type == 2: proto_counts["UDP"] += 1
                
                # Count Remote IPs (only if connected)
                if conn.raddr:
                    ip = conn.raddr.ip
                    ip_counts[ip] = ip_counts.get(ip, 0) + 1
            
            # Sort IPs by connection count
            sorted_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:8]
            return sorted_ips, proto_counts
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            return [], {"TCP": 0, "UDP": 0}
