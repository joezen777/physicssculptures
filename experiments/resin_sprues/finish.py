"""Compose a sheet index, check quantities/hashes, and package the resin export."""
from pathlib import Path
from collections import Counter
import json,hashlib,zipfile,ast,textwrap
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent;OUT=ROOT.parent/"print_petg_12/output/stl/resin_sprue_sheets"
rows=json.loads((OUT/"sprue_manifest.json").read_text())
expected=json.loads((ROOT.parent/"print_petg_12/output/parts.json").read_text())
total=Counter()
for r in rows:
    assert hashlib.sha256((OUT/r["file"]).read_bytes()).hexdigest()==r["sha256"]
    assert len(r["labels"])==sum(r["parts_per_sheet"].values())
    assert all(a["font_pt"]==12 and a["emboss_mm"]==.8 for a in r["labels"])
    for key,n in r["parts_per_sheet"].items():total[key]+=n*r["print_copies"]
assert dict(total)=={r["id"]:r["quantity"] for r in expected}
for f in list(ROOT.glob("*.py"))+[ROOT/"render.FCMacro"]:ast.parse(f.read_text())
W,H=4000,5920
im=Image.new("RGB",(W,H),"white");d=ImageDraw.Draw(im)
def font(n,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
def text(x,y,s,n=32,b=False,fill="#173546"):d.text((x,y),s,font=font(n,b),fill=fill)
text(65,45,"RESIN SPRUE SHEETS",72,True)
text(68,145,"Photon Mono M5s | ABS-Like Resin Pro 2 | 12 pt raised IDs | +0.8 mm emboss",35)
text(68,204,"Print the number of COMPLETE SHEETS in each filename. Add final resin supports in your slicer.",31)
for i,r in enumerate(rows):
    x=40+(i%4)*990;y=300+(i//4)*1090
    img=Image.open(ROOT/"previews"/(r["id"]+".png")).convert("RGB")
    img.thumbnail((950,880));im.paste(img,(x+(950-img.width)//2,y+64))
    text(x+15,y,r["id"]+"   PRINT "+str(r["print_copies"])+"x",39,True)
    parttext=" + ".join(k+" x"+str(v) for k,v in r["parts_per_sheet"].items())
    text(x+15,y+951,parttext,32,True)
    text(x+15,y+995," x ".join(str(round(v,1)) for v in r["size_mm"])+" mm",27)
text(65,5780,"Frames are disposable. Keep all purchased metal bearings, shafts, spacers and fasteners.",30)
text(65,5830,"R02/R03 reach 198 mm: check total height after adding supports or a raft. Print R19 fit coupons first.",28)
im.save(OUT/"sprue_sheets_preview.png")
thumb=im.copy();thumb.thumbnail((1200,1800));thumb.save(OUT/"sprue_sheets_thumbnail.png")

source=ROOT.parent/"print_petg_12/output"
guide=(source/"PRINT_AND_ASSEMBLE.md").read_text()
guide=guide[guide.index("## Purchased parts"):guide.index("## Design and verification references")]
guide=guide.replace("Print and inspect the coupons, then all P01-P19 parts in their filename quantities.","Print and inspect the R19 coupons, then print R01-R18 in their sheet filename quantities; trim away the sprues to recover P01-P19.")
(OUT/"ASSEMBLY_GUIDE.md").write_text("# Resin kit assembly reference\n\nUse README.md in this folder for resin printing and sheet quantities. Functional geometry and purchased hardware match the original prototype.\n\n"+guide.rstrip()+"\n")
(OUT/"hardware_bom.csv").write_bytes((source/"hardware_bom.csv").read_bytes())
(OUT/"assembly_reference.png").write_bytes((source/"exploded_assembly_labeled.png").read_bytes())
target=ROOT/"resin_sprue_sheets.zip"

files=sorted(OUT.glob("*.stl"))+[OUT/n for n in ["README.md","sprue_manifest.csv","sprue_manifest.json","validation.json","sprue_sheets_preview.png","sprue_sheets_thumbnail.png","embossed_labels_detail.png","ASSEMBLY_GUIDE.md","hardware_bom.csv","assembly_reference.png"]]
with zipfile.ZipFile(target,"w",zipfile.ZIP_DEFLATED) as z:
    for f in files:z.write(f,"resin_sprue_sheets/"+f.name)
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
    for f in files:assert z.read("resin_sprue_sheets/"+f.name)==f.read_bytes()
print("PASS: 19 sheets; all kit quantities and raised labels; unchanged hashes; ZIP verified.",flush=True)
print("ZIP MiB:",round(target.stat().st_size/1024**2,1),flush=True)
