#!/usr/bin/env bash
# ==============================================================================
# Automated Experiment Runner: E10_scalability
# Distributed Honeypot Benchmark Framework
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BENCHMARK_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

export PYTHONPATH="${BENCHMARK_ROOT}:${PYTHONPATH:-}"

echo "======================================================================"
echo "[RUNNER] Initializing Experiment E10_scalability"
echo "Benchmark Root: ${BENCHMARK_ROOT}"
echo "Timestamp:      $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "======================================================================"

python "${BENCHMARK_ROOT}/experiments/E10_scalability/runner.py"

EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "[SUCCESS] Experiment E10_scalability executed successfully."
else
    echo "[ERROR] Experiment E10_scalability failed with exit code $EXIT_CODE." >&2
    exit $EXIT_CODE
fi
