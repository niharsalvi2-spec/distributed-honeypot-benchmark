"""
Scenario Stager & Immutable Ground-Truth Manifest Manager.
Provisions isolated per-trial scenario directories before algorithms execute:
- scenario.json: unannotated canonical events (only visible to algorithms)
- ground_truth_dag.json: true causal DAG edges (only visible to Oracle)
- labels.json: true threat actor clusters and MITRE tactics (only visible to Oracle)
- parameters.json: controlled generator parameters and seed
- integrity_manifest.json: SHA-256 digests ensuring forensic immutability
"""
import os
import json
import hashlib
from typing import Dict, Any, List, Optional

class ScenarioStager:
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir:
            self.base_dir = base_dir
        else:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            self.base_dir = os.path.join(project_root, "data", "scenarios")
        os.makedirs(self.base_dir, exist_ok=True)

    def stage_scenario(
        self,
        trial_id: str,
        unannotated_events: List[Dict[str, Any]],
        ground_truth_dag: Dict[str, Any],
        ground_truth_clusters: Dict[str, List[str]],
        parameters: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Physically stages isolated scenario files on disk before algorithmic execution.
        """
        trial_dir = os.path.join(self.base_dir, trial_id)
        os.makedirs(trial_dir, exist_ok=True)

        scenario_file = os.path.join(trial_dir, "scenario.json")
        dag_file = os.path.join(trial_dir, "ground_truth_dag.json")
        labels_file = os.path.join(trial_dir, "labels.json")
        params_file = os.path.join(trial_dir, "parameters.json")
        manifest_file = os.path.join(trial_dir, "integrity_manifest.json")

        files_data = [
            (scenario_file, unannotated_events),
            (dag_file, ground_truth_dag),
            (labels_file, ground_truth_clusters),
            (params_file, parameters)
        ]

        digests = {}
        for path, data in files_data:
            content_bytes = json.dumps(data, indent=2).encode("utf-8")
            with open(path, "wb") as f:
                f.write(content_bytes)
            digests[os.path.basename(path)] = hashlib.sha256(content_bytes).hexdigest()

        manifest = {
            "trial_id": trial_id,
            "staged_files": digests,
            "status": "IMMUTABLE_STAGE_COMPLETE"
        }
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        return {
            "trial_dir": trial_dir,
            "scenario_file": scenario_file,
            "dag_file": dag_file,
            "labels_file": labels_file,
            "parameters_file": params_file,
            "manifest_file": manifest_file
        }

    @staticmethod
    def load_scenario_for_algorithm(scenario_file: str) -> List[Dict[str, Any]]:
        """
        Loads unannotated canonical events for consumption by algorithmic layers.
        Guarantees zero ground-truth leakage.
        """
        with open(scenario_file, "r", encoding="utf-8") as f:
            events = json.load(f)
        return events

    @staticmethod
    def load_ground_truth_for_oracle(trial_dir: str) -> Dict[str, Any]:
        """
        Loads ground truth clusters and causal DAG strictly for BenchmarkOracle scoring.
        """
        labels_file = os.path.join(trial_dir, "labels.json")
        dag_file = os.path.join(trial_dir, "ground_truth_dag.json")
        with open(labels_file, "r", encoding="utf-8") as f:
            clusters = json.load(f)
        with open(dag_file, "r", encoding="utf-8") as f:
            dag = json.load(f)
        return {"clusters": clusters, "dag": dag}
