"""Check the saved full-wall modular fan tunnel."""
from pathlib import Path
import json,math
import FreeCAD as App,Part
from FreeCAD import Vector as V
OUT=Path(__file__).resolve().parent/"output"
(OUT/"verification.json").unlink(missing_ok=True)
checks=json.loads((OUT/"checks.json").read_text());n=checks["modules"]
doc=App.openDocument(str(OUT/"tower_draft.FCStd"))
names={x["name"] for x in json.loads((OUT/"motion.json").read_text())}
parts=[o for o in doc.Objects if o.Name in names]
assert all(o.Shape.isValid() and o.Shape.Volume>0 for o in parts)
assert len([o for o in parts if "608" in o.Name])==3*n+2
assert len([o for o in parts if "604" in o.Name])==3*n
assert not checks["invalid"]
assert all(x["sun_planet_mm3"]<1e-5 and x["ring_planet_mm3"]<1e-5 for x in checks["mesh_samples"])
print("Full native geometry and mesh samples valid",flush=True)
# Check both an intact shell wall and open floor passages in every pot.
module_checks=[]
for level in range(n):
    s=doc.getObject("L%d_cone"%level).Shape;b=88*level
    fan_material=s.isInside(V(35,0,b),1e-6,True)
    open_gap=not s.isInside(V(35*math.cos(math.pi/6),35*math.sin(math.pi/6),b),1e-6,True)
    # At z=30 the shell is between approximately radius 69.34 and 72.41.
    full_wall=all(s.isInside(V(71*math.cos(a),71*math.sin(a),b+30),1e-6,True) for a in [i*math.pi/4 for i in range(8)])
    assert fan_material and open_gap and full_wall,(level,fan_material,open_gap,full_wall)
    module_checks.append(dict(level=level+1,fan_floor=True,open_floor_gap=True,full_circumference=True))
pairs=[]
for level in range(n):
    b="L%d_"%level
    pairs.extend([(b+"cone",b+"fixed_carrier"),(b+"center_gear_female_hex",b+"fixed_carrier"),
                  (b+"center_gear_female_hex",b+"output_inner_race_spacer")])
    for j in range(3):
        pairs.extend([(b+"planet_%d"%j,b+"planet_spacer_%d"%j),
                      (b+"planet_%d"%j,b+"planet_%d_604"%j),
                      (b+"planet_%d"%j,b+"planet_axle_%d"%j),
                      (b+"planet_spacer_%d"%j,b+"planet_axle_%d"%j)])
        bearing=doc.getObject(b+"planet_%d_604"%j).Shape.BoundBox
        assert abs(bearing.XLength-12)<1e-5 and abs(bearing.ZLength-4)<1e-5
        axle=doc.getObject(b+"planet_axle_%d"%j).Shape.BoundBox
        assert abs(axle.XLength-4)<1e-5
    if level<n-1:
        pairs.extend([(b+"center_gear_female_hex","L%d_cone"%(level+1)),
                      (b+"air_transition","L%d_cone"%(level+1))])
pairs.extend([("Top_ring_fan","Stationary_top_ring_and_spider"),("Top_ring_fan","Top_fan_inner_spacer"),
              ("Top_ring_fan","L%d_center_gear_female_hex"%(n-1)),
              ("L%d_air_transition"%(n-1),"Stationary_top_ring_and_spider"),
              ("Universal_base_drive_adapter","L0_cone"),
              ("Universal_base_drive_adapter","Bottom_extra_608"),
              ("Universal_base_drive_adapter","Bottom_sail_arms"),
              ("Universal_base_drive_adapter","Bottom_between_bearings_spacer"),
              ("L0_cone","Bottom_sail_arms"),("Bottom_sail_arms","Stationary_base")])
for j in range(3):
    pairs.extend([("Circular_wind_sail_%d"%j,"Stationary_base"),("Circular_wind_sail_%d"%j,"L0_cone")])
results=[]
for a,b in pairs:
    vol=doc.getObject(a).Shape.common(doc.getObject(b).Shape).Volume
    results.append(dict(a=a,b=b,overlap_mm3=vol))
assert all(p["overlap_mm3"]<1e-5 for p in results),results
print("Module walls, fan openings and selected assembly clearances passed",flush=True)
# Check guard material at ring radii and all six arm endpoints.
guard=doc.getObject("Stationary_top_ring_and_spider").Shape
z=88*n+20
for r in range(17,72,6):
    assert guard.isInside(V(r,0,z),1e-6,True)
for j in range(6):
    a=math.radians(j*60+18)
    assert guard.isInside(V(43.5*math.cos(a),43.5*math.sin(a),z),1e-6,True)
# Full rotational blade envelope clears the elevated guard.
sweep=Part.makeCylinder(70.7,9,V(0,0,88*n-4.5)).cut(Part.makeCylinder(15,9,V(0,0,88*n-4.5)))
assert guard.common(sweep).Volume<1e-5
step=Part.read(str(OUT/"tower_full.step"))
native_volume=sum(o.Shape.Volume for o in parts)
error=abs(step.Volume-native_volume)/native_volume
assert step.isValid() and error<1e-6
report=dict(status="PASS",components=len(parts),bearings_608=3*n+2,bearings_604=3*n,ratios=checks["ratios"],
            module_checks=module_checks,static_clearances=results,step_solids=len(step.Solids),
            step_relative_volume_error=error,
            scope="Sampled geometry only; no airtightness, startup, load or airflow qualification")
(OUT/"verification.json").write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!="static_clearances"},indent=2))
