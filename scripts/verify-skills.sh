#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "Redirecting to python version..."
python3 scripts/verify-skills.py "$@"
