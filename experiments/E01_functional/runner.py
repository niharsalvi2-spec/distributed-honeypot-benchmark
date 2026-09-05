"""
Experiment Runner: E01_functional
"""
import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import os
from benchmark.run_manager import RunManager
from benchmark.experiment import BaseExperiment
from experiments.E01_functional.collect import collect_telemetry
from experiments.E01_functional.analyze import analyze_run

class E01FunctionalExperiment(BaseExperiment):
    def setup(self) -> bool:
        repos = ["cowrie", "opencanary", "dionaea", "tpot", "mhn", "conpot", "honeytrap"]
        for r in repos:
            p = os.path.join(project_root, "data", "raw", r, "run_001")
            if not os.path.exists(p):
                return False
        return True

    def execute(self) -> dict:
        import time
        t0 = time.time()
        repos = ["cowrie", "opencanary", "dionaea", "tpot", "mhn", "conpot", "honeytrap"]
        total_raw_bytes = 0
        file_count = 0
        for r in repos:
            p = os.path.join(project_root, "data", "raw", r, "run_001")
            if os.path.exists(p):
                for f in os.listdir(p):
                    fp = os.path.join(p, f)
                    if os.path.isfile(fp):
                        total_raw_bytes += os.path.getsize(fp)
                        file_count += 1
        duration_ms = (time.time() - t0) * 1000.0
        return {
            "workload": "multi_repository_functional_ingestion",
            "repositories_verified": len(repos),
            "staged_file_count": file_count,
            "raw_payload_bytes": total_raw_bytes,
            "ingestion_duration_ms": round(duration_ms, 2),
            "status": "COMPLETED"
        }

    def collect(self) -> dict:
        return collect_telemetry(self.run_id)

    def analyze(self) -> dict:
        return analyze_run(self.run_id)

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    manager = RunManager(root_dir)
    paths = manager.initialize_run("E01")
    exp = E01FunctionalExperiment("E01", {})
    exp.run_id = paths["run_id"]
    results = exp.run_all()
    manager.finalize_run(paths["run_id"], results["analysis"])
    print(f"[E01_functional] Run finalized: {paths['run_id']} | Metrics: {results['analysis']}")

if __name__ == "__main__":
    main()
