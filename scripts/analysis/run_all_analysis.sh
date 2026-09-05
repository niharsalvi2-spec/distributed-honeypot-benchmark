#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

bash "${SCRIPT_DIR}/generate_report_data.sh"
bash "${SCRIPT_DIR}/generate_figures.sh"
bash "${SCRIPT_DIR}/generate_tables.sh"
python "${SCRIPT_DIR}/generate_benchmark_specs_from_yaml.py"

echo "[ANALYSIS] Complete analytical suite executed successfully."
