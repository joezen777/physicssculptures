"""Full-size resin sprue sheets; run with bundled FreeCAD Python from WSL."""
from pathlib import Path
from collections import Counter
import math,json,csv,hashlib,time,os
import FreeCAD as App,Part,MeshPart,Mesh
from FreeCAD import Vector as V
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/"print_petg_12"/"output"
OUT=SOURCE/"stl"/"resin_sprue_sheets";OUT.mkdir(exist_ok=True)
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_PT=12;FONT_MM=FONT_PT*25.4/72;EMBOSS=.8
RAIL=2.4;LIFT=6.;GAP=3.;BORDER=3.;LABEL_BAND=8.
BED=(218.,123.,200.)
rows=json.loads((SOURCE/"parts.json").read_text())
catalog={r["id"]:r for r in rows};scene=json.loads((SOURCE/"scene.json").read_text())
source=App.openDocument(str(SOURCE/"print_prototype.FCStd"))
resume=os.environ.get("RESIN_RESUME")=="1" and (ROOT/"resin_sprue_sheets.FCStd").exists()
doc=App.openDocument(str(ROOT/"resin_sprue_sheets.FCStd")) if resume else App.newDocument("ResinSprueSheets")
shapes={};anchors={};report=json.loads((OUT/"sprue_manifest.json").read_text()) if resume else []
def log(s):print(s,flush=True)
def moved(shape,x=0,y=0,z=0):
    s=shape.copy();s.translate(V(x,y,z));return s
def normalize(s):
    b=s.BoundBox;s.translate(V(-b.XMin,-b.YMin,-b.ZMin));return s
def canonical(key):
    if key.startswith("C"):
        if key=="C01":w,d,h,holes=90,38,10,[(16,22.2),(45,22.4),(74,22.6)];yc=20
        else:w,d,h,holes=66,28,6,[(12,12.2),(33,12.4),(54,12.6)];yc=14
        s=Part.makeBox(w,d,h)
        for x,diam in holes:s=s.cut(Part.makeCylinder(diam/2,h+2,V(x,yc,-1)))
        return s
    name=next(s["name"] for s in scene if s["key"]==key)
    s=source.getObject(name).Shape.copy()
    if key in ("P07","P08"):s.rotate(V(),V(0,0,1),-10)
    if key=="P16":s.rotate(V(),V(1,0,0),90)
    return normalize(s)
# Z rotation first; X tilt second. Model axes, not slicer-relative Euler fields.
orient={
"P01":(0,25),"P02":(0,90),"P03":(0,90),"P04":(90,25),
"P05":(0,25),"P06":(0,30),"P07":(0,65),"P08":(0,55),
"P09":(90,30),"P10":(0,70),"P11":(0,70),"P12":(0,70),
"P13":(0,25),"P14":(90,25),"P15":(0,15),"P16":(0,60),
"P17":(0,60),"P18":(0,75),"P19":(0,65),"C01":(0,20),"C02":(0,20)}
if resume:
    for o in list(doc.Objects):
        if o.Name not in {r["id"] for r in report}:doc.removeObject(o.Name)
for key in catalog:
    s=canonical(key);original_volume=s.Volume
    z,x=orient[key];s.rotate(V(),V(0,0,1),z);s.rotate(V(),V(1,0,0),x);normalize(s)
    assert abs(s.Volume/catalog[key]["volume_mm3"]-1)<1e-6,key
    assert s.isValid() and len(s.Solids)==1,key
    shapes[key]=s
    b=s.BoundBox
    log(key+" oriented "+str([round(b.XLength,2),round(b.YLength,2),round(b.ZLength,2)]))
def lettering(text):
    wires=Part.makeWireString(text,FONT,FONT_MM,0)
    solids=[]
    for glyph in wires:
        face=Part.makeFace(glyph,"Part::FaceMakerBullseye")
        solids.append(face.extrude(V(0,0,EMBOSS+.1)))
    s=Part.makeCompound(solids);return normalize(s)
def anchor_points(key):
    if key in anchors:return anchors[key]
    s=shapes[key];b=s.BoundBox;points,facets=s.tessellate(.15)
    buckets={}
    rz,rx=orient[key]
    inverse=App.Rotation(V(1,0,0),rx).multiply(App.Rotation(V(0,0,1),rz)).inverted()
    for face in facets:
        a,c,d=[points[i] for i in face];n=(c-a).cross(d-a)
        if n.Length<1e-8 or n.z/n.Length>-.35:continue
        if key in ("P06","P07","P09") and inverse.multVec(n).z/n.Length>-.95:continue
        p=(a+c+d)/3
        cell=(min(2,int(3*p.x/max(b.XLength,1))),min(1,int(2*p.y/max(b.YLength,1))))
        if cell not in buckets or p.z<buckets[cell].z:buckets[cell]=p
    found=[]
    for p in buckets.values():
        hit=s.common(Part.makeLine(V(p.x,p.y,-1),V(p.x,p.y,b.ZMax+1)))
        if hit.isNull():continue
        z=hit.BoundBox.ZMin
        if z<-.001:continue
        if any(math.hypot(p.x-q[0],p.y-q[1])<2 for q in found):continue
        found.append((p.x,p.y,z))
    found=[p for p in found if p[2]<=max(45,b.ZLength*.3)]
    assert len(found)>=2,(key,len(found))
    anchors[key]=found;return found
# A sheet filename's quantity is the number of copies of that complete sheet.
sheets=[
("R01","608_retainers",["P01"]*8,4,1,False),
("R02","pot_fan_A",["P02"],1,2,True),
("R03","pot_fan_B",["P03"],1,1,True),
("R04","fixed_carrier",["P04"],1,3,False),
("R05","lower_sun_housings",["P05"]*3,3,1,False),
("R06","sun_socket",["P06"],1,3,False),
("R07","planet_gears",["P07"]*9,3,1,False),
("R08","604_retainers",["P08"]*9,3,1,False),
("R09","ring_half",["P09"],1,6,False),
("R10","interstage_collar",["P10"],1,2,False),
("R11","terminal_collar",["P11"],1,1,False),
("R12","stationary_base",["P12"],1,1,False),
("R13","wind_drive_and_hub",["P13","P14"],2,1,False),
("R14","curved_sail_arms",["P15"]*3,2,1,False),
("R15","wind_cups",["P16"]*3,3,1,False),
("R16","top_fan",["P17"],1,1,False),
("R17","guard_shroud",["P18"],1,1,False),
("R18","guard_grille",["P19"],1,1,False),
("R19","bearing_fit_coupons",["C01","C02"],2,1,False)]
total=Counter()
for sid,name,keys,cols,copies,side_label in sheets:
    if any(r["id"]==sid for r in report):
        for key in keys:total[key]+=copies
        log("RESUME cached "+sid);continue
    log("BUILD "+sid+" "+name)
    cw=max(shapes[k].BoundBox.XLength for k in keys)
    ch=max(shapes[k].BoundBox.YLength for k in keys)
    nr=math.ceil(len(keys)/cols)
    if side_label:w=cw+23;h=ch+6
    else:w=2*BORDER+cols*cw+(cols-1)*GAP;h=2*BORDER+nr*(ch+LABEL_BAND)+(nr-1)*GAP
    assert w<=216 and h<=121,(sid,"frame bed fit",w,h)
    base=Part.makeBox(w,h,RAIL).cut(Part.makeBox(w-2*RAIL,h-2*RAIL,RAIL,V(RAIL,RAIL,0)))
    additions=[];placed=[];label_info=[];anchor_info=[]
    for j,key in enumerate(keys):
        s=shapes[key];bb=s.BoundBox
        if side_label:px,py=20.,3.
        else:
            px=BORDER+(j%cols)*(cw+GAP)+(cw-bb.XLength)/2
            py=BORDER+(j//cols)*(ch+LABEL_BAND+GAP)+LABEL_BAND+(ch-bb.YLength)/2
        ps=moved(s,px,py,LIFT);placed.append(ps)
        letters=lettering(key);lb=letters.BoundBox
        tagw=max(13.,lb.XLength+2);tagh=max(6.3,lb.YLength+1.6)
        if side_label:tx,ty=RAIL-.2,(h-tagh)/2
        else:tx,ty=px+(bb.XLength-tagw)/2,py-LABEL_BAND
        tag=Part.makeBox(tagw,tagh,RAIL,V(tx,ty,0));additions.append(tag)
        # A full-width runner joins every label and vertical sprue to the frame.
        additions.append(Part.makeBox(w,RAIL,RAIL,V(0,ty,0)))
        additions.append(moved(letters,tx+(tagw-lb.XLength)/2,ty+(tagh-lb.YLength)/2,RAIL-.1))
        label_info.append(dict(part=key,text=key,font_pt=FONT_PT,nominal_font_mm=FONT_MM,emboss_mm=EMBOSS,position=[tx,ty]))
        points=anchor_points(key)
        for ax,ay,az in points:
            ax+=px;ay+=py;az+=LIFT
            # Flat runner + upright sacrificial sprue; narrow end trims off the part.
            additions.append(Part.makeBox(RAIL,h,RAIL,V(ax-RAIL/2,0,0)))
            stemtop=az-1.2
            additions.append(Part.makeCylinder(1.2,stemtop-RAIL+.2,V(ax,ay,RAIL-.1)))
            additions.append(Part.makeCone(1.2,.45,1.2,V(ax,ay,stemtop-.1)))
            additions.append(Part.makeCylinder(.45,.65,V(ax,ay,az-.15)))
            anchor_info.append(dict(part=key,point=[ax,ay,az],neck_diameter_mm=.9))
        total[key]+=copies
    all_shape=base.multiFuse(additions+placed,0.0001).removeSplitter()
    assert all_shape.isValid() and len(all_shape.Solids)==1,(sid,"not a connected sprue",len(all_shape.Solids))
    bb=all_shape.BoundBox;dims=[bb.XLength,bb.YLength,bb.ZLength]
    assert all(d<=lim+1e-5 for d,lim in zip(dims,BED)),(sid,dims)
    mesh=MeshPart.meshFromShape(Shape=all_shape,LinearDeflection=.025,AngularDeflection=.10,Relative=False)
    assert mesh.isSolid(),sid
    filename=sid+"_"+name+"_print-"+str(copies)+"x.stl";path=OUT/filename
    mesh.write(str(path))
    check=Mesh.Mesh(str(path));assert check.isSolid() and check.countComponents()==1,sid
    obj=doc.addObject("PartDesign::Feature",sid);obj.Label=sid+" "+name+" | print "+str(copies)+"x";obj.Shape=all_shape
    obj.addProperty("App::PropertyInteger","PrintCopies");obj.PrintCopies=copies
    obj.addProperty("App::PropertyString","STLFile");obj.STLFile=filename
    row=dict(id=sid,name=name,file=filename,print_copies=copies,parts_per_sheet=dict(Counter(keys)),
        size_mm=[round(d,3) for d in dims],part_lift_mm=LIFT,frame_height_mm=RAIL,
        font_points=FONT_PT,emboss_mm=EMBOSS,labels=label_info,anchors=anchor_info,
        support_status="Sprue anchors only; add and inspect final resin supports in slicer.",
        rotation_z_then_x_degrees={k:orient[k] for k in set(keys)},
        solid_resin_ml=round(all_shape.Volume/1000,3),triangles=mesh.CountFacets,
        sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    report.append(row);report.sort(key=lambda r:r["id"])
    doc.recompute();doc.saveAs(str(ROOT/"resin_sprue_sheets.FCStd"))
    (OUT/"sprue_manifest.json").write_text(json.dumps(report,indent=2))
    log("PASS "+filename+" "+str(row["size_mm"]))
expected={r["id"]:r["quantity"] for r in rows}
assert dict(total)==expected,(total,expected)
doc.recompute();doc.saveAs(str(ROOT/"resin_sprue_sheets.FCStd"))
App.closeDocument(source.Name);App.closeDocument(doc.Name)
with (OUT/"sprue_manifest.csv").open("w",newline="") as f:
    fields=["sheet","file","print_copies","parts_per_sheet","size_x_mm","size_y_mm","size_z_mm","solid_resin_ml","additional_supports_required"]
    writer=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");writer.writeheader()
    for r in report:
        writer.writerow(dict(sheet=r["id"],file=r["file"],print_copies=r["print_copies"],
        parts_per_sheet="; ".join(k+" x"+str(v) for k,v in r["parts_per_sheet"].items()),
        size_x_mm=r["size_mm"][0],size_y_mm=r["size_mm"][1],size_z_mm=r["size_mm"][2],
        solid_resin_ml=r["solid_resin_ml"],additional_supports_required="YES"))
validation=dict(status="PASS",printer="Anycubic Photon Mono M5s",build_volume_mm=BED,
    material="Anycubic ABS-Like Resin Pro 2",sheet_files=len(report),total_sheet_copies=sum(r["print_copies"] for r in report),
    printed_part_counts=dict(total),all_closed_single_component_meshes=True,all_sheet_envelopes_fit=True,
    all_part_labels_font_pt=FONT_PT,all_part_labels_emboss_mm=EMBOSS,
    nominal_solid_resin_ml=sum(r["solid_resin_ml"]*r["print_copies"] for r in report),
    geometry_scope="Original 1:1 parts; rotation and translation only, plus sacrificial sprues.",
    support_scope="Frames and sprue connections are included. Full print supports and exposure must be prepared in resin slicer; not physically print-tested.")
(OUT/"validation.json").write_text(json.dumps(validation,indent=2))
log(json.dumps(validation,indent=2))
