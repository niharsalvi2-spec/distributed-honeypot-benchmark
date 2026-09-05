"""
Abstract Logical Clock Base Class.
"""
from abc import ABC, abstractmethod

class LogicalClock(ABC):
    @abstractmethod
    def tick(self):
        pass

    @abstractmethod
    def update(self, received):
        pass
