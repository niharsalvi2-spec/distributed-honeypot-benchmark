"""
Unified Attacker Behaviour Profile Generator.
Constructs comprehensive behavioral fingerprint summarizing attacker tactics.
"""
from typing import List, Dict, Any
from collections import Counter

class AttackerProfileGenerator:
    @staticmethod
    def generate_profile(actor_ip: str, sequences: List[Dict[str, Any]]) -> Dict[str, Any]:
        total_events = sum(s.get("total_events", 0) for s in sequences)
        services_observed = Counter()
        stages_observed = Counter()
        
        for s in sequences:
            for item in s.get("attack_chain", []):
                services_observed[item["service"]] += 1
                stages_observed[item["tactical_stage"]] += 1
                
        return {
            "attacker_profile_id": f"prof_{actor_ip.replace('.', '_')}",
            "primary_ip": actor_ip,
            "total_sequences": len(sequences),
            "total_events": total_events,
            "targeted_services": dict(services_observed),
            "tactical_stages": dict(stages_observed),
            "attack_velocity_eps": round(total_events / 60.0, 2),
            "risk_score": 85 if len(services_observed) > 1 else 40
        }
