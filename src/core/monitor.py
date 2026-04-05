import psutil
import time
import pandas as pd
import numpy as np
import pickle
import os
import platform
from pathlib import Path
from sklearn.ensemble import IsolationForest
from collections import deque


class AIResourceMonitor:
    """Optimized AI Monitor with high-performance prediction and intelligent caching."""
    def __init__(self, resource_type="network", window_size=60, retrain_interval_sec=60):
        self.resource_type = resource_type
        self.window_size = window_size
        self.retrain_interval_sec = retrain_interval_sec
        self.history = deque(maxlen=window_size)
        
        # Isolation Forest: Efficient ensemble for anomaly detection
        self.model = IsolationForest(n_estimators=100, contamination=0.02, random_state=42)
        self.is_model_trained = False

        self.cache_dir = self._get_cache_dir()
        self.cache_path = self.cache_dir / f"{resource_type}_model.pkl"
        self._load_cached_model()

        self.last_val = 0
        self.last_io = psutil.net_io_counters()
        self.last_time = time.time()
        self.last_retrain_time = time.time()

    def _get_cache_dir(self):
        system = platform.system()
        home = Path.home()
        if system == "Windows":
            path = Path(os.getenv('LOCALAPPDATA', home / 'AppData/Local')) / 'netspy' / 'Cache'
        elif system == "Darwin":
            path = home / 'Library/Caches/netspy'
        else:
            path = home / '.cache/netspy'
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _load_cached_model(self):
        if self.cache_path.exists():
            try:
                with open(self.cache_path, 'rb') as f:
                    self.model = pickle.load(f)
                    self.is_model_trained = True
            except: pass

    def save_cached_model(self):
        if self.is_model_trained:
            try:
                with open(self.cache_path, 'wb') as f:
                    pickle.dump(self.model, f)
            except: pass

    def get_current_value(self):
        if self.resource_type == "cpu":
            return psutil.cpu_percent()
        elif self.resource_type == "ram":
            return psutil.virtual_memory().percent
        elif self.resource_type == "network":
            current_io = psutil.net_io_counters()
            current_time = time.time()
            time_elapsed = current_time - self.last_time
            if time_elapsed <= 0: return self.last_val
            val = (current_io.bytes_sent - self.last_io.bytes_sent + current_io.bytes_recv - self.last_io.bytes_recv) / time_elapsed
            self.last_io = current_io
            self.last_time = current_time
            self.last_val = val
            return val
        return 0

    def step(self):
        """High-performance step optimized for high-frequency loops."""
        val = self.get_current_value()
        
        # Feature Engineering (Delta & Trend)
        delta = val - self.last_val
        self.last_val = val
        
        # Fast moving average calculation
        history_vals = [h[0] for h in self.history]
        moving_avg = np.mean(history_vals) if history_vals else val
        features = [val, delta, val - moving_avg]
        self.history.append(features)
        
        is_anomaly = False
        now = time.time()

        # Retrain only if enough time has passed (e.g. 60 seconds)
        if len(self.history) == self.window_size:
            if not self.is_model_trained or (now - self.last_retrain_time) > self.retrain_interval_sec:
                # Use pandas only for the heavy training phase
                data = pd.DataFrame(list(self.history), columns=["val", "delta", "trend"])
                self.model.fit(data)
                self.is_model_trained = True
                self.last_retrain_time = now

        # High-speed Prediction
        if self.is_model_trained:
            # Wrap in DataFrame to provide feature names and satisfy sklearn's validation
            # without the overhead of full pandas re-initialization if possible, 
            # or just use the DataFrame approach which is safer for name consistency.
            df_predict = pd.DataFrame([features], columns=["val", "delta", "trend"])
            prediction = self.model.predict(df_predict)
            if prediction[0] == -1:
                is_anomaly = True

        return val, is_anomaly

    def get_connection_stats(self):
        """Cached connection stats to avoid system call overhead."""
        if hasattr(self, '_last_conn_check') and (time.time() - self._last_conn_check < 2.0):
            return self._cached_conn_stats
            
        try:
            connections = psutil.net_connections(kind='inet')
            ip_counts = {}
            proto_counts = {"TCP": 0, "UDP": 0}
            for conn in connections:
                if conn.type == 1: proto_counts["TCP"] += 1
                elif conn.type == 2: proto_counts["UDP"] += 1
                if conn.raddr:
                    ip = conn.raddr.ip
                    ip_counts[ip] = ip_counts.get(ip, 0) + 1
            sorted_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:8]
            self._cached_conn_stats = (sorted_ips, proto_counts)
            self._last_conn_check = time.time()
            return self._cached_conn_stats
        except:
            return [], {"TCP": 0, "UDP": 0}
