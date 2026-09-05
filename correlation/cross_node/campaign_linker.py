"""
Campaign Linker.
Aggregates distributed sessions into strategic attack campaigns.
"""
from typing import List, Dict, Any

class CampaignLinker:
    @staticmethod
    def cluster_campaigns(sessions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        campaigns = {}
        for s in sessions:
            actor = s.get("actor_ip", "unknown")
            campaigns.setdefault(f"campaign_{actor}", []).append(s)
        return campaigns
