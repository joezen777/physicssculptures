#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
exec "$HOME/.venvs/angularmomflyer/bin/python" gyro_sim.py --view "$@"
