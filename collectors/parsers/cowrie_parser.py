"""
Cowrie Honeypot Telemetry Parser.
Parses native Cowrie JSON log records into intermediate parsed structures.
"""
from typing import Dict, Any, Optional
from datetime import datetime

class CowrieParser:
    """Parses Cowrie SSH and Telnet session logs."""

    EVENT_TYPE_MAP = {
        "cowrie.session.connect": "CONNECTION_OPENED",
        "cowrie.session.closed": "CONNECTION_CLOSED",
        "cowrie.login.success": "AUTH_SUCCESS",
        "cowrie.login.failed": "AUTH_FAILED",
        "cowrie.command.input": "COMMAND_EXEC",
        "cowrie.command.failed": "COMMAND_FAILED",
        "cowrie.session.file_download": "FILE_DOWNLOAD",
        "cowrie.session.file_upload": "FILE_UPLOAD",
        "cowrie.client.version": "CLIENT_VERSION"
    }

    def parse(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        event_id = raw_record.get("eventid", "cowrie.unknown")
        mapped_type = self.EVENT_TYPE_MAP.get(event_id, "GENERIC_EVENT")
        
        return {
            "parser": "cowrie",
            "event_type": mapped_type,
            "raw_event_id": event_id,
            "timestamp": raw_record.get("timestamp"),
            "session_id": raw_record.get("session"),
            "source_ip": raw_record.get("src_ip"),
            "source_port": raw_record.get("src_port"),
            "destination_ip": raw_record.get("dst_ip"),
            "destination_port": raw_record.get("dst_port", 2222),
            "protocol": raw_record.get("protocol", "SSH"),
            "credentials": {
                "username": raw_record.get("username"),
                "password": raw_record.get("password")
            },
            "command": raw_record.get("input"),
            "file_info": {
                "shasum": raw_record.get("shasum"),
                "url": raw_record.get("url"),
                "outfile": raw_record.get("outfile")
            },
            "client_version": raw_record.get("version"),
            "sensor": raw_record.get("sensor", "cowrie-sensor")
        }
