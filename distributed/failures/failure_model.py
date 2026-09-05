"""
Formal Failure Model Definitions for Distributed Honeypot Testbed.
"""
import enum

class FailureType(enum.Enum):
    CRASH_STOP = "crash_stop"
    CRASH_RECOVERY = "crash_recovery"
    NETWORK_PARTITION = "network_partition"
    CLOCK_DRIFT = "clock_drift"
    PACKET_CORRUPTION = "packet_corruption"
