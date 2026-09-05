"""
False Positive Correlation Diagnostics.
Analyzes why unrelated events were incorrectly correlated (e.g. shared ISP/proxy).
"""
from typing import List, Tuple, Dict, Any

def analyze_false_positives(predicted_pairs: List[Tuple[str, str]],
                            ground_truth_pairs: List[Tuple[str, str]],
                            events_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    fp_set = set(predicted_pairs) - set(ground_truth_pairs)
    diagnostics = []
    for e1_id, e2_id in fp_set:
        e1 = events_dict.get(e1_id, {})
        e2 = events_dict.get(e2_id, {})
        reason = "SHARED_SUBNET" if e1.get("source", {}).get("subnet") == e2.get("source", {}).get("subnet") else "TEMPORAL_COINCIDENCE"
        diagnostics.append({
            "pair": (e1_id, e2_id),
            "diagnosed_root_cause": reason
        })
    return diagnostics
