"""Launch the first stacking-cone draft in Linux FreeCAD or Open STEP Viewer."""
from pathlib import Path
import argparse,subprocess,os
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument("--render",action="store_true")
p.add_argument("--viewer",action="store_true")
a=p.parse_args()
if a.viewer:
    step=ROOT/"output/tower_cutaway.step"
    if not step.exists():raise SystemExit("Build the FreeCAD draft first.")
    target=subprocess.check_output(["wslpath","-w",str(step)],text=True).strip()
    subprocess.Popen(["/mnt/c/Program Files/ODA/Open STEP Viewer 25.2.0/OpenSTEPViewer.exe",target],
                     stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
else:
    exe=os.environ.get("FREECAD_APP",str(Path.home()/"Applications/freecad-experiment/squashfs-root/AppRun"))
    env=os.environ.copy();env["TOWER_RENDER"]="1" if a.render else "0"
    env["QTWEBENGINE_DISABLE_SANDBOX"]="1"
    with open(ROOT/"build.log","w") as log:
        subprocess.Popen([exe,str(ROOT/"build.FCMacro")],env=env,stdout=log,stderr=log,start_new_session=True)
