from pathlib import Path
import subprocess,os,json
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'output/sail_80x120'
app=Path.home()/'Applications/freecad-experiment/squashfs-root/AppRun'
env=os.environ.copy();env['PYTHONPATH']=str(app.parent/'usr/lib');env['QTWEBENGINE_DISABLE_SANDBOX']='1'
if not (OUT/'render_complete.txt').exists():
    with (OUT/'render.log').open('w') as f:subprocess.run([str(app),str(ROOT/'render_sail_80x120.FCMacro')],env=env,stdout=f,stderr=f,check=True)
assert (OUT/'render_complete.txt').exists()
config=(ROOT/'slicer_check.ini').read_text().replace('= 1.2\n','= 0.2\n').replace('= 1.32','= 0.22').replace('= 0.4','= 0.12').replace('support_material_buildplate_only = 1','support_material_buildplate_only = 0')
(OUT/'slicer_check_0p2mm.ini').write_text(config)
cache=Path.home()/'.cache/angularmomflyer/slicer';exe=cache/'root/usr/bin/prusa-slicer'
env['LD_LIBRARY_PATH']=str(cache/'root/usr/lib/x86_64-linux-gnu')
rows=[]
for part in [dict(id=p.name[:3],file=p.name) for p in sorted(OUT.glob('*.stl'))]:
    gcode=cache/(part['id']+'_sail80x120_check.gcode')
    r=subprocess.run([str(exe),'--load',str(OUT/'slicer_check_0p2mm.ini'),'--export-gcode','--center','110,110','--support-material','--output',str(gcode),str(OUT/part['file'])],env=env,capture_output=True,text=True)
    assert r.returncode==0,r.stderr
    text=gcode.read_text()
    assert ';LAYER_CHANGE' in text and 'G1 ' in text
    rows.append(dict(part=part['id'],status='PASS',layers=text.count(';LAYER_CHANGE'),warnings=r.stderr))
(OUT/'slice_validation.json').write_text(json.dumps(dict(status='PASS',nozzle_mm=.2,layer_mm=.12,results=rows,scope='Geometry toolpath check only; no calibrated machine G-code supplied.'),indent=2))
print('Render and slice checks passed.')
