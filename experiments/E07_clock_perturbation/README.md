# E07: Clock Perturbation and Event Ordering Degradation

## Overview
Evaluates physical timestamp inversion rates vs Lamport and Vector clocks under clock drift, skew, and network jitter.

## Execution Architecture
- `runner.py`: Orchestrates lifecycle execution (`setup` -> `execute` -> `collect` -> `analyze`).
- `collect.py`: Ingests scenario telemetry, writes raw events to `data/raw/`, and outputs canonical normalized events to `data/normalized/<run_id>/`.
- `analyze.py`: Computes statistical metrics, hypothesis validation, and writes results to `results/<run_id>/metrics.json`.

## Reproduction Command
```bash
python experiments/E07_clock_perturbation/runner.py
```
