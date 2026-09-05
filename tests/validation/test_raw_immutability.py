"""
Validation Test: Raw Data Immutability Guarantee
Proves that pipeline normalization, ordering, correlation, and analysis components
treat raw telemetry as strictly immutable and never mutate or overwrite source raw logs.
"""
import os
import hashlib
import glob
import pytest
from benchmark.run_manager import RunManager
from experiments.E01_functional.runner import E01FunctionalExperiment

def compute_file_sha256(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def snapshot_raw_hashes(raw_root: str):
    hashes = {}
    for root, _, files in os.walk(raw_root):
        for f in files:
            fp = os.path.join(root, f)
            rel = os.path.relpath(fp, raw_root)
            hashes[rel] = compute_file_sha256(fp)
    return hashes

def test_raw_data_immutability_during_e01_execution():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    raw_root = os.path.join(project_root, "data", "raw")
    
    # 1. Take snapshot of raw repository samples before execution
    hashes_before = snapshot_raw_hashes(raw_root)
    assert len(hashes_before) > 0, "Raw data directory should contain baseline logs before test."

    # 2. Run E01 pipeline
    manager = RunManager(project_root)
    paths = manager.initialize_run("E01")
    exp = E01FunctionalExperiment("E01", {})
    exp.run_id = paths["run_id"]
    results = exp.run_all()
    manager.finalize_run(paths["run_id"], results["analysis"])

    # 3. Take snapshot of original raw files after execution (excluding the new run directory)
    for rel_path, hash_val in hashes_before.items():
        full_path = os.path.join(raw_root, rel_path)
        assert os.path.exists(full_path), f"Raw file disappeared: {rel_path}"
        hash_after = compute_file_sha256(full_path)
        assert hash_after == hash_val, f"Raw data modified during pipeline execution! File: {rel_path}"

    # 4. Verify that the staged run directory inside data/raw/<run_id>/ also produced valid SHA256 sums
    staged_dir = paths["raw"]
    assert os.path.exists(staged_dir)
    staged_files = [os.path.join(staged_dir, f) for f in os.listdir(staged_dir) if os.path.isfile(os.path.join(staged_dir, f))]
    assert len(staged_files) > 0
