"""
Repository Descriptor and Lifecycle Controller.
Encapsulates metadata, native configuration mapping, port allocation,
and deployment controls for audited honeypot repositories.
"""
import os
import yaml
from typing import Dict, Any, List, Optional

class HoneypotRepository:
    """
    Represents an audited honeypot codebase (Cowrie, OpenCanary, Dionaea, etc.)
    with its specific deployment characteristics, supported protocols, and audit status.
    """
    SUPPORTED_REPOSITORIES = {
        "cowrie": {
            "protocols": ["ssh", "telnet"],
            "default_ports": [2222, 2223],
            "log_format": "json",
            "audit_level": "Level-5 (Controlled Experiment)",
            "primary": True
        },
        "opencanary": {
            "protocols": ["ssh", "ftp", "http", "smb"],
            "default_ports": [21, 80, 445, 5000],
            "log_format": "json",
            "audit_level": "Level-5 (Controlled Experiment)",
            "primary": True
        },
        "dionaea": {
            "protocols": ["smb", "ftp", "tftp", "mysql"],
            "default_ports": [445, 21, 69, 3306],
            "log_format": "json/sqlite",
            "audit_level": "Level-5 (Controlled Experiment)",
            "primary": True
        },
        "tpot": {
            "protocols": ["all"],
            "default_ports": [64297],
            "log_format": "multi-json",
            "audit_level": "Level-5 (Controlled Experiment)",
            "primary": True
        },
        "mhn": {
            "protocols": ["management", "hpfeeds"],
            "default_ports": [10000],
            "log_format": "json",
            "audit_level": "Level-5 (Controlled Experiment)",
            "primary": True
        },
        "conpot": {
            "protocols": ["modbus", "s7comm", "bacnet"],
            "default_ports": [502, 102, 47808],
            "log_format": "json",
            "audit_level": "Level-5 (Controlled Experiment)",
            "primary": False
        },
        "honeytrap": {
            "protocols": ["dynamic"],
            "default_ports": [8080],
            "log_format": "json",
            "audit_level": "Level-5 (Controlled Experiment)",
            "primary": False
        }
    }

    def __init__(self, repo_name: str, base_dir: str = "repositories"):
        self.name = repo_name.lower()
        self.base_dir = base_dir
        self.repo_path = os.path.join(base_dir, self.name)
        self.metadata = self.SUPPORTED_REPOSITORIES.get(self.name, {
            "protocols": ["generic"],
            "default_ports": [8080],
            "log_format": "json",
            "audit_level": "Unverified",
            "primary": False
        })

    def is_cloned(self) -> bool:
        return os.path.isdir(self.repo_path) and os.path.exists(os.path.join(self.repo_path, ".git"))

    def get_protocols(self) -> List[str]:
        return self.metadata.get("protocols", [])

    def get_default_ports(self) -> List[int]:
        return self.metadata.get("default_ports", [])

    def get_audit_level(self) -> str:
        return self.metadata.get("audit_level", "Unverified")

    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Loads native or benchmark configuration for this repository."""
        if not config_path:
            config_path = os.path.join("config", f"{self.name}.yaml")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def get_summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "cloned": self.is_cloned(),
            "repo_path": self.repo_path,
            "protocols": self.get_protocols(),
            "default_ports": self.get_default_ports(),
            "audit_level": self.get_audit_level(),
            "is_primary": self.metadata.get("primary", False)
        }

# Backward compatibility alias
Repository = HoneypotRepository
