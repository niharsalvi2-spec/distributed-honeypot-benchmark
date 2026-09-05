#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BENCHMARK_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
export PYTHONPATH="${BENCHMARK_ROOT}:${PYTHONPATH:-}"

echo "[ANALYSIS] Compiling research paper tables..."
python "${BENCHMARK_ROOT}/scripts/analysis/generate_tables.py"
echo "[ANALYSIS] Tables written to artifacts/tables/"
