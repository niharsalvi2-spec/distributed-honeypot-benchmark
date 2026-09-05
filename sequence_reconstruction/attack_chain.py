"""
Attack Kill-Chain Synthesizer.
Maps reconstructed sequences into tactical stages (Recon -> Auth -> Action).
"""
from typing import List, Dict, Any

class AttackChainSynthesizer:
    STAGE_MAP = {
        "http": "RECONNAISSANCE",
        "ssh": "CREDENTIAL_EXPLOITATION",
        "ftp": "DATA_EXFILTRATION",
        "smb": "LATERAL_MOVEMENT"
    }

    @classmethod
    def synthesize_chain(cls, ordered_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chain = []
        for e in ordered_events:
            svc = e.get("service", {}).get("service_id", "unknown")
            stage = cls.STAGE_MAP.get(svc, "EXECUTION")
            chain.append({
                "event_id": e["event_id"],
                "service": svc,
                "tactical_stage": stage,
                "timestamp": e.get("timestamps", {}).get("physical_raw")
            })
        return chain
