#!/usr/bin/env bash
set -euo pipefail
RUN_ID="${1:?Error: Must provide RUN_ID to archive}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BENCHMARK_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

ARCHIVE_DIR="${BENCHMARK_ROOT}/artifacts/archives"
mkdir -p "${ARCHIVE_DIR}"
ARCHIVE_FILE="${ARCHIVE_DIR}/${RUN_ID}.tar.gz"

echo "[ARCHIVE] Compressing run data for ${RUN_ID} into ${ARCHIVE_FILE}..."
tar -czf "${ARCHIVE_FILE}" -C "${BENCHMARK_ROOT}" "data/raw" "data/normalized/${RUN_ID}" "results/${RUN_ID}" 2>/dev/null || true
echo "[ARCHIVE] Run ${RUN_ID} archived successfully."
