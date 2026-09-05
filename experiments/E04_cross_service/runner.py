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
        return True

    def execute(self) -> dict:
        return {"workload": "cross_service_pivoting", "status": "COMPLETED"}

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
