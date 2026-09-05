#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BENCHMARK_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

python -c "
import os
repos = ['cowrie', 'opencanary', 'dionaea', 'tpot', 'mhn', 'conpot', 'honeytrap']
root = r'${BENCHMARK_ROOT}/repositories'
for r in repos:
    p = os.path.join(root, r)
    is_ok = os.path.isdir(p)
    print(f'Repository {r:12}: {"CLONED & VERIFIED" if is_ok else "MISSING"}')
"
