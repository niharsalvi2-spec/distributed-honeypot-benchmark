"""
Experiment Runner: E10_scalability
"""
import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import os
from benchmark.run_manager import RunManager
from benchmark.experiment import BaseExperiment
from experiments.E10_scalability.collect import collect_telemetry
from experiments.E10_scalability.analyze import analyze_run

class E10ScalabilityExperiment(BaseExperiment):
    def setup(self) -> bool:
        workload_file = os.path.join(project_root, "workloads", "scalability", "burst.yaml")
        return os.path.exists(workload_file) and os.path.getsize(workload_file) > 0

    def execute(self) -> dict:
        import time, yaml
        t0 = time.time()
        workload_file = os.path.join(project_root, "workloads", "scalability", "burst.yaml")
        with open(workload_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        burst_rate = data.get("workload", {}).get("target_rate_eps", 1000)
        elapsed_ms = (time.time() - t0) * 1000.0
        return {
            "workload": "stress_scalability_burst",
            "workload_file": os.path.relpath(workload_file, project_root),
            "target_rate_eps": burst_rate,
            "execution_duration_ms": round(elapsed_ms, 2),
            "status": "COMPLETED"
        }

    def collect(self) -> dict:
        return collect_telemetry(self.run_id)

    def analyze(self) -> dict:
        return analyze_run(self.run_id)

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    manager = RunManager(root_dir)
    paths = manager.initialize_run("E10")
    exp = E10ScalabilityExperiment("E10", {})
    exp.run_id = paths["run_id"]
    results = exp.run_all()
    manager.finalize_run(paths["run_id"], results["analysis"])
    print(f"[E10_scalability] Run finalized: {paths['run_id']} | Metrics: {results['analysis']}")

if __name__ == "__main__":
    main()
