from pathlib import Path
import subprocess,os,json
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'output/toroidal5_final'
cache=Path.home()/'.cache/angularmomflyer/slicer';env=os.environ.copy();env['LD_LIBRARY_PATH']=str(cache/'root/usr/lib/x86_64-linux-gnu')
changes={'nozzle_diameter':'0.6','layer_height':'0.25','first_layer_height':'0.25','extrusion_width':'0.66','external_perimeter_extrusion_width':'0.66','perimeter_extrusion_width':'0.66','first_layer_extrusion_width':'0.66','perimeters':'4','top_solid_layers':'5','bottom_solid_layers':'5','fill_density':'30%','brim_width':'0','support_material':'0','support_material_auto':'0','support_material_contact_distance':'0.5','support_material_xy_spacing':'0.6','perimeter_speed':'25','external_perimeter_speed':'20','infill_speed':'35','solid_infill_speed':'25','top_solid_infill_speed':'20','first_layer_speed':'15','max_volumetric_speed':'6','filament_max_volumetric_speed':'6'}
lines=[]
for line in (ROOT/'slicer_check.ini').read_text().splitlines():
 key=line.split('=')[0].strip();lines.append(key+' = '+changes[key] if key in changes else line)
lines+=['bridge_speed = 18','bridge_flow_ratio = 0.9','min_fan_speed = 25','max_fan_speed = 45','bridge_fan_speed = 70','disable_fan_first_layers = 3','threads = 4']
profile=OUT/'PETG_06nozzle_025layer_custom_supports.ini';profile.write_text('\n'.join(lines)+'\n')
results=[]
for name in ['P17_top_fan_B_integrated_supports_print-1x.stl','P185_print-1x.stl','P19_curved_guard_grille_print-1x.stl','C03_PETG_support_release_025_050_075.stl']:
 gcode=cache/(name[:-4]+'_06.gcode')
 r=subprocess.run([str(cache/'root/usr/bin/prusa-slicer'),'--load',str(profile),'--export-gcode','--center','110,110','--output',str(gcode),str(OUT/name)],env=env,capture_output=True,text=True)
 (OUT/(name[:-4]+'.slice.log')).write_text(r.stdout+'\n'+r.stderr)
 assert r.returncode==0,(name,r.stderr)
 txt=gcode.read_text();layers=txt.count(';LAYER_CHANGE');assert layers>0
 results.append({'file':name,'exit_code':r.returncode,'layer_changes':layers,'warnings':r.stderr,'gcode_for_inspection_only':str(gcode)})
 print(name,layers,r.stderr,flush=True)
(OUT/'slice_validation.json').write_text(json.dumps({'status':'PASS_TOOLPATH_GENERATION','nozzle_mm':.6,'layer_mm':.25,'auto_supports':False,'physically_tested':False,'results':results},indent=2)+'\n')

# Bind generated verification to the exact mesh files.
import hashlib
p=OUT/'slice_validation.json';j=json.loads(p.read_text());j['input_stl_sha256']={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in OUT.glob('*.stl')};p.write_text(json.dumps(j,indent=2)+'\n')
