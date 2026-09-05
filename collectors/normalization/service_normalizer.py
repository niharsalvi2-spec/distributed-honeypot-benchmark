"""
Service & Protocol Normalizer.
Maps destination ports and protocols to standardized canonical service identifiers.
"""
from typing import Dict, Any, Optional

class ServiceNormalizer:
    PORT_SERVICE_MAP = {
        22: "ssh", 2222: "ssh",
        21: "ftp", 2121: "ftp",
        80: "http", 8080: "http", 443: "https", 8443: "https",
        445: "smb", 139: "smb", 4450: "smb",
        3306: "mysql", 1433: "mssql", 6379: "redis", 27017: "mongodb",
        502: "modbus", 102: "s7comm", 47808: "bacnet",
        23: "telnet", 2323: "telnet"
    }

    @classmethod
    def normalize(cls, service_hint: Optional[str], port: Optional[int], protocol: Optional[str] = "TCP") -> Dict[str, Any]:
        p = int(port or 0)
        norm_svc = (service_hint or "").lower().strip()
        if not norm_svc or norm_svc in ["unknown", "generic"]:
            norm_svc = cls.PORT_SERVICE_MAP.get(p, "custom_service")
            
        return {
            "service_id": norm_svc,
            "service_port": p,
            "transport_protocol": (protocol or "TCP").upper().strip()
        }
