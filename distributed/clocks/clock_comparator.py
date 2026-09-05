"""
Clock Comparator.
Quantifies sequence ordering error and Kendall's Tau correlation between
physical arrival timestamps, Lamport topological order, and ground-truth sequences.
"""
from typing import List, Dict, Any, Tuple
from scipy.stats import kendalltau

class ClockComparator:
    @staticmethod
    def compute_inversions(reference_seq: List[str], observed_seq: List[str]) -> Tuple[int, float]:
        """Calculates pairwise inversions and inversion rate."""
        if not reference_seq or not observed_seq or len(reference_seq) != len(observed_seq):
            return 0, 0.0
            
        pos_map = {item: idx for idx, item in enumerate(reference_seq)}
        projected = [pos_map[item] for item in observed_seq if item in pos_map]
        
        inversions = 0
        n = len(projected)
        for i in range(n):
            for j in range(i + 1, n):
                if projected[i] > projected[j]:
                    inversions += 1
                    
        total_pairs = (n * (n - 1)) / 2.0 if n > 1 else 1.0
        inversion_rate = round(inversions / total_pairs, 4)
        return inversions, inversion_rate

    @staticmethod
    def compute_kendall_tau(reference_seq: List[str], observed_seq: List[str]) -> float:
        """Computes Kendall's rank correlation coefficient."""
        pos_map = {item: idx for idx, item in enumerate(reference_seq)}
        y_ref = list(range(len(reference_seq)))
        y_obs = [pos_map[item] for item in observed_seq if item in pos_map]
        if len(y_ref) < 2 or len(y_obs) < 2:
            return 1.0
        tau, _ = kendalltau(y_ref, y_obs)
        return float(tau if tau is not None else 0.0)
