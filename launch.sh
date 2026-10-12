#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
exec "${ANGULARMOMFLYER_PYTHON:-.venv/bin/python}" gyro_sim.py --view "$@"
