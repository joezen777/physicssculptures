"""Inspect toolpaths using 0.2 mm nozzle settings; no printer execution."""
from pathlib import Path
import subprocess,os,json,zipfile
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output/scimitar_40mm'
cache=Path.home()/'.cache/angularmomflyer/slicer'
env=os.environ.copy();env['LD_LIBRARY_PATH']=str(cache/'root/usr/lib/x86_64-linux-gnu')
text=(ROOT/'slicer_check.ini').read_text()
changes={'nozzle_diameter':'0.2','layer_height':'0.12','first_layer_height':'0.16',
'extrusion_width':'0.22','external_perimeter_extrusion_width':'0.22',
'perimeter_extrusion_width':'0.22','first_layer_extrusion_width':'0.24','perimeters':'5',
'support_material':'1','support_material_buildplate_only':'0','support_material_contact_distance':'0.16',
'support_material_xy_spacing':'0.35','support_material_spacing':'1.5','brim_width':'6'}
lines=[]
for line in text.splitlines():
    key=line.split('=')[0].strip()
    lines.append(key+' = '+changes[key] if key in changes else line)
profile=OUT/'inspection_0p2mm.ini';profile.write_text('\n'.join(lines)+'\n')
reports=[]
for key in ['P17S','P18S']:
    gcode=cache/(key+'_scimitar_check.gcode')
    cmd=[str(cache/'root/usr/bin/prusa-slicer'),'--load',str(profile),'--export-gcode','--center','110,110','--output',str(gcode),str(OUT/(key+'_print-1x.stl'))]
    r=subprocess.run(cmd,env=env,capture_output=True,text=True)
    (ROOT/(key+'_scimitar_slice.log')).write_text(r.stdout+'\n'+r.stderr)
    assert r.returncode==0,(key,r.stderr)
    layers=0;moves=0
    for line in gcode.open():
        layers+=line.startswith(';LAYER_CHANGE')
        moves+=line.startswith('G1 ') and ' E' in line and (' X' in line or ' Y' in line)
    assert layers>0 and moves>0
    reports.append(dict(part=key,layers=layers,extruding_moves=moves,exit_code=r.returncode,warnings=r.stderr))
report=dict(status='PASS',nozzle_mm=.2,layer_mm=.12,supports='everywhere',scope='Toolpath generation only; not calibrated machine G-code',results=reports)
(OUT/'slice_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
