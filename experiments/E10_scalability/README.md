# E10: High-Rate Scalability & Resource Saturation

## Overview
Evaluates Events Per Second (EPS) throughput, memory growth slope, and CPU utilization under heavy workload.

## Execution Architecture
- `runner.py`: Orchestrates lifecycle execution (`setup` -> `execute` -> `collect` -> `analyze`).
- `collect.py`: Ingests scenario telemetry, writes raw events to `data/raw/`, and outputs canonical normalized events to `data/normalized/<run_id>/`.
- `analyze.py`: Computes statistical metrics, hypothesis validation, and writes results to `results/<run_id>/metrics.json`.

## Reproduction Command
```bash
python experiments/E10_scalability/runner.py
```
