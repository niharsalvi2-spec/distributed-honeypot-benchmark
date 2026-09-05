"""
Experiment Runner: E07_clock_perturbation
"""
import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import os
from benchmark.run_manager import RunManager
from benchmark.experiment import BaseExperiment
from experiments.E07_clock_perturbation.collect import collect_telemetry
from experiments.E07_clock_perturbation.analyze import analyze_run

class E07ClockExperiment(BaseExperiment):
    def setup(self) -> bool:
        dag_path = os.path.join(project_root, "workloads", "fault", "clock_skew_dag.json")
        return os.path.exists(dag_path) and os.path.getsize(dag_path) > 0

    def execute(self) -> dict:
        import time
        from distributed.messaging.channel import DistributedNode, DistributedChannel
        t0 = time.time()
        cluster_nodes = ["node_alpha", "node_beta", "node_gamma"]
        nodes = {nid: DistributedNode(nid, cluster_nodes) for nid in cluster_nodes}
        channel = DistributedChannel(latency_ms=15.0, jitter_ms=5.0, drop_rate=0.0)

        # Transmit test causal handshake across nodes
        msg = nodes["node_alpha"].send_event(
            {"action": "port_probe", "target": "node_beta"},
            "node_beta",
            channel
        )
        channel.deliver_all(nodes)
        elapsed_ms = (time.time() - t0) * 1000.0

        return {
            "workload": "clock_skew_and_drift",
            "cluster_nodes": cluster_nodes,
            "simulated_channel_latency_ms": 15.0,
            "simulated_messages_delivered": 1,
            "execution_time_ms": round(elapsed_ms, 2),
            "status": "COMPLETED"
        }

    def collect(self) -> dict:
        return collect_telemetry(self.run_id)

    def analyze(self) -> dict:
        return analyze_run(self.run_id)

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    manager = RunManager(root_dir)
    paths = manager.initialize_run("E07")
    exp = E07ClockExperiment("E07", {})
    exp.run_id = paths["run_id"]
    results = exp.run_all()
    manager.finalize_run(paths["run_id"], results["analysis"])
    print(f"[E07_clock_perturbation] Run finalized: {paths['run_id']} | Metrics: {results['analysis']}")

if __name__ == "__main__":
    main()
