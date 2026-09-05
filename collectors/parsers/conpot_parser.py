"""
Conpot ICS/SCADA Telemetry Parser.
Parses industrial automation protocol interactions (Modbus, S7, BACnet).
"""
from typing import Dict, Any

class ConpotParser:
    def parse(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "parser": "conpot",
            "event_type": "ICS_PROBE",
            "protocol": raw_record.get("protocol", "modbus"),
            "timestamp": raw_record.get("timestamp"),
            "source_ip": raw_record.get("remote", {}).get("ip"),
            "source_port": raw_record.get("remote", {}).get("port"),
            "slave_id": raw_record.get("slave_id"),
            "function_code": raw_record.get("function_code"),
            "request": raw_record.get("request")
        }
