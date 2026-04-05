import psutil
import time
import pandas as pd
from sklearn.ensemble import IsolationForest
from collections import deque


class AIResourceMonitor:
    """General AI Monitor for any system resource (CPU, RAM, Network)."""
    def __init__(self, resource_type="network", window_size=30, retrain_interval=15):
        self.resource_type = resource_type
        self.window_size = window_size
        self.retrain_interval = retrain_interval

        self.history = deque(maxlen=window_size)
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.is_model_trained = False

        # For network speed calculation
        self.last_io = psutil.net_io_counters()
        self.last_time = time.time()
        
        self.seconds_running = 0

    def get_current_value(self):
        """Fetches the current value based on resource type."""
        if self.resource_type == "cpu":
            return psutil.cpu_percent()
        
        elif self.resource_type == "ram":
            return psutil.virtual_memory().percent
        
        elif self.resource_type == "network":
            current_io = psutil.net_io_counters()
            current_time = time.time()
            time_elapsed = current_time - self.last_time
            
            if time_elapsed <= 0: return 0
            
            sent = (current_io.bytes_sent - self.last_io.bytes_sent) / time_elapsed
            recv = (current_io.bytes_recv - self.last_io.bytes_recv) / time_elapsed
            
            self.last_io = current_io
            self.last_time = current_time
            return sent + recv
        
        return 0

    def step(self):
        """Performs a single monitoring step and returns (value, is_anomaly)."""
        value = self.get_current_value()
        self.history.append([value])
        self.seconds_running += 1

        is_anomaly = False

        # Retrain logic
        if len(self.history) == self.window_size:
            if not self.is_model_trained or self.seconds_running % self.retrain_interval == 0:
                df = pd.DataFrame(list(self.history), columns=["val"])
                self.model.fit(df)
                self.is_model_trained = True

        # Prediction logic
        if self.is_model_trained:
            df_predict = pd.DataFrame([[value]], columns=["val"])
            prediction = self.model.predict(df_predict)
            if prediction[0] == -1:
                is_anomaly = True

        return value, is_anomaly
