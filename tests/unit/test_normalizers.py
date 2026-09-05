"""
Unit Tests for Canonical Normalization Modules.
"""
import pytest
from collectors.normalization.timestamp_normalizer import TimestampNormalizer
from collectors.normalization.source_normalizer import SourceNormalizer
from collectors.normalization.service_normalizer import ServiceNormalizer

def test_timestamp_normalizer():
    # Epoch float
    iso_out = TimestampNormalizer.normalize(1700000000.0)
    assert iso_out.endswith("Z")
    assert "T" in iso_out

    # ISO string
    iso_str = "2026-08-15 12:34:56.789"
    norm = TimestampNormalizer.normalize(iso_str)
    assert norm.startswith("2026-08-15T12:34:56")

def test_source_normalizer():
    res = SourceNormalizer.normalize("192.168.1.55", 22)
    assert res["is_valid"] is True
    assert res["is_private"] is True
    assert res["subnet"] == "192.168.1.0/24"
    assert res["port"] == 22

    # Invalid IP fallback
    res_bad = SourceNormalizer.normalize("invalid_ip")
    assert res_bad["is_valid"] is False
    assert res_bad["ip"] == "0.0.0.0"

def test_service_normalizer():
    svc = ServiceNormalizer.normalize("ssh", 2222)
    assert svc["service_id"] == "ssh"
    assert svc["service_port"] == 2222
    assert svc["transport_protocol"] == "TCP"
