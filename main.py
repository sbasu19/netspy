import psutil
import time
import pandas as pd
from sklearn.ensemble import IsolationForest
from collections import deque


class SmartBandwidthMonitor:
    def __init__(self, window_size=60):
        self.window_size = window_sizegit 
        time_elapsed = current_time - self.last_time

        bytes_sent = (current_io.bytes_sent - self.last_io.bytes_sent) / time_elapsed
        bytes_recv = (current_io.bytes_recv - self.last_io.bytes_recv) / time_elapsed

        self.last_io = current_io
        self.last_time = current_time

        return bytes_sent, bytes_recv

    def monitor(self):
        print("Starting Smart Bandwidth Monitor... (Gathering baseline data)")

        try:
            while True:
                sent, recv = self.get_current_speed()
                total_speed = sent + recv

                # Add current speed to history
                self.history.append([total_speed])

                # We need enough data to train the model initially
                if len(self.history) == self.window_size:
                    df = pd.DataFrame(self.history, columns=["total_speed"])

                    # Periodically retrain the model on the recent window
                    self.model.fit(df)
                    self.is_model_trained = True

                # Check for anomalies if the model is ready
                if self.is_model_trained:
                    # Predict: 1 is normal, -1 is an anomaly
                    prediction = self.model.predict([[total_speed]])

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

                time.sleep(1)  # Poll every 1 second

        except KeyboardInterrupt:
            print("\nMonitoring stopped.")


if __name__ == "__main__":
    monitor = SmartBandwidthMonitor(window_size=30)  # 30 seconds baseline for testing
    monitor.monitor()