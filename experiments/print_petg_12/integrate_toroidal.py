"""Update only the top rotor/guard and 500 mm rod hardware in the current assembly."""
from pathlib import Path
import json,csv,shutil,zipfile,hashlib
import FreeCAD as App,Part
from FreeCAD import Vector as V
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'output';RELEASE=OUT/'toroidal5_final';STL=OUT/'stl'
geo=json.loads((RELEASE/'geometry_validation.json').read_text());slicing=json.loads((RELEASE/'slice_validation.json').read_text());supports=json.loads((RELEASE/'support_validation.json').read_text())
assert geo['closed_loop_passages']==5 and geo['hub_interface_delta_mm3']<1e-5
assert slicing['status']=='PASS_TOOLPATH_GENERATION' and supports['rotor_support_overlap_mm3']<1e-4
cura=json.loads((RELEASE/'cura_toolpath_validation.json').read_text())
assert cura['engine_exit_code']==0
assert cura['supported_stl_sha256']==hashlib.sha256((RELEASE/'P17_top_fan_B_integrated_supports_print-1x.stl').read_bytes()).hexdigest()
for report in [geo,slicing,supports]:
 for filename,digest in report['input_stl_sha256'].items():
  assert hashlib.sha256((RELEASE/filename).read_bytes()).hexdigest()==digest,filename
oldfiles=['P17_top_fan_B_print-1x.stl','P18_top_guard_shroud_print-1x.stl','P19_curved_guard_grille_print-1x.stl']
archive=OUT/'retired_top_fan_before_toroidal5.zip'
if not archive.exists():
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for name in oldfiles:z.write(STL/name,name)
  z.writestr('RETIRED.txt','Superseded top fan and shorter guard. Do not mix with the 500 mm rod / 53 mm top spacer release.\n')
source=App.openDocument(str(OUT/'print_prototype.FCStd'));new=App.openDocument(str(RELEASE/'toroidal5_final.FCStd'))
scene=json.loads((OUT/'scene.json').read_text())
for row in scene:
 o=source.getObject(row['name']);key=row['key'];s=o.Shape.copy()
 if key in ['P17','P18','P19']:
  o.Shape=new.getObject(key).Shape.copy()
  if key=='P17':o.Label='P17 toroidal5 top fan'
 elif key=='M8_rod':
  o.Shape=Part.makeCylinder(4,500,V(0,0,-68));o.Label='M8 steel threaded rod, 500 mm end to end'
 elif row.get('stage')==3 and key in ['T8_21','T8_53']:
  o.Shape=Part.makeCylinder(6,53,V(0,0,359)).cut(Part.makeCylinder(4.1,53,V(0,0,359)));o.Label='Steel tube ID8.2 OD12 L53';o.PartID='T8_53';row['key']='T8_53'
 elif row.get('stage')==3 and key in ['M8_nut','M8_acorn']:
  target=412 if key=='M8_nut' else 424;s.translate(V(0,0,target-s.BoundBox.ZMin));o.Shape=s
 center=o.Shape.BoundBox.Center;row['center']=[center.x,center.y,center.z]
source.recompute();source.save()
(OUT/'scene.json').write_text(json.dumps(scene,indent=2)+'\n')
for name in ['P17_top_fan_B_print-1x.stl','P17_top_fan_B_integrated_supports_print-1x.stl','P19_curved_guard_grille_print-1x.stl','P185_print-1x.stl','C03_PETG_support_release_025_050_075.stl']:
 shutil.copy2(RELEASE/name,STL/name)
shutil.copy2(RELEASE/'P185_print-1x.stl',STL/'P18_top_guard_shroud_print-1x.stl')
parts=json.loads((OUT/'parts.json').read_text());byid={r['id']:r for r in geo['parts']}
for r in parts:
 if r['id'] in byid:
  newpart=byid[r['id']];r.update(size_mm=[round(x,2) for x in newpart['dimensions_mm']],triangles=newpart['triangles'],volume_mm3=newpart['volume_mm3'])
  if r['id']=='P17':r.update(support='Use integrated-support alternate STL; auto supports OFF',orientation='upright',note='Toroidal5; 0.6 mm nozzle, 0.25 mm layers. Print bare OR supported, not both.')
  elif r['id']=='P18':r.update(orientation='upside_down',support='None',note='72 mm tall; alias P185_print-1x.stl. Requires 500 mm rod and 53 mm top steel spacer.')
  else:r['note']='Geometry unchanged; install at z=412, raised 32 mm. Existing grille reusable.'
(OUT/'parts.json').write_text(json.dumps(parts,indent=2)+'\n')
with (OUT/'print_manifest.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(parts[0]),lineterminator='\n');w.writeheader();w.writerows(parts)
p=OUT/'hardware_bom.csv';s=p.read_text().replace('Steel; cut and deburr to 468 mm','Steel; 500 mm end to end; deburr ends').replace('ID8.2 / OD12 / L21 mm','ID8.2 / OD12 / L53 mm');p.write_text(s)
# Preserve historical evidence, but explicitly withdraw its claim for replaced parts.
for name in ['validation.json','slice_validation.json','release_summary.json']:
 p=OUT/name;j=json.loads(p.read_text());j['top_part_override']={'parts':['P17','P18','P19'],'authoritative_report':'toroidal5_final/geometry_validation.json','slicing_report':'toroidal5_final/slice_validation.json','note':'Historical top-part dimensions, hashes, toolpaths and renderings below are superseded; other parts were not rebuilt. Top parts now use 0.6 mm nozzle / 0.25 mm layers.'};p.write_text(json.dumps(j,indent=2)+'\n')
checks={name:hashlib.sha256((STL/name).read_bytes()).hexdigest() for name in oldfiles+['P17_top_fan_B_integrated_supports_print-1x.stl','P185_print-1x.stl']}
assert checks['P18_top_guard_shroud_print-1x.stl']==checks['P185_print-1x.stl']
(RELEASE/'integration_validation.json').write_text(json.dumps({'status':'PASS','rod_mm':500,'top_steel_spacer_mm':53,'grille_elevation_mm':412,'production_stl_sha256':checks,'grille_reprint_required':False},indent=2)+'\n')
print('Production assembly, top STL files, manifest and hardware BOM updated.',flush=True)
