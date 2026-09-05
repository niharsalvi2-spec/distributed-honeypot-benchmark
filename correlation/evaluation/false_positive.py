"""
False Positive Link & Spurious Correlation Identification.
Identifies predicted attack links that do not correspond to true causal relations.
"""
from typing import Set, Tuple, List, Dict, Any

class FalsePositiveEvaluator:
    """
    Evaluates False Positive (FP) spurious links in correlated attack graphs.
    """
    @staticmethod
    def count_false_positives(predicted_links: Set[Tuple[str, str]], ground_truth_links: Set[Tuple[str, str]]) -> int:
        """Counts predicted edges that are NOT present in ground truth."""
        return len(predicted_links.difference(ground_truth_links))

    @staticmethod
    def extract_false_positive_links(predicted_links: Set[Tuple[str, str]], ground_truth_links: Set[Tuple[str, str]]) -> Set[Tuple[str, str]]:
        """Returns the set of erroneous spurious edges."""
        return predicted_links.difference(ground_truth_links)

def compute_fp(predicted: Set[Tuple[str, str]], ground_truth: Set[Tuple[str, str]]) -> int:
    return FalsePositiveEvaluator.count_false_positives(predicted, ground_truth)
