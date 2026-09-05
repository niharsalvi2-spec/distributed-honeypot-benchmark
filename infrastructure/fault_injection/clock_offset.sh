#!/usr/bin/env bash
set -euo pipefail
echo "[Fault Injection] Executing: clock_offset.sh"
date -s "@$(($(date +%s) + ${1:-5}))"
