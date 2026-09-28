"""Read back the bevel CAD draft and check selected static clearances."""
from pathlib import Path
import json
import FreeCAD as App, Part
ROOT=Path(__file__).resolve().parent;OUT=ROOT/"output"
doc=App.openDocument(str(OUT/"bevel_cones.FCStd"))
parts=[o for o in doc.Objects if o.TypeId=="PartDesign::Feature"]
checks=json.loads((OUT/"checks.json").read_text())
assert not checks["invalid"]
for sample in checks["gear_mesh_samples"]:
 assert sample["lower_overlap_mm3"]<1e-5 and sample["upper_overlap_mm3"]<1e-5,sample
pairs=[]
for level in range(checks["stages"]):
 pairs.append(("L%d_upper_bevel_hex"%level,"L%d_upper_608"%level))
 for j in range(3):
  pairs.append(("L%d_fan_blade_insert"%level,"L%d_radial_pinion_%d"%(level,j)))
  pairs.append(("L%d_radial_pinion_%d"%(level,j),"L%d_carrier_arm_%d"%(level,j)))
 if level:
  pairs.append(("L%d_pointed_cone"%level,"L%d_upper_608"%(level-1)))
  pairs.append(("L%d_pointed_cone"%level,"L%d_upper_bevel_hex"%(level-1)))
pairs.append(("Fan","L%d_upper_608"%(checks["stages"]-1)))
pairs.append(("Fan","L%d_upper_bevel_hex"%(checks["stages"]-1)))
assert all(len(o.Shape.Solids)==1 for o in parts),[(o.Name,len(o.Shape.Solids)) for o in parts if len(o.Shape.Solids)!=1]
result={"native_components":len(parts),"invalid_native":[o.Name for o in parts if not o.Shape.isValid()],"selected_clearances":[]}
for a,b in pairs:
 volume=doc.getObject(a).Shape.common(doc.getObject(b).Shape).Volume
 result["selected_clearances"].append({"a":a,"b":b,"overlap_mm3":volume})
step=Part.read(str(OUT/"bevel_cones_full.step"))
result["step_valid"]=step.isValid();result["step_solids"]=len(step.Solids)
result["status"]="PASS" if not result["invalid_native"] and result["step_valid"] and all(p["overlap_mm3"]<1e-5 for p in result["selected_clearances"]) else "FAIL"
(OUT/"verification.json").write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
assert result["status"]=="PASS"
