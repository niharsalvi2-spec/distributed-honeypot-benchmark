#!/usr/bin/env bash
set -euo pipefail
echo "[Fault Injection] Executing: kill_node.sh"
docker stop "benchmark_$1"
