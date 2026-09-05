"""
Scientific Validation Tests: Benchmark Oracle & Feature Ablation
Validates that:
1. Oracle accurately quantifies Sequence Reconstruction Accuracy (SRA) and Causal Inversions.
2. Oracle detects and penalizes cross-attacker contamination.
3. Feature ablation scientifically demonstrates why IP-only attribution fails under lateral movement.
"""
import pytest
from ground_truth.oracle import BenchmarkOracle
from analysis.feature_ablation.ablation_runner import FeatureAblationBenchmark

@pytest.fixture
def oracle():
    return BenchmarkOracle()

def test_oracle_perfect_sequence_accuracy(oracle):
    """
    Scientific Test: Given ground truth sequence A -> B -> C -> D -> E -> F,
    asserts that SRA is 1.0 and pairwise causal inversions equal 0.
    """
    perfect_seq = [
        "evt-alpha-001",
        "evt-alpha-002",
        "evt-alpha-003",
        "evt-alpha-004",
        "evt-alpha-005",
        "evt-alpha-006"
    ]
    metrics = oracle.evaluate_ordering(perfect_seq, actor_id="ACTOR_ALPHA")
    assert metrics["sra"] == 1.0
    assert metrics["inversion_count"] == 0
    assert metrics["inversion_rate"] == 0.0
    assert metrics["kendall_tau"] == 1.0

def test_oracle_detects_causal_inversions(oracle):
    """
    Scientific Test: Given an inverted sequence where payload drop occurs before reconnaissance,
    asserts that the Oracle detects inversions and SRA strictly drops.
    """
    inverted_seq = [
        "evt-alpha-006",  # Payload drop observed first (severe clock skew)
        "evt-alpha-001",  # Recon observed second
        "evt-alpha-002"
    ]
    metrics = oracle.evaluate_ordering(inverted_seq, actor_id="ACTOR_ALPHA")
    assert metrics["inversion_count"] >= 2
    assert metrics["inversion_rate"] > 0.0
    assert metrics["sra"] < 1.0

def test_oracle_perfect_correlation_clusters(oracle):
    """
    Scientific Test: When prediction matches ground truth clusters,
    Precision, Recall, and F1 must be 1.0 with 0 contamination.
    """
    predicted_clusters = [
        ["evt-alpha-001", "evt-alpha-002", "evt-alpha-003", "evt-alpha-004", "evt-alpha-005", "evt-alpha-006"],
        ["evt-beta-001", "evt-beta-002", "evt-beta-003"]
    ]
    metrics = oracle.evaluate_correlation(predicted_clusters, only_attack_clusters=True)
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["f1_score"] == 1.0
    assert metrics["cross_attacker_contamination_count"] == 0

def test_oracle_detects_cross_attacker_contamination(oracle):
    """
    Scientific Test: If an algorithm falsely groups Attacker Alpha and Attacker Beta into the same session,
    the Oracle must catch the disallowed cross-attacker pair and penalize precision.
    """
    contaminated_clusters = [
        ["evt-alpha-001", "evt-beta-001", "evt-alpha-002"]  # Merged Alpha and Beta
    ]
    metrics = oracle.evaluate_correlation(contaminated_clusters, only_attack_clusters=True)
    assert metrics["cross_attacker_contamination_count"] >= 1
    assert metrics["precision"] < 1.0

def test_feature_ablation_oracle_validation(oracle):
    """
    Scientific Test: Verifies empirical feature ablation against Ground Truth Oracle:
    - IP-only model suffers reduced recall due to internal lateral movement IP change.
    - Temporal-only model suffers reduced precision and contamination due to overlapping attackers.
    - Full Multi-Tier model achieves F1 >= 0.85 without cross-attacker contamination.
    """
    ablation = FeatureAblationBenchmark(oracle=oracle)
    results = ablation.evaluate_all()

    source_only = results["1. Source-Only (IP Baseline)"]
    temporal_only = results["2. Temporal-Only (Window Baseline)"]
    multi_tier = results["5. Full Multi-Tier Model (Our Benchmark)"]

    # 1. IP-only recall is strictly lower than Multi-Tier (fails on lateral pivot)
    assert source_only["recall"] < multi_tier["recall"]

    # 2. Temporal-only precision is strictly lower than Multi-Tier and has contamination
    assert temporal_only["precision"] < multi_tier["precision"]
    assert temporal_only["cross_attacker_contamination_count"] > 0

    # 3. Multi-tier achieves target F1
    assert multi_tier["f1_score"] >= 0.85
    assert multi_tier["cross_attacker_contamination_count"] == 0

def test_oracle_everything_split_collapses_recall(oracle):
    """
    Scientific Test B: Everything Split.
    If an algorithm isolates every event into its own single-element cluster,
    pairwise True Positives must be 0, Recall must collapse to 0.0, and F1 must be 0.0.
    """
    all_events = [
        "evt-alpha-001", "evt-alpha-002", "evt-alpha-003",
        "evt-alpha-004", "evt-alpha-005", "evt-alpha-006",
        "evt-beta-001", "evt-beta-002", "evt-beta-003"
    ]
    split_clusters = [[eid] for eid in all_events]
    metrics = oracle.evaluate_correlation(split_clusters, only_attack_clusters=True)
    assert metrics["true_positives"] == 0
    assert metrics["recall"] == 0.0
    assert metrics["f1_score"] == 0.0

def test_oracle_everything_merged_collapses_precision(oracle):
    """
    Scientific Test C: Everything Merged.
    If an algorithm merges all independent actors into a single giant blob,
    Recall is 1.0 but False Positives surge, Precision drops, and Cross-Attacker Contamination is detected.
    """
    all_events = [
        "evt-alpha-001", "evt-alpha-002", "evt-alpha-003",
        "evt-alpha-004", "evt-alpha-005", "evt-alpha-006",
        "evt-beta-001", "evt-beta-002", "evt-beta-003"
    ]
    merged_cluster = [all_events]
    metrics = oracle.evaluate_correlation(merged_cluster, only_attack_clusters=True)
    assert metrics["recall"] == 1.0
    assert metrics["precision"] < 0.60
    assert metrics["cross_attacker_contamination_count"] >= 4

def test_oracle_missing_events_penalizes_completeness(oracle):
    """
    Scientific Test D: Partial Sequence / Incomplete Reconstruction.
    Reconstructing only 2 out of 6 events in correct order gives SRA=1.0,
    but completeness=0.3333, so composite_sequence_score must be penalized.
    """
    partial_seq = ["evt-alpha-001", "evt-alpha-002"]
    metrics = oracle.evaluate_ordering(partial_seq, actor_id="ACTOR_ALPHA")
    assert metrics["sra"] == 1.0
    assert metrics["completeness"] == round(2 / 6, 4)
    assert metrics["composite_sequence_score"] < 0.40

def test_oracle_partial_order_evaluation(oracle):
    """
    Scientific Test E: Partial Order DAG Evaluation.
    Evaluates topological relations (BEFORE / AFTER / EQUAL).
    """
    relations = {
        ("evt-alpha-001", "evt-alpha-002"): "BEFORE",
        ("evt-alpha-002", "evt-alpha-003"): "BEFORE",
        ("evt-alpha-003", "evt-alpha-001"): "AFTER"
    }
    metrics = oracle.evaluate_partial_order(relations, actor_id="ACTOR_ALPHA")
    assert metrics["relation_accuracy"] == 1.0
    assert metrics["correct_relations"] == 3

def test_oracle_detects_concurrency_in_branching_dag(oracle):
    """
    Scientific Test F: Concurrency in Branching DAG (A -> B, A -> C, B -> D, C -> D).
    Proves that B and C are correctly identified as CONCURRENT (B || C) by DAG reachability
    rather than being forced into a false linear total order.
    """
    branching_dag = {
        "nodes": ["A", "B", "C", "D"],
        "edges": [
            {"from": "A", "to": "B"},
            {"from": "A", "to": "C"},
            {"from": "B", "to": "D"},
            {"from": "C", "to": "D"}
        ]
    }
    # Relations: A before B, A before C, B || C, C || B, B before D, C before D
    predicted_relations = {
        ("A", "B"): "BEFORE",
        ("A", "C"): "BEFORE",
        ("B", "C"): "CONCURRENT",
        ("C", "B"): "CONCURRENT",
        ("B", "D"): "BEFORE",
        ("C", "D"): "BEFORE",
        ("D", "A"): "AFTER"
    }
    metrics = oracle.evaluate_partial_order(predicted_relations, causal_dag=branching_dag)
    assert metrics["relation_accuracy"] == 1.0
    assert metrics["concurrency_metrics"]["ground_truth_concurrent_pairs"] == 2
    assert metrics["concurrency_metrics"]["true_positives"] == 2
    assert metrics["concurrency_metrics"]["false_positives"] == 0
    assert metrics["concurrency_metrics"]["precision"] == 1.0
    assert metrics["concurrency_metrics"]["recall"] == 1.0
    assert metrics["concurrency_metrics"]["f1_score"] == 1.0

