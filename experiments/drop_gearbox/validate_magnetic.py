"""Validate delivered magnetic geometry; does not validate magnetic torque."""
from pathlib import Path
import json
import FreeCAD as App,Part
OUT=Path(__file__).resolve().parent/"magnetic_output"
doc=App.openDocument(str(OUT/"magnetic.FCStd"))
objs=[o for o in doc.Objects if hasattr(o,"Shape")]
assert all(o.Shape.isValid() and o.Shape.Volume>0 for o in objs)
for i in range(1,4):
    for name,count,lo,hi in [("inner_pole",8,23,26),("outer_pole",24,33,36),("modulator_",16,28,31)]:
        selected=[o for o in objs if o.Name.startswith("M%d_%s"%(i,name))]
        assert len(selected)==count,(name,len(selected))
        radii=[(v.Point.x**2+v.Point.y**2)**.5 for o in selected for v in o.Shape.Vertexes]
        assert abs(min(radii)-lo)<1e-6 and abs(max(radii)-hi)<1e-6
p=json.loads((OUT/"physics.json").read_text())
M=p["M"];k=p["free_reaction_per_shell"]
assert M[0][0]*M[1][1]-M[0][1]**2>0
assert abs(M[1][0]+k*M[1][1])<1e-12
shape=Part.Shape();shape.read(str(OUT/"magnetic_cutaway.step"))
expected=sum(o.Shape.Volume for o in objs)
assert shape.isValid()
assert abs(shape.Volume-expected)/expected<1e-6
r=dict(status="passed",objects=len(objs),step_solids=len(shape.Solids),
       checks=["solid validity","magnet and modulator counts","two 2mm radial gaps",
               "positive inertia matrix","free-reaction momentum","STEP roundtrip volume"],
       scope="Geometry and imposed kinematics only; no electromagnetic or bearing validation")
(OUT/"verification.json").write_text(json.dumps(r,indent=2))
print(json.dumps(r,indent=2))
