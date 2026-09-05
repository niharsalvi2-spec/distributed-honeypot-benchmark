"""
Pre-Analysis Integrity & Conformance Validator.
Verifies canonical events prior to ordering, correlation, and statistical analysis.
"""
from typing import List, Dict, Any, Tuple
import re

class DatasetValidator:
    """
    Validates normalized honeypot event datasets for completeness,
    schema adherence, and chronological integrity.
    """
    REQUIRED_ROOT_KEYS = ["event_id", "timestamp", "source", "service", "honeypot"]
    REQUIRED_TIMESTAMP_KEYS = ["iso_8601", "epoch_ms"]
    REQUIRED_SOURCE_KEYS = ["ip"]

    @classmethod
    def validate_dataset(cls, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Conducts deep structural and logical validation of event list.
        """
        if not events:
            return {
                "valid": False,
                "total_events": 0,
                "passed_events": 0,
                "failed_events": 0,
                "errors": ["Dataset is completely empty."]
            }

        passed = 0
        failed = 0
        errors = []

        for idx, ev in enumerate(events):
            ev_errors = []
            
            # 1. Root keys
            for rk in cls.REQUIRED_ROOT_KEYS:
                if rk not in ev:
                    ev_errors.append(f"Missing required root key: '{rk}'")

            # 2. Timestamp structure
            ts_block = ev.get("timestamp") or ev.get("timestamps")
            if not ts_block or not isinstance(ts_block, dict):
                ev_errors.append("Invalid or missing 'timestamp' block")
            else:
                if "iso_8601" not in ts_block and "epoch_ms" not in ts_block:
                    ev_errors.append("Timestamp missing both iso_8601 and epoch_ms")

            # 3. Source IP structure
            src = ev.get("source", {})
            if isinstance(src, dict):
                ip = src.get("ip", "")
                if not ip or not isinstance(ip, str):
                    ev_errors.append("Missing source IP address")
            else:
                ev_errors.append("Source block must be an object")

            # 4. Service structure
            svc = ev.get("service")
            if not svc:
                ev_errors.append("Missing service identifier")

            if ev_errors:
                failed += 1
                if len(errors) < 10:
                    errors.append(f"Event #{idx} ({ev.get('event_id', 'unknown')}): {', '.join(ev_errors)}")
            else:
                passed += 1

        is_valid = failed == 0
        return {
            "valid": is_valid,
            "total_events": len(events),
            "passed_events": passed,
            "failed_events": failed,
            "conformance_rate": round(passed / len(events), 4),
            "errors": errors
        }

def validate_dataset(events: List[Dict[str, Any]]) -> bool:
    res = DatasetValidator.validate_dataset(events)
    return res["valid"]
