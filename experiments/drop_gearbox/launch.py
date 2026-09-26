"""Launch Linux FreeCAD and optionally the installed Windows Open STEP Viewer from WSL."""
import argparse
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--viewer",action="store_true",help="Open cutaway STEP in installed ODA viewer")
parser.add_argument("--render",action="store_true",help="Also save 72 animation frames")
parser.add_argument("--rebuild",action="store_true",help="Regenerate geometry and STEP exports")
parser.add_argument("--magnetic",action="store_true",help="Use the magnetic concept variant")
args=parser.parse_args()
if args.viewer:
    exe=Path("/mnt/c/Program Files/ODA/Open STEP Viewer 25.2.0/OpenSTEPViewer.exe")
    step=ROOT/("magnetic_output/magnetic_cutaway.step" if args.magnetic else "output/drop_gearbox_cutaway.step")
    if not step.exists(): raise SystemExit("Run FreeCAD generation first.")
    winpath=subprocess.check_output(["wslpath","-w",str(step)],text=True).strip()
    subprocess.Popen([str(exe),winpath],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
else:
    default=Path.home()/"Applications/freecad-experiment/squashfs-root/AppRun"
    exe=Path(os.environ.get("FREECAD_APP",str(default)))
    if not exe.exists(): raise SystemExit("Set FREECAD_APP to your Linux FreeCAD executable or AppRun.")
    env=os.environ.copy();env["DROP_RENDER"]="1" if args.render else "0"
    env["QTWEBENGINE_DISABLE_SANDBOX"]="1"
    log=open(ROOT/"freecad.log","w")
    subprocess.Popen([str(exe),str(ROOT/("magnetic.FCMacro" if args.magnetic else "build.FCMacro" if args.rebuild or not (ROOT/"output/drop_gearbox.FCStd").exists() else "animate.FCMacro"))],env=env,stdout=log,stderr=log,start_new_session=True)
