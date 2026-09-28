"""Validate saved four-level geometry and selected clearances."""
from pathlib import Path
import json
import FreeCAD as App,Part
OUT=Path(__file__).resolve().parent/"output"
doc=App.openDocument(str(OUT/"tower_draft.FCStd"))
names={x["name"] for x in json.loads((OUT/"motion.json").read_text())}
parts=[o for o in doc.Objects if o.Name in names]
assert all(o.Shape.isValid() and o.Shape.Volume>0 for o in parts)
print("Native geometry valid",flush=True)
bearings=[o for o in parts if "608" in o.Name]
assert len(bearings)==20,len(bearings)
checks=json.loads((OUT/"checks.json").read_text())
assert not checks["invalid"]
assert all(x["sun_planet_mm3"]<1e-5 and x["ring_planet_mm3"]<1e-5 for x in checks["mesh_samples"]),checks
pairs=[]
for level in range(3):
    b="L%d_"%level
    pairs.extend([(b+"cone",b+"fixed_carrier"),(b+"center_gear_female_hex",b+"fixed_carrier"),
                  (b+"center_gear_female_hex",b+"output_inner_race_spacer")])
    for j in range(3):
        pairs.append((b+"planet_%d"%j,b+"planet_spacer_%d"%j))
    if level<2:pairs.append((b+"center_gear_female_hex","L%d_cone"%(level+1)))
pairs.extend([("Top_ring_fan","Stationary_top_ring_and_spider"),("Top_ring_fan","Top_fan_inner_spacer"),
              ("Top_ring_fan","L2_center_gear_female_hex"),("L0_cone","Bottom_between_bearings_spacer"),
              ("L0_cone","Bottom_lower_inner_spacer"),("Bottom_sail_arms","Stationary_base")])
for j in range(3):
    pairs.extend([("Circular_wind_sail_%d"%j,"Stationary_base"),("Circular_wind_sail_%d"%j,"L0_cone")])
results=[]
for a,b in pairs:
    vol=doc.getObject(a).Shape.common(doc.getObject(b).Shape).Volume
    results.append(dict(a=a,b=b,overlap_mm3=vol))
assert all(p["overlap_mm3"]<1e-5 for p in results),results
print("Selected clearances passed; reading STEP",flush=True)
step=Part.read(str(OUT/"tower_cutaway.step"))
print("STEP imported; checking validity and volume",flush=True)
native_volume=sum(o.Shape.Volume for o in parts)
error=abs(step.Volume-native_volume)/native_volume
assert step.isValid() and error<1e-6
report=dict(status="PASS",components=len(parts),bearings_608=len(bearings),
            ratios=checks["ratios"],mesh_poses=len(checks["mesh_samples"]),
            static_clearances=results,step_solids=len(step.Solids),step_relative_volume_error=error,
            scope="Sampled meshes and selected static pairs only; no startup or airflow validation")
(OUT/"verification.json").write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!="static_clearances"},indent=2))
