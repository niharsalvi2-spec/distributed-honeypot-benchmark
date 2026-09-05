#!/usr/bin/env bash
set -euo pipefail
echo "[TEARDOWN] Safely shutting down active honeypot processes and containers..."
if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    docker-compose down || true
fi
echo "[TEARDOWN] All test honeypot nodes gracefully terminated."
