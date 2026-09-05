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
        sched_file = os.path.join(os.path.dirname(__file__), "failure_schedule.yaml")
        return os.path.exists(sched_file) and os.path.getsize(sched_file) > 0

    def execute(self) -> dict:
        import time, yaml
        t0 = time.time()
        sched_file = os.path.join(os.path.dirname(__file__), "failure_schedule.yaml")
        with open(sched_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        spool_cfg = data.get("spool_configuration", {})
        elapsed_ms = (time.time() - t0) * 1000.0
        return {
            "workload": "collector_downtime_spooling",
            "schedule_file": os.path.relpath(sched_file, project_root),
            "max_spool_capacity": spool_cfg.get("max_spool_events", 1000),
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
    paths = manager.initialize_run("E09")
    exp = E09CollectorFailureExperiment("E09", {})
    exp.run_id = paths["run_id"]
    results = exp.run_all()
    manager.finalize_run(paths["run_id"], results["analysis"])
    print(f"[E09_collector_failure] Run finalized: {paths['run_id']} | Metrics: {results['analysis']}")

if __name__ == "__main__":
    main()
