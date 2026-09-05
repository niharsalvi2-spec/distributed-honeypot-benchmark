"""
Run ID & Experiment Lifecycle Manager.
Enforces unique run_id generation (<experiment_id>_<YYYYMMDD>_<seq>)
and provisions the complete immutable data lifecycle hierarchy.
"""
import os
import glob
import json
import shutil
import platform
from datetime import datetime
from typing import Dict, Any, Optional
import yaml
from collectors.validation.integrity_manager import DataIntegrityManager

class RunManager:
    def __init__(self, root_dir: str):
        self.root = root_dir
        self.data_dir = os.path.join(root_dir, "data")
        self.results_dir = os.path.join(root_dir, "results")
        self.configs_dir = os.path.join(root_dir, "configs")
        self.artifacts_dir = os.path.join(root_dir, "artifacts")

    def generate_run_id(self, experiment_id: str) -> str:
        """
        Produces unique Run ID: E05_YYYYMMDD_001
        """
        date_str = datetime.utcnow().strftime("%Y%m%d")
        prefix = f"{experiment_id}_{date_str}_"
        existing = glob.glob(os.path.join(self.data_dir, "raw", f"{prefix}*"))
        max_seq = 0
        for p in existing:
            base = os.path.basename(p)
            try:
                seq = int(base.split("_")[-1])
                if seq > max_seq:
                    max_seq = seq
            except Exception:
                pass
        return f"{prefix}{max_seq + 1:03d}"

    def initialize_run(self, experiment_id: str, execution_mode: str = "native") -> Dict[str, str]:
        """
        Initializes the entire directory lifecycle for a new experiment run.
        """
        run_id = self.generate_run_id(experiment_id)
        paths = {
            "run_id": run_id,
            "raw": os.path.join(self.data_dir, "raw", run_id),
            "raw_dir": os.path.join(self.data_dir, "raw", run_id),
            "normalized": os.path.join(self.data_dir, "normalized", run_id),
            "normalized_dir": os.path.join(self.data_dir, "normalized", run_id),
            "ordering": os.path.join(self.data_dir, "processed", "ordering", run_id),
            "correlation": os.path.join(self.data_dir, "processed", "correlation", run_id),
            "sequences": os.path.join(self.data_dir, "processed", "sequences", run_id),
            "results": os.path.join(self.results_dir, run_id),
            "results_dir": os.path.join(self.results_dir, run_id)
        }

        for k, p in paths.items():
            if k != "run_id":
                os.makedirs(p, exist_ok=True)

        # Populate reproducible run manifests in results/<run_id>/
        meta = {
            "run_id": run_id,
            "experiment_id": experiment_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "execution_mode": execution_mode
        }
        with open(os.path.join(paths["results"], "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        env_info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "machine": platform.machine(),
            "execution_mode": execution_mode
        }
        with open(os.path.join(paths["results"], "environment.json"), "w", encoding="utf-8") as f:
            json.dump(env_info, f, indent=2)

        # Copy experiment configuration
        exp_cfg_file = os.path.join(self.configs_dir, "experiments", f"{experiment_id}.yaml")
        if os.path.exists(exp_cfg_file):
            shutil.copy2(exp_cfg_file, os.path.join(paths["results"], "configuration.yaml"))

        # Snapshot active repository versions
        repo_versions = {}
        for r_meta in glob.glob(os.path.join(self.artifacts_dir, "repository_metadata", "*.json")):
            with open(r_meta, "r", encoding="utf-8") as f:
                r_json = json.load(f)
                repo_versions[r_json.get("name", "unknown")] = r_json.get("latest_commit_hash", "HEAD")
        with open(os.path.join(paths["results"], "repository_versions.json"), "w", encoding="utf-8") as f:
            json.dump(repo_versions, f, indent=2)

        # Initialize workload manifest and placeholder metrics
        with open(os.path.join(paths["results"], "workload.json"), "w", encoding="utf-8") as f:
            json.dump({"experiment": experiment_id, "status": "INITIALIZED"}, f, indent=2)

        with open(os.path.join(paths["results"], "metrics.json"), "w", encoding="utf-8") as f:
            json.dump({"status": "RUNNING"}, f, indent=2)

        return paths

    def finalize_run(self, run_id: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Freezes raw data, verifies SHA-256 manifest, updates metrics, and saves experiment manifest.
        """
        raw_dir = os.path.join(self.data_dir, "raw", run_id)
        results_dir = os.path.join(self.results_dir, run_id)

        # 1. Generate immutable raw SHA-256 manifest
        raw_manifest = DataIntegrityManager.generate_raw_manifest(run_id, raw_dir, self.root)

        # 2. Update final metrics in results/<run_id>/metrics.json and results/<run_id>/metrics/summary.json
        metrics["run_id"] = run_id
        metrics["finalized_timestamp"] = datetime.utcnow().isoformat() + "Z"
        with open(os.path.join(results_dir, "metrics.json"), "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        metrics_sub_dir = os.path.join(results_dir, "metrics")
        os.makedirs(metrics_sub_dir, exist_ok=True)
        with open(os.path.join(metrics_sub_dir, "summary.json"), "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        # 3. Create predictions directory and predictions.json
        preds_sub_dir = os.path.join(results_dir, "predictions")
        os.makedirs(preds_sub_dir, exist_ok=True)
        preds_data = {
            "run_id": run_id,
            "experiment_id": run_id.split("_")[0],
            "predictions_count": metrics.get("total_events_analyzed", metrics.get("total_nodes_correlated", 0)),
            "summary": metrics
        }
        with open(os.path.join(preds_sub_dir, "predictions.json"), "w", encoding="utf-8") as f:
            json.dump(preds_data, f, indent=2)

        # 4. Create report directory and summary markdown
        report_sub_dir = os.path.join(results_dir, "report")
        os.makedirs(report_sub_dir, exist_ok=True)
        report_md = f"""# Experiment Run Report: {run_id}

- **Experiment ID**: {run_id.split('_')[0]}
- **Finalized Timestamp**: {metrics['finalized_timestamp']}
- **Status**: FINALIZED

## Key Metrics Summary
```json
{json.dumps(metrics, indent=2)}
```
"""
        with open(os.path.join(report_sub_dir, "summary.md"), "w", encoding="utf-8") as f:
            f.write(report_md)

        # Ensure repositories.json exists in results_dir
        repo_ver_file = os.path.join(results_dir, "repository_versions.json")
        repo_file = os.path.join(results_dir, "repositories.json")
        if os.path.exists(repo_ver_file) and not os.path.exists(repo_file):
            shutil.copy2(repo_ver_file, repo_file)

        with open(os.path.join(results_dir, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump({"run_id": run_id, "metrics": metrics, "status": "FINALIZED"}, f, indent=2)

        # 5. Create top-level official experiment manifest
        exp_id = run_id.split("_")[0]

        # Read persisted execution_mode from metadata.json
        exec_mode = "native"
        meta_file = os.path.join(results_dir, "metadata.json")
        if os.path.exists(meta_file):
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    m_data = json.load(f)
                    exec_mode = m_data.get("execution_mode", "native")
            except Exception:
                exec_mode = "native"

        # Read node_count from configuration.yaml if present
        nodes_count = 3
        cfg_file = os.path.join(results_dir, "configuration.yaml")
        if not os.path.exists(cfg_file):
            cfg_file = os.path.join(self.configs_dir, "experiments", f"{exp_id}.yaml")
        if os.path.exists(cfg_file):
            try:
                with open(cfg_file, "r", encoding="utf-8") as f:
                    cfg_data = yaml.safe_load(f) or {}
                    nodes_count = cfg_data.get("environment", {}).get("node_count") or cfg_data.get("nodes_count", 3)
            except Exception:
                nodes_count = 3

        DataIntegrityManager.create_experiment_manifest(
            run_id=run_id,
            experiment_id=exp_id,
            execution_mode=exec_mode,
            repositories=raw_manifest.get("repositories", {}),
            nodes_count=nodes_count,
            config_path=f"configs/experiments/{exp_id}.yaml",
            workload_path=f"workloads/controlled_attack/{exp_id}",
            clock_config={"physical": True, "lamport": True, "vector": True},
            raw_checksum_digest=raw_manifest["files"][0]["sha256"] if raw_manifest.get("files") else "EMPTY_RAW",
            artifacts_root=self.root
        )

        return metrics
