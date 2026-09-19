#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
exec "$HOME/.venvs/angularmomflyer/bin/python" -m uvicorn server:app --host 127.0.0.1 --port 8766
