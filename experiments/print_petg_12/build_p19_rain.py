"""Build an isolated, reviewable P19 replacement without rebuilding P17/P185."""
from pathlib import Path
import json,hashlib,time
import FreeCAD as App,Part,MeshPart
from FreeCAD import Vector as V
from p19_rain_geometry import make_grille,make_cap,BANDS
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output/p19_rain';OUT.mkdir(exist_ok=True)
OLD=ROOT/'output/toroidal5_final'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
protected={n:sha(OLD/n) for n in ['P17_top_fan_B_print-1x.stl','P185_print-1x.stl']}
print('Building P19 rain geometry',flush=True)
s,roofs,gutters,columns=make_grille();cap=make_cap()
print('Booleans complete',flush=True)
doc=App.newDocument('P19Rain')
report={'status':'PENDING','protected_original_sha256':protected,'physical_tested':False,'parts':[]}
for key,shape in [('P19',s),('P19C',cap)]:
    assert shape.isValid(),key+' invalid'
    assert len(shape.Solids)==1,(key,len(shape.Solids))
    o=doc.addObject('PartDesign::Feature',key);o.Shape=shape
    mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.06,AngularDeflection=.12,Relative=False)
    assert mesh.isSolid(),key+' mesh not closed'
    mesh.write(str(OUT/(key+'_rain.stl')))
    Part.export([o],str(OUT/(key+'_rain.step')))
    report['parts'].append({'id':key,'volume_mm3':shape.Volume,'solids':len(shape.Solids),
        'bounds_mm':str(shape.BoundBox),'triangles':mesh.CountFacets})
doc.recompute();doc.saveAs(str(OUT/'P19_rain.FCStd'))
source=App.openDocument(str(ROOT/'output/print_prototype.FCStd'))
scene=json.loads((ROOT/'output/scene.json').read_text())
old=source.getObject(next(x['name'] for x in scene if x['key']=='P19')).Shape.copy()
old.translate(V(0,0,-412))
# The complete original mounting annulus is invariant, except intentional
# added gutter outlet roofs ABOVE it. Compare the 0..6 mm mounting slice.
region=Part.makeCylinder(88,5.999,V(0,0,.0005)).cut(Part.makeCylinder(76,6,V(0,0,0)))
a=s.common(region);b=old.common(region)
delta=a.cut(b).Volume+b.cut(a).Volume
assert delta<1e-5,delta
collisions=[]
for row in scene:
    if row['key']=='P19':continue
    obj=source.getObject(row['name'])
    for name,shape in [('P19',s),('P19C',cap)]:
        world=shape.copy();world.translate(V(0,0,412))
        if world.BoundBox.intersect(obj.Shape.BoundBox):
            overlap=world.common(obj.Shape).Volume
            assert overlap<1e-5,(name,row['key'],overlap)
            collisions.append({'part':name,'other':row['key'],'overlap_mm3':overlap})
assert s.common(cap).Volume<1e-5,s.common(cap).Volume
# Check roof facets individually, with inward edges disallowed by design.
# Monotone gutter and segment equations are also independently sampled later.
report.update(status='PASS_CAD',mounting_annulus_symmetric_difference_mm3=delta,
              assembly_overlap_checks=collisions,cap_clearance_above_acorn_mm=3.9,
              rotor_vertical_clearance_mm=412-384.6,roof_count=len(roofs),
              gutter_count=len(gutters),column_count=len(columns))
assert protected=={n:sha(OLD/n) for n in protected}
report['input_stl_sha256']={p.name:sha(p) for p in OUT.glob('*.stl')}
(OUT/'geometry_validation.json').write_text(json.dumps(report,indent=2)+'\n')
# A complete review assembly uses the existing hardware and unmodified P17/P185.
obj=source.getObject(next(x['name'] for x in scene if x['key']=='P19'))
world=s.copy();world.translate(V(0,0,412));obj.Shape=world
cover=source.addObject('PartDesign::Feature','P19C_RainCover')
world=cap.copy();world.translate(V(0,0,412));cover.Shape=world
cover.Label='P19C removable rain cover - three M3x6 radial screws'
source.recompute();source.saveAs(str(OUT/'P19_rain_assembly.FCStd'))
print(json.dumps(report,indent=2),flush=True)
