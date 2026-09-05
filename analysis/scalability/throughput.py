"""
Throughput and Ingestion Latency Analyzer.
Calculates Events Per Second (EPS), sliding-window peak rates, and pipeline backpressure.
"""
from typing import List, Dict, Any
import numpy as np

class ThroughputAnalyzer:
    """
    Measures event pipeline processing capacity under controlled workload injection.
    """
    @staticmethod
    def compute_eps(total_events: int, elapsed_seconds: float) -> float:
        """Computes steady-state average events per second."""
        return round(float(total_events) / float(elapsed_seconds), 2) if elapsed_seconds > 0 else 0.0

    @staticmethod
    def compute_windowed_throughput(event_timestamps_sec: List[float], window_size_sec: float = 1.0) -> Dict[str, Any]:
        """
        Computes sustained, peak, and minimum throughput using a sliding window.
        """
        if not event_timestamps_sec:
            return {"mean_eps": 0.0, "peak_eps": 0.0, "min_eps": 0.0, "total_events": 0}

        sorted_ts = sorted(event_timestamps_sec)
        t_start = sorted_ts[0]
        t_end = sorted_ts[-1]
        duration = max(t_end - t_start, window_size_sec)

        num_bins = int(np.ceil(duration / window_size_sec))
        counts = [0] * max(num_bins, 1)

        for t in sorted_ts:
            idx = min(int((t - t_start) / window_size_sec), len(counts) - 1)
            counts[idx] += 1

        eps_series = [c / window_size_sec for c in counts]
        return {
            "mean_eps": round(float(np.mean(eps_series)), 2),
            "median_eps": round(float(np.median(eps_series)), 2),
            "peak_eps": round(float(np.max(eps_series)), 2),
            "min_eps": round(float(np.min(eps_series)), 2),
            "total_events": len(event_timestamps_sec),
            "duration_sec": round(duration, 2)
        }

def compute_eps(total_events: int, elapsed_seconds: float) -> float:
    return ThroughputAnalyzer.compute_eps(total_events, elapsed_seconds)
