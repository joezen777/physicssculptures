from pathlib import Path
import subprocess,os,json
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'output/sail_80x120'
app=Path.home()/'Applications/freecad-experiment/squashfs-root/AppRun'
env=os.environ.copy();env['PYTHONPATH']=str(app.parent/'usr/lib');env['QTWEBENGINE_DISABLE_SANDBOX']='1'
if not (OUT/'render_complete.txt').exists():
    with (OUT/'render.log').open('w') as f:subprocess.run([str(app),str(ROOT/'render_sail_80x120.FCMacro')],env=env,stdout=f,stderr=f,check=True)
assert (OUT/'render_complete.txt').exists()
# Explicit 0.2 mm overrides: the shared slicer_check.ini base profile changes nozzle over time.
SAIL_0P2={'nozzle_diameter':'0.2','layer_height':'0.12','first_layer_height':'0.12','extrusion_width':'0.22',
    'external_perimeter_extrusion_width':'0.22','perimeter_extrusion_width':'0.22','first_layer_extrusion_width':'0.22',
    'perimeters':'3','top_solid_layers':'6','bottom_solid_layers':'6','perimeter_speed':'10','external_perimeter_speed':'8',
    'infill_speed':'10','solid_infill_speed':'10','top_solid_infill_speed':'8','first_layer_speed':'6',
    'max_volumetric_speed':'5','filament_max_volumetric_speed':'5','support_material_buildplate_only':'0',
    'support_material_contact_distance':'0.12','support_material_xy_spacing':'0.2','support_material_spacing':'3','support_material_speed':'8'}
lines=[]
for line in (ROOT/'slicer_check.ini').read_text().splitlines():
    key=line.split('=')[0].strip()
    lines.append(key+' = '+SAIL_0P2[key] if '=' in line and key in SAIL_0P2 else line)
config='\n'.join(lines)+'\n'
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
