#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BENCHMARK_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

RUN_ID="${1:-default_run}"
REPO="${2:-cowrie}"

echo "[COLLECTION] Harvesting raw telemetry for Repo: ${REPO} | Run: ${RUN_ID}..."
python -c "
from benchmark.collector import BenchmarkCollector
c = BenchmarkCollector(r'${BENCHMARK_ROOT}/data/raw')
print('Collector ready for staging.')
"
