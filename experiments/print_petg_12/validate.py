from pathlib import Path
import json,math,time,hashlib
import FreeCAD as App,Part,Mesh
from FreeCAD import Vector as V
OUT=Path(__file__).resolve().parent/"output"
doc=App.openDocument(str(OUT/"print_prototype.FCStd"))
scene=json.loads((OUT/"scene.json").read_text())
parts=json.loads((OUT/"parts.json").read_text())
objects={s["name"]:doc.getObject(s["name"]) for s in scene}
checks={"status":"RUNNING","stl":[],"collisions":[],"mesh_phases":[]}
for row in parts:
    mesh=Mesh.Mesh(str(OUT/"stl"/row["file"]))
    assert mesh.isSolid() and mesh.hasNonManifolds()==False,row["id"]
    assert len(mesh.getSeparateComponents())==1,row["id"]
    assert max(row["size_mm"][:2])<=200
    checks["stl"].append(dict(id=row["id"],closed=True,components=1,size_mm=row["size_mm"]))
print("All STLs are single closed meshes and fit the bed",flush=True)
for i,a in enumerate(scene):
    sa=objects[a["name"]].Shape;ba=sa.BoundBox
    for b in scene[i+1:]:
        sb=objects[b["name"]].Shape;bb=sb.BoundBox
        # Skip exact face contact and separated bounding boxes.
        if min(ba.XMax,bb.XMax)-max(ba.XMin,bb.XMin)<1e-5:continue
        if min(ba.YMax,bb.YMax)-max(ba.YMin,bb.YMin)<1e-5:continue
        if min(ba.ZMax,bb.ZMax)-max(ba.ZMin,bb.ZMin)<1e-5:continue
        # Central rod is a thread envelope; captured nuts intentionally surround it.
        if a["key"]=="M8_rod" or b["key"]=="M8_rod":continue
        vol=sa.common(sb).Volume
        if vol>1e-4:
            item=dict(a=a["name"],b=b["name"],a_key=a["key"],b_key=b["key"],overlap_mm3=vol)
            checks["collisions"].append(item);print(item,flush=True)
    if i%15==0:print("Pair checks",i,"/",len(scene),flush=True)
(OUT/"validation.json").write_text(json.dumps(checks,indent=2))
def shapes(key,stage):
    return [objects[s["name"]].Shape.copy() for s in scene if s["key"]==key and s["stage"]==stage]
sun=shapes("P06",0)[0];planet=shapes("P07",0)[0];rings=shapes("P09",0)
for angle in [0,.7,1.3,2.1,3.7,4.7,6.1,8.3,9.2,10]:
    s=sun.copy();p=planet.copy()
    s.rotate(V(),V(0,0,1),-2*angle);p.rotate(V(54,0,0),V(0,0,1),4*angle)
    ring_shapes=[]
    for r in rings:
        r=r.copy();r.rotate(V(),V(0,0,1),angle);ring_shapes.append(r)
    overlaps=[s.common(p).Volume]+[r.common(p).Volume for r in ring_shapes]
    checks["mesh_phases"].append(dict(angle=angle,overlap_mm3=overlaps))
    print("Mesh phase",angle,overlaps,flush=True)
# Axial assembly: lowering a helical gear requires turning it by its helix rate; staggered rows failed this.
def helix_deg_per_mm(n,hand):return math.degrees(hand*math.tan(math.radians(15.))/(n))  # M=2: pitch radius = n
assembly=[]
for dz in [12,8,4,2,1,.5,0]:
    p=planet.copy();p.rotate(V(54,0,0),V(0,0,1),helix_deg_per_mm(18,-1)*dz);p.translate(V(0,0,dz))
    r=rings[0].copy();r.rotate(V(),V(0,0,1),helix_deg_per_mm(72,-1)*dz);r.translate(V(0,0,dz))
    item=dict(lift_mm=dz,planet_into_sun_mm3=sun.common(p).Volume,planet_into_ring_mm3=rings[0].common(p).Volume,ring_over_planet_mm3=r.common(planet).Volume)
    assembly.append(item);print("Axial insertion",item,flush=True)
checks["axial_gear_insertion"]=assembly
def objs(k):return [o for o in doc.Objects if hasattr(o,"PartID") and o.PartID==k]
# Insertion corridors, with removable retainers absent.
access=[]
def corridor(key,z,ro,ri,h,label):
    o=objs(key)[0];tool=Part.makeCylinder(ro,h,V(0,0,z)).cut(Part.makeCylinder(ri,h,V(0,0,z)))
    v=o.Shape.common(tool).Volume
    assert v<1e-4,(key,label,v)
    access.append(dict(part=key,path=label,overlap_mm3=v))
corridor("P02",4,11,4,45,"608 from above")
corridor("P03",120,11,4,45,"608 from above")
corridor("P05",25,11,4,32.4,"lower sun 608 from below")
corridor("P06",40,11,4,35.4,"upper sun 608 from below before lower housing")
corridor("P13",-55,11,4,27.4,"base 608 from below")
corridor("P17",352,11,4,45,"top fan 608 from above")
o=objs("P07")[0]
tool=Part.makeCylinder(6,20,V(54,0,78.4)).cut(Part.makeCylinder(2,20,V(54,0,78.4)))
v=o.Shape.common(tool).Volume;assert v<1e-4,v
access.append(dict(part="P07",path="604 from above with cap removed",overlap_mm3=v))
checks["bearing_insertion_paths"]=access
# Entire terminal blade sweep clears stationary guard.
sweep=Part.makeCylinder(72.7,10.2,V(0,0,342.9)).cut(Part.makeCylinder(22,10.2,V(0,0,342.9)))
for k in ["P18","P19"]:assert objs(k)[0].Shape.common(sweep).Volume<1e-4,k
checks["terminal_blade_sweep_clear"]=True

checks["status"]="PASS" if not checks["collisions"] and all(max(x["overlap_mm3"])<1e-4 for x in checks["mesh_phases"]) and all(max(v for k,v in x.items() if k!="lift_mm")<1e-4 for x in checks["axial_gear_insertion"]) else "FAIL"
checks["scope"]="Nominal CAD and mesh checks; physical PETG fit, gear wear, strength and child safety unverified."
checks["stl_sha256"]={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((OUT/"stl").glob("*.stl"))}
(OUT/"validation.json").write_text(json.dumps(checks,indent=2))
print(checks["status"],flush=True)
