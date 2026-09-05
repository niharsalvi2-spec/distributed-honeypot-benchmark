"""
Data Integrity & Chain-of-Custody Manager.
Enforces the immutable raw-data invariant via SHA-256 cryptographic manifests.
Halts with DataIntegrityError if any raw telemetry is modified.
"""
import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List

class DataIntegrityError(Exception):
    """Raised when SHA-256 validation of raw or normalized data fails."""
    pass

class DataIntegrityManager:
    @staticmethod
    def compute_sha256(filepath: str) -> str:
        """Computes SHA-256 digest of a file in 64KB blocks."""
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    @classmethod
    def generate_raw_manifest(cls, run_id: str, raw_dir: str, artifacts_root: str) -> Dict[str, Any]:
        """
        Calculates SHA-256 for every file in raw_dir and produces an immutable manifest.
        Stores in raw_dir/raw_manifest.json and artifacts/checksums/<run_id>.json.
        """
        files_manifest = []
        for root, _, files in os.walk(raw_dir):
            for fname in files:
                if fname in ["raw_manifest.json", "lineage_manifest.json"]:
                    continue
                full_path = os.path.join(root, fname)
                rel_path = os.path.relpath(full_path, raw_dir)
                digest = cls.compute_sha256(full_path)
                size_bytes = os.path.getsize(full_path)
                files_manifest.append({
                    "path": rel_path.replace("\\", "/"),
                    "sha256": digest,
                    "size_bytes": size_bytes
                })

        manifest = {
            "run_id": run_id,
            "pipeline_stage": "RAW_IMMUTABLE",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_files": len(files_manifest),
            "files": sorted(files_manifest, key=lambda x: x["path"])
        }

        # Write inside raw_dir
        raw_manifest_path = os.path.join(raw_dir, "raw_manifest.json")
        with open(raw_manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        # Write to persistent artifacts/checksums/
        checksums_dir = os.path.join(artifacts_root, "artifacts", "checksums")
        os.makedirs(checksums_dir, exist_ok=True)
        artifact_checksum_path = os.path.join(checksums_dir, f"{run_id}.sha256.json")
        with open(artifact_checksum_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        return manifest

    @classmethod
    def verify_raw_integrity(cls, run_id: str, raw_dir: str) -> bool:
        """
        Verifies every raw file against raw_manifest.json.
        Raises DataIntegrityError on any mismatch.
        """
        raw_manifest_path = os.path.join(raw_dir, "raw_manifest.json")
        if not os.path.exists(raw_manifest_path):
            raise DataIntegrityError(f"Missing raw manifest in {raw_dir} for run {run_id}")

        with open(raw_manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        for entry in manifest.get("files", []):
            rel_path = entry["path"]
            expected_sha = entry["sha256"]
            actual_path = os.path.join(raw_dir, rel_path.replace("/", os.sep))

            if not os.path.exists(actual_path):
                raise DataIntegrityError(f"DATA INTEGRITY FAILURE: Raw file deleted: {actual_path}")

            actual_sha = cls.compute_sha256(actual_path)
            if actual_sha != expected_sha:
                raise DataIntegrityError(
                    f"DATA INTEGRITY FAILURE: Raw file modified! Path: {rel_path}. "
                    f"Expected {expected_sha}, found {actual_sha}"
                )

        return True

    @classmethod
    def create_experiment_manifest(cls, run_id: str, experiment_id: str, execution_mode: str,
                                   repositories: Dict[str, str], nodes_count: int,
                                   config_path: str, workload_path: str,
                                   clock_config: Dict[str, bool], raw_checksum_digest: str,
                                   artifacts_root: str) -> Dict[str, Any]:
        """
        Constructs and records the official experiment manifest under artifacts/experiment_manifests/.
        """
        manifest = {
            "run_id": run_id,
            "experiment": experiment_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "execution_mode": execution_mode,
            "repositories": repositories,
            "nodes": nodes_count,
            "configuration": config_path,
            "workload": workload_path,
            "clock_configuration": clock_config,
            "raw_data": {
                "sha256_root": raw_checksum_digest
            }
        }

        manifest_dir = os.path.join(artifacts_root, "artifacts", "experiment_manifests")
        os.makedirs(manifest_dir, exist_ok=True)
        out_path = os.path.join(manifest_dir, f"{run_id}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        return manifest

# Backward compatibility alias
IntegrityManager = DataIntegrityManager
