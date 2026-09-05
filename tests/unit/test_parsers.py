"""
Unit Tests for Telemetry Parsers.
"""
import pytest
from collectors.parsers.cowrie_parser import CowrieParser
from collectors.parsers.opencanary_parser import OpenCanaryParser
from collectors.parsers.dionaea_parser import DionaeaParser

def test_cowrie_parser():
    parser = CowrieParser()
    raw = {
        "eventid": "cowrie.login.failed",
        "timestamp": "2026-08-15T10:00:00.123456Z",
        "src_ip": "192.168.1.100",
        "src_port": 54321,
        "username": "root",
        "password": "toor",
        "session": "sess_123"
    }
    parsed = parser.parse(raw)
    assert parsed["parser"] == "cowrie"
    assert parsed["event_type"] == "AUTH_FAILED"
    assert parsed["credentials"]["username"] == "root"
    assert parsed["source_ip"] == "192.168.1.100"

def test_opencanary_parser():
    parser = OpenCanaryParser()
    raw = {
        "logtype": 4000,
        "src_host": "10.0.0.5",
        "src_port": 4321,
        "logdata": {"USERNAME": "admin", "PASSWORD": "password123"}
    }
    parsed = parser.parse(raw)
    assert parsed["parser"] == "opencanary"
    assert parsed["service"] == "ssh"
    assert parsed["credentials"]["username"] == "admin"

def test_dionaea_parser():
    parser = DionaeaParser()
    raw = {
        "connection_type": "EXPLOIT",
        "remote_host": "172.16.0.4",
        "protocol": "smb",
        "download_sha256": "abcdef123456"
    }
    parsed = parser.parse(raw)
    assert parsed["parser"] == "dionaea"
    assert parsed["malware_download"]["sha256"] == "abcdef123456"
