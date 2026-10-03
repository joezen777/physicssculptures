"""Hardware sprues with analytic thread meshes and robust Manifold Boolean operations."""
from pathlib import Path
from collections import Counter
import math,json,csv,hashlib,os,subprocess,struct
import numpy as np
import manifold3d as m
ROOT=Path(__file__).resolve().parent
OUT=ROOT.parent/"print_petg_12/output/stl/resin_hardware_sprues"
SOURCE=ROOT.parent/"print_petg_12/output"
PITCH={2.5:.45,3:.5,4:.7,8:1.25}
catalog={};thread_cache={};checks=[]
def log(s):print(s,flush=True)
def cyl(r,h):return m.Manifold.cylinder(h,r,circular_segments=96)
def box(x,y,z):return m.Manifold.cube((x,y,z))
def move(s,x=0,y=0,z=0):return s.translate((x,y,z))
def union(shapes):return m.Manifold.batch_boolean(shapes,m.OpType.Add)
def hexagon(af,h):
    r=af/math.sqrt(3)
    return m.Manifold.extrude(m.CrossSection([[(r*math.cos(i*math.pi/3),r*math.sin(i*math.pi/3)) for i in range(6)]]),h)
def ring(ro,ri,h):return cyl(ro,h)-move(cyl(ri,h+2),z=-1)
def threaded(d,L,offset):
    key=(d,L,offset)
    if key in thread_cache:return thread_cache[key]
    p=PITCH[d];r=d/2+offset;root=r-.61343*p
    n=64 if d>=8 else 48
    nz=math.ceil(L/p*24)
    theta=np.arange(n)*2*np.pi/n
    z=np.linspace(0,L,nz+1)
    phase=(z[:,None]/p-theta[None,:]/(2*np.pi))%1
    distance=np.minimum(phase,1-phase)
    radius=r-(r-root)*np.clip((distance-1/16)/(5/12-1/16),0,1)
    v=np.stack([radius*np.cos(theta),radius*np.sin(theta),np.broadcast_to(z[:,None],radius.shape)],axis=-1).reshape(-1,3)
    faces=[]
    for i in range(nz):
        for j in range(n):
            a=i*n+j;b=i*n+(j+1)%n;c=(i+1)*n+j;e=(i+1)*n+(j+1)%n
            faces.extend([(a,b,e),(a,e,c)])
    low=len(v);high=low+1;v=np.vstack([v,[0,0,0],[0,0,L]])
    for j in range(n):
        faces.append((low,(j+1)%n,j))
        faces.append((high,nz*n+j,nz*n+(j+1)%n))
    s=m.Manifold(m.Mesh(np.asarray(v,np.float32),np.asarray(faces,np.uint32)))
    assert s.status()==m.Error.NoError and len(s.decompose())==1
    thread_cache[key]=s
    return s
def register(key,label,spec,s,points,tilt=15):
    assert s.status()==m.Error.NoError and len(s.decompose())==1,key
    original=s
    s=s.rotate((tilt,0,0));b=s.bounding_box();delta=np.array([-b[0],-b[1],-b[2]])
    s=s.translate(delta)
    a=math.radians(tilt);rotation=np.array([[1,0,0],[0,math.cos(a),-math.sin(a)],[0,math.sin(a),math.cos(a)]])
    anchors=[(rotation@np.array(p)+delta).tolist() for p in points]
    catalog[key]=dict(label=label,spec=spec,shape=s,original=original,anchors=anchors)
def screw(key,d,L,button=False):
    hr,hh,af={2.5:(2.25,2.5,2),3:(2.75,3,2.5),4:(3.5,4,3),8:(6.5,8,6)}[d]
    if button:
        hr,hh,af=3.8,2.2,2.5;cz=(hr*hr-4+hh*hh)/(2*hh)
        head=move(m.Manifold.sphere(math.sqrt(4+cz*cz),96),z=cz)^cyl(hr,hh)
        points=[(0,1.65,0),(0,-1.65,0)]
    else:
        head=cyl(hr,hh);points=[(hr*.76,0,0),(-hr*.76,0,0)]
    head=head-move(hexagon(af,hh*.6+.1),z=-.1)
    shaft=move(threaded(d,L+.02,-.025),z=hh-.02)
    body=head+shaft
    suffix=" button screw" if button else " axle bolt" if L==75 else " screw"
    register(key,"M"+str(d)+"x"+str(L)+(" B" if button else ""),"M"+str(d)+" x"+str(L)+suffix,body,points,10 if L==75 else 15)
def nut(key,d,acorn=False):
    af,h={2.5:(5,2),3:(5.5,2.4),4:(7,3.2),8:(13,6.5)}[d]
    body=hexagon(af,h);depth=h
    if acorn:
        body=body+(move(m.Manifold.sphere(6.4,96),z=h+.1)^move(cyl(6.4,6.7),z=h-.2));depth=8.5
    p=PITCH[d]
    body=body-move(threaded(d,depth+p*(1 if acorn else 2),.075),z=-p)
    chamfer=m.Manifold.cylinder(.4*p,d/2+.18,d/2-.35*p,circular_segments=96)
    # No entry chamfer: avoid coincident fine-thread/chamfer mesh edges.
    register(key,"M"+str(d)+(" CAP" if acorn else " N"),"M"+str(d)+(" acorn nut" if acorn else " nut"),body,[(0,af/2-.4,0),(0,-af/2+.4,0)],20)
for k,d,L,b in [("S25_16",2.5,16,False),("S3_16",3,16,False),("S3_20",3,20,False),("S4_20",4,20,False),("B4_10",4,10,True),("S4_25",4,25,False),("S4_16",4,16,False),("S4_75",4,75,False)]:
    screw(k,d,L,b);log("PART "+k)
for k,d in [("N25",2.5),("N3",3),("N4",4),("N8",8)]:nut(k,d)
nut("AC8",8,True)
for od in [7,9]:
    r=(od/2+2.1)/2
    register("W"+str(od),"W"+str(od),"M4 washer OD"+str(od),ring(od/2,2.1,.8),[(r,0,0),(-r,0,0)],20)
big=[];small=[]
for L,count in [(12.5,1),(32,1),(15,3),(5.9,3),(11,3),(44.6,3),(21,1)]:
    k="T8_"+str(L);big += [k]*count
    register(k,"8.2/12x"+str(L),"Tube ID8.2 OD12 L"+str(L),ring(6,4.1,L),[(5.05,0,0),(-5.05,0,0)],0)
for L in [37.2,10]:
    k="T4_"+str(L);small += [k]*9
    register(k,"4.2/6x"+str(L),"Tube ID4.2 OD6 L"+str(L),ring(3,2.1,L),[(2.55,0,0),(-2.55,0,0)],0)
for k,d in [("TEST25",2.5),("TEST3",3),("TEST4",4),("TEST8",8)]:screw(k,d,8)
for d,k in [(2.5,"N25"),(3,"N3"),(4,"N4"),(8,"N8")]:
    for angle in [0,90,180]:
        nutshape=catalog[k]["original"].rotate((0,0,angle)).translate((0,0,PITCH[d]*angle/360))
        vol=(threaded(d,8,-.025)^nutshape).volume()
        assert abs(vol)<1e-5,(d,angle,vol)
        checks.append(dict(size=d,rotation_degrees=angle,overlap_mm3=vol))
log("THREAD CHECKS PASS")
sheets=[
("H00","thread_fit_test",["TEST25","N25","TEST3","N3","TEST4","N4","TEST8","N8"],4,1,True),
("H01","M2p5x16_screws",["S25_16"]*9,3,3,False),
("H02","M3x16_screws",["S3_16"]*8,4,3,False),
("H03","M3x20_screws",["S3_20"]*9,3,1,False),
("H04","M4x20_screws",["S4_20"]*7,4,3,False),
("H05","M4x10_button_screws",["B4_10"]*6,3,1,False),
("H06","M4x25_screws",["S4_25"]*3,3,1,False),
("H07","M4x16_screws",["S4_16"]*6,3,1,False),
("H08","M4x75_axle_bolts",["S4_75"]*3,3,3,False),
("H09","M2p5_nuts",["N25"]*9,3,3,False),
("H10","M3_nuts",["N3"]*11,4,3,False),
("H11","M4_nuts",["N4"]*18,6,3,False),
("H12","M8_nuts",["N8"]*9,3,1,False),
("H13","M8_acorn_nut",["AC8"],1,1,False),
("H14","washers_OD7_and_OD9",["W7"]*9+["W9"]*3,6,1,False),
("H15","ID8p2_OD12_spacers",big,4,1,False),
("H16","ID4p2_OD6_spacers",small,5,1,False)]
(ROOT/"label_request.json").write_text(json.dumps([i["label"] for i in catalog.values()]))
exe=Path.home()/"Applications/freecad-experiment/squashfs-root/AppRun"
env=os.environ.copy();env["PYTHONPATH"]=str(exe.parent/"usr/lib")
subprocess.run([str(exe),"python",str(ROOT/"prepare_text.py")],env=env,check=True)
texts=json.loads((ROOT/"label_meshes.json").read_text())
for item in catalog.values():
    v,f=texts[item["label"]]
    item["text"]=m.Manifold(m.Mesh(np.asarray(v,np.float32),np.asarray(f,np.uint32)))
    assert item["text"].status()==m.Error.NoError
def size(s):
    b=s.bounding_box();return np.array(b[3:])-np.array(b[:3])
def stl(s,path):
    mesh=(s if path.name.startswith(("H15","H16")) else s.simplify(.002)).to_mesh();v=np.asarray(mesh.vert_properties)[:,:3];faces=np.asarray(mesh.tri_verts)
    t=v[faces];normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);length=np.linalg.norm(normal,axis=1);normal/=np.maximum(length[:,None],1e-20)
    data=np.zeros(len(faces),dtype=[("n","<f4",(3,)),("v","<f4",(3,3)),("a","<u2")]);data["n"]=normal;data["v"]=t
    path.write_bytes(b"Hardware sprues, millimeters".ljust(80,b" ")+struct.pack("<I",len(faces))+data.tobytes())
    return len(faces)
report=[];production=Counter()
components=ROOT/"render_meshes";components.mkdir(exist_ok=True)
for sid,name,keys,cols,copies,test in sheets:
    log("SHEET "+sid)
    cw=max(max(size(catalog[k]["shape"])[0],size(catalog[k]["text"])[0]+2) for k in keys)
    ch=max(size(catalog[k]["shape"])[1] for k in keys);nr=math.ceil(len(keys)/cols)
    w=6+cols*cw+(cols-1)*3;h=6+nr*(ch+8)+(nr-1)*3
    frame=box(w,h,2.4)-move(box(w-4.8,h-4.8,4.4),2.4,2.4,-1)
    pieces=[];labels=[];anchors=[];framebits=[frame];textbits=[]
    for i,k in enumerate(keys):
        item=catalog[k];dims=size(item["shape"]);td=size(item["text"])
        x=3+(i%cols)*(cw+3)+(cw-dims[0])/2;y=3+(i//cols)*(ch+11)+8+(ch-dims[1])/2
        pieces.append(move(item["shape"],x,y,6))
        tw=max(10,td[0]+2);th=max(6.3,td[1]+1.6)
        tx=x+(dims[0]-tw)/2;ty=y-8
        framebits.extend([move(box(w,2.4,2.4),y=ty),move(box(tw,th,2.6),tx,ty)])
        textbits.append(move(item["text"],tx+(tw-td[0])/2,ty+(th-td[1])/2,2.5))
        labels.append(dict(key=k,text=item["label"],font_pt=12,emboss_mm=.8,position=[tx,ty]))
        for p in item["anchors"]:
            ax,ay,az=p[0]+x,p[1]+y,p[2]+6
            framebits += [move(box(2.4,h,2.4),ax-1.2),move(cyl(.9,az-3.3),ax,ay,2.3),
                move(m.Manifold.cylinder(1,.9,.35,circular_segments=32),ax,ay,az-1.1),
                move(cyl(.35,.45),ax,ay,az-.15)]
            anchors.append(dict(key=k,point=[ax,ay,az],neck_diameter_mm=.7))
        if not test:production[item["spec"]]+=copies
    gray=union(framebits);gold=union(textbits);blue=union(pieces)
    whole=union([gray,gold,blue])
    assert whole.status()==m.Error.NoError and len(whole.decompose())==1,(sid,whole.status(),len(whole.decompose()))
    dims=size(whole);assert all(dims<=np.array([218,123,200])),(sid,dims)
    file=sid+"_"+name+"_print-"+str(copies)+"x.stl"
    triangles=stl(whole,OUT/file)
    for suffix,part in [("frame",gray),("labels",gold),("parts",blue)]:stl(part,components/(sid+"_"+suffix+".stl"))
    report.append(dict(id=sid,name=name,file=file,print_copies=copies,calibration_sheet=test,
        items_per_sheet=dict(Counter(catalog[k]["spec"] for k in keys)),size_mm=np.round(dims,3).tolist(),
        labels=labels,anchors=anchors,solid_resin_ml=whole.volume()/1000,triangles=triangles,
        sha256=hashlib.sha256((OUT/file).read_bytes()).hexdigest(),support_status="Add final resin supports and inspect sliced layers."))
    (OUT/"sprue_manifest.json").write_text(json.dumps(report,indent=2))
    log("PASS "+sid)
# Independently parse the purchased hardware bill of materials.
import re
expected=Counter()
for row in csv.DictReader((SOURCE/"hardware_bom.csv").open()):
    item,spec=row["item"],row["specification"]
    if item.startswith(("608","604")) or "threaded rod" in item:continue
    if item=="Steel tube spacer":
        a,b,c=re.search(r"ID([\d.]+) / OD([\d.]+) / L([\d.]+)",spec).groups();key="Tube ID"+a+" OD"+b+" L"+c
    elif "washer" in item:key="M4 washer OD"+re.search(r"([\d.]+) mm OD",spec).group(1)
    elif "acorn" in item:key="M8 acorn nut"
    elif "nut" in item:key=item.split()[0]+" nut"
    else:
        d,L=re.search(r"M([\d.]+) x(\d+)",spec).groups()
        key="M"+d+" x"+L+(" axle bolt" if L=="75" else " button screw" if "button" in item else " screw")
    expected[key]+=int(row["quantity"])
assert production==expected and sum(production.values())==274
with (OUT/"sprue_manifest.csv").open("w",newline="") as f:
    wr=csv.writer(f,lineterminator="\n");wr.writerow(["sheet","file","print_copies","items_per_sheet","size_mm","calibration_only"])
    for r in report:wr.writerow([r["id"],r["file"],r["print_copies"],r["items_per_sheet"],r["size_mm"],r["calibration_sheet"]])
result=dict(status="PASS",sheet_files=17,production_hardware_count=274,production_quantities=dict(production),calibration_items=8,
    thread_checks=checks,thread_method="Analytic radial profile sampled as closed helical mesh, Manifold Boolean operations",
    thread_resolution="48 angular samples (64 for M8), 24 axial steps per pitch",labels_font_pt=12,emboss_mm=.8,
    all_closed_connected_meshes=True,all_fit_M5s=True,excluded_purchased_parts={"608 bearings":11,"604 bearings":9,"M8 steel rod 468 mm":1})
(OUT/"validation.json").write_text(json.dumps(result,indent=2))
log("ALL HARDWARE SHEETS PASS")
