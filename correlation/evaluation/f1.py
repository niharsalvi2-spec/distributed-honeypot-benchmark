"""
F1-Score and Generalized F-Beta Metric Evaluator.
Computes harmonic and weighted trade-offs between Precision and Recall.
Formula: F1 = 2 * (Precision * Recall) / (Precision + Recall)
"""
from typing import Set, Tuple, Dict, Any, Optional

class F1Evaluator:
    @staticmethod
    def compute_f1(precision: float, recall: float) -> float:
        """Computes harmonic mean F1 score."""
        denom = precision + recall
        if denom == 0:
            return 0.0
        return round(float(2.0 * precision * recall / denom), 4)

    @staticmethod
    def compute_fbeta(precision: float, recall: float, beta: float = 1.0) -> float:
        """Computes generalized F-beta score where beta balances precision vs recall."""
        beta_sq = beta ** 2
        denom = (beta_sq * precision) + recall
        if denom == 0:
            return 0.0
        return round(float((1.0 + beta_sq) * (precision * recall) / denom), 4)

    @classmethod
    def evaluate_sets(cls, predicted_links: Set[Tuple[str, str]], ground_truth_links: Set[Tuple[str, str]]) -> Dict[str, float]:
        tp = len(predicted_links.intersection(ground_truth_links))
        fp = len(predicted_links.difference(ground_truth_links))
        fn = len(ground_truth_links.difference(predicted_links))

        prec = float(tp) / float(tp + fp) if (tp + fp) > 0 else (1.0 if tp == 0 and len(ground_truth_links) == 0 else 0.0)
        rec = float(tp) / float(tp + fn) if (tp + fn) > 0 else 1.0
        f1 = cls.compute_f1(prec, rec)
        f05 = cls.compute_fbeta(prec, rec, beta=0.5)
        f2 = cls.compute_fbeta(prec, rec, beta=2.0)

        return {
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": f1,
            "f0_5": f05,
            "f2": f2,
            "tp": tp,
            "fp": fp,
            "fn": fn
        }

def compute_f1(precision: float, recall: float) -> float:
    return F1Evaluator.compute_f1(precision, recall)
