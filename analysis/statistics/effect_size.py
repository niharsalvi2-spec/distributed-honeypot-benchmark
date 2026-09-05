"""
Effect Size Estimation Engine (Cohen's d and Cliff's Delta).
"""
from typing import List
import numpy as np

def compute_cohens_d(group1: List[float], group2: List[float]) -> float:
    if len(group1) < 2 or len(group2) < 2:
        return 0.0
    n1, n2 = len(group1), len(group2)
    s1, s2 = np.std(group1, ddof=1), np.std(group2, ddof=1)
    pooled_s = np.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))
    diff = np.mean(group1) - np.mean(group2)
    return round(float(diff / pooled_s), 4) if pooled_s > 0 else 0.0
