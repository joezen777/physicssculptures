"""Rebuild and check the PETG print set in WSL Ubuntu; close FreeCAD after rendering."""
from pathlib import Path
import os,subprocess,json,argparse
ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--render-only",action="store_true")
parser.add_argument("--slice-check",action="store_true",help="Use the locally cached PrusaSlicer for toolpath checks")
args=parser.parse_args()
exe=Path(os.getenv("FREECAD_APP",str(Path.home()/"Applications/freecad-experiment/squashfs-root/AppRun")))
env=os.environ.copy();env["PYTHONPATH"]=str(exe.parent/"usr/lib")
def run(script):subprocess.run([str(exe),"python",str(ROOT/script)],env=env,check=True)
if not args.render_only:
    run("build.py");run("validate.py");run("check_fasteners.py")
    for f in ["validation.json","fastener_validation.json"]:
        assert json.loads((ROOT/"output"/f).read_text())["status"]=="PASS",f
    if args.slice_check:subprocess.run(["python3",str(ROOT/"check_slicing.py")],check=True)
runtime=Path.home()/".cache/angularmomflyer/freecad-print12";runtime.mkdir(parents=True,exist_ok=True)
env["FREECAD_USER_HOME"]=str(runtime);env["XDG_CONFIG_HOME"]=str(runtime/"config")
env["QTWEBENGINE_DISABLE_SANDBOX"]="1"
with (ROOT/"render.log").open("w") as log:
    subprocess.run([str(exe),str(ROOT/"render.FCMacro")],env=env,stdout=log,stderr=log,check=True)
assert (ROOT/"output/render_complete.txt").exists()
run("make_poster.py")
subprocess.run(["python3",str(ROOT/"package.py")],check=True)
print("CAD and previews saved. FreeCAD has exited.")
