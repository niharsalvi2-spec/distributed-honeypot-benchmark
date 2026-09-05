"""
Metric Analyzer: E01_functional
Validates schema compliance, completeness ratios, and field coverage.
"""
import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import os
import json
from typing import Dict, Any
from collectors.validation.schema_validator import SchemaValidator
from collectors.validation.completeness_validator import CompletenessValidator
from collectors.validation.consistency_validator import ConsistencyValidator

def analyze_run(run_id: str) -> Dict[str, Any]:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    norm_file = os.path.join(project_root, "data", "normalized", run_id, "normalized_events.jsonl")
    
    events = []
    if os.path.exists(norm_file):
        with open(norm_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))

    schema_val = SchemaValidator()
    valid_count = 0
    completeness_scores = []
    repo_coverage = set()

    for ev in events:
        is_valid, _ = schema_val.validate(ev)
        if is_valid:
            valid_count += 1
        completeness_scores.append(CompletenessValidator.compute_completeness(ev))
        repo_coverage.add(ev.get("honeypot", {}).get("type", "unknown"))

    schema_compliance = valid_count / len(events) if events else 1.0
    mean_completeness = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 1.0

    return {
        "experiment_id": "E01",
        "run_id": run_id,
        "total_events_analyzed": len(events),
        "schema_compliance_rate": round(schema_compliance, 4),
        "mean_field_completeness": round(mean_completeness, 4),
        "distinct_repositories_verified": len(repo_coverage),
        "hypothesis_H1_supported": schema_compliance >= 0.95 and mean_completeness >= 0.80
    }
