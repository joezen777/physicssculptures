"""Generate and preview the resin sprue kit in WSL; close FreeCAD when finished."""
from pathlib import Path
import os,subprocess,argparse
ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--render-only",action="store_true");args=parser.parse_args()
exe=Path.home()/"Applications/freecad-experiment/squashfs-root/AppRun"
env=os.environ.copy();env["PYTHONPATH"]=str(exe.parent/"usr/lib")
def run(name):subprocess.run([str(exe),"python",str(ROOT/name)],env=env,check=True)
if not args.render_only:run("build.py")
runtime=Path.home()/".cache/angularmomflyer/freecad-resin";runtime.mkdir(parents=True,exist_ok=True)
env["FREECAD_USER_HOME"]=str(runtime);env["XDG_CONFIG_HOME"]=str(runtime/"config");env["QTWEBENGINE_DISABLE_SANDBOX"]="1"
for name in ["render_complete.txt","render_error.log"]:(ROOT/name).unlink(missing_ok=True)
with (ROOT/"render.log").open("w") as log:
    subprocess.run([str(exe),str(ROOT/"render.FCMacro")],env=env,stdout=log,stderr=log,check=True)
assert (ROOT/"render_complete.txt").exists(),(ROOT/"render_error.log").read_text()
run("finish.py")
print("Resin kit packaged. FreeCAD is closed.",flush=True)
