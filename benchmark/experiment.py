"""
Base Experiment Abstract Class.
Defines the lifecycle: setup -> execute -> collect -> analyze -> teardown.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseExperiment(ABC):
    def __init__(self, experiment_id: str, config: Dict[str, Any]):
        self.experiment_id = experiment_id
        self.config = config
        self.run_id = None

    @abstractmethod
    def setup(self) -> bool:
        pass

    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def collect(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def analyze(self) -> Dict[str, Any]:
        pass

    def run_all(self) -> Dict[str, Any]:
        self.setup()
        exec_res = self.execute()
        coll_res = self.collect()
        anlz_res = self.analyze()
        return {
            "experiment": self.experiment_id,
            "execution": exec_res,
            "collection": coll_res,
            "analysis": anlz_res
        }
