"""
Integration Test: Event Pipeline
Tests schema validation, normalization, and lineage tracking.
"""
import pytest
from collectors.normalization.normalize import EventNormalizer
from collectors.validation.schema_validator import SchemaValidator

def test_event_normalization_pipeline():
    normalizer = EventNormalizer()
    raw = {
        "event_id": "cowrie_test_01",
        "timestamp": "2026-09-06T12:00:00.000Z",
        "src_ip": "203.0.113.10",
        "src_port": 54321,
        "service": "ssh",
        "username": "admin",
        "password": "secret_password"
    }

    canonical = normalizer.normalize_event("cowrie", raw, run_id="run_pipeline_test")
    assert canonical["event_id"] == "cowrie_test_01"
    assert canonical["source"]["ip"] == "203.0.113.10"
    assert canonical["details"]["username"] == "admin"
    assert canonical["data_lineage"]["run_id"] == "run_pipeline_test"
    assert "raw_checksum" in canonical["data_lineage"]

    # Validate against canonical JSON schema
    validator = SchemaValidator()
    is_valid, errors = validator.validate(canonical)
    assert is_valid, f"Validation errors: {errors}"
