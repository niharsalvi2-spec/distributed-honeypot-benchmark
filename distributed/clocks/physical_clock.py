"""
High-Resolution Physical Clock with Synthetic Drift and Skew Injection.
"""
import time

class PhysicalClock:
    def __init__(self, skew_offset_ms: float = 0.0, drift_rate_ppm: float = 0.0):
        self.skew_offset_sec = skew_offset_ms / 1000.0
        self.drift_rate = drift_rate_ppm / 1e6
        self.start_wall_time = time.time()
        self.start_perf_time = time.perf_counter()

    def now(self) -> float:
        elapsed = time.perf_counter() - self.start_perf_time
        drift_error = elapsed * self.drift_rate
        return self.start_wall_time + elapsed + self.skew_offset_sec + drift_error
