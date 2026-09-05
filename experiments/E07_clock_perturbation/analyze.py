"""
Metric Analyzer: E07_clock_perturbation
Calculates Pairwise Sequence Inversions, Kendall's Tau, and SRA across clock models.
"""
import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import os
import json
from typing import Dict, Any
from distributed.clocks.clock_comparator import ClockComparator
from distributed.clocks.lamport_clock import LamportClock
from distributed.clocks.vector_clock import VectorClock
from sequence_reconstruction.sequence_validator import SequenceValidator

def analyze_run(run_id: str) -> Dict[str, Any]:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    norm_file = os.path.join(project_root, "data", "normalized", run_id, "normalized_events.jsonl")
    
    events = []
    if os.path.exists(norm_file):
        with open(norm_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))

    # Ground truth causal sequence
    gt_order = [e["event_id"] for e in sorted(events, key=lambda x: x["real_timestamp"])]

    # 1. Physical clock order (skewed)
    phys_sorted = sorted(events, key=lambda x: x["skewed_timestamp"])
    phys_order = [e["event_id"] for e in phys_sorted]
    phys_inv, phys_inv_rate = ClockComparator.compute_inversions(gt_order, phys_order)
    phys_tau = ClockComparator.compute_kendall_tau(gt_order, phys_order)
    phys_sra = SequenceValidator.compute_sra(gt_order, phys_order)

    # 2. Lamport Clock simulation
    lamport = LamportClock()
    lamport_tagged = []
    for e in events:
        c = lamport.tick()
        lamport_tagged.append((e["event_id"], c))
    lamp_order = [x[0] for x in sorted(lamport_tagged, key=lambda x: x[1])]
    lamp_inv, lamp_inv_rate = ClockComparator.compute_inversions(gt_order, lamp_order)
    lamp_tau = ClockComparator.compute_kendall_tau(gt_order, lamp_order)
    lamp_sra = SequenceValidator.compute_sra(gt_order, lamp_order)

    return {
        "experiment_id": "E07",
        "run_id": run_id,
        "physical_inversion_rate": round(phys_inv_rate, 4),
        "physical_kendall_tau": round(phys_tau, 4),
        "physical_sra": round(phys_sra, 4),
        "lamport_inversion_rate": round(lamp_inv_rate, 4),
        "lamport_kendall_tau": round(lamp_tau, 4),
        "lamport_sra": round(lamp_sra, 4),
        "hypothesis_H2_supported": phys_inv_rate > 0.05 and lamp_inv_rate < phys_inv_rate
    }
