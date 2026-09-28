"""Independently check the saved first-draft geometry with FreeCAD Python."""
from pathlib import Path
import json,math
import FreeCAD as App,Part
OUT=Path(__file__).resolve().parent/"output"
doc=App.openDocument(str(OUT/"tower_draft.FCStd"))
part_names={entry["name"] for entry in json.loads((OUT/"motion.json").read_text())}
objs=[o for o in doc.Objects if o.Name in part_names]
assert objs and all(o.Shape.isValid() and o.Shape.Volume>0 for o in objs)
samples=json.loads((OUT/"checks.json").read_text())
assert not samples["invalid"]
assert all(x["sun_planet_mm3"]<1e-5 and x["ring_planet_mm3"]<1e-5 for x in samples["mesh_samples"])
for level in range(2):
    b=88*level
    sun=doc.getObject("L%d_center_gear_female_hex"%level)
    assert abs(sun.Shape.BoundBox.ZMin-(b+31))<1e-6
    ring=doc.getObject("L%d_split_ring_0"%level)
    assert abs(ring.Shape.BoundBox.ZMin-(b+60))<1e-6
    assert abs(ring.Shape.BoundBox.ZMax-(b+68.4))<1e-6
pairs=[]
for lev in range(2):
    pairs.extend([
        ("L%d_center_gear_female_hex"%lev,"L%d_output_inner_race_spacer"%lev),
        ("L%d_center_gear_female_hex"%lev,"L%d_fixed_carrier"%lev),
        ("L%d_cone"%lev,"L%d_fixed_carrier"%lev),
        ("L%d_snap_cap"%lev,"L%d_planet_0"%lev)])
    for j in range(3):pairs.append(("L%d_planet_%d"%(lev,j),"L%d_planet_spacer_%d"%(lev,j)))
pairs.append(("L0_center_gear_female_hex","L1_cone"))
pairs.append(("L1_center_gear_female_hex","Top_fan_with_male_hex"))
pairs.extend([("L0_cone","Stationary_base"),("L0_cone","Bottom_inner_race_spacer"),("L0_cone","Stationary_8mm_shaft")])
intersections=[]
for a,b in pairs:
    volume=doc.getObject(a).Shape.common(doc.getObject(b).Shape).Volume
    intersections.append(dict(a=a,b=b,volume_mm3=volume))
assert max(x["volume_mm3"] for x in intersections)<1e-5,intersections
s=Part.Shape();s.read(str(OUT/"tower_cutaway.step"))
expected=sum(o.Shape.Volume for o in objs)
relative_error=abs(s.Volume-expected)/expected
print("STEP diagnostics",s.Volume,expected,relative_error,len(s.Solids),flush=True)
step_valid=s.isValid()
print("STEP validity",step_valid,flush=True)
assert step_valid and relative_error<1e-6
report=dict(status="passed",objects=len(objs),step_solids=len(s.Solids),
    sampled_mesh_poses=4,checked_clearance_pairs=intersections,
    step_roundtrip_relative_volume_error=abs(s.Volume-expected)/expected,
    scope="Selected static clearances and sampled mesh only, not complete assembly/strength validation")
(OUT/"verification.json").write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!="checked_clearance_pairs"},indent=2))
