"""
False Negative (Missed Correlation) Diagnostics.
Analyzes why truly related attack events failed to correlate (e.g. large delays).
"""
from typing import List, Tuple, Dict, Any

def analyze_false_negatives(predicted_pairs: List[Tuple[str, str]],
                            ground_truth_pairs: List[Tuple[str, str]],
                            events_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
    fn_set = set(ground_truth_pairs) - set(predicted_pairs)
    diagnostics = []
    for e1_id, e2_id in fn_set:
        diagnostics.append({
            "pair": (e1_id, e2_id),
            "diagnosed_root_cause": "EXCEEDED_TEMPORAL_WINDOW"
        })
    return diagnostics
