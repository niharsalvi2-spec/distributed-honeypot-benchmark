#!/usr/bin/env bash
set -euo pipefail
echo "[Fault Injection] Executing: packet_delay.sh"
tc qdisc add dev eth0 root netem delay "${1:-250ms}" "${2:-50ms}"
