"""
Behavioral Feature Vector Extraction.
Extracts numerical and categorical feature arrays for clustering and statistical modeling.
"""
from typing import Dict, Any, List

class BehaviourFeatureExtractor:
    @staticmethod
    def extract_features(profile: Dict[str, Any]) -> List[float]:
        return [
            float(profile.get("total_events", 0)),
            float(len(profile.get("targeted_services", {}))),
            float(len(profile.get("tactical_stages", {}))),
            float(profile.get("attack_velocity_eps", 0.0)),
            float(profile.get("risk_score", 0))
        ]
