"""
Modern Honey Network (MHN) Telemetry Parser.
Parses Hpfeeds broker message payloads from distributed sensors.
"""
from typing import Dict, Any

class MhnParser:
    def parse(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "parser": "mhn",
            "channel": raw_record.get("channel", "hpfeeds"),
            "sensor_id": raw_record.get("identifier"),
            "event_type": "SENSOR_TELEMETRY",
            "timestamp": raw_record.get("timestamp"),
            "source_ip": raw_record.get("source_ip"),
            "source_port": raw_record.get("source_port"),
            "destination_port": raw_record.get("destination_port"),
            "protocol": raw_record.get("protocol"),
            "hpfeeds_payload": raw_record.get("payload")
        }
