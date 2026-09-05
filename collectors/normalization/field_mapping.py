"""
Field Mapping Dictionary.
Formal translation rules between native repository keys and canonical schema.
"""
CANONICAL_FIELD_MAPPING = {
    "cowrie": {
        "src_ip": "source.ip",
        "src_port": "source.port",
        "dst_port": "service.service_port",
        "session": "session_id",
        "timestamp": "timestamps.physical_raw",
        "input": "payload.command"
    },
    "opencanary": {
        "src_host": "source.ip",
        "src_port": "source.port",
        "dst_port": "service.service_port",
        "utc_time": "timestamps.physical_raw"
    },
    "dionaea": {
        "remote_host": "source.ip",
        "remote_port": "source.port",
        "local_port": "service.service_port",
        "timestamp": "timestamps.physical_raw"
    }
}
