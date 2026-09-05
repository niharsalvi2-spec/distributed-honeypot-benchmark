#!/usr/bin/env bash
set -euo pipefail
echo "[Fault Injection] Executing: stop_collector.sh"
docker stop benchmark_collector
