# E08: Node Crash and Failover Resilience

## Overview
Evaluates event loss and recovery latency during honeypot node crash-stop failures.

## Execution Architecture
- `runner.py`: Orchestrates lifecycle execution (`setup` -> `execute` -> `collect` -> `analyze`).
- `collect.py`: Ingests scenario telemetry, writes raw events to `data/raw/`, and outputs canonical normalized events to `data/normalized/<run_id>/`.
- `analyze.py`: Computes statistical metrics, hypothesis validation, and writes results to `results/<run_id>/metrics.json`.

## Reproduction Command
```bash
python experiments/E08_node_failure/runner.py
```
