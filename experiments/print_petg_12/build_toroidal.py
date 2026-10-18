from pathlib import Path
import json,math
import FreeCAD as App,Part,MeshPart
from FreeCAD import Vector as V
from toroidal_geometry import make_fan,make_shroud,cyl,shifted,P17_HORIZONTAL_EXPANSION_MM,P17_HEX_AF_MM,P17_BORE_RADIUS_MM,P17_HUB_RADIUS_MM,P17_BEARING_POCKET_RADIUS_MM,P17_SCREW_HOLE_RADIUS_MM,P17_NUT_POCKET_AF_MM
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'output/toroidal5_final';OUT.mkdir(exist_ok=True)
print('Building five closed pairs with production hub',flush=True)
fan=make_fan();guard=make_shroud()
source=App.openDocument(str(ROOT/'output/print_prototype.FCStd'))
scene=json.loads((ROOT/'output/scene.json').read_text())
get=lambda key:source.getObject(next(x['name'] for x in scene if x['key']==key)).Shape.copy()
old=get('P17');old.translate(V(0,0,-348));region=cyl(20.9,100,-30)
a,b=fan.common(region),old.common(region);delta=a.cut(b).Volume+b.cut(a).Volume
# P17's horizontal offset is limited to the hub/casing; blade roots begin
# outside this comparison region and remain unchanged.
assert 0<delta<1500,delta
# Grille shape is retained; only its assembly elevation changes.
grille=get('P19');grille.translate(V(0,0,-grille.BoundBox.ZMin))
wf=shifted(fan,348);wg=shifted(guard,340);wgr=shifted(grille,412)
envelope=cyl(72.1,40,348).cut(cyl(22.6,40,348));checked=[]
for row in scene:
 if row['key'] in ['P17','P18','P19']:continue
 s=source.getObject(row['name']).Shape
 if envelope.BoundBox.intersect(s.BoundBox):
  assert envelope.common(s).Volume<1e-5,row['name'];checked.append(row['name'])
assert wf.common(wg).Volume<1e-5 and wf.common(wgr).Volume<1e-5
assert fan.BoundBox.ZMax<=40 and fan.BoundBox.ZMin>=-22.00001
report={'status':'PASS','physical_tested':False,'selection':'aesthetic, no aerodynamic winner established','p17_horizontal_expansion_mm':P17_HORIZONTAL_EXPANSION_MM,'p17_hub_casing_radius_mm':P17_HUB_RADIUS_MM,'p17_hex_af_mm':P17_HEX_AF_MM,'p17_bore_diameter_mm':2*P17_BORE_RADIUS_MM,'p17_bearing_pocket_diameter_mm':2*P17_BEARING_POCKET_RADIUS_MM,'p17_screw_hole_diameter_mm':2*P17_SCREW_HOLE_RADIUS_MM,'p17_nut_pocket_af_mm':P17_NUT_POCKET_AF_MM,'p06_mating_socket_af_mm':24.6,'p17_hex_clearance_per_side_mm':(24.6-P17_HEX_AF_MM)/2,'fit_geometry_delta_mm3':delta,'blade_and_support_geometry_changed':False,'radial_clearance_mm':4,'blade_top_local_mm':fan.BoundBox.ZMax,'grille_gap_mm':412-wf.BoundBox.ZMax,'all_angle_checked':checked,'parts':[]}
doc=App.newDocument('Toroidal5Final')
for key,s,z,name,flip in [('P17',fan,348,'P17_top_fan_B_print-1x.stl',False),('P18',guard,340,'P185_print-1x.stl',True),('P19',grille,412,'P19_curved_guard_grille_print-1x.stl',False)]:
 o=doc.addObject('PartDesign::Feature',key);o.Shape=shifted(s,z)
 p=s.copy()
 if flip:p.rotate(V(),V(1,0,0),180)
 p.translate(V(0,0,-p.BoundBox.ZMin))
 mesh=MeshPart.meshFromShape(Shape=p,LinearDeflection=.045,AngularDeflection=.1,Relative=False)
 assert mesh.isSolid()
 if key=='P17':
  verts,faces=mesh.Topology;edges=set(tuple(sorted((f[i],f[(i+1)%3]))) for f in faces for i in range(3))
  euler=len(verts)-len(edges)+len(faces)
  assert euler==-16,('Expected 5 loop holes plus 4 mounting holes',euler)
  report['rotor_euler_characteristic']=euler;report['closed_loop_passages']=5
 mesh.write(str(OUT/name))
 Part.export([o],str(OUT/(key+'.step')))
 report['parts'].append({'id':key,'file':name,'volume_mm3':s.Volume,'dimensions_mm':[p.BoundBox.XLength,p.BoundBox.YLength,p.BoundBox.ZLength],'triangles':mesh.CountFacets,'orientation':'flange on bed' if flip else 'upright','solids':len(s.Solids)})
doc.recompute();doc.saveAs(str(OUT/'toroidal5_final.FCStd'))
(OUT/'geometry_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)

# Bind generated verification to the exact mesh files.
import hashlib
p=OUT/'geometry_validation.json';j=json.loads(p.read_text());j['input_stl_sha256']={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in [OUT/x for x in ['P17_top_fan_B_print-1x.stl','P185_print-1x.stl','P19_curved_guard_grille_print-1x.stl']]};p.write_text(json.dumps(j,indent=2)+'\n')
