"""
Thread-safe Message Queue with Local Disk Spooling for Network Partition Tolerance.
"""
import queue
import os
import json
from typing import Optional, Any
from distributed.communication.message import Message

class ResilientQueue:
    def __init__(self, maxsize: int = 10000, spool_file: Optional[str] = None):
        self._queue = queue.Queue(maxsize=maxsize)
        self.spool_file = spool_file
        if spool_file and os.path.exists(spool_file):
            self._recover_spool()

    def put(self, message: Message, block: bool = True, timeout: Optional[float] = None) -> bool:
        try:
            self._queue.put(message, block=block, timeout=timeout)
            return True
        except queue.Full:
            if self.spool_file:
                self._spool_to_disk(message)
                return True
            return False

    def get(self, block: bool = True, timeout: Optional[float] = None) -> Optional[Message]:
        try:
            return self._queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None

    def size(self) -> int:
        return self._queue.qsize()

    def _spool_to_disk(self, message: Message):
        with open(self.spool_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(message.to_dict()) + "\n")

    def _recover_spool(self):
        with open(self.spool_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line.strip())
                    self._queue.put(Message.from_dict(data))
        # Clear spool after loading
        with open(self.spool_file, "w", encoding="utf-8") as f:
            pass

class ResilientDiskQueue:
    """
    Disk-backed persistent queue for partition tolerance during collector outages.
    """
    def __init__(self, spool_dir: str):
        self.spool_dir = spool_dir
        os.makedirs(spool_dir, exist_ok=True)
        self.spool_file = os.path.join(spool_dir, "queue_spool.jsonl")
        self._memory_queue = []
        if os.path.exists(self.spool_file):
            with open(self.spool_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        self._memory_queue.append(json.loads(line.strip()))

    def enqueue(self, item: Any):
        self._memory_queue.append(item)
        with open(self.spool_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(item) + "\n")

    def dequeue(self) -> Optional[Any]:
        if not self._memory_queue:
            return None
        item = self._memory_queue.pop(0)
        with open(self.spool_file, "w", encoding="utf-8") as f:
            for it in self._memory_queue:
                f.write(json.dumps(it) + "\n")
        return item

    def is_empty(self) -> bool:
        return len(self._memory_queue) == 0

    def size(self) -> int:
        return len(self._memory_queue)
