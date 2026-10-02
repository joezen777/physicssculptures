"""PETG / 1.2 mm nozzle fit prototype. Run using bundled FreeCAD Python."""
from pathlib import Path
import math,json,csv,os,time,traceback
import FreeCAD as App,Part,Mesh,MeshPart
from FreeCAD import Vector as V
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"output";STL=OUT/"stl"
OUT.mkdir(exist_ok=True);STL.mkdir(exist_ok=True)
for name in ["complete.txt","validation.json","fastener_validation.json","slice_validation.json","render_complete.txt"]:(OUT/name).unlink(missing_ok=True)
M=2.;NS=36;NP=18;NR=72;ROW=4.8;GAP=.8;FACE=10.4;PITCH=116.
COLORS={"pot":(.12,.48,.72),"gear":(.95,.62,.14),"planet":(.18,.65,.45),"ring":(.58,.38,.75),"fixed":(.28,.33,.39),"metal":(.68,.72,.76)}
catalog={};instances=[];hardware=[]
def log(s):print(s,flush=True)
def ann(ro,ri,h):return Part.makeCylinder(ro,h).cut(Part.makeCylinder(ri,h))
def shift(s,z=0,x=0,y=0):
    s=s.copy();s.translate(V(x,y,z));return s
def hexagon(af,h):
    r=af/math.sqrt(3);pts=[V(r*math.cos(j*math.pi/3),r*math.sin(j*math.pi/3),0) for j in range(6)]
    return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,h))
def cyl(r,h,z=0,x=0,y=0):return Part.makeCylinder(r,h,V(x,y,z))
def xyz(r,a):
    t=math.radians(a);return r*math.cos(t),r*math.sin(t)
def holes(s,r,angles,radius,z,h):
    for a in angles:
        x,y=xyz(r,a);s=s.cut(cyl(radius,h,z,x,y))
    return s
def nuttraps(s,r,angles,af,z,h):
    for a in angles:
        x,y=xyz(r,a);s=s.cut(shift(hexagon(af,h),z,x,y))
    return s
def radial_nut_slots(s,r,angles,z,af=5.8,h=2.8):
    for a in angles:
        slot=Part.makeBox(12,af,h,V(r,-af/2,z));slot.rotate(V(),V(0,0,1),a)
        x,y=xyz(r,a);s=s.cut(slot).cut(shift(hexagon(af,h),z,x,y))
    return s
def curved(r0,r1,w,h,z=0,a=0,bow=18):
    curves=[]
    for sign in [-1,1]:
        pts=[]
        for i in range(33):
            t=i/32;r=r0+(r1-r0)*t
            angle=math.radians(a+bow*math.sin(math.pi*t))+sign*w/(2*r)
            pts.append(V(r*math.cos(angle),r*math.sin(angle),z))
        c=Part.BSplineCurve();c.interpolate(pts);curves.append((c.toShape(),pts))
    e,p=curves[0];f,q=curves[1]
    return Part.Face(Part.Wire([e,Part.makeLine(p[-1],q[-1]),f.reversed(),Part.makeLine(q[0],p[0])])).extrude(V(0,0,h))
def inv(r,rb):
    t=math.sqrt(max(0,(r/rb)**2-1));return t-math.atan(t)
def profile(n,internal=False):
    rp=M*n/2;rb=rp*math.cos(math.radians(20))
    lo=rp-.8*M if internal else rp-1.25*M
    hi=rp+1.25*M if internal else rp+.8*M
    clearance=(.12/rp)*(1 if internal else -1)
    pts=[]
    for i in range(n):
        a=2*math.pi*i/n
        pts.append(V(lo*math.cos(a-math.pi/n),lo*math.sin(a-math.pi/n),0))
        for values in [range(13),range(12,-1,-1)]:
            side=-1 if values.start==0 else 1
            for j in values:
                r=lo+(hi-lo)*j/12;half=math.pi/(2*n)+inv(rp,rb)-inv(max(r,rb),rb)+clearance
                pts.append(V(r*math.cos(a+side*half),r*math.sin(a+side*half),0))
        pts.append(V(lo*math.cos(a+math.pi/n),lo*math.sin(a+math.pi/n),0))
    clean=[]
    for p in pts:
        if not clean or (p-clean[-1]).Length>1e-7:clean.append(p)
    if (clean[-1]-clean[0]).Length<1e-7:clean.pop()
    return Part.Face(Part.makePolygon(clean+[clean[0]]))
def double_gear(n):
    one=profile(n).extrude(V(0,0,ROW));two=one.copy()
    two.rotate(V(),V(0,0,1),180/n);two.translate(V(0,0,ROW+GAP))
    return one.fuse(two).fuse(cyl(M*(n/2-1.25)-.02,FACE))
def register(key,label,shape,color,orientation="flat",support="None",note=""):
    log("Part "+key+" "+label)
    shape=shape.removeSplitter()
    if not shape.isValid() or len(shape.Solids)!=1:raise ValueError((key,"invalid/disconnected",len(shape.Solids)))
    catalog[key]=dict(label=label,shape=shape,color=COLORS[color],orientation=orientation,support=support,note=note,count=0)
    return shape
def put(key,z=0,x=0,y=0,angle=0,stage=-1,order=0,ratio=0,rot=None):
    s=catalog[key]["shape"].copy()
    rotation=rot or App.Rotation(V(0,0,1),angle)
    placement=App.Placement(V(x,y,z),rotation)
    s.Placement=placement.multiply(s.Placement)
    item=dict(key=key,shape=s,placement=placement,stage=stage,order=order,ratio=ratio,angle=angle)
    instances.append(item);catalog[key]["count"]+=1
    return item
def metal(key,label,shape,z=0,x=0,y=0,stage=-1,order=0):
    s=shift(shape,z,x,y)
    hardware.append(dict(key=key,label=label,shape=s,stage=stage,order=order))
def bearing(kind,z,x=0,y=0,stage=-1,order=0):
    d,D,h=(8,22,7) if kind==608 else (4,12,4)
    metal("H"+str(kind),str(kind)+" purchased bearing",ann(D/2,d/2,h),z,x,y,stage,order)
def spacer8(z,h,stage=-1,order=0):metal("T8_"+str(h),"Steel tube ID8.2 OD12 L"+str(h),ann(6,4.1,h),z,stage=stage,order=order)
def nut8(z,stage=-1,order=0):metal("M8_nut","M8 steel hex nut",hexagon(13,6.5).cut(cyl(4,6.5)),z,stage=stage,order=order)

# Shared open-face 608 retainer: screw positions clear outer race.
cap=ann(22,9.5,3.6);cap=holes(cap,17.5,[0,120,240],1.8,-1,6)
register("P01","608_retainer",cap,"pot",note="Three M3 screws. Cap contacts housing; 0.4 mm nominal bearing end clearance.")
def fan_hub():
    hub=ann(22,6.3,11.4).fuse(shift(hexagon(24,22).cut(cyl(6.3,22)),-22))
    hub=hub.cut(cyl(11.2,8,4))
    hub=holes(hub,17.5,[0,120,240],1.8,-2,15)
    hub=nuttraps(hub,17.5,[0,120,240],5.8,0,2.8)
    return hub
def blade_set(rend,hand):
    blades=[]
    for a in range(0,360,60):
        b=Part.makeBox(rend-21,18,3.6,V(21,-9,-1.8))
        b.rotate(V(),V(1,0,0),22*hand);b.rotate(V(),V(0,0,1),a);blades.append(b)
    return blades
def pot(hand):
    body=Part.makeCone(60,88,80).cut(Part.makeCone(56.4,84.4,80))
    body=body.fuse(ann(60,56.4,4.8)).fuse(fan_hub())
    for b in blade_set(60,hand):body=body.fuse(b)
    body=body.fuse(shift(ann(86,75.4,4),72))
    body=body.fuse(shift(ann(96,82.4,6.4),80))
    body=holes(body,90,list(range(0,360,60)),2.25,79,10)
    body=nuttraps(body,90,list(range(0,360,60)),7.4,80,3.4)
    body=radial_nut_slots(body,90,list(range(0,360,60)),80,7.4,3.4)
    return body
register("P02","pot_fan_A",pot(1),"pot","upright","Build-plate supports under fan and connector; keep bearing seat clean","Levels 1 and 3.")
register("P03","pot_fan_B",pot(-1),"pot","upright","Build-plate supports under fan and connector; keep bearing seat clean","Level 2; reversed blade pitch.")

# M8 nut pockets provide positive stationary reaction rather than an unsupported slit clamp.
carrier=ann(22,4.3,12);carrier=carrier.cut(hexagon(13.5,6.8))
for a in [0,120,240]:
    x,y=xyz(54,a)
    carrier=carrier.fuse(curved(19,54,12,12,a=a)).fuse(cyl(9,12,0,x,y))
    carrier=carrier.cut(cyl(2.25,14,-1,x,y))
register("P04","fixed_curved_carrier",carrier,"fixed","flat","None","Captured M8 nut underneath, second nut above. M4 metal planet bolts.")

log("Coarse gear templates")
sun_teeth=double_gear(NS);planet_teeth=double_gear(NP)
# Sun housing splits at z64. Both bearing pockets open onto accessible assembly faces.
lower=shift(ann(22,6.3,14),50)
lower=lower.cut(cyl(11.2,7.4,50))
lower=lower.fuse(shift(ann(12.4,9.5,4),64))
lower=holes(lower,17.5,[0,120,240],1.8,49,17)
lower=holes(lower,17.5,[0,120,240],3.1,50,3.4)
lower=holes(lower,17.5,[60,180,300],1.8,49,15)
lower=radial_nut_slots(lower,17.5,[60,180,300],58.8)
register("P05","sun_lower_bearing_housing",shift(lower,-50),"gear","flat","None","608 enters bottom; three radial nut slots retain lower cap.")
upper=shift(ann(22,6.3,52),64).fuse(shift(sun_teeth,76))
upper=upper.cut(cyl(6.3,60,63))
upper=upper.cut(shift(ann(24,20,5.5),110.5))
upper=holes(upper,17.5,[0,120,240],2.6,113,4)
upper=upper.cut(cyl(12.7,4.4,64)).cut(cyl(11.2,7,68.4))
upper=upper.cut(shift(hexagon(24.6,22.2),94))
upper=holes(upper,17.5,[0,120,240],1.8,63,13)
upper=radial_nut_slots(upper,17.5,[0,120,240],68.8)
register("P06","sun_36T_socket",shift(upper,-64),"gear","upside_down","Support gear underside when required; block supports in bearing and nut slots","Upper 608 inserts from bottom; lower housing closes it.")

planet=planet_teeth.cut(cyl(3.5,FACE))
planet=planet.cut(cyl(6.2,4.4,2.4)).cut(cyl(8.9,3.6,6.8))
planet=holes(planet,10.5,[0,120,240],1.45,-1,13)
planet=nuttraps(planet,10.5,[0,120,240],5.4,0,2.4)
register("P07","planet_18T_604",planet,"planet","flat","None","604 inserts from top; three M2.5 nuts load from underside.")
pcap=shift(ann(15,4.7,3.6),3.6).fuse(ann(8.6,4.7,3.6))
pcap=holes(pcap,10.5,[0,120,240],1.45,3.5,5)
register("P08","604_retainer",pcap,"planet","upside_down","None","Fits counterbore; M2.5 x16 bolts and nuts.")

rows=[]
for j in range(2):
    hole=profile(NR,True).extrude(V(0,0,ROW));hole.rotate(V(),V(0,0,1),180/NR+j*180/NR)
    rows.append(shift(cyl(82,ROW).cut(hole),j*(ROW+GAP)))
ring=rows[0].fuse(rows[1]).fuse(shift(ann(82,74.6,GAP),ROW))
ring=ring.fuse(shift(ann(96,74.8,4.8),FACE))
ring=holes(ring,90,list(range(0,360,60)),2.25,-1,18)
half=ring.common(Part.makeBox(110,220,30,V(.3,-110,-1)))
register("P09","72T_ring_half",half,"ring","upside_down","None","Two identical halves per stage; second half rotated 180 degrees.")

def collar(top_r,height):
    s=Part.makeCone(94.4,top_r,height).cut(Part.makeCone(90.8,top_r-3.6,height))
    for a in range(0,360,60):
        x,y=xyz(90,a);s=s.fuse(cyl(6,4.8,0,x,y))
    s=holes(s,90,list(range(0,360,60)),2.25,-1,height+2)
    return holes(s,90,list(range(0,360,60)),4.2,4.8,height+1)
register("P10","interstage_air_collar",collar(66.4,28.8),"pot","upside_down","Local support for mounting bosses if slicer requires","Noncontact overlap at next pot; do not glue adjacent rotating levels.")
register("P11","terminal_air_collar",collar(83.2,20.8),"pot","upside_down","Local support for mounting bosses if slicer requires")

# Base and wind input.
base=ann(96,4.3,12);base=base.cut(hexagon(13.5,6.8))
for a in [0,120,240]:
    x,y=xyz(72,a);base=base.fuse(cyl(12,6,-6,x,y))
register("P12","stationary_base",base,"fixed","upside_down","None","M8 nut below and above base; feet recess rod end.")
adapter=shift(ann(22,6.3,35),-35).fuse(shift(ann(30,6.3,6),-24))
adapter=adapter.cut(shift(ann(24,17.5,18),-18))
adapter=adapter.fuse(shift(hexagon(36,12).cut(cyl(6.3,12)),-18))
adapter=adapter.cut(cyl(11.2,7.4,-35))
adapter=adapter.cut(shift(hexagon(24.6,22.4),-22.4))
adapter=holes(adapter,25,[30,150,270],2.25,-25,8)
adapter=nuttraps(adapter,25,[30,150,270],7.4,-24,3.4)
adapter=radial_nut_slots(adapter,25,[30,150,270],-24,7.4,3.4)
for a in [0,120,240]:
    x,y=xyz(29,a-18*math.sin(math.pi*5/84));adapter=adapter.cut(cyl(2.6,2.1,-20,x,y))
adapter=holes(adapter,17.5,[0,120,240],1.8,-36,15)
adapter=radial_nut_slots(adapter,17.5,[0,120,240],-27)
adapter=holes(adapter,17.5,[0,120,240],2.6,-3,4)
register("P13","base_drive_adapter",shift(adapter,35),"pot","upside_down","Support flange underside; block supports in socket","Bottom 608 inserts from below; P01 cap and M3 x16 fasteners.")
sailhub=cyl(30,12).cut(hexagon(36.6,12))
for a in [0,120,240]:
    sailhub=sailhub.fuse(curved(24,45,18,6,a=a,bow=0))
    # Curve-matching pad extends over the root of the bowed arm.
    for r in [29,39]:
        t=(r-24)/(108-24);aa=a-18*math.sin(math.pi*t);x,y=xyz(r,aa)
        sailhub=sailhub.fuse(cyl(7,6,0,x,y))
        sailhub=sailhub.cut(cyl(2.25,8,-1,x,y))
        sailhub=sailhub.cut(shift(hexagon(7.4,3.4),0,x,y))
for a in [0,120,240]:sailhub=sailhub.cut(curved(24,108,12.6,6.1,z=6,a=a,bow=-18))
sailhub=holes(sailhub,25,[30,150,270],2.25,-1,15)
register("P14","sail_hex_hub",sailhub,"pot","flat","None","Three M4 x20 adapter bolts; six recessed M4 x10 button-head arm bolts.")
arm=curved(24,108,12,6,bow=-18)
for r in [29,39]:
    aa=-18*math.sin(math.pi*(r-24)/84);x,y=xyz(r,aa);arm=arm.cut(cyl(2.25,8,-1,x,y)).cut(cyl(4.2,2.8,3.4,x,y))
arm=arm.fuse(Part.makeBox(16,6,16,V(100,-3,-5)))
arm=arm.cut(Part.makeBox(25,12,20,V(98,3,-6)))
arm=arm.cut(Part.makeCylinder(2.25,8,V(108,-4,3),V(0,1,0)))
arm=arm.cut(Part.makeCylinder(4.2,27,V(108,-30,3),V(0,1,0)))
register("P15","curved_sail_arm",arm,"pot","flat","Build-plate support under arm; upright end mounting tab","Each cup bolts to end tab using M4 x25.")
cup=Part.makeSphere(24,V(0,0,20)).cut(Part.makeSphere(20.4,V(0,0,20)))
cup=cup.common(Part.makeBox(60,60,14,V(-30,-30,-4)))
cup=cup.fuse(cyl(8,10,-8)).cut(cyl(2.25,22,-9))
register("P16","wind_cup",cup,"gear","upright","Build-plate support under bowl around mounting boss","Through M4 bolt, washer and nut accessible from open bowl.")
fan=fan_hub()
for b in blade_set(72,-1):fan=fan.fuse(b)
register("P17","top_fan_B",fan,"gear","upright","Build-plate support under blades and connector")

shroud=ann(79.6,76,34).fuse(shift(ann(88,76,6),34))
shroud=holes(shroud,82,list(range(0,360,60)),2.25,33,9)
shroud=nuttraps(shroud,82,list(range(0,360,60)),7.4,34,3.4)
register("P18","top_guard_shroud",shroud,"fixed","upside_down","None","Six M4 x16 bolts join grille.")
grille=ann(88,76,6).fuse(ann(22,4.3,12)).cut(hexagon(13.5,6.8))
for a in range(0,360,60):grille=grille.fuse(curved(19,79,7.2,6,a=a))
for r in range(25,74,6):grille=grille.fuse(ann(r+1.8,r-1.8,6))
grille=holes(grille,82,list(range(0,360,60)),2.25,-1,9)
register("P19","curved_guard_grille",grille,"fixed","flat","None","Nine rings, six spokes, nominal ring gaps 2.4 mm; not a certified child guard.")

# Assembly placements (all coordinates in mm).
put("P12",-66,order=0);nut8(-66);nut8(-54)
metal("M8_rod","M8 threaded steel rod, cut 468 mm",cyl(4,468),-68)
spacer8(-47.5,12.5);bearing(608,-35)
put("P01",-38.6,order=1);put("P13",-35,order=2,ratio=1)
spacer8(-28,32)
put("P14",-18,order=3,ratio=1)
for a in [0,120,240]:
    put("P15",-12,angle=a,order=4,ratio=1)
    x,y=xyz(108,a);tx,ty=xyz(11,a+90)
    rot=App.Rotation(V(0,0,1),V(-math.sin(math.radians(a)),math.cos(math.radians(a)),0))
    put("P16",-9,x+tx,y+ty,order=5,ratio=1,rot=rot)
for level in range(3):
    b=level*PITCH;ratio=(-2)**level
    put("P02" if level%2==0 else "P03",b,stage=level,order=0,ratio=ratio)
    bearing(608,b+4,stage=level,order=1)
    put("P01",b+11.4,stage=level,order=2,ratio=ratio)
    spacer8(b+11,15,level);nut8(b+26,level)
    put("P04",b+26,stage=level,order=3)
    nut8(b+38,level);spacer8(b+44.5,5.9,level)
    put("P01",b+46.4,angle=60,stage=level,order=4,ratio=-2*ratio)
    bearing(608,b+50.4,stage=level,order=5);spacer8(b+57.4,11,level)
    put("P05",b+50,stage=level,order=6,ratio=-2*ratio)
    bearing(608,b+68.4,stage=level,order=7)
    put("P06",b+64,stage=level,order=8,ratio=-2*ratio)
    for a in [0,120,240]:
        x,y=xyz(54,a)
        metal("M4x75","M4 x75 planet bolt",cyl(2,75),b+26,x,y,level,3)
        metal("M4_nut","M4 nut",hexagon(7,3.2).cut(cyl(2,3.2)),b+38,x,y,level,3)
        metal("T4_37.2","Steel tube ID4.2 OD6 L37.2",ann(3,2.1,37.2),b+41.2,x,y,level,4)
        bearing(604,b+78.4,x,y,level,6)
        put("P07",b+76,x,y,angle=10,stage=level,order=7,ratio=4*ratio)
        put("P08",b+82.8,x,y,angle=10,stage=level,order=9,ratio=4*ratio)
        metal("T4_10","Steel tube ID4.2 OD6 L10",ann(3,2.1,10),b+82.4,x,y,level,9)
        metal("M4_washer","M4 washer OD7",ann(3.5,2.1,.8),b+92.4,x,y,level,10)
        metal("M4_nut","M4 nut",hexagon(7,3.2).cut(cyl(2,3.2)),b+93.2,x,y,level,10)
    for a in [0,180]:put("P09",b+76,angle=a,stage=level,order=10,ratio=ratio)
    put("P10" if level<2 else "P11",b+91.2,stage=level,order=11,ratio=ratio)
    spacer8(b+75.4,44.6,level)
put("P17",348,stage=3,order=0,ratio=-8)
bearing(608,352,stage=3,order=1)
put("P01",359.4,stage=3,order=2,ratio=-8)
spacer8(359,21,3)
put("P18",340,stage=3,order=3)
nut8(380,3)
put("P19",380,stage=3,order=4)
metal("M8_acorn","M8 acorn nut",hexagon(13,10).cut(cyl(4,8)),392,stage=3,order=5)

# Fit coupons are separate from production counts.
coupon=Part.makeBox(90,38,10)
for x,d in [(16,22.2),(45,22.4),(74,22.6)]:coupon=coupon.cut(cyl(d/2,12,-1,x,20))
register("C01","608_fit_coupon",coupon,"fixed",note="Left to right: 22.2 / 22.4 / 22.6 mm. Print this first.")
coupon=Part.makeBox(66,28,6)
for x,d in [(12,12.2),(33,12.4),(54,12.6)]:coupon=coupon.cut(cyl(d/2,8,-1,x,14))
register("C02","604_fit_coupon",coupon,"fixed",note="Left to right: 12.2 / 12.4 / 12.6 mm.")
catalog["C01"]["count"]=catalog["C02"]["count"]=1

def export_all():
    doc=App.newDocument("PETG12_Prototype")
    for i,item in enumerate(instances):
        key=item["key"];o=doc.addObject("PartDesign::Feature",key+"_"+str(i+1))
        o.Label=key+" "+catalog[key]["label"];o.Shape=Part.makeCompound([item["shape"]])
        o.addProperty("App::PropertyString","PartID");o.PartID=key
        o.addProperty("App::PropertyFloat","SpeedRatio");o.SpeedRatio=item["ratio"]
        item["object"]=o
    for i,h in enumerate(hardware):
        o=doc.addObject("PartDesign::Feature","Hardware_"+str(i+1));o.Label=h["label"];o.Shape=Part.makeCompound([h["shape"]])
        o.addProperty("App::PropertyString","PartID");o.PartID=h["key"];h["object"]=o
    doc.recompute()
    doc.saveAs(str(OUT/"print_prototype.FCStd"))
    rows=[]
    for key,d in catalog.items():
        s=d["shape"].copy()
        if d["orientation"]=="upside_down":s.rotate(V(),V(1,0,0),180)
        box=s.BoundBox;s.translate(V(-box.XMin,-box.YMin,-box.ZMin))
        box=s.BoundBox
        assert box.XLength<=200 and box.YLength<=200 and box.ZLength<=240,(key,box)
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.06,AngularDeflection=.15,Relative=False)
        if not mesh.isSolid():raise ValueError((key,"mesh not closed"))
        file=key+"_"+d["label"]+"_print-"+str(d["count"])+"x.stl"
        mesh.write(str(STL/file))
        rows.append(dict(id=key,name=d["label"],quantity=d["count"],file=file,
                         size_mm=[round(box.XLength,2),round(box.YLength,2),round(box.ZLength,2)],
                         support=d["support"],orientation=d["orientation"],note=d["note"],
                         triangles=mesh.CountFacets,volume_mm3=s.Volume))
        log("STL "+file)
    (OUT/"parts.json").write_text(json.dumps(rows,indent=2))
    with (OUT/"print_manifest.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,lineterminator="\n",fieldnames=["id","name","quantity","file","size_mm","support","orientation","note","triangles","volume_mm3"]);w.writeheader();w.writerows(rows)
    scene=[]
    for item in instances:
        p=item["shape"].BoundBox.Center
        scene.append(dict(name=item["object"].Name,key=item["key"],stage=item["stage"],order=item["order"],center=[p.x,p.y,p.z],ratio=item["ratio"]))
    for h in hardware:
        p=h["shape"].BoundBox.Center
        scene.append(dict(name=h["object"].Name,key=h["key"],stage=h["stage"],order=h["order"],center=[p.x,p.y,p.z],hardware=True))
    (OUT/"scene.json").write_text(json.dumps(scene,indent=2))
    (OUT/"colors.json").write_text(json.dumps({k:d["color"] for k,d in catalog.items()}))
    return doc
if __name__=="__main__":
    export_all()
    (OUT/"complete.txt").write_text("STL and native prototype generated; validation is separate.\n")
