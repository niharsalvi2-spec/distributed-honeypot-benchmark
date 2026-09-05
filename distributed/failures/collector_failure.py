"""
Collector Downtime Simulator.
Simulates central ingestion outages to evaluate node queue spooling.
"""
class CollectorFailureSimulator:
    def __init__(self):
        self.collector_active = True

    def pause(self):
        self.collector_active = False

    def resume(self):
        self.collector_active = True
