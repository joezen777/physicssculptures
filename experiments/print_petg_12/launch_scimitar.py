"""Build, inspect, render and package the experimental scimitar rotor in WSL."""
from pathlib import Path
import os,subprocess,json,zipfile
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output/scimitar_40mm'
exe=Path(os.getenv('FREECAD_APP',str(Path.home()/'Applications/freecad-experiment/squashfs-root/AppRun')))
OUT.mkdir(exist_ok=True)
for stale in ['render_complete.txt','render_error.txt','slice_validation.json']:(OUT/stale).unlink(missing_ok=True)
env=os.environ.copy();env['PYTHONPATH']=str(exe.parent/'usr/lib');env['QTWEBENGINE_DISABLE_SANDBOX']='1'
for script,cmd in [('build',[str(exe),'python',str(ROOT/'build_scimitar.py')]),
                   ('aero',['python3',str(ROOT/'screen_scimitar.py')]),
                   ('render',[str(exe),str(ROOT/'render_scimitar.FCMacro')]),
                   ('slice',['python3',str(ROOT/'check_scimitar_slicing.py')])]:
    with (ROOT/('scimitar_'+script+'.log')).open('w') as log:
        subprocess.run(cmd,env=env,stdout=log,stderr=log,check=True)
for name in ('validation.json','slice_validation.json'):
    assert json.loads((OUT/name).read_text())['status']=='PASS'
assert (OUT/'render_complete.txt').read_text().strip()=='PASS'
with zipfile.ZipFile(OUT.parent/'scimitar_40mm_prototype.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(OUT.iterdir()):
        if p.is_file() and p.suffix not in ('.FCBak','.FCStd1'):z.write(p,p.name)
print('Prototype packaged; no physical or CFD validation claimed.')
