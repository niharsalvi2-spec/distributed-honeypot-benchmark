"""
Unit Test: Normalization Sub-modules
Tests TimestampNormalizer, SourceNormalizer, and ServiceNormalizer.
"""
import pytest
from collectors.normalization.timestamp_normalizer import TimestampNormalizer
from collectors.normalization.source_normalizer import SourceNormalizer
from collectors.normalization.service_normalizer import ServiceNormalizer

def test_timestamp_normalizer():
    # ISO string
    res = TimestampNormalizer.normalize("2026-09-06T12:30:00Z")
    assert res.startswith("2026-09-06T12:30:00")
    assert res.endswith("Z")

    # Unix timestamp float
    res2 = TimestampNormalizer.normalize(1757120000.0)
    assert "T" in res2
    assert res2.endswith("Z")

def test_source_normalizer():
    # Public IPv4 (Google DNS)
    res = SourceNormalizer.normalize("8.8.8.8", 2222)
    assert res["ip"] == "8.8.8.8"
    assert res["port"] == 2222
    assert res["is_private"] is False
    assert res["is_valid"] is True

    # Private IPv4 (RFC 1918)
    res_priv = SourceNormalizer.normalize("192.168.1.50", 80)
    assert res_priv["is_private"] is True
    assert res_priv["is_valid"] is True

def test_service_normalizer():
    res_ssh = ServiceNormalizer.normalize("custom_ssh", 2222)
    assert res_ssh["service_id"] == "custom_ssh"
    assert res_ssh["service_port"] == 2222

    res_inferred = ServiceNormalizer.normalize("", 21)
    assert res_inferred["service_id"] == "ftp"
