"""Run with the portable FreeCAD Python runtime after build completion."""
import json
import math
from pathlib import Path
import FreeCAD as App
import Part

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"output"
assert (OUT/"build_complete.txt").exists(),"Build incomplete"
doc=App.openDocument(str(OUT/"drop_gearbox.FCStd"))
objs=[o for o in doc.Objects if hasattr(o,"Shape")]
assert all(o.Shape.isValid() and o.Shape.Volume>0 for o in objs)
def center(shape):
    return sum((s.CenterOfMass*s.Volume for s in shape.Solids),App.Vector())/shape.Volume
centers=[center(doc.getObject("Upper_pitched_fin_%d"%i).Shape) for i in range(1,7)]
assert abs(sum(c.x for c in centers))<1e-6
assert abs(sum(c.y for c in centers))<1e-6
assert min(math.hypot(c.x,c.y) for c in centers)>48
for i in range(1,4):
    for j in range(1,4):
        c=center(doc.getObject("Stage_%d_planet_%d_24T"%(i,j)).Shape)
        assert abs(math.hypot(c.x,c.y)-24)<1e-6
v=json.loads((OUT/"validation.json").read_text())
assert not v["invalid_objects"]
assert max(max(x["sun_planet"],x["ring_planet"]) for x in v["mesh_intersections_mm3"])<1e-4
p=json.loads((OUT/"physics.json").read_text())
M=p["M"];k=p["free_reaction_per_shell"]
assert M[0][0]>0 and M[1][1]>0
assert M[0][0]*M[1][1]-M[0][1]**2>0
assert abs(M[1][0]+k*M[1][1])<1e-12
assert abs((64-63*k)-p["free_bottom_per_shell"])<1e-10
# STEP roundtrip: independently reload the delivered file and compare aggregate volume.
step=Part.Shape()
step.read(str(OUT/"drop_gearbox_cutaway.step"))
assert step.isValid()
expected=sum(o.Shape.Volume for o in objs)
assert abs(step.Volume-expected)/expected<1e-6,(step.Volume,expected)
report=dict(status="passed",object_count=len(objs),step_solid_count=len(step.Solids),
            step_volume_mm3=step.Volume,free_bottom_at_300rpm=300*p["free_bottom_per_shell"],
            checked=["CAD validity","six-fin radial balance","planet orbit radii",
                     "three sampled gear phases","positive kinetic energy",
                     "free generalized reaction momentum","cutaway STEP roundtrip volume"])
(OUT/"verification.json").write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
