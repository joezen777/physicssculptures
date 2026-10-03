"""Wrap the saved zoetrope UV paths into shallow recesses on the current pot shell."""
from pathlib import Path
import math,json,hashlib,re
from xml.etree import ElementTree as ET
import FreeCAD as App,Part
from FreeCAD import Vector as V
ROOT=Path(__file__).resolve().parent
ART=ROOT.parent/"pot_zoetrope/output"
CACHE=Path.home()/".cache/angularmomflyer/etched-pot-v1"
CACHE.mkdir(parents=True,exist_ok=True)
DEPTH=.6;HEIGHT=80.;RB=60.;RT=88.;Z_OFFSET=11.
def parse(direction):
    path=ART/("ball-uv-strip-"+direction+".svg")
    tree=ET.parse(path);root=tree.getroot()
    _,_,width,height=map(float,root.attrib["viewBox"].split())
    paths=[]
    for node in root.findall(".//{http://www.w3.org/2000/svg}path"):
        assert node.attrib["d"].endswith(" Z")
        pts=[tuple(map(float,p)) for p in re.findall(r"([-\d.]+),([-\d.]+)",node.attrib["d"])]
        paths.append((node.attrib["id"],pts))
    assert len(paths)==144
    return path,width,height,paths
def prism(points,width,height,frame):
    center=(frame+.5)*width/24
    # Four platform corners map within 0.002 mm; 32 ball vertices stay within 0.004 mm.
    dense=points[::3] if len(points)==96 else points
    wires=[]
    for radial in [45,100]:
        pts=[V(radial,radial*math.tan(2*math.pi*(x-center)/width),Z_OFFSET+height-y) for x,y in dense]
        wires.append(Part.Wire(Part.makePolygon(pts+[pts[0]]).Edges))
    s=Part.makeLoft(wires,True,True)
    assert s.isValid() and len(s.Solids)==1
    s.rotate(V(),V(0,0,1),360*(frame+.5)/24)
    return s
def engraved_shell(direction):
    path,width,height,paths=parse(direction)
    digest=hashlib.sha256(b"angular-wedge-v2-r60-88-h80-z11-depth06-poly4-ball32"+path.read_bytes()).hexdigest()[:16]
    cache=CACHE/(direction+"_"+digest+".brep")
    metadata=CACHE/(direction+"_"+digest+".json")
    if cache.exists() and metadata.exists():
        shape=Part.Shape();shape.read(str(cache))
        assert shape.isValid() and len(shape.Solids)==1
        report=json.loads(metadata.read_text())
        (ART/("engraving_"+direction+".json")).write_text(json.dumps(report,indent=2))
        print("Cached zoetrope shell "+direction,flush=True)
        return shape
    outer=Part.makeCone(RB,RT,HEIGHT)
    inside=Part.makeCone(RB-3.6,RT-3.6,HEIGHT)
    shell=outer.cut(inside)
    band=Part.makeCone(RB+.2,RT+.2,HEIGHT).cut(Part.makeCone(RB-DEPTH,RT-DEPTH,HEIGHT))
    cutters=[];volumes=[];platforms={}
    for i,(name,pts) in enumerate(paths):
        frame=int(name.split("-")[1])
        if "platform" in name and name.rsplit("-",1)[1] in platforms:
            cutter=platforms[name.rsplit("-",1)[1]].copy()
            cutter.rotate(V(),V(0,0,1),frame*15)
        else:
            cutter=prism(pts,width,height,frame).common(band)
            assert cutter.isValid() and len(cutter.Solids)==1 and cutter.Volume>0,name
            if "platform" in name:platforms[name.rsplit("-",1)[1]]=cutter.copy()
        cutters.append(cutter);volumes.append(cutter.Volume)
        if i%24==0:print("Zoetrope "+direction+" cutters "+str(i)+"/144",flush=True)
    print("Cutting zoetrope "+direction+" into shell",flush=True)
    if cache.exists():
        etched=Part.Shape();etched.read(str(cache))
    else:
        etched=shell
        for frame in range(0,24,4):
            etched=etched.cut(Part.makeCompound(cutters[frame*6:(frame+4)*6])).removeSplitter()
            print("Etched "+direction+" frames through "+str(frame+3),flush=True)
        etched.exportBrep(str(cache))
    assert etched.isValid() and len(etched.Solids)==1
    removed=shell.Volume-etched.Volume
    assert removed>100 and removed<1000,removed
    # A full 3 mm radial inner liner must remain untouched.
    liner=Part.makeCone(RB-DEPTH,RT-DEPTH,HEIGHT).cut(inside)
    missing=liner.cut(etched).Volume
    assert missing<1e-4,missing
    # Every path crosses the actual wall; no missing or through-cut artwork.
    per_path=[]
    for i,((name,_),cutter) in enumerate(zip(paths,cutters)):
        removed_here=shell.common(cutter).Volume
        pts=paths[i][1];x=sum(p[0] for p in pts)/len(pts);y=sum(p[1] for p in pts)/len(pts)
        z=Z_OFFSET+height-y;theta=2*math.pi*x/width;r=RB+(RT-RB)*z/HEIGHT-DEPTH/2
        empty=not etched.isInside(V(r*math.cos(theta),r*math.sin(theta),z),1e-6,True)
        assert removed_here>.05 and empty,(name,removed_here,empty)
        per_path.append(dict(path=name,removed_mm3=removed_here))
        if i%36==0:print("Checked "+direction+" paths "+str(i),flush=True)
    assert abs(sum(p["removed_mm3"] for p in per_path)-removed)<.01
    report=dict(status="PASS",source=str(path.relative_to(ROOT.parent.parent)),source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        direction_viewed_from_above=direction,frames=24,closed_paths=144,recess_depth_radial_mm=DEPTH,
        minimum_remaining_radial_wall_mm=3.,uv_width_mm=width,uv_height_mm=height,z_offset_mm=Z_OFFSET,
        pot_outer_radii_mm=[RB,RT],pot_height_mm=HEIGHT,removed_volume_mm3=removed,
        liner_missing_mm3=missing,per_path=per_path,artwork_scale="Original UV heights and 24 angular cells; no outline or background cut")
    etched.exportBrep(str(cache));metadata.write_text(json.dumps(report,indent=2))
    (ART/("engraving_"+direction+".json")).write_text(json.dumps(report,indent=2))
    return etched
if __name__=="__main__":
    for direction in ["ccw","cw"]:engraved_shell(direction)
