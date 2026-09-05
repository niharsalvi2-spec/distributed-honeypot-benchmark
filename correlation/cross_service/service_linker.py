"""
Cross-Service Transition Probability Linker.
Models causal attack transitions across heterogeneous protocols (e.g. HTTP -> SSH -> FTP).
"""
import math
from typing import Dict, Any, List, Tuple, Set

class ServiceLinker:
    # Empirical transition likelihood matrix
    TRANSITION_MATRIX = {
        ("http", "ssh"): 0.85,    # Web recon preceding SSH credential brute-force
        ("ssh", "ftp"): 0.75,     # SSH intrusion followed by FTP exfiltration
        ("http", "ftp"): 0.65,    # Web exploitation leading directly to FTP
        ("ssh", "ssh"): 0.90,     # Successive SSH attempts
        ("ftp", "ftp"): 0.80,     # Successive FTP interactions
        ("smb", "ssh"): 0.70,     # SMB reconnaissance to SSH pivot
        ("http", "smb"): 0.60
    }

    def __init__(self, time_window_sec: float = 60.0):
        self.time_window_sec = time_window_sec
        self.events: List[Dict[str, Any]] = []

    @classmethod
    def score_transition(cls, svc_a: str, svc_b: str) -> float:
        pair = (svc_a.lower(), svc_b.lower())
        rev_pair = (svc_b.lower(), svc_a.lower())
        return cls.TRANSITION_MATRIX.get(pair, cls.TRANSITION_MATRIX.get(rev_pair, 0.30))

    def ingest_event(self, event: Dict[str, Any]):
        self.events.append(event)

    def get_cross_service_links(self) -> List[Tuple[str, str]]:
        links = []
        n = len(self.events)
        for i in range(n):
            for j in range(i + 1, n):
                ev1 = self.events[i]
                ev2 = self.events[j]
                svc1 = ev1.get("service") or ev1.get("service_id", "")
                svc2 = ev2.get("service") or ev2.get("service_id", "")
                score = self.score_transition(svc1, svc2)
                if score >= 0.60:
                    links.append((ev1["event_id"], ev2["event_id"]))
        return links

# Alias for backward compatibility
CrossServiceLinker = ServiceLinker
