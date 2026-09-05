"""
FastAPI HTTP Telemetry Ingestion Daemon.
Receives asynchronous event envelopes from distributed honeypot nodes.
Appends directly to raw immutable storage without mutation.
"""
import os
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any, Optional

app = FastAPI(title="Distributed Honeypot Raw Ingestion API", version="1.0.0")

RAW_STORAGE_DIR = os.getenv("RAW_STORAGE_DIR", "data/raw/default_run")
os.makedirs(RAW_STORAGE_DIR, exist_ok=True)

class EventEnvelope(BaseModel):
    node_id: str
    service: str
    timestamp: Optional[str] = None
    payload: Dict[str, Any]

@app.get("/health")
def health_check():
    return {"status": "ACTIVE", "timestamp": datetime.utcnow().isoformat() + "Z"}

@app.post("/events")
async def ingest_event(envelope: EventEnvelope):
    try:
        run_file = os.path.join(RAW_STORAGE_DIR, f"{envelope.node_id}.jsonl")
        with open(run_file, "a", encoding="utf-8") as f:
            f.write(envelope.model_dump_json() + "\n")
        return {"status": "INGESTED", "node_id": envelope.node_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
