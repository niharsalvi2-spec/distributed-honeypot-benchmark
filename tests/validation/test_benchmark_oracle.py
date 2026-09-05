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
