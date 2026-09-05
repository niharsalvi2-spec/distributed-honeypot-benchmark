"""
Metric Analyzer: E07_clock_perturbation
Simulates true distributed message passing (send/receive) across independent sensor nodes
under clock skew, network delay, and jitter, and evaluates Physical vs Lamport vs Vector Clocks
using ground-truth DAG partial order analysis.
"""
import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import json
from typing import Dict, Any, List
from distributed.messaging.channel import DistributedNode, DistributedChannel
from distributed.clocks.clock_comparator import ClockComparator
from sequence_reconstruction.sequence_validator import SequenceValidator
from ground_truth.oracle import BenchmarkOracle

def analyze_run(run_id: str) -> Dict[str, Any]:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    norm_file = os.path.join(project_root, "data", "normalized", run_id, "normalized_events.jsonl")
    
    raw_events = []
    if os.path.exists(norm_file):
        with open(norm_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    raw_events.append(json.loads(line))

    # 1. Load Decoupled Ground Truth DAG from pre-defined workload
    dag_path = os.path.join(project_root, "workloads", "fault", "clock_skew_dag.json")
    with open(dag_path, "r", encoding="utf-8") as f:
        ground_truth_dag = json.load(f)

    # 2. Setup multi-node distributed cluster
    cluster_nodes = ["node_alpha", "node_beta", "node_gamma"]
    nodes = {nid: DistributedNode(nid, cluster_nodes) for nid in cluster_nodes}
    channel = DistributedChannel(latency_ms=15.0, jitter_ms=5.0, drop_rate=0.0)

    # Map outgoing and incoming causal dependencies from the DAG
    outgoing_edges = {}
    incoming_edges = {}
    for edge in ground_truth_dag.get("edges", []):
        outgoing_edges.setdefault(edge["from"], []).append(edge["to"])
        incoming_edges.setdefault(edge["to"], []).append(edge["from"])

    # 3. Simulate message passing across nodes following DAG dependencies
    lamport_timestamps = {}
    vector_clocks = {}
    pending_messages = {}

    for ev in raw_events:
        eid = ev["event_id"]
        nid = ev["node_id"]
        node = nodes[nid]

        # Check if this event receives messages from preceding events
        if eid in incoming_edges:
            for pred_eid in incoming_edges[eid]:
                if pred_eid in pending_messages:
                    msg = pending_messages[pred_eid]
                    node.receive_event(msg)

        # Local clock tick for event occurrence
        node.lamport_clock.tick()
        node.vector_clock.tick()

        # If this event has outgoing edges to subsequent events, dispatch message
        if eid in outgoing_edges:
            msg = node.send_event(ev, recipient_id="cluster_broadcast", channel=channel)
            pending_messages[eid] = msg

        lamport_timestamps[eid] = node.lamport_clock.read()
        vector_clocks[eid] = dict(node.vector_clock.clock)

    # 3. Ground Truth Total Order
    gt_order = [e["event_id"] for e in sorted(raw_events, key=lambda x: x["real_timestamp"])]

    # 4. Physical Clock Order (skewed)
    phys_sorted = sorted(raw_events, key=lambda x: x["skewed_timestamp"])
    phys_order = [e["event_id"] for e in phys_sorted]
    phys_inv, phys_inv_rate = ClockComparator.compute_inversions(gt_order, phys_order)
    phys_tau = ClockComparator.compute_kendall_tau(gt_order, phys_order)
    phys_sra = SequenceValidator.compute_sra(gt_order, phys_order)

    # 5. Lamport Logical Clock Order
    lamp_sorted = sorted(raw_events, key=lambda x: (lamport_timestamps.get(x["event_id"], 0), x["node_id"]))
    lamp_order = [e["event_id"] for e in lamp_sorted]
    lamp_inv, lamp_inv_rate = ClockComparator.compute_inversions(gt_order, lamp_order)
    lamp_tau = ClockComparator.compute_kendall_tau(gt_order, lamp_order)
    lamp_sra = SequenceValidator.compute_sra(gt_order, lamp_order)

    # 6. DAG Partial Order Evaluation using BenchmarkOracle
    # Compute pairwise relations using Vector Clocks
    from distributed.clocks.vector_clock import VectorClock
    predicted_relations = {}
    for i in range(len(raw_events)):
        for j in range(len(raw_events)):
            if i != j:
                u = raw_events[i]["event_id"]
                v = raw_events[j]["event_id"]
                rel = VectorClock.compare(vector_clocks[u], vector_clocks[v])
                predicted_relations[(u, v)] = rel

    oracle = BenchmarkOracle()
    dag_eval = oracle.evaluate_partial_order(
        predicted_relations,
        causal_dag=ground_truth_dag,
        true_sequence=gt_order
    )

    return {
        "experiment_id": "E07",
        "run_id": run_id,
        "physical_inversion_rate": round(phys_inv_rate, 4),
        "physical_kendall_tau": round(phys_tau, 4),
        "physical_sra": round(phys_sra, 4),
        "lamport_inversion_rate": round(lamp_inv_rate, 4),
        "lamport_kendall_tau": round(lamp_tau, 4),
        "lamport_sra": round(lamp_sra, 4),
        "dag_partial_order_accuracy": dag_eval.get("relation_accuracy", 1.0),
        "total_evaluated_pairs": dag_eval.get("total_evaluated_pairs", 0),
        "hypothesis_H3a_supported": lamp_inv_rate < phys_inv_rate,
        "hypothesis_H3b_supported": dag_eval.get("relation_accuracy", 1.0) >= 0.85
    }

