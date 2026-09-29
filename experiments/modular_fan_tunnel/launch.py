"""Build the modular fan tunnel in Linux FreeCAD or Open STEP Viewer."""
from pathlib import Path
import argparse,subprocess,os
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument("--render",action="store_true")
p.add_argument("--viewer",action="store_true")
p.add_argument("--keep-open",action="store_true",help="Keep FreeCAD open with animation after building")
a=p.parse_args()
if a.viewer:
    step=ROOT/"output/tower_full.step"
    if not step.exists():raise SystemExit("Build the FreeCAD draft first.")
    target=subprocess.check_output(["wslpath","-w",str(step)],text=True).strip()
    subprocess.Popen(["/mnt/c/Program Files/ODA/Open STEP Viewer 25.2.0/OpenSTEPViewer.exe",target],
                     stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
else:
    exe=os.environ.get("FREECAD_APP",str(Path.home()/"Applications/freecad-experiment/squashfs-root/AppRun"))
    env=os.environ.copy();env["TOWER_RENDER"]="1" if a.render else "0"
    env["TOWER_KEEP_OPEN"]="1" if a.keep_open else "0"
    env["QTWEBENGINE_DISABLE_SANDBOX"]="1"
    runtime=Path.home()/".cache/angularmomflyer/freecad-modular"
    runtime.mkdir(parents=True,exist_ok=True)
    env["FREECAD_USER_HOME"]=str(runtime)
    env["XDG_CONFIG_HOME"]=str(runtime/"config")
    with open(ROOT/"build.log","w") as log:
        subprocess.Popen([exe,str(ROOT/"run.FCMacro")],env=env,stdout=log,stderr=log,start_new_session=True)
