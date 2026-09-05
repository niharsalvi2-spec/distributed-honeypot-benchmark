"""
Experiment Runner: E04_cross_service
"""
import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import os
from benchmark.run_manager import RunManager
from benchmark.experiment import BaseExperiment
from experiments.E04_cross_service.collect import collect_telemetry
from experiments.E04_cross_service.analyze import analyze_run

class E04CrossServiceExperiment(BaseExperiment):
    def setup(self) -> bool:
        workload_file = os.path.join(project_root, "workloads", "controlled_attack", "cross_service", "http_to_ssh.yaml")
        return os.path.exists(workload_file) and os.path.getsize(workload_file) > 0

    def execute(self) -> dict:
        import time, yaml
        t0 = time.time()
        workload_file = os.path.join(project_root, "workloads", "controlled_attack", "cross_service", "http_to_ssh.yaml")
        with open(workload_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        stages = data.get("stages", [])
        elapsed_ms = (time.time() - t0) * 1000.0
        return {
            "workload": "cross_service_pivoting",
            "workload_file": os.path.relpath(workload_file, project_root),
            "attack_stages_count": len(stages),
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
    paths = manager.initialize_run("E04")
    exp = E04CrossServiceExperiment("E04", {})
    exp.run_id = paths["run_id"]
    results = exp.run_all()
    manager.finalize_run(paths["run_id"], results["analysis"])
    print(f"[E04_cross_service] Run finalized: {paths['run_id']} | Metrics: {results['analysis']}")

if __name__ == "__main__":
    main()
