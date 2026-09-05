"""
Unit Test: Canonical Event Schema Conformance
Validates correct vs malformed events using jsonschema.
"""
import pytest
from collectors.validation.schema_validator import SchemaValidator

def test_valid_canonical_event_schema():
    validator = SchemaValidator()
    valid_event = {
        "event_id": "can_12345678",
        "node_id": "node_alpha",
        "service_id": "ssh",
        "transport_protocol": "TCP",
        "source": {"ip": "192.0.2.15", "port": 49152},
        "timestamps": {
            "physical_raw": "2026-09-06T12:00:00Z",
            "physical_ingested": "2026-09-06T12:00:00Z",
            "lamport_logical": 1,
            "vector_clock": {"node_alpha": 1}
        },
        "event_type": "LOGIN_SUCCESS",
        "payload_features": {},
        "data_lineage": {
            "run_id": "run_001",
            "raw_repo": "cowrie",
            "raw_checksum": "a" * 64,
            "normalization_timestamp": "2026-09-06T12:00:00Z"
        }
    }
    is_valid, errors = validator.validate(valid_event)
    assert is_valid, f"Expected valid event, got errors: {errors}"

def test_invalid_canonical_event_schema():
    validator = SchemaValidator()
    invalid_event = {
        "event_id": "broken_event"
        # missing all required fields
    }
    is_valid, errors = validator.validate(invalid_event)
    assert not is_valid
    assert len(errors) > 0
