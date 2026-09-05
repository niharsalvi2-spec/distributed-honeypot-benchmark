"""
Unit Test: Lamport Logical Clock
Tests monotonicity, distributed message causality updates, and serialization.
"""
import pytest
from distributed.clocks.lamport_clock import LamportClock

def test_lamport_clock_monotonicity():
    clock = LamportClock("node_1")
    t1 = clock.tick()
    t2 = clock.tick()
    t3 = clock.tick()
    assert t1 < t2 < t3
    assert clock.read() == 3

def test_lamport_clock_update():
    c1 = LamportClock("node_1")
    c2 = LamportClock("node_2")

    c1.tick()  # c1 = 1
    msg_timestamp = c1.read()

    # Remote node receives message with timestamp 10
    c2.update(10)
    assert c2.read() == 11

def test_lamport_clock_serialization():
    clock = LamportClock("node_alpha", initial_value=42)
    d = clock.to_dict()
    assert d["value"] == 42
    assert d["node_id"] == "node_alpha"

    restored = LamportClock.from_dict(d)
    assert restored.read() == 42
    assert restored.node_id == "node_alpha"
