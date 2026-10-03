import os
"""Compose the engineering assembly poster from native CAD renders."""
from pathlib import Path
from collections import defaultdict
import json,csv,textwrap
from PIL import Image,ImageDraw,ImageFont,ImageChops
ROOT=Path(__file__).resolve().parent;OUT=ROOT/"output"
W,H=4700,15200
im=Image.new("RGB",(W,H),"white");d=ImageDraw.Draw(im)
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def font(n,b=False):return ImageFont.truetype(BOLD if b else FONT,n)
ink="#152c3a";muted="#4c6572";blue="#176c98";line="#8b9fa9"
def text(x,y,s,size=32,b=False,color=ink):d.text((x,y),s,font=font(size,b),fill=color)
def wrap(x,y,s,width=52,size=30,b=False,color=ink):
    for a in textwrap.wrap(s,width=width):
        text(x,y,a,size,b,color);y+=int(size*1.4)
    return y
text(70,48,"FOUR-LEVEL FAN TUNNEL",78,True)
text(74,146,"PETG  |  1.2 mm nozzle  |  Separate parts and assembly order",36,color=muted)
d.line((70,220,4630,220),fill=blue,width=6)
raw=Image.open(OUT/"exploded_raw.png").convert("RGB")
im.paste(raw,(800,300))
# Guide axis, unobtrusive and dashed.
for y in range(360,14800,45):d.line((1600,y,1600,y+18),fill="#d2dce1",width=2)
# Restore opaque render over guide; guide remains in white gaps only.
mask=ImageChops.difference(raw,Image.new("RGB",raw.size,"white")).convert("L").point(lambda x:255 if x>12 else 0)
im.paste(raw,(800,300),mask)
names={
"P01":"608 bearing retainer","P02":"Pot + fan floor A","P03":"Pot + fan floor B",
"P04":"Fixed curved carrier","P05":"Lower sun bearing housing","P06":"36-tooth sun + hex socket",
"P07":"18-tooth planet / 604 seat","P08":"604 bearing retainer","P09":"72-tooth ring half",
"P10":"Interstage air collar","P11":"Terminal air collar","P12":"Stationary base",
"P13":"Bottom drive adapter","P14":"Removable sail hub","P15":"Curved sail arm",
"P16":"Circular wind cup","P17":"Top fan, pitch B","P18":"Stationary guard shroud",
"P19":"Six-spoke guard grille","H608":"608 steel bearing","H604":"604 steel bearing",
"C01":"608 fit coupon","C02":"604 fit coupon"}
ann=json.loads((OUT/"annotations.json").read_text())
groups=defaultdict(list)
for a in ann:groups[(a["stage"],a["key"],a["role"] if a["hardware"] else a["order"])].append(a)
ordered=sorted(groups.items(),key=lambda item:sum(a["pixel"][1] for a in item[1])/len(item[1]))
columns=[[],[]]
for i,(key,items) in enumerate(ordered):
    y=300+sum(a["pixel"][1] for a in items)/len(items)
    columns[i%2].append((key,items,y))
for side,items in enumerate(columns):
    prev=290
    for key,points,target in items:
        y=max(target-35,prev+140);prev=y
        x=60 if side==0 else 2480
        stage,pid,order=key
        count=len(points)
        # Leader ends stop outside labels, never through the type.
        edge=735 if side==0 else 2460
        for a in points:
            ax=800+a["pixel"][0];ay=300+a["pixel"][1]
            elbow=765 if side==0 else 2430
            d.line([(ax,ay),(elbow,ay),(edge,y+24)],fill=line,width=2)
            d.ellipse((ax-5,ay-5,ax+5,ay+5),fill=blue)
        if points[0]["hardware"]:
            label=points[0]["spec"]
            wrap(x,y,label+"  x"+str(count),width=35,size=27,b=True,color=muted)
            wrap(x,y+70,str(order).capitalize(),width=36,size=24)
        else:
            text(x,y,pid+"  x"+str(count),34,True,color=blue)
            wrap(x,y+43,names[pid],width=29,size=27)
        assert y+135 < H-280,("Label overflow",key,y)
# Right-hand reference column.
x=3410
d.line((3320,265,3320,14930),fill="#d9e2e7",width=3)
text(x,285,"ASSEMBLED REFERENCE",38,True)
ref=Image.open(OUT/"assembled.png").convert("RGB")
bb=ImageChops.difference(ref,Image.new("RGB",ref.size,"white")).getbbox()
ref=ref.crop(bb);ref.thumbnail((1000,1660))
im.paste(ref,(x+(1180-ref.width)//2,365))
y=2080
text(x,y,"PRINT QUANTITIES",40,True);y+=66
text(x,y,"Filename quantities cover the entire tower.",27,color=muted);y+=58
rows=json.loads((OUT/"parts.json").read_text())
for r in rows:
    if r["id"].startswith("C"):continue
    d.line((x,y+62,x+1190,y+62),fill="#e3eaee",width=2)
    text(x,y,r["id"],31,True,color=blue)
    text(x+100,y,names[r["id"]],29)
    text(x+1100,y,str(r["quantity"])+"x",31,True)
    y+=73
y+=30
text(x,y,"PRINT FIRST: C01 + C02",34,True);y+=54
y=wrap(x,y,"Print one of each fit coupon before committing to the large parts. Do not scale the bearing seats or whole assembly.",width=61,size=28)+45
text(x,y,"PURCHASED HARDWARE",37,True);y+=62
purchased=[
("608 bearings, 8 x 22 x 7 mm","11"),
("604 bearings, 4 x 12 x 4 mm","9"),
("M8 threaded steel rod, 468 mm","1"),
("M8 hex nuts + M8 acorn nut","9 + 1"),
("M4 x75 planet axle bolts","9"),
("M3 x16 retainer screws","24"),
("M3 x20 sun-housing screws","9"),
("M3 hex nuts","33"),
("M2.5 x16 screws + matching nuts","27 each"),
("M4 x20 ring/collar + sail-hub bolts","21"),
("M4 x10 button-head arm screws","6"),
("M4 x16 guard bolts","6"),
("M4 x25 cup bolts","3"),
("M4 hex nuts, all locations","54"),
("M4 washers: OD7 / OD9","9 / 3")]
for label,qty in purchased:
    text(x,y,label,27);text(x+1070,y,qty,28,True);y+=56
y+=25
text(x,y,"STEEL INNER-RACE SPACERS",32,True);y+=55
y=wrap(x,y,"ID8.2 / OD12 tube lengths (mm): 12.5 x1, 32 x1, 15 x3, 5.9 x3, 11 x3, 44.6 x3, 21 x1.",width=59,size=28)+22
y=wrap(x,y,"ID4.2 / OD6 tube lengths (mm): 37.2 x9 and 10 x9. Cut ends square and deburr.",width=59,size=28)+35
text(x,y,"HOW TO READ THIS VIEW",34,True);y+=58
for item in [
"Build upward from the base. Preassemble bearings and their removable caps before stacking.",
"Pot sequence: A, B, A; then the top fan B. Adjacent stages reverse rotation.",
"Fit the ring halves sideways after meshing the sun and three planets. Rotate the second identical half 180 degrees.",
"Every required bearing, bolt, screw, nut, washer and steel spacer is drawn individually in gray, beside its joint. Threads are simplified.",
"Use the numbered assembly guide for bolt lengths, nut pockets and spacer locations."]:
    y=wrap(x,y,item,width=59,size=28)+26
text(70,14920,"ALL PRINTED AND PURCHASED ASSEMBLY PARTS SHOWN  •  Part IDs match STL filenames",36,True)
text(70,14980,"Prototype fit set: verify coupon fit, remove supports, and hand-turn each stage before adding the next.",30,color=muted)
text(70,15030,"Nominal CAD and slicing checks are not physical load, airflow, durability or child-safety certification.",28,color=muted)
import runpy
runpy.run_path(str(ROOT/"make_joint_posters.py"),run_name="__main__")
for stem,yy in [("planet_joint",7800),("cup_joint",9800)]:
    detail=Image.open(OUT/(stem+"_labeled.png")).convert("RGB")
    detail.thumbnail((1210,1900));im.paste(detail,(3410,yy))
text(3410,11400,"EVERY PIECE ACCOUNTED FOR",34,True)
wrap(3410,11465,"295 purchased hardware pieces + 59 printed assembly pieces. Counts checked against the hardware list. Fit coupons are print trials and are not part of the assembled tower.",width=57,size=30)
wrap(3410,11750,"The M8 rod is drawn alongside the base at its actual 468 mm length. Exploded spacing is enlarged for clarity; do not cut the rod to match the height of this separated view.",width=57,size=30)
im.save(OUT/"exploded_assembly_labeled_new.png")
os.replace(OUT/"exploded_assembly_labeled_new.png",OUT/"exploded_assembly_labeled.png")
preview=im.copy();preview.thumbnail((1410,4560));preview.save(OUT/"assembly_guide_preview.png")
print("Poster saved",im.size)
