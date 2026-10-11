from pathlib import Path
import json,math,hashlib
import FreeCAD as App,Part,MeshPart
from FreeCAD import Vector as V
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'/'sail_80x120'
OUT.mkdir(exist_ok=True)
for name in ['validation.json','slice_validation.json','render_complete.txt']:(OUT/name).unlink(missing_ok=True)
source=App.openDocument(str(ROOT/'output/print_prototype.FCStd'))
scene=json.loads((ROOT/'output/scene.json').read_text())
def get(key):return source.getObject(next(r['name'] for r in scene if r['key']==key)).Shape.copy()
oldarm=get('P15');hub=get('P14')
def box(x,y,z,dx,dy,dz):return Part.makeBox(dx,dy,dz,V(x,y,z))
# Preserve the complete original root and its holes in assembly coordinates.
root=oldarm.common(box(-100,-100,-50,155,200,100))
pts=[(48,-24),(60,-28),(166,-53),(191,-53),(191,-45),(169,-45),(64,-12),(48,-10)]
wire=Part.makePolygon([V(x,y,-12) for x,y in pts]+[V(*pts[0],-12)])
body=Part.Face(wire).extrude(V(0,0,6))
arm=root.fuse(body).fuse(box(169,-51,-17,22,6,24))
# Broad vertical web outside preserved hub engagement.
ribpts=[(58,-22),(164,-49),(169,-49),(169,-45),(164,-45),(58,-18)]
rib=Part.Face(Part.makePolygon([V(x,y,-12) for x,y in ribpts]+[V(*ribpts[0],-12)])).extrude(V(0,0,12))
arm=arm.fuse(rib)
# Anti-twist cheeks with 0.30 mm side clearance around 16 mm P16 boss.
arm=arm.fuse(box(169,-49,-17,2.7,9,16)).fuse(box(188.3,-49,-17,2.7,9,16))
hole=Part.makeCylinder(2.25,40,V(180,-60,-9),V(0,1,0))
arm=arm.cut(hole).removeSplitter()
# Vertical half-cylinder: 80 wide x 120 high, 3.2 mm shell, open toward +Y.
outer=Part.makeCylinder(40,120,V(180,0,-40))
inner=Part.makeCylinder(36.8,122,V(180,0,-41))
half=box(130,-50,-41,100,50,122)
sail=outer.cut(inner).common(half)
# 5 mm radial rims, 3.2 mm high at both ends.
for z in [-40,76.8]:
    rim=Part.makeCylinder(40,3.2,V(180,0,z)).cut(Part.makeCylinder(35,3.2,V(180,0,z))).common(half)
    sail=sail.fuse(rim)
sail=sail.fuse(box(172,-45,-17,16,13,16)).cut(hole).removeSplitter()
assert len(arm.Solids)==len(sail.Solids)==1
assert arm.isValid() and sail.isValid()
# Exact preservation of root inside x<=46 (P14 outermost engagement ends at x~46).
region=box(-100,-100,-50,146,200,100)
a=oldarm.common(region);b=arm.common(region)
root_delta=a.cut(b).Volume+b.cut(a).Volume
assert root_delta<1e-6,root_delta
assert arm.common(hub).Volume<1e-5
assert arm.common(sail).Volume<1e-5
doc=App.newDocument('Sail80x120')
rows=[]
for key,shape in [('P15',arm),('P16',sail)]:
    obj=doc.addObject('PartDesign::Feature',key);obj.Shape=shape
    obj.addProperty('App::PropertyString','PartID');obj.PartID=key
    printshape=shape.copy()
    bb=printshape.BoundBox;printshape.translate(V(-bb.XMin,-bb.YMin,-bb.ZMin))
    mesh=MeshPart.meshFromShape(Shape=printshape,LinearDeflection=.08,AngularDeflection=.12,Relative=False)
    assert mesh.isSolid()
    filename=key+('_arm_180mm_print-3x.stl' if key=='P15' else '_scoop_80x120mm_print-3x.stl')
    mesh.write(str(OUT/filename))
    bb=printshape.BoundBox
    rows.append(dict(id=key,file=filename,quantity=3,size_mm=[bb.XLength,bb.YLength,bb.ZLength],volume_mm3=shape.Volume,triangles=mesh.CountFacets,closed_mesh=True))
doc.recompute();doc.saveAs(str(OUT/'P15_P16_sail_80x120.FCStd'))
# Swept axisymmetric envelope: all other existing printed parts must stay inside 100 mm
# wherever tall scoop overlaps vertically. Validate actual sampled angular positions too.
fixed=[(source.getObject(r['name']).Shape,r.get('ratio',0)) for r in scene if r['key'] not in ('P15','P16')]
checks=[]
for key,s in [('P15',arm),('P16',sail)]:
    min_distance=1e9
    for deg in range(0,360,10):
        test=s.copy();test.rotate(V(),V(0,0,1),deg)
        for original,ratio in fixed:
            if key=='P16':
                bb=original.BoundBox
                bound=math.hypot(max(abs(bb.XMin),abs(bb.XMax)),max(abs(bb.YMin),abs(bb.YMax)))
                if bound<140:continue
            other=original.copy()
            if ratio:other.rotate(V(),V(0,0,1),deg*ratio)
            if test.BoundBox.intersect(other.BoundBox):
                overlap=test.common(other).Volume
                assert overlap<1e-4,(key,deg,overlap)
        # pair spacing for other two identical arm/sail sets
        for delta in [120,240]:
            for part in [arm,sail]:
                other=part.copy();other.rotate(V(),V(0,0,1),delta)
                # only compare self's home position to other assemblies
                if deg==0:assert s.common(other).Volume<1e-4
    checks.append(dict(part=key,sampled_rotation_step_degrees=10,interference=False))
# preserve original hub file hash for traceability
hubfile=ROOT/'output/stl/P14_sail_hex_hub_print-1x.stl'
report=dict(status='PASS',root_symmetric_difference_mm3=root_delta,P14_sha256=hashlib.sha256(hubfile.read_bytes()).hexdigest(),parts=rows,checks=checks,physical_tested=False,notes='Original full assembly unchanged; angular collision sampling is not structural validation.')
(OUT/'validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
