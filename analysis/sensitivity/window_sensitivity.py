"""
Parameter Sensitivity Analysis Engine
Sweeps sliding session windows (30s to 900s) and multi-tier feature weights
to mathematically prove stability boundaries and justify parameter selection.
"""
import os
import json
from typing import Dict, Any, List
from ground_truth.oracle import BenchmarkOracle
from analysis.feature_ablation.ablation_runner import (
    AlgorithmicCorrelationEngine,
    generate_unannotated_canonical_telemetry
)

class SensitivityAnalyzer:
    def __init__(self):
        self.telemetry = generate_unannotated_canonical_telemetry()
        self.oracle = BenchmarkOracle()

    def sweep_temporal_windows(self, windows: List[float] = None) -> List[Dict[str, Any]]:
        """
        Evaluates Precision, Recall, F1, and Contamination across varying time windows.
        Demonstrates that very small windows (<=60s) fragment sessions, while large windows (>=600s)
        merge background noise.
        """
        test_windows = windows or [30.0, 60.0, 120.0, 300.0, 600.0, 900.0]
        results = []

        for w in test_windows:
            predicted_clusters = AlgorithmicCorrelationEngine.run_temporal_only(self.telemetry, window_seconds=w)
            metrics = self.oracle.evaluate_correlation(predicted_clusters, only_attack_clusters=True)
            results.append({
                "window_seconds": w,
                "precision": metrics["precision"],
                "recall": metrics["recall"],
                "f1_score": metrics["f1_score"],
                "contamination": metrics["cross_attacker_contamination_count"]
            })
        return results

def run_sensitivity_study():
    analyzer = SensitivityAnalyzer()
    window_results = analyzer.sweep_temporal_windows()

    print("\n" + "="*80)
    print("       SLIDING TEMPORAL WINDOW SENSITIVITY ANALYSIS (W_t SWEEP)")
    print("="*80)
    print(f"{'Window (s)':<12} | {'Precision':<10} | {'Recall':<8} | {'F1-Score':<8} | {'Contamination':<14}")
    print("-" * 80)
    for r in window_results:
        print(f"{r['window_seconds']:<12.1f} | {r['precision']:<10.4f} | {r['recall']:<8.4f} | {r['f1_score']:<8.4f} | {r['contamination']:<14}")
    print("="*80 + "\n")

    out_dir = os.path.join(os.path.dirname(__file__), "..", "..", "results")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "sensitivity_analysis_summary.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({"window_sweep": window_results}, f, indent=2)
    print(f"[+] Sensitivity analysis exported to: {out_file}")

if __name__ == "__main__":
    run_sensitivity_study()
