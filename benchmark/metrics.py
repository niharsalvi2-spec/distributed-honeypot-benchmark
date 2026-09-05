"""
Consolidated Metrics Aggregator.
"""
from typing import Dict, Any, List

class MetricAggregator:
    @staticmethod
    def aggregate(trial_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not trial_metrics:
            return {}
        keys = trial_metrics[0].keys()
        summary = {}
        for k in keys:
            vals = [m[k] for m in trial_metrics if isinstance(m.get(k), (int, float))]
            if vals:
                summary[f"{k}_mean"] = round(sum(vals) / len(vals), 4)
        return summary
