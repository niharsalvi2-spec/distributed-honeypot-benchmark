"""
OpenCanary Multi-Service Telemetry Parser.
Parses native OpenCanary syslog and JSON alert payloads.
"""
from typing import Dict, Any

class OpenCanaryParser:
    """Parses OpenCanary alerts spanning FTP, SSH, HTTP, SMB, and Portscan."""

    SERVICE_MAP = {
        1001: "portscan",
        2000: "ftp",
        3000: "http",
        4000: "ssh",
        5000: "smb",
        6000: "mssql",
        7000: "telnet",
        8000: "mysql"
    }

    def parse(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        log_type = raw_record.get("logtype")
        log_data = raw_record.get("logdata", {})
        service = self.SERVICE_MAP.get(log_type, raw_record.get("service", "unknown"))
        
        return {
            "parser": "opencanary",
            "event_type": f"ALERT_{service.upper()}",
            "logtype": log_type,
            "timestamp": raw_record.get("utc_time") or raw_record.get("timestamp"),
            "node_id": raw_record.get("node_id", "opencanary-node"),
            "source_ip": raw_record.get("src_host"),
            "source_port": raw_record.get("src_port"),
            "destination_ip": raw_record.get("dst_host"),
            "destination_port": raw_record.get("dst_port"),
            "service": service,
            "credentials": {
                "username": log_data.get("USERNAME") or log_data.get("user"),
                "password": log_data.get("PASSWORD") or log_data.get("password")
            },
            "request_details": {
                "path": log_data.get("PATH"),
                "headers": log_data.get("HEADERS"),
                "command": log_data.get("COMMAND")
            },
            "raw_logdata": log_data
        }
