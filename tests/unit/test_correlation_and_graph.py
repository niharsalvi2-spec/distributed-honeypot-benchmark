"""
Unit Tests for Multi-Evidence Correlation & Sequence Graph.
"""
import pytest
from correlation.cross_service.session_linker import SessionLinker
from correlation.graph.event_graph import EventGraphBuilder
from sequence_reconstruction.sequence_builder import SequenceBuilder
from sequence_reconstruction.sequence_validator import SequenceValidator
from sequence_reconstruction.attacker_profile import AttackerProfileGenerator

def test_session_linker_scoring():
    linker = SessionLinker()
    e1 = {
        "event_id": "e1",
        "source": {"ip": "192.168.1.100", "subnet": "192.168.1.0/24"},
        "service": {"service_id": "http"},
        "timestamps": {"physical_raw": "2026-08-15T10:00:00.000Z", "lamport_logical": 1}
    }
    e2 = {
        "event_id": "e2",
        "source": {"ip": "192.168.1.100", "subnet": "192.168.1.0/24"},
        "service": {"service_id": "ssh"},
        "timestamps": {"physical_raw": "2026-08-15T10:00:05.000Z", "lamport_logical": 2}
    }
    score, conf = linker.evaluate_pair(e1, e2)
    assert score >= 0.75
    assert conf == "STRONG"

def test_event_graph_and_sequence_reconstruction():
    events = [
        {
            "event_id": "e1",
            "source": {"ip": "10.0.0.1", "subnet": "10.0.0.0/24"},
            "service": {"service_id": "http"},
            "timestamps": {"physical_raw": "2026-08-15T10:00:00Z", "lamport_logical": 1}
        },
        {
            "event_id": "e2",
            "source": {"ip": "10.0.0.1", "subnet": "10.0.0.0/24"},
            "service": {"service_id": "ssh"},
            "timestamps": {"physical_raw": "2026-08-15T10:00:02Z", "lamport_logical": 2}
        }
    ]
    graph_builder = EventGraphBuilder()
    g = graph_builder.build_graph(events)
    clusters = graph_builder.get_attack_clusters()
    assert len(clusters) == 1
    
    seq = SequenceBuilder.reconstruct_sequence(events, "seq_001")
    assert seq["sequence_id"] == "seq_001"
    assert seq["total_events"] == 2
    assert seq["ordered_event_ids"] == ["e1", "e2"]
    
    # Validate SRA
    sra = SequenceValidator.compute_sra(["e1", "e2"], seq["ordered_event_ids"])
    assert sra == 1.0

def test_attacker_profile_generation():
    seq = {
        "total_events": 3,
        "attack_chain": [
            {"service": "http", "tactical_stage": "RECONNAISSANCE"},
            {"service": "ssh", "tactical_stage": "CREDENTIAL_EXPLOITATION"}
        ]
    }
    prof = AttackerProfileGenerator.generate_profile("192.168.1.100", [seq])
    assert prof["primary_ip"] == "192.168.1.100"
    assert prof["total_events"] == 3
    assert "http" in prof["targeted_services"]
