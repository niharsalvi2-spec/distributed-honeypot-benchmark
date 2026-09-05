"""
Precision Evaluation Engine for Attack Correlation.
Measures the proportion of identified correlations that are verifiably correct.
Formula: Precision = TP / (TP + FP)
"""
from typing import Set, Tuple, Optional

class PrecisionEvaluator:
    @staticmethod
    def compute_precision(tp: int, fp: int) -> float:
        """
        Computes precision metric bounded between [0.0, 1.0].
        Returns 1.0 if no links were predicted and none were expected (perfect selectivity).
        Returns 0.0 if spurious links exist with no true positives.
        """
        total = tp + fp
        if total == 0:
            return 1.0 if tp == 0 else 0.0
        return round(float(tp) / float(total), 4)

    @classmethod
    def evaluate_sets(cls, predicted_links: Set[Tuple[str, str]], ground_truth_links: Set[Tuple[str, str]]) -> float:
        tp = len(predicted_links.intersection(ground_truth_links))
        fp = len(predicted_links.difference(ground_truth_links))
        return cls.compute_precision(tp, fp)

def compute_precision(tp: int, fp: int) -> float:
    return PrecisionEvaluator.compute_precision(tp, fp)
