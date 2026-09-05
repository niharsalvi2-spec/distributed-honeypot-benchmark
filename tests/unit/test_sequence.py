"""
Unit Test: Sequence Reconstruction and Accuracy (SRA)
Tests CausalGraphBuilder, AttackChainBuilder, and SequenceValidator.
"""
import pytest
from sequence_reconstruction.causal_graph import CausalGraphBuilder
from sequence_reconstruction.sequence_validator import SequenceValidator

def test_causal_graph_topological_sort():
    builder = CausalGraphBuilder()
    builder.add_event("A", {"timestamp": 100})
    builder.add_event("B", {"timestamp": 200})
    builder.add_event("C", {"timestamp": 300})

    builder.add_causal_edge("A", "B", relation="leads_to")
    builder.add_causal_edge("B", "C", relation="leads_to")

    sorted_seq = builder.get_topological_sequence()
    assert sorted_seq == ["A", "B", "C"]

def test_sequence_reconstruction_accuracy():
    ground_truth = ["E1", "E2", "E3", "E4", "E5"]
    observed_perfect = ["E1", "E2", "E3", "E4", "E5"]
    observed_inverted = ["E1", "E3", "E2", "E4", "E5"]  # 1 inversion

    sra_perfect = SequenceValidator.compute_sra(ground_truth, observed_perfect)
    assert sra_perfect == 1.0

    sra_inverted = SequenceValidator.compute_sra(ground_truth, observed_inverted)
    assert 0.0 < sra_inverted < 1.0
