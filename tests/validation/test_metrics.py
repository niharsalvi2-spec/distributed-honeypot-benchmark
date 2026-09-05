"""
Validation Test: Correlation and Evaluation Metrics
Tests mathematical boundary conditions and correctness of TP, FP, FN, Precision, Recall, and F1.
"""
import pytest
from correlation.evaluation.precision import PrecisionEvaluator
from correlation.evaluation.recall import RecallEvaluator
from correlation.evaluation.f1 import F1Evaluator
from correlation.evaluation.correlation_accuracy import CorrelationEvaluator

def test_precision_recall_f1_calculations():
    # Perfectly overlapping sets
    pred = {("A", "B"), ("B", "C")}
    gt = {("A", "B"), ("B", "C")}
    res = CorrelationEvaluator.evaluate(pred, gt)
    assert res["precision"] == 1.0
    assert res["recall"] == 1.0
    assert res["f1"] == 1.0

    # Disjoint sets
    pred_disjoint = {("X", "Y")}
    res_disjoint = CorrelationEvaluator.evaluate(pred_disjoint, gt)
    assert res_disjoint["precision"] == 0.0
    assert res_disjoint["recall"] == 0.0
    assert res_disjoint["f1"] == 0.0

def test_fbeta_weighting():
    # High precision, lower recall
    prec = 0.90
    rec = 0.50
    f1 = F1Evaluator.compute_f1(prec, rec)
    f05 = F1Evaluator.compute_fbeta(prec, rec, beta=0.5)  # favors precision
    f2 = F1Evaluator.compute_fbeta(prec, rec, beta=2.0)   # favors recall

    assert f05 > f1 > f2
