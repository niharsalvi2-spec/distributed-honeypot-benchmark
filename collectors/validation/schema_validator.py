"""
Schema Validator.
Validates canonical events against collectors/schema/canonical_event.json using jsonschema.
"""
import os
import json
from typing import Dict, Any, Tuple, Optional, List
import jsonschema

class SchemaValidator:
    def __init__(self, schema_path: Optional[str] = None):
        if not schema_path:
            schema_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "schema", "canonical_event.json"))
        with open(schema_path, "r", encoding="utf-8") as f:
            self.schema = json.load(f)
        self.validator = jsonschema.Draft7Validator(self.schema)

    def validate(self, event_record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = [err.message for err in self.validator.iter_errors(event_record)]
        return len(errors) == 0, errors
