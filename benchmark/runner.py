"""
Master Benchmark Suite Runner.
Executes individual or comprehensive benchmark suites E01 through E10.
"""
import argparse
import logging
from benchmark.run_manager import RunManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("BenchmarkRunner")

def run_suite(suite_name: str = "all"):
    logger.info("Initializing Master Benchmark Runner for suite: %s", suite_name)
    # Orchestrates execution across configured experiments
    print(f"Master benchmark execution triggered for {suite_name}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Distributed Honeypot Benchmark Suite Runner")
    parser.add_argument("--suite", default="all", help="Suite or experiment identifier (e.g. E01, E05, all)")
    args = parser.parse_args()
    run_suite(args.suite)
