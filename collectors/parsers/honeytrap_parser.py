"""
Honeytrap Dynamic Port Parser.
Parses dynamic socket connection banners and initial payload probes.
"""
from typing import Dict, Any

class HoneytrapParser:
    def parse(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "parser": "honeytrap",
            "event_type": "PORT_INTERACTION",
            "timestamp": raw_record.get("timestamp"),
            "source_ip": raw_record.get("source_ip"),
            "source_port": raw_record.get("source_port"),
            "destination_port": raw_record.get("destination_port"),
            "banner_sent": raw_record.get("banner"),
            "payload_hex": raw_record.get("payload")
        }
