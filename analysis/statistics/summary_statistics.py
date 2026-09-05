"""
Parametric and Non-Parametric Summary Statistics.
"""
import numpy as np
from scipy import stats
from typing import List, Dict, Any

def compute_summary_stats(data: List[float]) -> Dict[str, float]:
    if not data:
        return {}
    arr = np.array(data)
    return {
        "count": len(arr),
        "mean": round(float(np.mean(arr)), 4),
        "std": round(float(np.std(arr, ddof=1)), 4) if len(arr) > 1 else 0.0,
        "median": round(float(np.median(arr)), 4),
        "iqr": round(float(stats.iqr(arr)), 4),
        "skewness": round(float(stats.skew(arr)), 4)
    }
