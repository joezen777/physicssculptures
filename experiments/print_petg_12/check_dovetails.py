"""Check axial assembly paths for both split-part dovetail joints."""
from pathlib import Path
import json,FreeCAD as App
from FreeCAD import Vector as V
ROOT=Path(__file__).resolve().parent;OUT=ROOT/"output"
doc=App.openDocument(str(OUT/"print_prototype.FCStd"))
scene=json.loads((OUT/"scene.json").read_text())
def parts(key):return [doc.getObject(r["name"]).Shape.copy() for r in scene if r["key"]==key and r["stage"]==0]
checks=[]
for name,a,b in [("P05/P06 sun housing",parts("P05")[0],parts("P06")[0]),("P09 ring halves",*parts("P09"))]:
    for dz in [12,8,4,2,1,0]:
        s=b.copy();s.translate(V(0,0,dz));v=a.common(s).Volume
        assert v<1e-4,(name,dz,v)
        checks.append(dict(joint=name,axial_separation_mm=dz,overlap_mm3=v))
(OUT/"dovetail_validation.json").write_text(json.dumps(dict(status="PASS",socket_clearance_mm=.3,axial_insertion_checks=checks,physical_fit_tested=False),indent=2))
App.closeDocument(doc.Name)
print("PASS: both dovetail joints have clear axial assembly paths.")
