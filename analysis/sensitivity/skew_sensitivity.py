"""
Clock Skew Sensitivity Analysis
Sweeps physical clock drift (0ms to 5000ms) to measure the breakdown point of physical timestamp ordering
compared to logical Lamport ordering and vector clock concurrency.
"""
import os
import json
import random
from typing import Dict, Any, List
from distributed.clocks.clock_comparator import ClockComparator
from distributed.clocks.lamport_clock import LamportClock
from sequence_reconstruction.sequence_validator import SequenceValidator

class ClockSkewSensitivity:
    def __init__(self, num_events: int = 20, seed: int = 42):
        self.num_events = num_events
        self.seed = seed
        self.rng = random.Random(seed)

    def sweep_skew(self, skew_levels_ms: List[float] = None) -> List[Dict[str, Any]]:
        levels = skew_levels_ms or [0.0, 100.0, 500.0, 1000.0, 2000.0, 5000.0]
        nodes = ["node_alpha", "node_beta", "node_gamma"]
        results = []

        base_t = 1700000000.0

        for skew_ms in levels:
            skew_sec = skew_ms / 1000.0
            # Assign random drift within [-skew_sec, +skew_sec] for each node
            node_drifts = {
                nid: self.rng.uniform(-skew_sec, skew_sec) if skew_sec > 0 else 0.0
                for nid in nodes
            }

            # Generate synthetic causal event sequence
            events = []
            lamport = LamportClock()
            for idx in range(self.num_events):
                nid = nodes[idx % len(nodes)]
                real_ts = base_t + (idx * 0.5)  # 500ms separation
                phys_ts = real_ts + node_drifts[nid]
                lamp_ts = lamport.tick()
                events.append({
                    "event_id": f"ev_{idx:03d}",
                    "real_timestamp": real_ts,
                    "physical_timestamp": phys_ts,
                    "lamport_timestamp": lamp_ts,
                    "node_id": nid
                })

            gt_order = [e["event_id"] for e in sorted(events, key=lambda x: x["real_timestamp"])]

            # 1. Physical ordering under drift
            phys_order = [e["event_id"] for e in sorted(events, key=lambda x: x["physical_timestamp"])]
            phys_inv, phys_inv_rate = ClockComparator.compute_inversions(gt_order, phys_order)
            phys_tau = ClockComparator.compute_kendall_tau(gt_order, phys_order)
            phys_sra = SequenceValidator.compute_sra(gt_order, phys_order)

            # 2. Logical Lamport ordering
            lamp_order = [e["event_id"] for e in sorted(events, key=lambda x: (x["lamport_timestamp"], x["node_id"]))]
            lamp_inv, lamp_inv_rate = ClockComparator.compute_inversions(gt_order, lamp_order)
            lamp_tau = ClockComparator.compute_kendall_tau(gt_order, lamp_order)
            lamp_sra = SequenceValidator.compute_sra(gt_order, lamp_order)

            results.append({
                "skew_drift_ms": skew_ms,
                "physical_inversion_rate": round(phys_inv_rate, 4),
                "physical_kendall_tau": round(phys_tau, 4),
                "physical_sra": round(phys_sra, 4),
                "lamport_inversion_rate": round(lamp_inv_rate, 4),
                "lamport_kendall_tau": round(lamp_tau, 4),
                "lamport_sra": round(lamp_sra, 4)
            })

        return results

def run_skew_study():
    study = ClockSkewSensitivity()
    results = study.sweep_skew()

    print("\n" + "="*85)
    print("       DISTRIBUTED CLOCK SKEW SENSITIVITY STUDY (DRIFT SWEEP)")
    print("="*85)
    print(f"{'Skew (ms)':<10} | {'Phys Inversion':<15} | {'Phys Tau':<10} | {'Lamp Inversion':<15} | {'Lamp Tau':<10}")
    print("-" * 85)
    for r in results:
        print(f"{r['skew_drift_ms']:<10.0f} | {r['physical_inversion_rate']:<15.4f} | {r['physical_kendall_tau']:<10.4f} | {r['lamport_inversion_rate']:<15.4f} | {r['lamport_kendall_tau']:<10.4f}")
    print("="*85 + "\n")

    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "results"))
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "skew_sensitivity_summary.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({"skew_sweep": results}, f, indent=2)
    print(f"[+] Clock skew sensitivity exported to: {out_file}")

if __name__ == "__main__":
    run_skew_study()
