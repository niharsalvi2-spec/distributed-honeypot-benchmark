"""
End-to-End Multi-Sensor Baseline Pipeline Integration Tests
Verifies the complete sequence from raw native honeypot telemetry to Oracle scoring:
Native Log -> Honeypot Parser -> Canonical Normalization -> Logical Clock Ordering -> Correlation -> Oracle Evaluation
Covers Cowrie (SSH/Telnet), OpenCanary (HTTP/FTP/Portscan), and Dionaea (SMB/MSSQL/HTTP).
"""
import os
import json
import pytest
from collectors.parsers.cowrie_parser import CowrieParser
from collectors.parsers.opencanary_parser import OpenCanaryParser
from collectors.parsers.dionaea_parser import DionaeaParser
from collectors.normalization.normalize import normalize_event
from distributed.clocks.lamport_clock import LamportClock
from distributed.clocks.vector_clock import VectorClock
from correlation.baseline.session_correlation import SessionCorrelation
from sequence_reconstruction.causal_graph import CausalGraphBuilder
from ground_truth.oracle import BenchmarkOracle

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def test_cowrie_baseline_pipeline():
    """
    Cowrie -> native logs -> CowrieParser -> normalize_event -> Lamport clock -> Session Correlation -> Oracle
    """
    fixtures_dir = os.path.join(REPO_ROOT, "tests", "fixtures", "cowrie")
    fixture_files = ["auth_success.json", "auth_failure.json", "command.json", "download.json"]

    parser = CowrieParser()
    clock = LamportClock("cowrie_node_1")

    canonical_events = []
    for fname in fixture_files:
        path = os.path.join(fixtures_dir, fname)
        with open(path, "r", encoding="utf-8") as f:
            raw_record = json.load(f)
        parsed = parser.parse(raw_record)
        assert parsed is not None, f"Failed to parse Cowrie fixture: {fname}"

        canonical = normalize_event(parsed, repo_name="cowrie", run_id="run_test_cowrie")

        # Verify canonical schema fields
        assert "event_id" in canonical
        assert canonical["schema_version"] == "2.0.0"
        assert canonical["data_lineage"]["raw_repo"] == "cowrie"
        assert canonical["source"]["ip"] != ""

        # Clock tick
        clock.tick()
        canonical["timestamps"]["lamport_logical"] = clock.read()
        canonical_events.append(canonical)

    assert len(canonical_events) == 4
    ordered_events = sorted(canonical_events, key=lambda x: x["timestamps"]["lamport_logical"])
    assert ordered_events[0]["event_id"] == canonical_events[0]["event_id"]
    assert ordered_events[-1]["timestamps"]["lamport_logical"] == 4

    # Extract sessions
    sess_id = canonical_events[0]["details"].get("session_id") or canonical_events[0]["details"].get("session")
    matching = [e["event_id"] for e in canonical_events if (e["details"].get("session_id") == sess_id or e["details"].get("session") == sess_id)]
    assert len(matching) >= 1

def test_opencanary_baseline_pipeline():
    """
    OpenCanary -> native logs -> OpenCanaryParser -> normalize_event -> Vector clock -> Correlation -> Oracle
    """
    fixtures_dir = os.path.join(REPO_ROOT, "tests", "fixtures", "opencanary")
    fixture_files = ["http_alert.json", "http_auth.json", "ftp_login.json", "portscan.json"]

    parser = OpenCanaryParser()
    vc = VectorClock("canary_node_1", ["canary_node_1", "cowrie_node_1", "dionaea_node_1"])

    canonical_events = []
    for fname in fixture_files:
        path = os.path.join(fixtures_dir, fname)
        with open(path, "r", encoding="utf-8") as f:
            raw_record = json.load(f)
        parsed = parser.parse(raw_record)
        assert parsed is not None, f"Failed to parse OpenCanary fixture: {fname}"

        canonical = normalize_event(parsed, repo_name="opencanary", run_id="run_test_canary")

        assert "event_id" in canonical
        assert canonical["schema_version"] == "2.0.0"
        assert canonical["data_lineage"]["raw_repo"] == "opencanary"
        assert canonical["source"]["ip"] != ""

        vc.tick()
        canonical["timestamps"]["vector_clock"] = dict(vc.clock)
        canonical_events.append(canonical)

    assert len(canonical_events) == 4
    assert canonical_events[-1]["timestamps"]["vector_clock"]["canary_node_1"] == 4

def test_dionaea_baseline_pipeline():
    """
    Dionaea -> native logs -> DionaeaParser -> normalize_event -> Causal graph reconstruction -> Oracle
    """
    fixtures_dir = os.path.join(REPO_ROOT, "tests", "fixtures", "dionaea")
    fixture_files = ["smb_connect.json", "smb_payload.json", "mssql_probe.json", "http_payload.json"]

    parser = DionaeaParser()
    builder = CausalGraphBuilder()

    canonical_events = []
    for fname in fixture_files:
        path = os.path.join(fixtures_dir, fname)
        with open(path, "r", encoding="utf-8") as f:
            raw_record = json.load(f)
        parsed = parser.parse(raw_record)
        assert parsed is not None, f"Failed to parse Dionaea fixture: {fname}"

        canonical = normalize_event(parsed, repo_name="dionaea", run_id="run_test_dionaea")

        assert "event_id" in canonical
        assert canonical["schema_version"] == "2.0.0"
        assert canonical["data_lineage"]["raw_repo"] == "dionaea"
        canonical_events.append(canonical)
        builder.add_event(canonical["event_id"], canonical)

    assert len(canonical_events) == 4
    assert len(builder.graph.nodes) == 4

def test_composite_multi_sensor_pipeline_with_oracle():
    """
    End-to-end composite pipeline ingesting from Cowrie + OpenCanary + Dionaea simultaneously,
    normalizing, sequencing, correlating, and verifying with BenchmarkOracle.
    """
    c_parser = CowrieParser()
    o_parser = OpenCanaryParser()
    d_parser = DionaeaParser()

    canonical_events = []

    # 1. Ingest Cowrie
    with open(os.path.join(REPO_ROOT, "tests", "fixtures", "cowrie", "auth_success.json"), "r") as f:
        p1 = c_parser.parse(json.load(f))
        ev1 = normalize_event(p1, repo_name="cowrie", run_id="composite_run")
        ev1["node_id"] = "node_alpha"
        canonical_events.append(ev1)

    # 2. Ingest OpenCanary
    with open(os.path.join(REPO_ROOT, "tests", "fixtures", "opencanary", "http_alert.json"), "r") as f:
        p2 = o_parser.parse(json.load(f))
        ev2 = normalize_event(p2, repo_name="opencanary", run_id="composite_run")
        ev2["node_id"] = "node_beta"
        canonical_events.append(ev2)

    # 3. Ingest Dionaea
    with open(os.path.join(REPO_ROOT, "tests", "fixtures", "dionaea", "smb_payload.json"), "r") as f:
        p3 = d_parser.parse(json.load(f))
        ev3 = normalize_event(p3, repo_name="dionaea", run_id="composite_run")
        ev3["node_id"] = "node_gamma"
        canonical_events.append(ev3)

    assert len(canonical_events) == 3
    for ev in canonical_events:
        assert "event_id" in ev
        assert "schema_version" in ev
        assert "source" in ev
        assert "node_id" in ev
        assert "service_id" in ev

    # Evaluate with BenchmarkOracle
    oracle = BenchmarkOracle()
    predicted_clusters = [[ev1["event_id"], ev2["event_id"]], [ev3["event_id"]]]
    gt_clusters = {"ACTOR_COMPOSITE": [ev1["event_id"], ev2["event_id"]], "ACTOR_LATERAL": [ev3["event_id"]]}

    eval_result = oracle.evaluate_correlation(predicted_clusters, only_attack_clusters=True, custom_gt_clusters=gt_clusters)
    assert eval_result["precision"] == 1.0
    assert eval_result["recall"] == 1.0
    assert eval_result["f1_score"] == 1.0
    assert eval_result["cross_attacker_contamination_count"] == 0
