"""
System Resource Usage Profile Analyzer.
"""
import numpy as np
from typing import List, Dict, Any

def summarize_resources(cpu_samples: List[float], mem_samples: List[float]) -> Dict[str, Any]:
    return {
        "cpu_mean": round(float(np.mean(cpu_samples)), 2) if cpu_samples else 0.0,
        "cpu_max": round(float(np.max(cpu_samples)), 2) if cpu_samples else 0.0,
        "mem_mean_percent": round(float(np.mean(mem_samples)), 2) if mem_samples else 0.0
    }
