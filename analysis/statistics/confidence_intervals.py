"""
Bootstrap & Student-t Confidence Intervals (95% and 99%).
"""
import numpy as np
from scipy import stats
from typing import List, Dict, Any, Tuple

def compute_ci(data: List[float], confidence: float = 0.95) -> Tuple[float, float]:
    if len(data) < 2:
        val = data[0] if data else 0.0
        return val, val
    arr = np.array(data)
    mean = np.mean(arr)
    sem = stats.sem(arr)
    interval = sem * stats.t.ppf((1 + confidence) / 2., len(arr) - 1)
    return round(float(mean - interval), 4), round(float(mean + interval), 4)
