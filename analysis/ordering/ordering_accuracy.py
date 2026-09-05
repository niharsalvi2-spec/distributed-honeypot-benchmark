"""
Event Ordering Accuracy Comparison.
Computes Sequence Reconstruction Accuracy (SRA) across Physical, Lamport, and Vector clocks.
"""
from typing import List, Dict
from sequence_reconstruction.sequence_validator import SequenceValidator

def compare_clock_accuracies(truth_seq: List[str], physical_seq: List[str],
                             lamport_seq: List[str], vector_seq: List[str]) -> Dict[str, float]:
    return {
        "physical_sra": round(SequenceValidator.compute_sra(truth_seq, physical_seq), 4),
        "lamport_sra": round(SequenceValidator.compute_sra(truth_seq, lamport_seq), 4),
        "vector_sra": round(SequenceValidator.compute_sra(truth_seq, vector_seq), 4)
    }
