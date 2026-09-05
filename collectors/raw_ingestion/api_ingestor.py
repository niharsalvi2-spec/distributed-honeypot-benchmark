"""
Raw event ingestion module: api_ingestor.py
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def ingest_raw(data: Any) -> Dict[str, Any]:
    """Ingests and validates raw telemetry input."""
    logger.info("Ingesting raw data: %s", type(data))
    return {"status": "received", "raw_payload": data}
