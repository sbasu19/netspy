import psutil
import time
import pandas as pd
from sklearn.ensemble import IsolationForest
from collections import deque


class SmartBandwidthMonitor:
    def __init__(self, window_size=30, retrain_interval=10):
        self.window_size = window_size
        self.retrain_interval = retrain_interval  # How often to retrain (in seconds)

        self.history = deque(maxlen=window_size)
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.is_model_trained = False

        self.last_io = psutil.net_io_counters()
        self.last_time = time.time()
        self.seconds_running = 0  # Keeps track of time for the retrain interval

    def get_current_speed(self):
        """Calculates bytes sent/received per second."""
        current_io = psutil.net_io_counters()
        current_time = time.time()

        time_elapsed = current_time - self.last_time

        bytes_sent = (current_io.bytes_sent - self.last_io.bytes_sent) / time_elapsed
        bytes_recv = (current_io.bytes_recv - self.last_io.bytes_recv) / time_elapsed

        self.last_io = current_io
        self.last_time = current_time

        return bytes_sent, bytes_recv

    def run(self):
        """Starts the monitoring loop."""
        print("Starting netspy... (Gathering baseline data)")

        try:
            while True:
                sent, recv = self.get_current_speed()
                total_speed = sent + recv

                self.history.append([total_speed])
                self.seconds_running += 1

                # Only retrain if we have a full window AND it's time to retrain
                if len(self.history) == self.window_size:
                    if (
                        not self.is_model_trained
                        or self.seconds_running % self.retrain_interval == 0
                    ):
                        df = pd.DataFrame(self.history, columns=["total_speed"])
                        self.model.fit(df)
                        self.is_model_trained = True

                if self.is_model_trained:
                    # FIXED: Wrap prediction in DataFrame to remove the warning
                    df_predict = pd.DataFrame([[total_speed]], columns=["total_speed"])
                    prediction = self.model.predict(df_predict)

                    if prediction[0] == -1:
                        print(
                            f"⚠️ ANOMALY DETECTED! Unusual Traffic Spike: {total_speed / 1024:.2f} KB/s"
                        )
                    else:
                        print(f"Traffic Normal: {total_speed / 1024:.2f} KB/s")
                else:
                    print(
                        f"Gathering baseline... {len(self.history)}/{self.window_size}"
                    )

                time.sleep(1)

        except KeyboardInterrupt:
            print("\nMonitoring stopped.")

    def step(self):
        """Called by the GUI every second to get the latest data."""
        sent, recv = self.get_current_speed()
        total_speed = sent + recv

        self.history.append([total_speed])
        self.seconds_running += 1

        is_anomaly = False

        if len(self.history) == self.window_size:
            if (
                not self.is_model_trained
                or self.seconds_running % self.retrain_interval == 0
            ):
                df = pd.DataFrame(self.history, columns=["total_speed"])
                self.model.fit(df)
                self.is_model_trained = True

        if self.is_model_trained:
            df_predict = pd.DataFrame([[total_speed]], columns=["total_speed"])
            prediction = self.model.predict(df_predict)

            if prediction[0] == -1:
                is_anomaly = True

        return total_speed, is_anomaly
