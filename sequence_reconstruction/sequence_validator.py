"""
Sequence Validation & Fidelity Engine.
Measures Sequence Reconstruction Accuracy (SRA) and Levenshtein edit distance
between reconstructed sequences and ground truth.
"""
from typing import List
from scipy.stats import kendalltau

class SequenceValidator:
    @staticmethod
    def compute_sra(expected_seq: List[str], reconstructed_seq: List[str]) -> float:
        """Returns 1.0 if sequence matches ground truth exactly, otherwise proportion of correct order."""
        if expected_seq == reconstructed_seq:
            return 1.0
        pos_map = {item: idx for idx, item in enumerate(expected_seq)}
        proj = [pos_map[item] for item in reconstructed_seq if item in pos_map]
        correct_pairs = 0
        total_pairs = 0
        n = len(proj)
        for i in range(n):
            for j in range(i + 1, n):
                total_pairs += 1
                if proj[i] < proj[j]:
                    correct_pairs += 1
        return correct_pairs / total_pairs if total_pairs > 0 else 0.0
