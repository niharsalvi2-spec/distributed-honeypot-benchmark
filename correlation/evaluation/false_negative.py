"""
False Negative Link & Missed Attack Sequence Identification.
Identifies ground-truth causal links that the correlation engine failed to connect.
"""
from typing import Set, Tuple, List, Dict, Any

class FalseNegativeEvaluator:
    """
    Evaluates False Negative (FN) missed edges in correlated attack graphs.
    """
    @staticmethod
    def count_false_negatives(predicted_links: Set[Tuple[str, str]], ground_truth_links: Set[Tuple[str, str]]) -> int:
        """Counts ground-truth edges missing from predicted links."""
        return len(ground_truth_links.difference(predicted_links))

    @staticmethod
    def extract_false_negative_links(predicted_links: Set[Tuple[str, str]], ground_truth_links: Set[Tuple[str, str]]) -> Set[Tuple[str, str]]:
        """Returns the set of missed causal attack edges."""
        return ground_truth_links.difference(predicted_links)

def compute_fn(predicted: Set[Tuple[str, str]], ground_truth: Set[Tuple[str, str]]) -> int:
    return FalseNegativeEvaluator.count_false_negatives(predicted, ground_truth)
