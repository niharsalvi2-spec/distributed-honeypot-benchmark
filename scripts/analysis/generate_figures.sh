#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BENCHMARK_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
export PYTHONPATH="${BENCHMARK_ROOT}:${PYTHONPATH:-}"

echo "[ANALYSIS] Generating empirical benchmark figures..."
python "${BENCHMARK_ROOT}/scripts/analysis/generate_figures.py"
echo "[ANALYSIS] Figures generated in artifacts/figures/"
