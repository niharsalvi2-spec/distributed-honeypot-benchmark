"""
Empirical Negative Controls Benchmark Engine
Evaluates correlation algorithms against 6 adversarial and negative control scenarios:
1. Shared IP / NAT collision (Same IP, Different Attacker)
2. Dynamic IP / Multi-Node Pivot (Different IP, Same Attacker)
3. Concurrent Overlapping Attackers (Simultaneous independent sessions)
4. Missing Telemetry Events (Packet loss / log drop)
5. Duplicate Telemetry Events (Transport retransmission)
6. Out-of-Order Telemetry (Network arrival jitter)
"""
import os
import json
from typing import Dict, Any, List
from ground_truth.generator.scenario_generator import ScenarioGenerator
from ground_truth.oracle import BenchmarkOracle
from analysis.feature_ablation.ablation_runner import AlgorithmicCorrelationEngine

class NegativeControlsBenchmark:
    def __init__(self, seed: int = 42):
        self.scenario_gen = ScenarioGenerator(seed=seed)
        self.oracle = BenchmarkOracle()

    def evaluate_scenario(self, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        events = scenario_data["events"]
        gt_clusters = scenario_data.get("ground_truth_clusters", {})

        # 1. IP-Only Baseline
        ip_clusters = AlgorithmicCorrelationEngine.run_source_only(events)
        ip_metrics = self._evaluate_custom_gt(ip_clusters, gt_clusters)

        # 2. Temporal-Only Baseline
        temp_clusters = AlgorithmicCorrelationEngine.run_temporal_only(events)
        temp_metrics = self._evaluate_custom_gt(temp_clusters, gt_clusters)

        # 3. Proposed Multi-Tier Model
        proposed_clusters = AlgorithmicCorrelationEngine.run_full_multi_tier(events)
        proposed_metrics = self._evaluate_custom_gt(proposed_clusters, gt_clusters)

        return {
            "scenario": scenario_data["scenario"],
            "event_count": len(events),
            "ip_only_baseline": ip_metrics,
            "temporal_only_baseline": temp_metrics,
            "proposed_multi_tier": proposed_metrics,
            "empirical_finding": self._derive_finding(scenario_data["scenario"], ip_metrics, proposed_metrics)
        }

    def _evaluate_custom_gt(self, predicted_clusters: List[List[str]], gt_clusters: Dict[str, List[str]]) -> Dict[str, Any]:
        # Form pairwise co-membership from gt_clusters
        gt_pairs = set()
        for actor, eids in gt_clusters.items():
            for i in range(len(eids)):
                for j in range(i + 1, len(eids)):
                    gt_pairs.add(tuple(sorted((eids[i], eids[j]))))

        pred_pairs = set()
        for cl in predicted_clusters:
            for i in range(len(cl)):
                for j in range(i + 1, len(cl)):
                    pred_pairs.add(tuple(sorted((cl[i], cl[j]))))

        tp = len(gt_pairs.intersection(pred_pairs))
        fp = len(pred_pairs.difference(gt_pairs))
        fn = len(gt_pairs.difference(pred_pairs))

        prec = round(tp / (tp + fp), 4) if (tp + fp) > 0 else (1.0 if len(gt_pairs) == 0 else 0.0)
        rec = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
        f1 = round((2 * prec * rec) / (prec + rec), 4) if (prec + rec) > 0 else 0.0

        # Disallowed cross-attacker pairs (contamination)
        actors = list(gt_clusters.keys())
        contamination = 0
        for i in range(len(actors)):
            for j in range(i + 1, len(actors)):
                for e1 in gt_clusters[actors[i]]:
                    for e2 in gt_clusters[actors[j]]:
                        if tuple(sorted((e1, e2))) in pred_pairs:
                            contamination += 1

        return {
            "precision": prec,
            "recall": rec,
            "f1_score": f1,
            "cross_attacker_contamination": contamination
        }

    def _derive_finding(self, scenario_name: str, ip_metrics: Dict[str, Any], proposed_metrics: Dict[str, Any]) -> str:
        if "NAT" in scenario_name:
            return f"IP-only produced {ip_metrics['cross_attacker_contamination']} false merge contamination; Proposed achieved contamination = {proposed_metrics['cross_attacker_contamination']}."
        elif "DIFFERENT_IP" in scenario_name:
            return f"IP-only recall collapsed to {ip_metrics['recall']}; Proposed achieved recall = {proposed_metrics['recall']} across rotated IPs."
        return f"Proposed model achieved F1={proposed_metrics['f1_score']} vs IP-only F1={ip_metrics['f1_score']}."

    def run_all_negative_controls(self) -> Dict[str, Any]:
        scenarios = [
            self.scenario_gen.generate_scenario_1_shared_ip_nat(),
            self.scenario_gen.generate_scenario_2_different_ip_same_attacker(),
            self.scenario_gen.generate_scenario_3_concurrent_attackers(),
            self.scenario_gen.generate_scenario_4_missing_event(),
            self.scenario_gen.generate_scenario_5_duplicate_events(),
            self.scenario_gen.generate_scenario_6_out_of_order()
        ]

        evaluated_scenarios = []
        for sc in scenarios:
            res = self.evaluate_scenario(sc)
            evaluated_scenarios.append(res)

        summary = {
            "benchmark": "NEGATIVE_CONTROLS_EVALUATION",
            "total_scenarios": len(evaluated_scenarios),
            "results": evaluated_scenarios
        }

        # Export results
        out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "results"))
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, "negative_controls_summary.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        return summary

def main():
    bench = NegativeControlsBenchmark(seed=42)
    summary = bench.run_all_negative_controls()

    print("\n" + "="*95)
    print("               EMPIRICAL NEGATIVE CONTROLS BENCHMARK REPORT")
    print("="*95)
    print(f"{'Scenario Name':<35} | {'IP Baseline F1 (Contam)':<25} | {'Proposed Multi-Tier F1 (Contam)':<30}")
    print("-" * 95)
    for s in summary["results"]:
        sc_name = s["scenario"]
        ip = s["ip_only_baseline"]
        prop = s["proposed_multi_tier"]
        ip_str = f"{ip['f1_score']:.4f} (Contam: {ip['cross_attacker_contamination']})"
        prop_str = f"{prop['f1_score']:.4f} (Contam: {prop['cross_attacker_contamination']})"
        print(f"{sc_name:<35} | {ip_str:<25} | {prop_str:<30}")
    print("="*95 + "\n")
    print(f"[+] Empirical negative controls summary saved to: results/negative_controls_summary.json")

if __name__ == "__main__":
    main()
