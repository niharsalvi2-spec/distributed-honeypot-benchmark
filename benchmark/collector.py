"""
Benchmark Telemetry & Log Collector.
Coordinates retrieval, hashing, integrity verification, and staging of raw logs
from distributed honeypot execution nodes (Native and Docker).
"""
import os
import shutil
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime
from collectors.validation.integrity_manager import IntegrityManager

class BenchmarkCollector:
    """
    Coordinates log extraction from active honeypot nodes and stages them
    into the immutable data/raw/<repo>/<run_id>/ pipeline.
    """
    def __init__(self, base_raw_dir: str = "data/raw"):
        self.base_raw_dir = base_raw_dir
        self.integrity_mgr = IntegrityManager()

    def stage_node_logs(self, repository: str, run_id: str, node_id: str, source_log_path: str) -> Dict[str, Any]:
        """
        Transfers raw log file from a node's local output directory into the
        experiment's run staging area, computing SHA-256 and registering lineage.
        """
        target_dir = os.path.join(self.base_raw_dir, repository, run_id)
        os.makedirs(target_dir, exist_ok=True)
        
        target_filename = f"{node_id}_{os.path.basename(source_log_path)}"
        target_path = os.path.join(target_dir, target_filename)

        if os.path.exists(source_log_path):
            shutil.copy2(source_log_path, target_path)
            file_hash = self._compute_sha256(target_path)
            file_size = os.path.getsize(target_path)
        else:
            # Create an initialized raw telemetry stream file if node emitted asynchronously
            with open(target_path, "w", encoding="utf-8") as f:
                f.write("")
            file_hash = self._compute_sha256(target_path)
            file_size = 0

        # Update SHA-256 integrity manifest
        manifest_path = os.path.join(target_dir, "manifest.sha256")
        with open(manifest_path, "a", encoding="utf-8") as mf:
            mf.write(f"{file_hash}  {target_filename}\n")

        return {
            "repository": repository,
            "run_id": run_id,
            "node_id": node_id,
            "staged_path": target_path,
            "sha256": file_hash,
            "size_bytes": file_size,
            "staged_at": datetime.utcnow().isoformat() + "Z"
        }

    def collect_all_nodes(self, repository: str, run_id: str, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for n in nodes:
            res = self.stage_node_logs(
                repository=repository,
                run_id=run_id,
                node_id=n.get("node_id", "node_default"),
                source_log_path=n.get("log_path", "")
            )
            results.append(res)
        return results

    @staticmethod
    def _compute_sha256(filepath: str) -> str:
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()

# Backward compatibility alias
Collector = BenchmarkCollector
