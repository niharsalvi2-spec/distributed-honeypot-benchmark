"""
Network Partition and Packet Delay Simulator.
"""
import time
import random

class NetworkFailureSimulator:
    @staticmethod
    def simulate_delay(min_ms: float = 50.0, max_ms: float = 300.0):
        delay = random.uniform(min_ms, max_ms) / 1000.0
        time.sleep(delay)
