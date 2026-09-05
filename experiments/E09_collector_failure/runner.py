"""
Experiment Runner: E09_collector_failure
"""
import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import os
from benchmark.run_manager import RunManager
from benchmark.experiment import BaseExperiment
from experiments.E09_collector_failure.collect import collect_telemetry
from experiments.E09_collector_failure.analyze import analyze_run

class E09CollectorFailureExperiment(BaseExperiment):
    def setup(self) -> bool:
        return True

    def execute(self) -> dict:
        return {"workload": "collector_downtime_spooling", "status": "COMPLETED"}

    def collect(self) -> dict:
        return collect_telemetry(self.run_id)

    def analyze(self) -> dict:
        return analyze_run(self.run_id)

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    manager = RunManager(root_dir)
    paths = manager.initialize_run("E09")
    exp = E09CollectorFailureExperiment("E09", {})
    exp.run_id = paths["run_id"]
    results = exp.run_all()
    manager.finalize_run(paths["run_id"], results["analysis"])
    print(f"[E09_collector_failure] Run finalized: {paths['run_id']} | Metrics: {results['analysis']}")

if __name__ == "__main__":
    main()
