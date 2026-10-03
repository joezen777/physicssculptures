"""Update only the two loose pot STLs with the saved engraving."""
from pathlib import Path
import json,hashlib,os
import FreeCAD as App,Part,Mesh,MeshPart
from FreeCAD import Vector as V
from etch_zoetrope import engraved_shell
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"output";ART=ROOT.parent/"pot_zoetrope/output"
doc=App.openDocument(str(OUT/"print_prototype.FCStd"))
scene=json.loads((OUT/"scene.json").read_text())
parts={p["id"]:p for p in json.loads((OUT/"parts.json").read_text())}
smooth=Part.makeCone(60,88,80).cut(Part.makeCone(56.4,84.4,80))
review=App.newDocument("Engraved_P02_P03")
reports=[];pending=[]
for key,direction in [("P02","ccw"),("P03","cw")]:
    row=next(r for r in scene if r["key"]==key)
    original=doc.getObject(row["name"]).Shape.copy();original.translate(V(0,0,-116*row["stage"]))
    engraved=engraved_shell(direction)
    cuts=smooth.cut(engraved)
    assert cuts.isValid() and len(cuts.Solids)==144,(key,len(cuts.Solids))
    expected=smooth.Volume-engraved.Volume
    print("Applying "+key+" engraving to the existing part",flush=True)
    result=original.cut(cuts).removeSplitter()
    assert result.isValid() and len(result.Solids)==1,key
    actual=original.Volume-result.Volume
    assert abs(actual-expected)<.01,(key,actual,expected)
    result_box=result.optimalBoundingBox(False,False);original_box=original.optimalBoundingBox(False,False)
    for axis in ["XMin","XMax","YMin","YMax","ZMin","ZMax"]:
        assert abs(getattr(result_box,axis)-getattr(original_box,axis))<.02,(key,axis,getattr(result_box,axis),getattr(original_box,axis))
    o=review.addObject("PartDesign::Feature",key);o.Label=key+" engraved "+direction.upper();o.Shape=result
    printable=result.copy();b=printable.optimalBoundingBox(False,False);printable.translate(V(-b.XMin,-b.YMin,-b.ZMin))
    mesh=MeshPart.meshFromShape(Shape=printable,LinearDeflection=.06,AngularDeflection=.15,Relative=False)
    file=parts[key]["file"];target=OUT/"stl"/file;temporary=ART/(file+".pending.stl")
    mesh.write(str(temporary));check=Mesh.Mesh(str(temporary))
    assert check.isSolid() and check.countComponents()==1 and not check.hasNonManifolds(),key
    pending.append((temporary,target))
    reports.append(dict(part=key,file=file,direction=direction,recess_depth_mm=.6,
        remaining_radial_wall_mm=3.,engraved_paths=144,frames=24,removed_volume_mm3=actual,
        closed_single_mesh=True,unchanged_envelope=True,sha256=hashlib.sha256(temporary.read_bytes()).hexdigest()))
    print("PASS "+key,flush=True)
review.recompute();review.saveAs(str(ART/"engraved_P02_P03.FCStd"))
for temporary,target in pending:os.replace(temporary,target)
(ART/"engraved_parts_validation.json").write_text(json.dumps(dict(status="PASS",scope="Only loose P02/P03 STLs replaced; full assembly and print archives not rebuilt.",parts=reports),indent=2))
App.closeDocument(review.Name);App.closeDocument(doc.Name)
print("Updated only P02 and P03 loose STLs.",flush=True)
