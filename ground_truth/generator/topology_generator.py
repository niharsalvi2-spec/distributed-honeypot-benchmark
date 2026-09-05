"""
Distributed Honeypot Topology Generator
Models multi-sensor decoy deployments across geographic/network clusters.
"""
from typing import Dict, Any, List, Optional

class HoneypotNode:
    def __init__(self, node_id: str, ip_address: str, subnet: str, services: List[str], honeypot_type: str):
        self.node_id = node_id
        self.ip_address = ip_address
        self.subnet = subnet
        self.services = services
        self.honeypot_type = honeypot_type

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "ip_address": self.ip_address,
            "subnet": self.subnet,
            "services": self.services,
            "honeypot_type": self.honeypot_type
        }

class TopologyGenerator:
    """
    Generates standard multi-node sensor topologies for benchmark experiments.
    """
    DEFAULT_CONFIGS = [
        {"services": ["ssh"], "type": "cowrie"},
        {"services": ["http"], "type": "opencanary"},
        {"services": ["smb", "ftp"], "type": "dionaea"},
        {"services": ["modbus"], "type": "conpot"},
        {"services": ["dynamic"], "type": "honeytrap"}
    ]

    @classmethod
    def generate_topology(cls, node_count: int = 3, subnet_prefix: str = "10.0.100") -> List[HoneypotNode]:
        nodes = []
        for i in range(node_count):
            cfg = cls.DEFAULT_CONFIGS[i % len(cls.DEFAULT_CONFIGS)]
            node = HoneypotNode(
                node_id=f"node_{i+1:02d}",
                ip_address=f"{subnet_prefix}.{10 + i}",
                subnet=f"{subnet_prefix}.0/24",
                services=cfg["services"],
                honeypot_type=cfg["type"]
            )
            nodes.append(node)
        return nodes
