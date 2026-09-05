"""
Statistical Validation & 30-Trial Monte Carlo Evaluation Engine
Executes repeated independent trials with randomized network jitter, clock perturbation,
and variable noise injection to produce publication-grade statistical confidence intervals:
- Sample Size n = 30
- Mean, Median, Std, Variance, Min, Max
- 95% Confidence Interval (CI_95)
"""
import os
import json
import math
import random
from typing import List, Dict, Any
from ground_truth.oracle import BenchmarkOracle
from analysis.feature_ablation.ablation_runner import (
    AlgorithmicCorrelationEngine,
    generate_unannotated_canonical_telemetry
)

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

    def run_trials(self) -> Dict[str, Any]:
        precision_list = []
        recall_list = []
        f1_list = []
        contamination_list = []
        trial_records = []

        base_telemetry = generate_unannotated_canonical_telemetry()

        for t_idx in range(1, self.trials_count + 1):
            seed = self.base_seed + t_idx
            random.seed(seed)

            # Perturb timestamps with randomized network jitter [-50ms, +150ms]
            perturbed_events = []
            for ev in base_telemetry:
                ev_copy = dict(ev)
                jitter_sec = random.uniform(-0.05, 0.15)
                ev_copy["timestamp"] = ev["timestamp"] + jitter_sec
                perturbed_events.append(ev_copy)

            # Add randomized benign background scan noise (1 to 4 extra noise events)
            extra_noise_count = random.randint(1, 4)
            for n_idx in range(extra_noise_count):
                perturbed_events.append({
                    "event_id": f"evt-rand-noise-{t_idx}-{n_idx}",
                    "timestamp": 1700000000.0 + random.uniform(0, 300),
                    "source_ip": f"198.18.{random.randint(10, 50)}.{random.randint(1, 250)}",
                    "target_node": random.choice(["node-1", "node-2"]),
                    "service": random.choice(["HTTP", "SSH", "NTP"]),
                    "event_type": "noise_probe",
                    "payload": "RANDOM_PROBE /test",
                    "causal_token": None
                })

            # Execute algorithmic correlation
            predicted_clusters = AlgorithmicCorrelationEngine.run_full_multi_tier(perturbed_events)

            # Evaluate against independent Oracle
            metrics = self.oracle.evaluate_correlation(predicted_clusters, only_attack_clusters=True)

            precision_list.append(metrics["precision"])
            recall_list.append(metrics["recall"])
            f1_list.append(metrics["f1_score"])
            contamination_list.append(metrics["cross_attacker_contamination_count"])

            trial_records.append({
                "trial": t_idx,
                "seed": seed,
                "noise_count": extra_noise_count,
                "precision": metrics["precision"],
                "recall": metrics["recall"],
                "f1_score": metrics["f1_score"],
                "contamination": metrics["cross_attacker_contamination_count"]
            })

        summary = {
            "experiment_id": "E05_STATISTICAL_TRIALS",
            "total_trials": self.trials_count,
            "base_seed": self.base_seed,
            "metrics": {
                "precision": compute_statistics(precision_list),
                "recall": compute_statistics(recall_list),
                "f1_score": compute_statistics(f1_list),
                "contamination": compute_statistics(contamination_list)
            },
            "trials_summary": trial_records[:5]  # Sample first 5
        }

        return summary

def main():
    runner = StatisticalTrialRunner(trials_count=30)
    summary = runner.run_trials()

    print("\n" + "="*85)
    print(f"      30-TRIAL STATISTICAL EVALUATION REPORT (SEED 42001 - 42030)")
    print("="*85)
    print(f"{'Metric':<16} | {'Mean':<8} | {'Median':<8} | {'Std':<8} | {'95% Confidence Interval':<24}")
    print("-" * 85)
    for m_name in ["precision", "recall", "f1_score", "contamination"]:
        s = summary["metrics"][m_name]
        print(f"{m_name.upper():<16} | {s['mean']:<8.4f} | {s['median']:<8.4f} | {s['std']:<8.4f} | {s['ci_95_display']:<24}")
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
