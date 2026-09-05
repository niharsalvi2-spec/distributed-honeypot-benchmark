"""
Dionaea Honeypot Telemetry Parser.
Parses connection logs, protocol emulations (SMB/MSSQL/FTP), and captured payloads.
"""
from typing import Dict, Any

class DionaeaParser:
    def parse(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "parser": "dionaea",
            "event_type": raw_record.get("connection_type", "EXPLOITATION_ATTEMPT"),
            "timestamp": raw_record.get("timestamp"),
            "connection_id": raw_record.get("connection_id"),
            "source_ip": raw_record.get("remote_host"),
            "source_port": raw_record.get("remote_port"),
            "destination_ip": raw_record.get("local_host"),
            "destination_port": raw_record.get("local_port"),
            "protocol": raw_record.get("protocol", "smb"),
            "malware_download": {
                "md5": raw_record.get("download_md5"),
                "sha256": raw_record.get("download_sha256"),
                "url": raw_record.get("download_url")
            }
        }
