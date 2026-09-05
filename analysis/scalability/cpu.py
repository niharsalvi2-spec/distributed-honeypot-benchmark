"""
CPU Utilization Profiler & Statistical Analyzer.
Computes comprehensive CPU consumption metrics across benchmark trials.
"""
from typing import List, Dict, Any
import numpy as np

class CPUProfiler:
    """
    Analyzes CPU utilization time-series samples collected from honeypot collector nodes.
    """
    @staticmethod
    def get_cpu_stats(samples: List[float]) -> Dict[str, float]:
        """
        Computes descriptive statistical properties of CPU percentage usage.
        """
        if not samples:
            return {
                "mean": 0.0,
                "median": 0.0,
                "min": 0.0,
                "max": 0.0,
                "std": 0.0,
                "p95": 0.0,
                "p99": 0.0
            }
        
        arr = np.array(samples, dtype=float)
        return {
            "mean": round(float(np.mean(arr)), 2),
            "median": round(float(np.median(arr)), 2),
            "min": round(float(np.min(arr)), 2),
            "max": round(float(np.max(arr)), 2),
            "std": round(float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0, 2),
            "p95": round(float(np.percentile(arr, 95)), 2),
            "p99": round(float(np.percentile(arr, 99)), 2)
        }

def get_cpu_stats(samples: List[float]) -> Dict[str, float]:
    return CPUProfiler.get_cpu_stats(samples)
