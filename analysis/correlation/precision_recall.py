"""
Precision-Recall Curve Generator.
Evaluates precision and recall across sweeping correlation thresholds.
"""
import numpy as np
from typing import List, Tuple, Dict, Any
from correlation.evaluation.correlation_accuracy import CorrelationEvaluator

def compute_pr_curve(candidate_pairs: List[Tuple[str, str, float]],
                     ground_truth_pairs: List[Tuple[str, str]]) -> Dict[str, Any]:
    thresholds = np.linspace(0.1, 0.9, 9)
    pr_curve = []
    truth_set = set(ground_truth_pairs)
    for t in thresholds:
        predicted = { (p[0], p[1]) for p in candidate_pairs if p[2] >= t }
        metrics = CorrelationEvaluator.evaluate(predicted, truth_set)
        pr_curve.append({
            "threshold": round(float(t), 2),
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1_score": metrics["f1_score"]
        })
    return {"pr_curve": pr_curve}
