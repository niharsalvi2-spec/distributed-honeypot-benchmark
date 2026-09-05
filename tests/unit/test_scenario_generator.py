"""
Unit Test: Synthetic Scenario Generator & Negative Controls
Verifies deterministic seed reproduction and the structure of negative control benchmarks.
"""
import pytest
from ground_truth.generator import ScenarioGenerator

def test_deterministic_seed_reproducibility():
    gen1 = ScenarioGenerator(seed=42)
    gen2 = ScenarioGenerator(seed=42)

    data1 = gen1.generate_custom_benchmark(actors=3, events_per_actor=10, noise_ratio=0.1)
    data2 = gen2.generate_custom_benchmark(actors=3, events_per_actor=10, noise_ratio=0.1)

    assert len(data1["events"]) == len(data2["events"])
    assert [e["event_id"] for e in data1["events"]] == [e["event_id"] for e in data2["events"]]
    assert [e["source_ip"] for e in data1["events"]] == [e["source_ip"] for e in data2["events"]]

def test_scenario_1_nat_negative_control():
    gen = ScenarioGenerator(seed=100)
    sc1 = gen.generate_scenario_1_shared_ip_nat()

    assert sc1["scenario"] == "SCENARIO_1_SHARED_IP_NAT"
    assert len(sc1["ground_truth_clusters"]) == 2
    assert "ACTOR_ALPHA" in sc1["ground_truth_clusters"]
    assert "ACTOR_BETA" in sc1["ground_truth_clusters"]

    # All events should share the exact same source IP
    source_ips = {e["source_ip"] for e in sc1["events"]}
    assert len(source_ips) == 1

def test_scenario_2_different_ip_same_attacker():
    gen = ScenarioGenerator(seed=100)
    sc2 = gen.generate_scenario_2_different_ip_same_attacker()

    assert sc2["scenario"] == "SCENARIO_2_DIFFERENT_IP_SAME_ATTACKER"
    assert len(sc2["ground_truth_clusters"]) == 1
    # Multiple distinct IPs exist for the same attacker
    source_ips = {e["source_ip"] for e in sc2["events"]}
    assert len(source_ips) == 2

def test_scenario_3_concurrent_attackers():
    gen = ScenarioGenerator(seed=100)
    sc3 = gen.generate_scenario_3_concurrent_attackers()

    assert sc3["scenario"] == "SCENARIO_3_CONCURRENT_ATTACKERS"
    assert len(sc3["ground_truth_clusters"]) == 2

def test_scenario_4_missing_event():
    gen = ScenarioGenerator(seed=100)
    sc4 = gen.generate_scenario_4_missing_event()

    assert sc4["scenario"] == "SCENARIO_4_MISSING_EVENT"
    assert sc4["dropped_event_id"] == "ev_piv_02"
    assert all(e["event_id"] != "ev_piv_02" for e in sc4["events"])

def test_scenario_5_duplicate_events():
    gen = ScenarioGenerator(seed=100)
    sc5 = gen.generate_scenario_5_duplicate_events()

    assert sc5["scenario"] == "SCENARIO_5_DUPLICATE_EVENTS"
    assert len(sc5["events"]) > 4  # Includes injected duplicates

def test_scenario_6_out_of_order():
    gen = ScenarioGenerator(seed=100)
    sc6 = gen.generate_scenario_6_out_of_order()

    assert sc6["scenario"] == "SCENARIO_6_OUT_OF_ORDER"
    assert sc6["causal_order"] != sc6["arrival_order"]
