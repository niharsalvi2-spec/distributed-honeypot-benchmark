"""
E01 Ingestion Benchmark Runner
Accepts --config parameter for configuration file input.
"""
import sys
import os
import argparse

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from experiments.E01_functional.runner import main as e01_main

def main():
    parser = argparse.ArgumentParser(description="E01 Baseline Ingestion Benchmark")
    parser.add_argument("--config", type=str, default="configs/experiments/E01.yaml", help="Configuration YAML path")
    args = parser.parse_args()
    e01_main()

if __name__ == "__main__":
    main()
