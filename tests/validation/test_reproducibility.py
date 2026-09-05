"""
Validation Test: RunManager Lineage & Reproducibility
Tests run ID generation, isolation of run directories, and manifest persistence.
"""
import os
import pytest
from benchmark.run_manager import RunManager

def test_run_manager_isolation(tmp_path):
    manager = RunManager(str(tmp_path))
    paths1 = manager.initialize_run("E01")
    paths2 = manager.initialize_run("E01")

    assert paths1["run_id"] != paths2["run_id"]
    assert os.path.exists(paths1["raw_dir"])
    assert os.path.exists(paths1["normalized_dir"])
    assert os.path.exists(paths1["results_dir"])

    manager.finalize_run(paths1["run_id"], {"test_metric": 0.99})
    manifest_path = os.path.join(paths1["results_dir"], "manifest.json")
    assert os.path.exists(manifest_path)
