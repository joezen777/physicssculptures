#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PYTHON="${WHISTLE_PYTHON:-$HOME/.venvs/angularmomflyer/bin/python}"
if [ ! -f web/dist/whistle.html ]; then
  echo "Build the frontend first: cd web && npm run build"
  exit 1
fi
exec "$PYTHON" whistle_server.py
