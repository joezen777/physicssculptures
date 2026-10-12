"""Check complete hardware representation and refresh the downloadable print kit."""
from pathlib import Path
from collections import Counter
import csv,json,re,zipfile,ast,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent;OUT=ROOT/"output"
def bom_key(row):
    item,spec=row["item"],row["specification"]
    if item.startswith(("608","604")):return item[:3]+" bearing"
    if item=="Steel tube spacer":
        a,b,c=re.search(r"ID([\d.]+) / OD([\d.]+) / L([\d.]+)",spec).groups()
        return "Tube ID"+a+" OD"+b+" L"+c
    if "washer" in item:return "M4 washer OD"+re.search(r"([\d.]+) mm OD",spec).group(1)
    if "threaded rod" in item:return "M8 rod L468"
    if "acorn" in item:return "M8 acorn nut"
    if "nut" in item:return item.split()[0]+" nut"
    size,length=re.search(r"M([\d.]+) x(\d+)",spec).groups()
    return "M"+size+" x"+length+(" axle bolt" if length=="75" else " button screw" if "button" in item else " screw")
ann=json.loads((OUT/"annotations.json").read_text())
actual=Counter(a["spec"] for a in ann if a["hardware"])
expected=Counter()
for row in csv.DictReader((OUT/"hardware_bom.csv").open()):expected[bom_key(row)]+=int(row["quantity"])
assert actual==expected,(actual,expected)
assert len(ann)==351 and sum(actual.values())==295
assert len({a["name"] for a in ann})==len(ann)
with zipfile.ZipFile(OUT/"exploded_assembly.FCStd") as z:
    root=ET.fromstring(z.read("Document.xml"))
    names={o.attrib["name"] for o in root.find("Objects") if o.attrib.get("type")=="PartDesign::Feature"}
assert names=={a["name"] for a in ann}
for stem,number in [("cup_joint",5),("planet_joint",16)]:
    details=json.loads((OUT/(stem+"_annotations.json")).read_text())
    assert len(details)==number,(stem,len(details))
    assert all(0<=a["pixel"][0]<=1400 and 0<=a["pixel"][1]<=(1600 if stem=="cup_joint" else 2600) for a in details)
for path in list(ROOT.glob("*.py"))+[ROOT/"render.FCMacro"]:ast.parse(path.read_text())
report=json.loads((OUT/"exploded_hardware_validation.json").read_text())
report.update(bom_csv_quantities_match=True,native_exploded_object_names_match=True,joint_details_checked=True)
(OUT/"exploded_hardware_validation.json").write_text(json.dumps(report,indent=2)+"\n")
names=["PRINT_AND_ASSEMBLE.md","print_manifest.csv","hardware_bom.csv","parts.json","release_summary.json",
       "dovetail_validation.json","sun_housing_dovetails.png","helical_gear_mesh.png","helical_ring_assembly.png","validation.json","fastener_validation.json","slice_validation.json","exploded_hardware_validation.json",
       "exploded_assembly_labeled.png","assembly_guide_preview.png","assembled.png",
       "planet_joint_labeled.png","cup_joint_labeled.png","print_prototype.FCStd","exploded_assembly.FCStd"]
files=[(p,"stl/"+p.name) for p in sorted((OUT/"stl").glob("*.stl"))]
files += [(OUT/name,name) for name in names]+[(ROOT/"slicer_check.ini","slicer_check.ini")]
target=ROOT/"print_package_PETG.zip"
with zipfile.ZipFile(target,"w",zipfile.ZIP_DEFLATED) as z:
    for path,name in files:z.write(path,"fan_tunnel_PETG/"+name)
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
    for path,name in files:assert z.read("fan_tunnel_PETG/"+name)==path.read_bytes()
print("PASS: all BOM quantities, 351 native objects, joint detail coverage, syntax, and ZIP contents.")
print("Package:",round(target.stat().st_size/1024**2,1),"MiB")
