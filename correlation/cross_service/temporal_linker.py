"""
Exponential Decay Temporal Proximity Calculator.
Score = exp(-lambda * delta_t)
"""
import math
import dateutil.parser
from typing import Dict, Any

class TemporalLinker:
    def __init__(self, decay_rate: float = 0.05):
        self.decay_rate = decay_rate

    def compute_proximity(self, e1: Dict[str, Any], e2: Dict[str, Any]) -> float:
        t1 = dateutil.parser.parse(e1["timestamps"]["physical_raw"]).timestamp()
        t2 = dateutil.parser.parse(e2["timestamps"]["physical_raw"]).timestamp()
        delta_t = abs(t1 - t2)
        return math.exp(-self.decay_rate * delta_t)
