"""
Synthetic Threat Actor Generator
Generates reproducible threat actor profiles with distinct TTPs, IP strategies, and behavioral attributes.
"""
import random
from typing import Dict, Any, List, Optional

class ThreatActor:
    def __init__(self, actor_id: str, source_ips: List[str], tactics: List[str],
                 preferred_services: List[str], user_agent: str, credential_profile: Dict[str, str]):
        self.actor_id = actor_id
        self.source_ips = source_ips
        self.tactics = tactics
        self.preferred_services = preferred_services
        self.user_agent = user_agent
        self.credential_profile = credential_profile

    def to_dict(self) -> Dict[str, Any]:
        return {
            "actor_id": self.actor_id,
            "source_ips": self.source_ips,
            "tactics": self.tactics,
            "preferred_services": self.preferred_services,
            "user_agent": self.user_agent,
            "credential_profile": self.credential_profile
        }

class ActorGenerator:
    """
    Generates deterministic threat actor profiles given a random seed.
    """
    COMMON_TACTICS = [
        "TA0001_Initial_Access",
        "TA0002_Execution",
        "TA0003_Persistence",
        "TA0006_Credential_Access",
        "TA0007_Discovery",
        "TA0008_Lateral_Movement",
        "TA0010_Exfiltration"
    ]

    SERVICES = ["ssh", "http", "ftp", "smb", "mysql"]

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "curl/7.68.0",
        "Go-http-client/1.1",
        "Python-urllib/3.10",
        "Nmap Scripting Engine"
    ]

    def __init__(self, seed: Optional[int] = 42):
        self.rng = random.Random(seed)

    def generate_actor(self, actor_id: str, fixed_ip: Optional[str] = None,
                       num_ips: int = 1) -> ThreatActor:
        if fixed_ip:
            ips = [fixed_ip]
        else:
            ips = [
                f"{self.rng.randint(11, 220)}.{self.rng.randint(1, 254)}.{self.rng.randint(1, 254)}.{self.rng.randint(1, 254)}"
                for _ in range(num_ips)
            ]

        num_tactics = self.rng.randint(3, 5)
        tactics = self.rng.sample(self.COMMON_TACTICS, min(num_tactics, len(self.COMMON_TACTICS)))
        tactics.sort(key=lambda t: self.COMMON_TACTICS.index(t))

        num_services = self.rng.randint(1, 3)
        preferred_services = self.rng.sample(self.SERVICES, num_services)

        user_agent = self.rng.choice(self.USER_AGENTS)
        cred = {
            "username": self.rng.choice(["admin", "root", "guest", "testuser", "operator"]),
            "password": self.rng.choice(["admin123", "password", "123456", "toor", "default"])
        }

        return ThreatActor(
            actor_id=actor_id,
            source_ips=ips,
            tactics=tactics,
            preferred_services=preferred_services,
            user_agent=user_agent,
            credential_profile=cred
        )

    def generate_actors(self, count: int) -> List[ThreatActor]:
        actors = []
        for i in range(count):
            actor_id = f"ACTOR_{chr(65 + i) if i < 26 else f'EXT_{i}'}"
            actors.append(self.generate_actor(actor_id))
        return actors
