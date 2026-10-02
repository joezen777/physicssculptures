"""Readable enlarged details from the same FreeCAD exploded geometry."""
from pathlib import Path
from collections import defaultdict
import json,textwrap
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).resolve().parent/"output"
def compose(which,title,subtitle):
    raw=Image.open(OUT/(which+"_raw.png")).convert("RGB")
    w,h=2700,raw.height+400
    im=Image.new("RGB",(w,h),"white");d=ImageDraw.Draw(im)
    def font(n,b=False):
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
    def text(x,y,s,n=35,b=False,color="#152c3a"):d.text((x,y),s,font=font(n,b),fill=color)
    def wrap(x,y,s,n=32,width=26,b=False):
        for line in textwrap.wrap(s,width):
            text(x,y,line,n,b);y+=n*1.35
        return y
    text(60,35,title,58,True);wrap(60,116,subtitle,32,130)
    im.paste(raw,(650,210))
    ann=json.loads((OUT/(which+"_annotations.json")).read_text())
    groups=defaultdict(list)
    for a in ann:groups[a["role"]].append(a)
    ordered=sorted(groups.items(),key=lambda kv:sum(a["pixel"][1] for a in kv[1])/len(kv[1]))
    last=[230,230]
    for i,(role,items) in enumerate(ordered):
        side=i%2;target=210+sum(a["pixel"][1] for a in items)/len(items)
        y=max(target-40,last[side]+165);last[side]=y
        if which=="cup_joint":y=380+(i//2)*450+(side*170)
        x=45 if side==0 else 2120;edge=610 if side==0 else 2090
        for a in items:
            ax=650+a["pixel"][0];ay=210+a["pixel"][1]
            elbow=630 if side==0 else 2070
            d.line([(ax,ay),(elbow,ay),(edge,y+30)],fill="#8297a2",width=3)
            d.ellipse((ax-6,ay-6,ax+6,ay+6),fill="#176c98")
        a=items[0]
        name=a["spec"] if a["hardware"] else {"P04":"P04 fixed carrier","P07":"P07 planet gear","P08":"P08 bearing cap","P15":"P15 curved arm","P16":"P16 wind cup"}[a["key"]]
        yy=wrap(x,y,name+" x"+str(len(items)),34,25,True)
        if a["hardware"]:wrap(x,yy+8,role.capitalize(),28,30)
        assert y+150<h-90,(which,role,y)
    text(60,h-85,"Exploded spacing is illustrative. Use the assembly guide for tightening and insertion order.",29)
    im.save(OUT/(which+"_labeled.png"))
    return im
if __name__=="__main__":
    compose("planet_joint","604 PLANET BEARING / P04 AXLE","One of nine identical axle stacks. Steel spacers clamp only the inner bearing race; P08 retains the outer race in P07.")
    compose("cup_joint","P16 WIND CUP / P15 ARM","One of three joints. M4 x25 bolt enters from the arm side; the OD9 washer and M4 nut sit inside the cup.")
