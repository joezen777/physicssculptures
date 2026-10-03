"""Verify and package the hardware-only resin sprues."""
from pathlib import Path
from collections import Counter
import json,hashlib,zipfile,ast,textwrap
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent/"print_petg_12/output"
OUT=SOURCE/"stl/resin_hardware_sprues"
rows=json.loads((OUT/"sprue_manifest.json").read_text())
validation=json.loads((OUT/"validation.json").read_text())
counts=Counter();calibration=0
for r in rows:
    assert hashlib.sha256((OUT/r["file"]).read_bytes()).hexdigest()==r["sha256"]
    assert len(r["labels"])==sum(r["items_per_sheet"].values())
    assert all(x["font_pt"]==12 and x["emboss_mm"]==.8 for x in r["labels"])
    if r["calibration_sheet"]:calibration+=sum(r["items_per_sheet"].values())*r["print_copies"]
    else:
        for k,n in r["items_per_sheet"].items():counts[k]+=n*r["print_copies"]
assert dict(counts)==validation["production_quantities"] and sum(counts.values())==274
assert calibration==8 and len(rows)==17
for f in list(ROOT.glob("*.py"))+[ROOT/"render.FCMacro"]:ast.parse(f.read_text())
W,H=4000,5920;im=Image.new("RGB",(W,H),"white");d=ImageDraw.Draw(im)
def font(n,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
def text(x,y,s,n=32,b=False):d.text((x,y),s,font=font(n,b),fill="#173546")
text(65,45,"RESIN HARDWARE SPRUES",72,True)
text(68,145,"Screws, nuts, washers and tube spacers | 12 pt raised size labels | +0.8 mm emboss",34)
text(68,204,"274 BOM pieces + H00 thread-fit tests. Resin prototypes: use metal hardware for running the turbine.",30)
for i,r in enumerate(rows):
    x=40+(i%4)*990;y=300+(i//4)*1090
    pic=Image.open(ROOT/"previews"/(r["id"]+".png")).convert("RGB");pic.thumbnail((950,880))
    im.paste(pic,(x+(950-pic.width)//2,y+64))
    text(x+15,y,r["id"]+"   PRINT "+str(r["print_copies"])+"x",39,True)
    if r["id"]=="H00":caption="Four screw/nut test pairs"
    elif r["id"]=="H14":caption="OD7 washers x9 + OD9 x3"
    elif r["id"]=="H15":caption="15 spacers: ID8.2 / OD12"
    elif r["id"]=="H16":caption="18 spacers: ID4.2 / OD6"
    else:caption=" + ".join(k+" x"+str(v) for k,v in r["items_per_sheet"].items())
    text(x+15,y+951,caption,29,True)
    text(x+15,y+995," x ".join(str(round(v,1)) for v in r["size_mm"])+" mm",27)
text(65,5780,"Modeled coarse helical threads. Print H00 first; add final resin supports after inspecting sliced layers.",29)
text(65,5830,"Bearings and the 468 mm main steel rod remain purchased parts. Sheet filename counts cover the full kit.",28)
im.save(OUT/"hardware_sprues_preview.png")
thumb=im.copy();thumb.thumbnail((1200,1800));thumb.save(OUT/"hardware_sprues_thumbnail.png")
(OUT/"original_hardware_bom.csv").write_bytes((SOURCE/"hardware_bom.csv").read_bytes())
target=ROOT/"resin_hardware_sprues.zip"
names=["README.md","sprue_manifest.csv","sprue_manifest.json","validation.json","hardware_sprues_preview.png",
    "hardware_sprues_thumbnail.png","embossed_labels_detail.png","spacers_detail.png","original_hardware_bom.csv"]
files=sorted(OUT.glob("H*.stl"))+[OUT/n for n in names]
with zipfile.ZipFile(target,"w",zipfile.ZIP_DEFLATED) as z:
    for f in files:z.write(f,"resin_hardware_sprues/"+f.name)
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
    for f in files:assert z.read("resin_hardware_sprues/"+f.name)==f.read_bytes()
print("PASS: 17 sheets; 274 hardware pieces + 8 test pieces; 12 pt raised labels; archive verified.",flush=True)
print("ZIP MiB:",round(target.stat().st_size/1024**2,1),flush=True)
