"""
Cryptographic Node Identity Generator.
Produces deterministic UUIDv5 identities based on node name and MAC/host seed.
"""
import uuid

class NodeIdentity:
    NAMESPACE_HONEYPOT = uuid.UUID('12345678-1234-5678-1234-567812345678')

    @classmethod
    def generate(cls, node_name: str) -> str:
        return str(uuid.uuid5(cls.NAMESPACE_HONEYPOT, node_name))
