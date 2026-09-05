"""
Consolidated Correlation Evaluator.
Given predicted pairs and ground truth pairs, computes full metrics dictionary.
"""
from typing import Set, Tuple, Dict, Any
from correlation.evaluation.true_positive import compute_tp
from correlation.evaluation.false_positive import compute_fp
from correlation.evaluation.false_negative import compute_fn
from correlation.evaluation.precision import compute_precision
from correlation.evaluation.recall import compute_recall
from correlation.evaluation.f1 import compute_f1

class CorrelationEvaluator:
    @staticmethod
    def evaluate(predicted_pairs: Set[Tuple[str, str]], ground_truth_pairs: Set[Tuple[str, str]]) -> Dict[str, Any]:
        # Normalize undirected tuples
        pred_norm = {tuple(sorted(p)) for p in predicted_pairs}
        truth_norm = {tuple(sorted(p)) for p in ground_truth_pairs}

        tp = compute_tp(pred_norm, truth_norm)
        fp = compute_fp(pred_norm, truth_norm)
        fn = compute_fn(pred_norm, truth_norm)
        p = compute_precision(tp, fp)
        r = compute_recall(tp, fn)
        f1 = compute_f1(p, r)

        return {
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "precision": round(p, 4),
            "recall": round(r, 4),
            "f1": round(f1, 4),
            "f1_score": round(f1, 4)
        }
