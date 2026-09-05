"""
F1 Score Optimization & Sensitivity Analyzer.
Finds optimal decision threshold maximizing F1 score for cross-service correlation.
"""
from typing import List, Tuple, Dict, Any
import numpy as np
from correlation.evaluation.correlation_accuracy import CorrelationEvaluator

def find_optimal_threshold(candidate_pairs: List[Tuple[str, str, float]],
                           ground_truth_pairs: List[Tuple[str, str]]) -> Dict[str, Any]:
    thresholds = np.linspace(0.2, 0.85, 14)
    best_f1 = -1.0
    best_threshold = 0.5
    best_metrics = {}
    truth_set = set(ground_truth_pairs)

    for t in thresholds:
        predicted = { (p[0], p[1]) for p in candidate_pairs if p[2] >= t }
        metrics = CorrelationEvaluator.evaluate(predicted, truth_set)
        if metrics["f1_score"] > best_f1:
            best_f1 = metrics["f1_score"]
            best_threshold = round(float(t), 2)
            best_metrics = metrics

    return {
        "optimal_threshold": best_threshold,
        "max_f1_score": best_f1,
        "metrics_at_optimum": best_metrics
    }
