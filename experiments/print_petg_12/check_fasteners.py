"""Check representative envelopes for every specified assembly fastener."""
from pathlib import Path
import math,json
import FreeCAD as App,Part
from FreeCAD import Vector as V
OUT=Path(__file__).resolve().parent/"output"
doc=App.openDocument(str(OUT/"print_prototype.FCStd"))
parts=[o for o in doc.Objects if hasattr(o,"PartID") and o.PartID.startswith("P")]
bolts=[]
def at(r,a):return r*math.cos(math.radians(a)),r*math.sin(math.radians(a))
def bolt(name,x,y,z,length,r,headr,headh,up=True,axis=None):
    v=axis or V(0,0,1 if up else -1)
    shaft=Part.makeCylinder(r,length,V(x,y,z),v)
    head=Part.makeCylinder(headr,headh,V(x,y,z)-v*headh,v)
    bolts.append((name,shaft.fuse(head)))
def axial(name,radius,angles,z,length,r,headr,headh,up=True):
    for a in angles:
        x,y=at(radius,a);bolt(name,x,y,z,length,r,headr,headh,up)
axial("base_608_cap",17.5,[0,120,240],-38.6,16,1.5,2.75,3)
axial("sail_hub",25,[30,150,270],-6,20,2,3.5,4,False)
for a in [0,120,240]:
    for r in [29,39]:
        x,y=at(r,a-18*math.sin(math.pi*(r-24)/84))
        bolt("arm_M4x10_button",x,y,-8.6,10,2,3.8,2.2,False)
    x,y=at(108,a);tx,ty=at(-3,a+90)
    bolt("cup_M4x25",x+tx,y+ty,-9,25,2,3.5,4,axis=V(-math.sin(math.radians(a)),math.cos(math.radians(a)),0))
for level in range(3):
    b=116*level
    axial("pot_608_cap",17.5,[0,120,240],b+15,16,1.5,2.75,3,False)
    axial("sun_lower_cap",17.5,[60,180,300],b+46.4,16,1.5,2.75,3)
    axial("sun_join_M3x20",17.5,[0,120,240],b+53.4,20,1.5,2.75,3)
    axial("ring_collar",90,range(0,360,60),b+96,20,2,3.5,4,False)
    for a in [0,120,240]:
        x,y=at(54,a)
        for h in [10,130,250]:
            dx,dy=at(10.5,h)
            bolt("604_cap",x+dx,y+dy,b+90,16,1.25,2.25,2.5,False)
axial("top_608_cap",17.5,[0,120,240],363,16,1.5,2.75,3,False)
axial("guard",82,range(0,360,60),386,16,2,3.5,4,False)
bad=[]
for name,s in bolts:
    a=s.BoundBox
    for o in parts:
        b=o.Shape.BoundBox
        if min(a.XMax,b.XMax)-max(a.XMin,b.XMin)<1e-5:continue
        if min(a.YMax,b.YMax)-max(a.YMin,b.YMin)<1e-5:continue
        if min(a.ZMax,b.ZMax)-max(a.ZMin,b.ZMin)<1e-5:continue
        v=s.common(o.Shape).Volume
        if v>1e-4:
            item=dict(fastener=name,part=o.Name,overlap_mm3=v)
            bad.append(item);print(item,flush=True)
result=dict(status="PASS" if not bad else "FAIL",fastener_count=len(bolts),collisions=bad,scope="Nominal steel shaft/head envelopes against printed parts; threads simplified.")
(OUT/"fastener_validation.json").write_text(json.dumps(result,indent=2))
print(result["status"],len(bolts),"fasteners",flush=True)
