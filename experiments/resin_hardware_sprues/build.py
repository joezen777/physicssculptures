"""Compatibility entry point: run the analytic mesh generator in its WSL environment."""
from pathlib import Path
import os,subprocess
ROOT=Path(__file__).resolve().parent
python=Path.home()/".cache/angularmomflyer/meshchecks/bin/python"
env={k:v for k,v in os.environ.items() if k not in ["PYTHONHOME","PYTHONPATH","LD_LIBRARY_PATH"]}
subprocess.run([str(python),str(ROOT/"mesh_build.py")],env=env,check=True)
