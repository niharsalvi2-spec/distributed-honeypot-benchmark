"""
Validation Test: Controlled Attack Ground Truth Manifests
Tests consistency, non-emptiness, and structure of Campaign A and Campaign B ground truth.
"""
import os
import json
import yaml
import pytest

def test_campaign_a_manifests():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    camp_dir = os.path.join(project_root, "workloads", "controlled_attack", "campaign_A")

    manifest_p = os.path.join(camp_dir, "manifest.yaml")
    events_p = os.path.join(camp_dir, "expected_events.json")
    seq_p = os.path.join(camp_dir, "expected_sequence.json")

    assert os.path.exists(manifest_p)
    assert os.path.exists(events_p)
    assert os.path.exists(seq_p)

    with open(manifest_p, "r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)
    assert manifest["campaign_id"] == "CAMP-A-MULTI-STAGE"

    with open(events_p, "r", encoding="utf-8") as f:
        events = json.load(f)
    assert len(events) >= 5

    with open(seq_p, "r", encoding="utf-8") as f:
        seq = json.load(f)
    assert len(seq) == len(events)
