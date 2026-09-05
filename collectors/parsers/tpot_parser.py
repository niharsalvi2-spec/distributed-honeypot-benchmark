"""
T-Pot Platform Telemetry Parser.
Normalizes heterogeneous multi-container events collected via Logstash.
"""
from typing import Dict, Any

class TpotParser:
    def parse(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        tpot_type = raw_record.get("type", "tpot_unknown")
        return {
            "parser": "tpot",
            "sub_sensor": tpot_type,
            "event_type": raw_record.get("tpot_event_type", "TPOT_ALERT"),
            "timestamp": raw_record.get("@timestamp") or raw_record.get("timestamp"),
            "source_ip": raw_record.get("src_ip"),
            "source_port": raw_record.get("src_port"),
            "destination_ip": raw_record.get("dest_ip"),
            "destination_port": raw_record.get("dest_port"),
            "geoip": raw_record.get("geoip", {}),
            "payload": raw_record
        }
