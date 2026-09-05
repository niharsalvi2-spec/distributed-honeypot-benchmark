"""
Source Network Metadata Normalizer.
Validates IPs, checks private/loopback status, extracts /24 subnets.
"""
import ipaddress
from typing import Dict, Any, Optional

class SourceNormalizer:
    @staticmethod
    def normalize(ip_str: Optional[str], port: Optional[int] = 0) -> Dict[str, Any]:
        ip_clean = (ip_str or "127.0.0.1").strip()
        is_valid = True
        is_private = False
        subnet_24 = "127.0.0.0/24"
        
        try:
            ip_obj = ipaddress.ip_address(ip_clean)
            is_private = ip_obj.is_private or ip_obj.is_loopback
            if ip_obj.version == 4:
                network = ipaddress.ip_network(f"{ip_clean}/24", strict=False)
                subnet_24 = str(network)
            else:
                network = ipaddress.ip_network(f"{ip_clean}/64", strict=False)
                subnet_24 = str(network)
        except ValueError:
            is_valid = False
            ip_clean = "0.0.0.0"

        safe_port = 0
        try:
            safe_port = int(port or 0)
            if not (0 <= safe_port <= 65535):
                safe_port = 0
        except (ValueError, TypeError):
            safe_port = 0

        return {
            "ip": ip_clean,
            "port": safe_port,
            "subnet": subnet_24,
            "is_valid": is_valid,
            "is_private": is_private
        }
