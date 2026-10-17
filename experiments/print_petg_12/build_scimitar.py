from pathlib import Path
import json, math
import FreeCAD as App, Part, MeshPart
from FreeCAD import Vector as V
from scimitar_geometry import station,RADII,THICKNESS,CAMBER
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output/scimitar_40mm';OUT.mkdir(exist_ok=True)
(OUT/'validation.json').unlink(missing_ok=True)
def cyl(r,h,z=0):return Part.makeCylinder(r,h,V(0,0,z))
def ann(ro,ri,h):return cyl(ro,h).cut(cyl(ri,h))
def hexagon(af,h):
    r=af/math.sqrt(3);p=[V(r*math.cos(j*math.pi/3),r*math.sin(j*math.pi/3),0) for j in range(6)]
    return Part.Face(Part.makePolygon(p+[p[0]])).extrude(V(0,0,h))
def moved(s,z):s=s.copy();s.translate(V(0,0,z));return s
# Reproduce original interface without importing/rebuilding the production package.
hub=ann(22,6.3,11.4).fuse(moved(hexagon(24,22).cut(cyl(6.3,22)),-22)).cut(cyl(11.2,8,4))
for a in (0,120,240):
    x,y=17.5*math.cos(math.radians(a)),17.5*math.sin(math.radians(a))
    hole=cyl(1.8,15,-2);hole.translate(V(x,y,0));hub=hub.cut(hole)
    nut=hexagon(5.8,2.8);nut.translate(V(x,y,0));hub=hub.cut(nut)
def edge(points):
    c=Part.BSplineCurve();c.interpolate(points);return c.toShape()
def section(r,lip=False):
    beta,w,h,b,sweep=station(r)
    # Negative hand retained: z falls as theta increases.
    sides=[]
    for sign in (1,-1):
        pts=[]
        for j in range(41):
            s=j/40;theta=sweep+(s-.5)*w
            z=b+h*(1-s)+CAMBER*math.sin(math.pi*s)
            if lip:z-=5
            z+=sign*(5 if lip else THICKNESS/2)
            pts.append(V(r*math.cos(theta),r*math.sin(theta),z))
        sides.append(pts)
    a,b=sides
    return Part.Wire([edge(a),Part.makeLine(a[-1],b[-1]),edge(list(reversed(b))),Part.makeLine(b[0],a[0])])
def loftsolid(wires):
    shell=Part.makeLoft(wires,False,True)
    caps=[Part.makeRuledSurface(w.Edges[0],w.Edges[2].reversed()) for w in (wires[0],wires[-1])]
    solid=Part.makeSolid(Part.makeShell(shell.Faces+[f for c in caps for f in c.Faces]))
    if solid.Volume<0:solid.reverse()
    assert solid.isValid(), 'loftsolid invalid'
    return solid
print('Lofting blade',flush=True)
blade=loftsolid([section(r) for r in RADII])
lip=loftsolid([section(r,True) for r in [70.4,71.2,72]])
print('blade/lip',blade.isValid(),len(blade.Solids),blade.Volume,lip.isValid(),len(lip.Solids),lip.Volume,flush=True)
blade=blade.fuse(lip).cut(cyl(22.6,60,11.4)).removeSplitter()
assert blade.isValid() and len(blade.Solids)==1
fan=hub
for a in (0,120,240):
    b=blade.copy();b.rotate(V(),V(0,0,1),a);fan=fan.fuse(b)
fan=fan.removeSplitter()
print('Rotor fused',flush=True)
assert fan.isValid() and len(fan.Solids)==1
# Stock interfaces and flange reproduced; shroud extends 32 mm.
shroud=ann(79.6,76,66).fuse(moved(ann(88,76,6),66))
for a in range(0,360,60):
    x,y=82*math.cos(math.radians(a)),82*math.sin(math.radians(a))
    h=cyl(2.25,9,65);h.translate(V(x,y,0));shroud=shroud.cut(h)
    n=moved(hexagon(7.4,3.4),66);n.translate(V(x,y,0));shroud=shroud.cut(n)
source=App.openDocument(str(ROOT/'output/print_prototype.FCStd'))
scene=json.loads((ROOT/'output/scene.json').read_text())
oldfan=source.getObject(next(x['name'] for x in scene if x['key']=='P17')).Shape.copy()
oldfan.translate(V(0,0,-348))
region=cyl(20.9,100,-30)
delta=fan.common(region).cut(oldfan.common(region)).Volume+oldfan.common(region).cut(fan.common(region)).Volume
assert delta<1e-5,delta
grille=source.getObject(next(x['name'] for x in scene if x['key']=='P19')).Shape.copy()
grille.translate(V(0,0,32))
worldfan=moved(fan,348);worldguard=moved(shroud,340)
# Conservative all-angle envelope against all other printed parts, except supported mating hub.
envelope=cyl(72.05,40,348).cut(cyl(22.6,40,348))
collision=[]
for row in scene:
    if row['key'] in ('P17','P18','P19'):continue
    s=source.getObject(row['name']).Shape
    if envelope.BoundBox.intersect(s.BoundBox):
        volume=envelope.common(s).Volume
        assert volume<1e-5,(row['name'],volume)
        collision.append(row['name'])
assert worldfan.common(worldguard).Volume<1e-5
assert worldfan.common(grille).Volume<1e-5
assert worldfan.BoundBox.ZMax<388 and worldfan.BoundBox.ZMin==326
assert blade.BoundBox.ZMin>=-1e-6 and blade.BoundBox.ZMax<=40
doc=App.newDocument('Scimitar40Prototype')
parts=[]
for key,s,z,color in [('P17S',fan,348,(.9,.55,.15)),('P18S',shroud,340,(.28,.33,.39))]:
    o=doc.addObject('PartDesign::Feature',key);o.Shape=moved(s,z)
    p=s.copy();p.translate(V(0,0,-s.BoundBox.ZMin))
    mesh=MeshPart.meshFromShape(Shape=p,LinearDeflection=.06,AngularDeflection=.1,Relative=False)
    assert mesh.isSolid()
    mesh.write(str(OUT/(key+'_print-1x.stl')))
    Part.export([o],str(OUT/(key+'.step')))
    step=OUT/(key+'.step');step.write_text('\n'.join(line.rstrip() for line in step.read_text().splitlines())+'\n')
    parts.append(dict(id=key,volume_mm3=s.Volume,mesh_closed=True,triangles=mesh.CountFacets,
        bounds_mm=[s.BoundBox.XLength,s.BoundBox.YLength,s.BoundBox.ZLength]))
o=doc.addObject('PartDesign::Feature','P19_reference');o.Shape=grille
doc.recompute();doc.saveAs(str(OUT/'scimitar_40mm.FCStd'))
# Area of developed mean-camber surface, excluding winglets and the buried root.
area=0;projected=0
for i in range(1000):
    r=22.6+(72-22.6)*(i+.5)/1000;dr=(72-22.6)/1000
    beta,w,h,_,_=station(r)
    projected+=3*r*w*dr
    area+=3*math.hypot(r*w,h)*dr
report=dict(status='PASS',physical_tested=False,airfoil='specified cambered shell, not Eppler 420',
    parts=parts,hub_interface_delta_mm3=delta,blade_height_mm=blade.BoundBox.ZLength,
    blade_z_mm=[blade.BoundBox.ZMin,blade.BoundBox.ZMax],
    developed_solidity_excluding_lips=area/(math.pi*(72**2-22.6**2)),
    projected_solidity_excluding_lips=projected/(math.pi*(72**2-22.6**2)),
    guard_extension_mm=32,grille_bottom_z_mm=grille.BoundBox.ZMin,
    blade_to_grille_vertical_gap_mm=grille.BoundBox.ZMin-worldfan.BoundBox.ZMax,
    radial_clearance_mm=4,all_angle_envelope_checked_parts=collision,
    notes='Geometry validity and printed-part clearance only; no strength, balance or aerodynamic validation.')
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
