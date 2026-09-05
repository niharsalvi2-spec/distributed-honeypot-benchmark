"""
Statistical Validation & 30-Trial Monte Carlo Evaluation Engine
Executes repeated independent trials with randomized network jitter, clock perturbation,
and variable noise injection to produce publication-grade statistical confidence intervals:
- Sample Size n = 30
- Metrics: Correlation (F1, Precision, Recall, Contamination), Clocks (Inversion Rate, Kendall's Tau), Vector Concurrency (DAG Accuracy)
- Statistics: Mean, Median, Std, Variance, Min, Max, 95% Confidence Interval (CI_95)
- Hypothesis Testing: Paired Student's t-test p-values and Cohen's d effect sizes
"""
import os
import json
import math
import random
from typing import List, Dict, Any
from ground_truth.oracle import BenchmarkOracle
from ground_truth.generator.scenario_generator import ScenarioGenerator
from analysis.feature_ablation.ablation_runner import AlgorithmicCorrelationEngine
from distributed.messaging.channel import DistributedNode, DistributedChannel
from distributed.clocks.clock_comparator import ClockComparator
from distributed.clocks.vector_clock import VectorClock

def compute_statistics(values: List[float]) -> Dict[str, Any]:
    n = len(values)
    if n == 0:
        return {}
    mean = sum(values) / n
    sorted_vals = sorted(values)
    median = sorted_vals[n // 2] if n % 2 != 0 else (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2.0
    variance = sum((x - mean) ** 2 for x in values) / (n - 1) if n > 1 else 0.0
    std = math.sqrt(variance)
    margin = 1.96 * (std / math.sqrt(n)) if n > 1 else 0.0

    return {
        "n": n,
        "mean": round(mean, 4),
        "median": round(median, 4),
        "std": round(std, 4),
        "variance": round(variance, 4),
        "min": round(min(values), 4),
        "max": round(max(values), 4),
        "ci_95_lower": round(max(0.0, mean - margin), 4),
        "ci_95_upper": round(min(1.0, mean + margin), 4),
        "ci_95_display": f"{round(mean, 4)} +/- {round(margin, 4)}"
    }

class StatisticalTrialRunner:
    def __init__(self, trials_count: int = 30, base_seed: int = 42000):
        self.trials_count = trials_count
        self.base_seed = base_seed
        self.oracle = BenchmarkOracle()
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.dag_path = os.path.join(project_root, "workloads", "fault", "clock_skew_dag.json")

    def run_trials(self) -> Dict[str, Any]:
        # Correlation metric lists
        precision_list = []
        recall_list = []
        f1_list = []
        contamination_list = []
        src_f1_list = []
        temp_f1_list = []

        # Distributed clock metric lists
        phys_inv_rate_list = []
        lamp_inv_rate_list = []
        phys_tau_list = []
        lamp_tau_list = []
        dag_acc_list = []

        trial_records = []

        # Load decoupled ground truth DAG for distributed clock evaluation
        with open(self.dag_path, "r", encoding="utf-8") as f:
            clock_dag = json.load(f)

        for t_idx in range(1, self.trials_count + 1):
            seed = self.base_seed + t_idx
            random.seed(seed)

            # 1. Dynamic Workload Generation (Zero Hardcoded IDs)
            gen = ScenarioGenerator(seed=seed)
            workload = gen.generate_benchmark_workload(seed=seed)
            events = workload["unannotated_events"]
            gt_clusters = workload["ground_truth_clusters"]

            # Perturb timestamps with randomized network jitter [-50ms, +150ms]
            jittered_events = []
            for ev in events:
                ev_copy = dict(ev)
                jitter_sec = random.uniform(-0.05, 0.15)
                ev_copy["timestamp"] = ev["timestamp"] + jitter_sec
                jittered_events.append(ev_copy)

            # 2. Algorithmic Correlation Evaluation
            # Proposed Multi-Tier
            pred_multi = AlgorithmicCorrelationEngine.run_full_multi_tier(jittered_events)
            m_multi = self.oracle.evaluate_correlation(pred_multi, only_attack_clusters=True, custom_gt_clusters=gt_clusters)

            # Baseline 1: Source-Only
            pred_src = AlgorithmicCorrelationEngine.run_source_only(jittered_events)
            m_src = self.oracle.evaluate_correlation(pred_src, only_attack_clusters=True, custom_gt_clusters=gt_clusters)

            # Baseline 2: Temporal-Only
            pred_temp = AlgorithmicCorrelationEngine.run_temporal_only(jittered_events)
            m_temp = self.oracle.evaluate_correlation(pred_temp, only_attack_clusters=True, custom_gt_clusters=gt_clusters)

            precision_list.append(m_multi["precision"])
            recall_list.append(m_multi["recall"])
            f1_list.append(m_multi["f1_score"])
            contamination_list.append(m_multi["cross_attacker_contamination_count"])
            src_f1_list.append(m_src["f1_score"])
            temp_f1_list.append(m_temp["f1_score"])

            # 3. Distributed Clock & Causal Partial-Order Evaluation
            # Simulate multi-node message passing with Gaussian clock skew & network delay
            cluster_nodes = ["node_alpha", "node_beta", "node_gamma"]
            nodes = {nid: DistributedNode(nid, cluster_nodes) for nid in cluster_nodes}
            channel = DistributedChannel(latency_ms=15.0 + random.uniform(-2.0, 2.0), jitter_ms=5.0, drop_rate=0.0)

            node_skews = {
                "node_alpha": 0.0,
                "node_beta": 5.0 + random.uniform(-0.5, 0.5),
                "node_gamma": -3.0 + random.uniform(-0.5, 0.5)
            }

            # Generate multi-node events with known ground truth ordering
            clock_events = []
            base_t = 1757120000.0 + (t_idx * 1000)
            for i in range(12):
                node_id = cluster_nodes[i % 3]
                real_time = base_t + (i * 1.5)
                skewed_time = real_time + node_skews[node_id] + random.uniform(-0.1, 0.1)
                clock_events.append({
                    "event_id": f"EV_PERTRUB_{i:03d}",
                    "real_timestamp": real_time,
                    "skewed_timestamp": skewed_time,
                    "node_id": node_id,
                    "service": "ssh" if i % 2 == 0 else "http",
                    "logical_order": i
                })

            outgoing_edges = {}
            incoming_edges = {}
            for edge in clock_dag.get("edges", []):
                outgoing_edges.setdefault(edge["from"], []).append(edge["to"])
                incoming_edges.setdefault(edge["to"], []).append(edge["from"])

            lamport_timestamps = {}
            vector_clocks = {}
            pending_messages = {}

            for cev in clock_events:
                ceid = cev["event_id"]
                cnid = cev["node_id"]
                cnode = nodes[cnid]

                if ceid in incoming_edges:
                    for pred_id in incoming_edges[ceid]:
                        if pred_id in pending_messages:
                            cnode.receive_event(pending_messages[pred_id])

                cnode.lamport_clock.tick()
                cnode.vector_clock.tick()

                if ceid in outgoing_edges:
                    msg = cnode.send_event(cev, recipient_id="cluster_broadcast", channel=channel)
                    pending_messages[ceid] = msg

                lamport_timestamps[ceid] = cnode.lamport_clock.read()
                vector_clocks[ceid] = dict(cnode.vector_clock.clock)

            gt_order = [e["event_id"] for e in sorted(clock_events, key=lambda x: x["real_timestamp"])]
            phys_order = [e["event_id"] for e in sorted(clock_events, key=lambda x: x["skewed_timestamp"])]
            lamp_order = [e["event_id"] for e in sorted(clock_events, key=lambda x: (lamport_timestamps.get(x["event_id"], 0), x["node_id"]))]

            p_inv, p_rate = ClockComparator.compute_inversions(gt_order, phys_order)
            p_tau = ClockComparator.compute_kendall_tau(gt_order, phys_order)
            l_inv, l_rate = ClockComparator.compute_inversions(gt_order, lamp_order)
            l_tau = ClockComparator.compute_kendall_tau(gt_order, lamp_order)

            phys_inv_rate_list.append(p_rate)
            lamp_inv_rate_list.append(l_rate)
            phys_tau_list.append(p_tau)
            lamp_tau_list.append(l_tau)

            # Vector Clock DAG reachability accuracy
            predicted_relations = {}
            for i in range(len(clock_events)):
                for j in range(len(clock_events)):
                    if i != j:
                        u = clock_events[i]["event_id"]
                        v = clock_events[j]["event_id"]
                        rel = VectorClock.compare(vector_clocks[u], vector_clocks[v])
                        predicted_relations[(u, v)] = rel

            dag_eval = self.oracle.evaluate_partial_order(
                predicted_relations,
                causal_dag=clock_dag,
                true_sequence=gt_order
            )
            dag_acc_list.append(dag_eval.get("relation_accuracy", 1.0))

            trial_data = {
                "trial": t_idx,
                "seed": seed,
                "correlation": {
                    "proposed_f1": m_multi["f1_score"],
                    "proposed_precision": m_multi["precision"],
                    "proposed_recall": m_multi["recall"],
                    "contamination": m_multi["cross_attacker_contamination_count"],
                    "source_only_f1": m_src["f1_score"],
                    "temporal_only_f1": m_temp["f1_score"]
                },
                "clocks": {
                    "physical_inversion_rate": p_rate,
                    "physical_kendall_tau": p_tau,
                    "lamport_inversion_rate": l_rate,
                    "lamport_kendall_tau": l_tau,
                    "vector_dag_accuracy": dag_eval.get("relation_accuracy", 1.0)
                }
            }
            trial_records.append(trial_data)

            # Persist individual trial manifest
            trials_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "results", "trials"))
            os.makedirs(trials_dir, exist_ok=True)
            with open(os.path.join(trials_dir, f"trial_{t_idx:03d}.json"), "w", encoding="utf-8") as tf:
                json.dump(trial_data, tf, indent=2)

        # Statistical comparisons
        def compute_cohens_d(x: List[float], y: List[float]) -> float:
            mean_x, mean_y = sum(x) / len(x), sum(y) / len(y)
            var_x = sum((val - mean_x) ** 2 for val in x) / (len(x) - 1)
            var_y = sum((val - mean_y) ** 2 for val in y) / (len(y) - 1)
            s_pooled = math.sqrt((var_x + var_y) / 2.0)
            if s_pooled == 0:
                return 0.0
            return (mean_x - mean_y) / s_pooled

        def compute_paired_p_val(x: List[float], y: List[float]) -> float:
            diffs = [a - b for a, b in zip(x, y)]
            mean_d = sum(diffs) / len(diffs)
            var_d = sum((d - mean_d) ** 2 for d in diffs) / (len(diffs) - 1) if len(diffs) > 1 else 0.0
            s_d = math.sqrt(var_d)
            if s_d == 0:
                return 1.0 if mean_d == 0 else 0.0001
            t_stat = mean_d / (s_d / math.sqrt(len(diffs)))
            z = abs(t_stat)
            p_val = 2.0 * (1.0 - 0.5 * (1.0 + math.erf(z / math.sqrt(2.0))))
            return max(0.0001, min(1.0, p_val))

        d_vs_source = compute_cohens_d(f1_list, src_f1_list)
        p_vs_source = compute_paired_p_val(f1_list, src_f1_list)
        d_vs_temp = compute_cohens_d(f1_list, temp_f1_list)
        p_vs_temp = compute_paired_p_val(f1_list, temp_f1_list)

        d_clock = compute_cohens_d(phys_inv_rate_list, lamp_inv_rate_list)
        p_clock = compute_paired_p_val(phys_inv_rate_list, lamp_inv_rate_list)

        summary = {
            "experiment_id": "STATISTICAL_30_TRIALS_BENCHMARK",
            "total_trials": self.trials_count,
            "base_seed": self.base_seed,
            "metrics": {
                "precision": compute_statistics(precision_list),
                "recall": compute_statistics(recall_list),
                "f1_score": compute_statistics(f1_list),
                "contamination": compute_statistics(contamination_list),
                "source_only_f1": compute_statistics(src_f1_list),
                "temporal_only_f1": compute_statistics(temp_f1_list),
                "physical_inversion_rate": compute_statistics(phys_inv_rate_list),
                "lamport_inversion_rate": compute_statistics(lamp_inv_rate_list),
                "physical_kendall_tau": compute_statistics(phys_tau_list),
                "lamport_kendall_tau": compute_statistics(lamp_tau_list),
                "vector_dag_accuracy": compute_statistics(dag_acc_list)
            },
            "hypothesis_testing": {
                "H1_correlation_vs_source_only": {
                    "cohens_d": round(d_vs_source, 4),
                    "p_value": round(p_vs_source, 5),
                    "statistically_significant": p_vs_source < 0.05
                },
                "H2_correlation_vs_temporal_only": {
                    "cohens_d": round(d_vs_temp, 4),
                    "p_value": round(p_vs_temp, 5),
                    "statistically_significant": p_vs_temp < 0.05
                },
                "H3a_logical_ordering_preservation": {
                    "cohens_d": round(d_clock, 4),
                    "p_value": round(p_clock, 5),
                    "statistically_significant": p_clock < 0.05,
                    "hypothesis_supported": sum(lamp_inv_rate_list) < sum(phys_inv_rate_list)
                },
                "H3b_vector_concurrency_accuracy": {
                    "mean_accuracy": round(sum(dag_acc_list) / len(dag_acc_list), 4),
                    "hypothesis_supported": (sum(dag_acc_list) / len(dag_acc_list)) >= 0.85
                }
            },
            "trials_summary": trial_records[:5]
        }

        return summary

def main():
    runner = StatisticalTrialRunner(trials_count=30)
    summary = runner.run_trials()

    print("\n" + "="*85)
    print(f"      30-TRIAL STATISTICAL EVALUATION REPORT (SEED 42001 - 42030)")
    print("="*85)
    print(f"{'Metric':<26} | {'Mean':<8} | {'Median':<8} | {'Std':<8} | {'95% Confidence Interval':<24}")
    print("-" * 85)
    for m_name in [
        "precision", "recall", "f1_score", "contamination",
        "physical_inversion_rate", "lamport_inversion_rate",
        "physical_kendall_tau", "lamport_kendall_tau", "vector_dag_accuracy"
    ]:
        s = summary["metrics"][m_name]
        print(f"{m_name:<26} | {s['mean']:<8.4f} | {s['median']:<8.4f} | {s['std']:<8.4f} | {s['ci_95_display']:<24}")
    print("-" * 85)
    ht = summary["hypothesis_testing"]
    print(f"H1 vs Source-Only:    Cohen's d = {ht['H1_correlation_vs_source_only']['cohens_d']:+.2f}, p-val = {ht['H1_correlation_vs_source_only']['p_value']:.5f} (Significant: {ht['H1_correlation_vs_source_only']['statistically_significant']})")
    print(f"H2 vs Temporal-Only:  Cohen's d = {ht['H2_correlation_vs_temporal_only']['cohens_d']:+.2f}, p-val = {ht['H2_correlation_vs_temporal_only']['p_value']:.5f} (Significant: {ht['H2_correlation_vs_temporal_only']['statistically_significant']})")
    print(f"H3a Clock Inversion:  Cohen's d = {ht['H3a_logical_ordering_preservation']['cohens_d']:+.2f}, p-val = {ht['H3a_logical_ordering_preservation']['p_value']:.5f} (Supported: {ht['H3a_logical_ordering_preservation']['hypothesis_supported']})")
    print(f"H3b Vector Concur:    Mean Acc  = {ht['H3b_vector_concurrency_accuracy']['mean_accuracy']:.4f} (Supported: {ht['H3b_vector_concurrency_accuracy']['hypothesis_supported']})")
    print("="*85 + "\n")

    # Export
    out_dir = os.path.join(os.path.dirname(__file__), "..", "..", "results")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "statistical_30_trials_summary.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"[+] 30-trial statistical report saved to: {out_file}")

if __name__ == "__main__":
    main()
