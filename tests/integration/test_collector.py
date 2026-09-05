"""
Integration Test: BenchmarkCollector
Tests end-to-end log harvesting, directory staging, and SHA-256 integrity verification.
"""
import os
import tempfile
import pytest
from benchmark.collector import BenchmarkCollector
from collectors.validation.integrity_manager import DataIntegrityManager

def test_collector_staging_and_hashing(tmp_path):
    raw_root = str(tmp_path / "data" / "raw")
    collector = BenchmarkCollector(base_raw_dir=raw_root)

    # Create dummy source log file
    source_file = tmp_path / "source_cowrie.json"
    source_file.write_text('{"eventid": "cowrie.session.connect", "src_ip": "192.0.2.1"}\n', encoding="utf-8")

    result = collector.stage_node_logs(
        repository="cowrie",
        run_id="run_test_001",
        node_id="node_01",
        source_log_path=str(source_file)
    )

    assert result["repository"] == "cowrie"
    assert result["run_id"] == "run_test_001"
    assert result["node_id"] == "node_01"
    assert os.path.exists(result["staged_path"])
    assert len(result["sha256"]) == 64
    assert result["size_bytes"] > 0

    # Verify manifest.sha256 exists in staged directory
    manifest_file = os.path.join(raw_root, "cowrie", "run_test_001", "manifest.sha256")
    assert os.path.exists(manifest_file)
    with open(manifest_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert result["sha256"] in content
