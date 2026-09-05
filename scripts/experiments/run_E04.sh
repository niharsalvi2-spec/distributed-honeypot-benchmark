#!/usr/bin/env bash
# ==============================================================================
# Automated Experiment Runner: E04_cross_service
# Distributed Honeypot Benchmark Framework
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BENCHMARK_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

export PYTHONPATH="${BENCHMARK_ROOT}:${PYTHONPATH:-}"

echo "======================================================================"
echo "[RUNNER] Initializing Experiment E04_cross_service"
echo "Benchmark Root: ${BENCHMARK_ROOT}"
echo "Timestamp:      $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "======================================================================"

python "${BENCHMARK_ROOT}/experiments/E04_cross_service/runner.py"

EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "[SUCCESS] Experiment E04_cross_service executed successfully."
else
    echo "[ERROR] Experiment E04_cross_service failed with exit code $EXIT_CODE." >&2
    exit $EXIT_CODE
fi
