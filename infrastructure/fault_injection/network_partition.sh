#!/usr/bin/env bash
set -euo pipefail
echo "[Fault Injection] Executing: network_partition.sh"
docker network disconnect benchmark-net "$1"
