"""
Memory Footprint & Leakage Profiler.
Computes memory consumption, peak heap usage, and consumption trends.
"""
from typing import List, Dict, Any
import numpy as np

class MemoryProfiler:
    """
    Analyzes physical resident memory (RSS) and heap allocations across nodes.
    """
    @staticmethod
    def get_mem_stats(samples_mb: List[float]) -> Dict[str, float]:
        if not samples_mb:
            return {
                "mean_mb": 0.0,
                "median_mb": 0.0,
                "min_mb": 0.0,
                "peak_mb": 0.0,
                "std_mb": 0.0,
                "growth_mb": 0.0
            }

        arr = np.array(samples_mb, dtype=float)
        growth = float(arr[-1] - arr[0]) if len(arr) > 1 else 0.0
        return {
            "mean_mb": round(float(np.mean(arr)), 2),
            "median_mb": round(float(np.median(arr)), 2),
            "min_mb": round(float(np.min(arr)), 2),
            "peak_mb": round(float(np.max(arr)), 2),
            "std_mb": round(float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0, 2),
            "growth_mb": round(growth, 2)
        }

def get_mem_stats(samples: List[float]) -> Dict[str, float]:
    return MemoryProfiler.get_mem_stats(samples)
