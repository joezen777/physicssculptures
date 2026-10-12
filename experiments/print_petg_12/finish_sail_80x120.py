from pathlib import Path
import subprocess,os,json,re
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'output/sail_80x120'
app=Path.home()/'Applications/freecad-experiment/squashfs-root/AppRun'
env=os.environ.copy();env['PYTHONPATH']=str(app.parent/'usr/lib');env['QTWEBENGINE_DISABLE_SANDBOX']='1'
if not (OUT/'render_complete.txt').exists():
    with (OUT/'render.log').open('w') as f:subprocess.run([str(app),str(ROOT/'render_sail_80x120.FCMacro')],env=env,stdout=f,stderr=f,check=True)
assert (OUT/'render_complete.txt').exists()
# The shared slicer_check.ini is the 0.4 mm inspection profile; sails also need supports off the part itself.
SAIL_OVERRIDES={'support_material_buildplate_only':'0'}
lines=[]
for line in (ROOT/'slicer_check.ini').read_text().splitlines():
    key=line.split('=')[0].strip()
    lines.append(key+' = '+SAIL_OVERRIDES[key] if '=' in line and key in SAIL_OVERRIDES else line)
config='\n'.join(lines)+'\n'
(OUT/'slicer_check_0p4mm.ini').write_text(config)
cache=Path.home()/'.cache/angularmomflyer/slicer';exe=cache/'root/usr/bin/prusa-slicer'
env['LD_LIBRARY_PATH']=str(cache/'root/usr/lib/x86_64-linux-gnu')
rows=[]
for part in [dict(id=p.name[:3],file=p.name) for p in sorted(OUT.glob('*.stl'))]:
    gcode=cache/(part['id']+'_sail80x120_0p4_check.gcode')
    r=subprocess.run([str(exe),'--load',str(OUT/'slicer_check_0p4mm.ini'),'--export-gcode','--center','110,110','--support-material','--output',str(gcode),str(OUT/part['file'])],env=env,capture_output=True,text=True)
    assert r.returncode==0,r.stderr
    text=gcode.read_text()
    assert ';LAYER_CHANGE' in text and 'G1 ' in text
    rows.append(dict(part=part['id'],status='PASS',layers=text.count(';LAYER_CHANGE'),filament_mm=float(re.search(r'; filament used \[mm\] = ([\d.]+)',text).group(1)),warnings=r.stderr.strip()))
(OUT/'slice_validation.json').write_text(json.dumps(dict(status='PASS',nozzle_mm=.4,layer_mm=.2,results=rows,scope='Geometry toolpath check only; no calibrated machine G-code supplied.'),indent=2))
print('Render and slice checks passed.')
