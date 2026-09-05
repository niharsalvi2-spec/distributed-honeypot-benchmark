import os
import pytest
from benchmark.run_manager import RunManager

def test_run_manager_lifecycle(tmp_path):
    manager = RunManager(str(tmp_path))
    
    # 1. Generate run ID
    run_id = manager.generate_run_id("E05")
    assert run_id.startswith("E05_")
    assert run_id.endswith("_001")
    
    # 2. Initialize run hierarchy
    paths = manager.initialize_run("E05", execution_mode="native")
    assert os.path.exists(paths["raw"])
    assert os.path.exists(paths["normalized"])
    assert os.path.exists(paths["ordering"])
    assert os.path.exists(paths["correlation"])
    assert os.path.exists(paths["sequences"])
    assert os.path.exists(paths["results"])
    
    # Verify manifests created in results/
    assert os.path.exists(os.path.join(paths["results"], "metadata.json"))
    assert os.path.exists(os.path.join(paths["results"], "environment.json"))
    assert os.path.exists(os.path.join(paths["results"], "repository_versions.json"))
    
    # 3. Add a sample raw file and finalize
    raw_file = os.path.join(paths["raw"], "ssh_node_01.jsonl")
    with open(raw_file, "w") as f:
        f.write('{"event": "test"}\n')
        
    final_metrics = manager.finalize_run(run_id, {"accuracy": 0.95})
    assert final_metrics["accuracy"] == 0.95
    assert os.path.exists(os.path.join(paths["raw"], "raw_manifest.json"))
    assert os.path.exists(os.path.join(tmp_path, "artifacts", "experiment_manifests", f"{run_id}.json"))
