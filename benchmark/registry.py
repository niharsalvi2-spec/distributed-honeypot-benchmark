"""
Experiment Registry.
"""
from typing import Dict, Type, Optional
from benchmark.experiment import BaseExperiment

class ExperimentRegistry:
    _registry: Dict[str, Type[BaseExperiment]] = {}

    @classmethod
    def register(cls, exp_id: str, exp_cls: Type[BaseExperiment]):
        cls._registry[exp_id] = exp_cls

    @classmethod
    def get(cls, exp_id: str) -> Optional[Type[BaseExperiment]]:
        return cls._registry.get(exp_id)
