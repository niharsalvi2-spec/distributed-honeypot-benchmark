import os
import pytest
from collectors.validation.integrity_manager import DataIntegrityManager, DataIntegrityError

def test_data_integrity_and_manifest(tmp_path):
    raw_dir = tmp_path / "raw" / "E05_run_001"
    raw_dir.mkdir(parents=True)
    
    # Create sample raw log file
    log_file = raw_dir / "ssh_node_01.jsonl"
    log_file.write_text('{"event": "login", "user": "root"}\n', encoding="utf-8")
    
    # Generate manifest
    manifest = DataIntegrityManager.generate_raw_manifest(
        run_id="E05_run_001",
        raw_dir=str(raw_dir),
        artifacts_root=str(tmp_path)
    )
    assert manifest["run_id"] == "E05_run_001"
    assert len(manifest["files"]) == 1
    orig_sha = manifest["files"][0]["sha256"]
    
    # Verify integrity passes
    assert DataIntegrityManager.verify_raw_integrity("E05_run_001", str(raw_dir)) is True
    
    # Simulate tampering with raw log
    log_file.write_text('{"event": "login", "user": "MALICIOUS_TAMPER"}\n', encoding="utf-8")
    
    # Verification MUST fail with DataIntegrityError
    with pytest.raises(DataIntegrityError, match="DATA INTEGRITY FAILURE"):
        DataIntegrityManager.verify_raw_integrity("E05_run_001", str(raw_dir))

def test_experiment_manifest_creation(tmp_path):
    exp_manifest = DataIntegrityManager.create_experiment_manifest(
        run_id="E05_20260906_001",
        experiment_id="E05",
        execution_mode="native",
        repositories={"cowrie": "3e8f0682f483", "opencanary": "86f072541e3f"},
        nodes_count=3,
        config_path="configs/experiments/E05.yaml",
        workload_path="workloads/controlled_attack/campaign_A/",
        clock_config={"physical": True, "lamport": True, "vector": True},
        raw_checksum_digest="mock_sha256_root_digest",
        artifacts_root=str(tmp_path)
    )
    assert exp_manifest["run_id"] == "E05_20260906_001"
    assert exp_manifest["nodes"] == 3
    out_file = tmp_path / "artifacts" / "experiment_manifests" / "E05_20260906_001.json"
    assert out_file.exists()
