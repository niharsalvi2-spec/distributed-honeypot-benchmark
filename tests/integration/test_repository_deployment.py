"""
Integration Test: Honeypot Repository Deployment Descriptors
Tests repository metadata, port bindings, and configuration retrieval across all 7 audited repos.
"""
import pytest
from benchmark.repository import HoneypotRepository

@pytest.mark.parametrize("repo_name, expected_proto", [
    ("cowrie", "ssh"),
    ("opencanary", "ftp"),
    ("dionaea", "smb"),
    ("conpot", "modbus"),
    ("honeytrap", "dynamic"),
    ("tpot", "all"),
    ("mhn", "hpfeeds")
])
def test_repository_descriptors(repo_name, expected_proto):
    repo = HoneypotRepository(repo_name)
    assert repo.name == repo_name
    assert expected_proto in repo.get_protocols()
    assert len(repo.get_default_ports()) > 0
    assert repo.get_audit_level() == "Level-5 (Controlled Experiment)"
