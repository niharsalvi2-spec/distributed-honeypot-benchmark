"""
Pairwise Sequence Inversion Rate Calculator.
"""
from typing import List, Tuple, Dict, Any
from distributed.clocks.clock_comparator import ClockComparator

def get_inversion_summary(ground_truth: List[str], observed: List[str]) -> Dict[str, Any]:
    inversions, rate = ClockComparator.compute_inversions(ground_truth, observed)
    tau = ClockComparator.compute_kendall_tau(ground_truth, observed)
    return {
        "total_inversions": inversions,
        "inversion_rate": round(rate, 4),
        "kendall_tau": round(tau, 4)
    }
