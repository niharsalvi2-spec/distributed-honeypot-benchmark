"""
Unified Benchmark CLI Runner
Enables one-command execution of individual experiments (E01–E10) or the complete benchmark suite.
Usage:
    python -m benchmark.run E01
    python -m benchmark.run E05
    python -m benchmark.run ALL
"""
import sys
import os
import time
import argparse
import yaml
import importlib
from typing import Dict, Any, List

def get_registry_experiments(root_dir: str) -> Dict[str, Any]:
    reg_path = os.path.join(root_dir, "configs", "experiments", "experiment_registry.yaml")
    if not os.path.exists(reg_path):
        return {}
    with open(reg_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("experiments", {})

EXPERIMENT_RUNNER_MAP = {
    "E01": "experiments.E01_functional.runner",
    "E02": "experiments.E02_authentication.runner",
    "E03": "experiments.E03_session_capture.runner",
    "E04": "experiments.E04_cross_service.runner",
    "E05": "experiments.E05_cross_node.runner",
    "E06": "experiments.E06_interleaved_attackers.runner",
    "E07": "experiments.E07_clock_perturbation.runner",
    "E08": "experiments.E08_node_failure.runner",
    "E09": "experiments.E09_collector_failure.runner",
    "E10": "experiments.E10_scalability.runner",
}

def execute_experiment(exp_id: str, root_dir: str) -> bool:
    print(f"\n=================================================================")
    print(f"  EXECUTING BENCHMARK: {exp_id}")
    print(f"=================================================================")
    runner_module_name = EXPERIMENT_RUNNER_MAP.get(exp_id)
    if not runner_module_name:
        print(f"[-] Unknown experiment ID: {exp_id}")
        return False

    t0 = time.time()
    try:
        mod = importlib.import_module(runner_module_name)
        if hasattr(mod, "main"):
            mod.main()
        else:
            print(f"[-] Runner module {runner_module_name} has no main() entrypoint.")
            return False
        elapsed = time.time() - t0
        print(f"[+] {exp_id} completed successfully in {elapsed:.2f}s")
        return True
    except Exception as ex:
        print(f"[-] Error executing {exp_id}: {ex}")
        import traceback
        traceback.print_exc()
        return False

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

    parser = argparse.ArgumentParser(description="Distributed Honeypot Benchmark Master Runner")
    parser.add_argument("experiment", nargs="?", default="E01",
                        help="Experiment ID to execute (E01-E10) or ALL")
    parser.add_argument("--config", type=str, default=None, help="Custom configuration YAML path")
    parser.add_argument("--mode", type=str, default="native", choices=["native", "docker"],
                        help="Execution mode (default: native)")

    args = parser.parse_args()
    target = args.experiment.upper()

    if target == "ALL":
        targets = [f"E{i:02d}" for i in range(1, 11)]
    else:
        targets = [target]

    successes = 0
    failures = 0

    print(f"Distributed Honeypot Benchmark Suite")
    print(f"Target(s): {', '.join(targets)} | Mode: {args.mode}")

    for t in targets:
        ok = execute_experiment(t, root_dir)
        if ok:
            successes += 1
        else:
            failures += 1

    print("\n-----------------------------------------------------------------")
    print(f"BENCHMARK EXECUTION SUMMARY")
    print(f"Total: {len(targets)} | Passed: {successes} | Failed: {failures}")
    print("-----------------------------------------------------------------")
    if failures > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
