# E03: Interactive Session & Shell Command Capture

## Overview
Evaluates keystroke logging, interactive terminal command extraction, and shell sequence integrity.

## Execution Architecture
- `runner.py`: Orchestrates lifecycle execution (`setup` -> `execute` -> `collect` -> `analyze`).
- `collect.py`: Ingests scenario telemetry, writes raw events to `data/raw/`, and outputs canonical normalized events to `data/normalized/<run_id>/`.
- `analyze.py`: Computes statistical metrics, hypothesis validation, and writes results to `results/<run_id>/metrics.json`.

## Reproduction Command
```bash
python experiments/E03_session_capture/runner.py
```
