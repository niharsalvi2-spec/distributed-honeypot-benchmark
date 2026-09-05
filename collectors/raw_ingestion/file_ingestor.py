"""
File Ingestion Daemon.
Monitors native log files (e.g. cowrie.json, opencanary.log) and ingests into raw testbed storage.
"""
import os
import json
import shutil
import time
from typing import List

class FileIngestor:
    def __init__(self, target_raw_dir: str):
        self.target_raw_dir = target_raw_dir
        os.makedirs(target_raw_dir, exist_ok=True)

    def harvest_file(self, src_file: str, sensor_name: str) -> int:
        if not os.path.exists(src_file):
            return 0
        dst_file = os.path.join(self.target_raw_dir, f"{sensor_name}.jsonl")
        lines_copied = 0
        with open(src_file, "r", encoding="utf-8", errors="ignore") as sf, open(dst_file, "a", encoding="utf-8") as df:
            for line in sf:
                if line.strip():
                    df.write(line.strip() + "\n")
                    lines_copied += 1
        return lines_copied
