from pathlib import Path
import subprocess,os,json
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'output/arm_joint_variants'
app=Path.home()/'Applications/freecad-experiment/squashfs-root/AppRun'
env=os.environ.copy();env['PYTHONPATH']=str(app.parent/'usr/lib');env['QTWEBENGINE_DISABLE_SANDBOX']='1'
if not (OUT/'render_complete.txt').exists():
    with (OUT/'render.log').open('w') as f:subprocess.run([str(app),str(ROOT/'render_arm_joint_variants.FCMacro')],env=env,stdout=f,stderr=f,check=True)
assert (OUT/'render_complete.txt').exists()
config=(ROOT/'output/sail_80x120/slicer_check_0p2mm.ini').read_text()
(OUT/'slicer_check_0p2mm.ini').write_text(config)
cache=Path.home()/'.cache/angularmomflyer/slicer';exe=cache/'root/usr/bin/prusa-slicer'
env['LD_LIBRARY_PATH']=str(cache/'root/usr/lib/x86_64-linux-gnu')
results=[]
for row in json.loads((OUT/'validation.json').read_text())['parts']:
    path=cache/(row['id']+'_joint_check.gcode')
    r=subprocess.run([str(exe),'--load',str(OUT/'slicer_check_0p2mm.ini'),'--export-gcode','--center','110,110','--support-material','--output',str(path),str(OUT/row['file'])],env=env,capture_output=True,text=True)
    assert r.returncode==0,(row['id'],r.stderr)
    text=path.read_text();assert ';LAYER_CHANGE' in text
    results.append(dict(id=row['id'],status='PASS',layers=text.count(';LAYER_CHANGE'),warnings=r.stderr))
    print('Slice PASS '+row['id'],flush=True)
(OUT/'slice_validation.json').write_text(json.dumps(dict(status='PASS',nozzle_mm=.2,layer_mm=.12,results=results,scope='Toolpath generation, not calibrated machine G-code or print qualification.'),indent=2))
