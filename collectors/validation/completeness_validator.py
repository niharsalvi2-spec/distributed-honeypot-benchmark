"""
Completeness Validator.
Verifies that all non-nullable critical research fields are populated.
"""
from typing import Dict, Any, List

class CompletenessValidator:
    REQUIRED_FIELDS = [
        "event_id", "node_id", "service_id", "source", "timestamps", "event_type"
    ]

    @classmethod
    def check(cls, event: Dict[str, Any]) -> List[str]:
        missing = []
        for f in cls.REQUIRED_FIELDS:
            if f not in event or event[f] is None:
                missing.append(f)
        return missing

    @classmethod
    def compute_completeness(cls, event: Dict[str, Any]) -> float:
        missing = cls.check(event)
        return (len(cls.REQUIRED_FIELDS) - len(missing)) / len(cls.REQUIRED_FIELDS)

