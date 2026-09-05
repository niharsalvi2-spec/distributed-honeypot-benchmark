#!/usr/bin/env bash
set -euo pipefail
RUN_ID="${1:-all}"
echo "[COLLECTION] Evaluating metrics for run: ${RUN_ID}"
