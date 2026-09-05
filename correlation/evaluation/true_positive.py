"""
True Positive Link & Event Identification.
Matches correlated event pairs against ground-truth attack sequence edges.
"""
from typing import Set, Tuple, List, Dict, Any

class TruePositiveEvaluator:
    """
    Evaluates True Positive (TP) links in correlated attack graphs.
    """
    @staticmethod
    def count_true_positives(predicted_links: Set[Tuple[str, str]], ground_truth_links: Set[Tuple[str, str]]) -> int:
        """Counts intersecting edges between predicted and ground truth links."""
        return len(predicted_links.intersection(ground_truth_links))

    @staticmethod
    def extract_true_positive_links(predicted_links: Set[Tuple[str, str]], ground_truth_links: Set[Tuple[str, str]]) -> Set[Tuple[str, str]]:
        """Returns the set of correctly identified edges."""
        return predicted_links.intersection(ground_truth_links)

def compute_tp(predicted: Set[Tuple[str, str]], ground_truth: Set[Tuple[str, str]]) -> int:
    return TruePositiveEvaluator.count_true_positives(predicted, ground_truth)
