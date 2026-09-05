#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BENCHMARK_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
export PYTHONPATH="${BENCHMARK_ROOT}:${PYTHONPATH:-}"

echo "[ANALYSIS] Aggregating multi-run results..."
python -c "
import os, json, glob

results_dir = r'${BENCHMARK_ROOT}/results'
runs = glob.glob(os.path.join(results_dir, 'E*_*'))
summary = {}
for r in runs:
    mp = os.path.join(r, 'metrics.json')
    if os.path.exists(mp):
        with open(mp, 'r', encoding='utf-8') as f:
            summary[os.path.basename(r)] = json.load(f)

final_dir = os.path.join(results_dir, 'final')
os.makedirs(final_dir, exist_ok=True)
with open(os.path.join(final_dir, 'summary_report.json'), 'w', encoding='utf-8') as f:
    json.dump(summary, f, indent=2)
print(f'Aggregated {len(summary)} experiment runs into results/final/summary_report.json')
"
