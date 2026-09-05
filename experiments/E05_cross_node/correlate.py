"""
Correlation Engine: E05_cross_node
"""
from typing import List, Dict, Any
from correlation.cross_service.session_linker import SessionLinker

def execute_correlation(events: List[Dict[str, Any]]):
    linker = SessionLinker()
    return linker
