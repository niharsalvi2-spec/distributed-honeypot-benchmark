# E06: Interleaved Concurrent Attack Separation

## Overview
Evaluates causal graph disambiguation of multiple concurrent attackers executing overlapping traces.

## Execution Architecture
- `runner.py`: Orchestrates lifecycle execution (`setup` -> `execute` -> `collect` -> `analyze`).
- `collect.py`: Ingests scenario telemetry, writes raw events to `data/raw/`, and outputs canonical normalized events to `data/normalized/<run_id>/`.
- `analyze.py`: Computes statistical metrics, hypothesis validation, and writes results to `results/<run_id>/metrics.json`.

## Reproduction Command
```bash
python experiments/E06_interleaved_attackers/runner.py
```
