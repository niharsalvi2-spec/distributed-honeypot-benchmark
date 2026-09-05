"""
Unit Test: Baseline Correlation Engines
Tests IP, Session, Timestamp, and Rule-based Correlation Engines.
"""
import pytest
from correlation.baseline.ip_correlation import IPCorrelationEngine
from correlation.baseline.session_correlation import SessionCorrelationEngine
from correlation.baseline.timestamp_correlation import TimestampCorrelationEngine
from correlation.baseline.rule_based import RuleBasedCorrelationEngine

def test_ip_correlation_engine():
    e1 = {"event_id": "1", "source": {"ip": "10.0.0.1"}}
    e2 = {"event_id": "2", "source": {"ip": "10.0.0.1"}}
    e3 = {"event_id": "3", "source": {"ip": "10.0.0.2"}}

    assert IPCorrelationEngine.match(e1, e2) is True
    assert IPCorrelationEngine.match(e1, e3) is False

def test_session_correlation_engine():
    e1 = {"event_id": "1", "details": {"session_id": "sess_100"}}
    e2 = {"event_id": "2", "details": {"session_id": "sess_100"}}
    e3 = {"event_id": "3", "details": {"session_id": "sess_200"}}

    assert SessionCorrelationEngine.match(e1, e2) is True
    assert SessionCorrelationEngine.match(e1, e3) is False

def test_timestamp_correlation_engine():
    e1 = {"event_id": "1", "timestamps": {"epoch_ms": 1000}}
    e2 = {"event_id": "2", "timestamps": {"epoch_ms": 2500}}
    e3 = {"event_id": "3", "timestamps": {"epoch_ms": 15000}}

    assert TimestampCorrelationEngine.is_within_window(e1, e2, window_ms=3000) is True
    assert TimestampCorrelationEngine.is_within_window(e1, e3, window_ms=3000) is False

def test_rule_based_correlation_engine():
    rule = RuleBasedCorrelationEngine()
    e1 = {"event_id": "1", "source": {"ip": "1.2.3.4"}, "service": "http"}
    e2 = {"event_id": "2", "source": {"ip": "1.2.3.4"}, "service": "ssh"}
    
    score = rule.evaluate(e1, e2)
    assert score > 0.5
