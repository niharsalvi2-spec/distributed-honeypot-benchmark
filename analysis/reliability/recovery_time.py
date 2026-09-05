"""
Recovery & Buffer Draining Latency Calculator.
Calculates Mean Time to Recovery (MTTR), partition healing latency, and queue drain duration.
"""
from typing import List, Dict, Any
import numpy as np

class RecoveryTimeAnalyzer:
    """
    Measures node failover recovery times, network reconnect times, and backlog draining latencies.
    """
    @staticmethod
    def compute_recovery_latency(reconnect_time: float, buffer_empty_time: float) -> float:
        """Computes time taken from reconnection until local queue backlog is cleared."""
        return max(0.0, round(float(buffer_empty_time - reconnect_time), 3))

    @staticmethod
    def compute_mttr(outage_durations: List[float]) -> Dict[str, float]:
        """Calculates Mean Time To Recovery (MTTR) across multiple failure injection trials."""
        if not outage_durations:
            return {"mttr_seconds": 0.0, "min_seconds": 0.0, "max_seconds": 0.0, "std_seconds": 0.0}
        
        arr = np.array(outage_durations, dtype=float)
        return {
            "mttr_seconds": round(float(np.mean(arr)), 3),
            "median_seconds": round(float(np.median(arr)), 3),
            "min_seconds": round(float(np.min(arr)), 3),
            "max_seconds": round(float(np.max(arr)), 3),
            "std_seconds": round(float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0, 3)
        }

def compute_recovery_latency(reconnect_time: float, buffer_empty_time: float) -> float:
    return RecoveryTimeAnalyzer.compute_recovery_latency(reconnect_time, buffer_empty_time)
