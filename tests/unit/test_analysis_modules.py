"""
Unit Tests for Analysis Modules (PR, F1, Statistics, Hypothesis Testing).
"""
import pytest
from analysis.correlation.f1_analysis import find_optimal_threshold
from analysis.correlation.precision_recall import compute_pr_curve
from analysis.statistics.summary_statistics import compute_summary_stats
from analysis.statistics.confidence_intervals import compute_ci
from analysis.statistics.hypothesis_tests import HypothesisTester

def test_f1_and_pr_curve():
    candidates = [
        ("e1", "e2", 0.90),
        ("e2", "e3", 0.80),
        ("e1", "e4", 0.30)
    ]
    ground_truth = [("e1", "e2"), ("e2", "e3")]
    
    opt = find_optimal_threshold(candidates, ground_truth)
    assert opt["max_f1_score"] == 1.0
    
    pr = compute_pr_curve(candidates, ground_truth)
    assert len(pr["pr_curve"]) > 0

def test_statistical_calculations():
    data = [10.0, 12.0, 11.0, 13.0, 11.5, 12.5]
    summary = compute_summary_stats(data)
    assert summary["count"] == 6
    assert summary["mean"] > 11.0
    
    ci_low, ci_high = compute_ci(data, 0.95)
    assert ci_low < summary["mean"] < ci_high

def test_hypothesis_tester():
    # H3: Ordering error test
    phys_errors = [0.35, 0.40, 0.38, 0.42, 0.39]
    log_errors = [0.02, 0.01, 0.04, 0.02, 0.01]
    res = HypothesisTester.test_h3_ordering_error_reduction(phys_errors, log_errors)
    assert res["hypothesis"] == "H3_Logical_Event_Ordering"
    assert res["reject_null"] is True
