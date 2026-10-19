"""Inspection-only toolpaths for the user's Ender 3 V2 / Sprite / 0.2 mm nozzle."""
from pathlib import Path
import subprocess,os,json,hashlib
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'output/p19_rain'
cache=Path.home()/'.cache/angularmomflyer/slicer'
env=os.environ.copy();env['LD_LIBRARY_PATH']=str(cache/'root/usr/lib/x86_64-linux-gnu')
changes={'nozzle_diameter':'0.2','layer_height':'0.12','first_layer_height':'0.16',
'extrusion_width':'0.22','external_perimeter_extrusion_width':'0.22','perimeter_extrusion_width':'0.22',
'first_layer_extrusion_width':'0.24','perimeters':'4','top_solid_layers':'8','bottom_solid_layers':'6',
'fill_density':'25%','brim_width':'4','support_material':'1','support_material_auto':'1',
'support_material_contact_distance':'0.18','support_material_xy_spacing':'0.3',
'support_material_buildplate_only':'0','support_material_spacing':'2',
'support_material_interface_layers':'2','support_material_pattern':'rectilinear',
'perimeter_speed':'20','external_perimeter_speed':'15','infill_speed':'25',
'solid_infill_speed':'20','top_solid_infill_speed':'15','first_layer_speed':'12',
'max_volumetric_speed':'2','filament_max_volumetric_speed':'2'}
lines=[]
seen=set()
for line in (ROOT/'slicer_check.ini').read_text().splitlines():
 key=line.split('=')[0].strip();seen.add(key)
 lines.append(key+' = '+changes[key] if key in changes else line)
lines.extend(k+' = '+v for k,v in changes.items() if k not in seen)
lines+=['bridge_speed = 15','bridge_flow_ratio = 0.9','threads = 4']
profile=OUT/'PETG_02nozzle_012layer_supports.ini';profile.write_text('\n'.join(lines)+'\n')
results=[]
for name in ['P19_rain.stl','P19C_rain.stl']:
 gcode=OUT/(name[:-4]+'.gcode')
 run=subprocess.run([str(cache/'root/usr/bin/prusa-slicer'),'--load',str(profile),
 '--export-gcode','--center','110,110','--output',str(gcode),str(OUT/name)],env=env,capture_output=True,text=True)
 (OUT/(name+'.slice.log')).write_text(run.stdout+'\n'+run.stderr)
 assert run.returncode==0,(name,run.stderr)
 txt=gcode.read_text()
 assert txt.count(';LAYER_CHANGE')>0
 assert ';TYPE:Support material' in txt
 results.append({'file':name,'exit_code':run.returncode,'layers':txt.count(';LAYER_CHANGE'),
 'warnings':run.stderr,'supports_generated':True,
 'statistics':[line for line in txt.splitlines() if line.startswith('; estimated printing time') or line.startswith('; filament used [g]')]})
 print(results[-1],flush=True)
report={'status':'PASS_TOOLPATH_GENERATION_ONLY','nozzle_mm':.2,'layer_mm':.12,
 'support_removal_physical_test_required':True,'results':results,
 'input_stl_sha256':{name:hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in ['P19_rain.stl','P19C_rain.stl']}}
(OUT/'slice_validation.json').write_text(json.dumps(report,indent=2)+'\n')
