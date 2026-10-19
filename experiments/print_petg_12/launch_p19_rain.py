from pathlib import Path
import subprocess,os,sys
root=Path(__file__).resolve().parent
exe=Path.home()/'Applications/freecad-experiment/squashfs-root/AppRun'
env=os.environ.copy();env['PYTHONPATH']=str(exe.parent/'usr/lib')
subprocess.run([str(exe),'python',str(root/(sys.argv[1] if len(sys.argv)>1 else 'build_p19_rain.py'))],env=env,check=True)
