"""Build and open the separate bevel variant in WSL FreeCAD."""
from pathlib import Path
import os,subprocess
root=Path(__file__).resolve().parent
env=os.environ.copy();env["QTWEBENGINE_DISABLE_SANDBOX"]="1"
exe=os.environ.get("FREECAD_APP",str(Path.home()/"Applications/freecad-experiment/squashfs-root/AppRun"))
with (root/"build.log").open("w") as log:
    subprocess.Popen([exe,str(root/"build.FCMacro")],stdout=log,stderr=log,env=env,start_new_session=True)
