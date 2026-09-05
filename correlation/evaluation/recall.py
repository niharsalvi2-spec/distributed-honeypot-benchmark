"""
Recall Evaluation Engine for Attack Correlation.
Measures the proportion of actual ground-truth causal links captured by the engine.
Formula: Recall = TP / (TP + FN)
"""
from typing import Set, Tuple, Optional

class RecallEvaluator:
    @staticmethod
    def compute_recall(tp: int, fn: int) -> float:
        """
        Computes recall metric bounded between [0.0, 1.0].
        Returns 1.0 if all expected links were recovered.
        Returns 0.0 if no ground truth links were identified.
        """
        total = tp + fn
        if total == 0:
            return 1.0
        return round(float(tp) / float(total), 4)

    @classmethod
    def evaluate_sets(cls, predicted_links: Set[Tuple[str, str]], ground_truth_links: Set[Tuple[str, str]]) -> float:
        tp = len(predicted_links.intersection(ground_truth_links))
        fn = len(ground_truth_links.difference(predicted_links))
        return cls.compute_recall(tp, fn)

def compute_recall(tp: int, fn: int) -> float:
    return RecallEvaluator.compute_recall(tp, fn)
