#!/usr/bin/env bash
set -euo pipefail
echo "[Fault Injection] Executing: restart_node.sh"
docker restart "benchmark_$1"
