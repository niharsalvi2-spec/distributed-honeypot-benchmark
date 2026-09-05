"""
Recovery & Buffer Synchronization Manager.
Flushes locally spooled buffers upon reconnection to the central collector.
"""
from distributed.communication.queue import ResilientQueue
from distributed.communication.transport import Transport

class RecoveryManager:
    @staticmethod
    def flush_spool(queue: ResilientQueue, transport: Transport) -> int:
        flushed = 0
        while True:
            msg = queue.get(block=False)
            if not msg:
                break
            if transport.send(msg):
                flushed += 1
            else:
                queue.put(msg)
                break
        return flushed
