"""Explicit CFD-only candidate surfaces; not print or strength qualified."""
from pathlib import Path
import math,json
import FreeCAD as App,Part,MeshPart
from FreeCAD import Vector as V
OUT=Path(__file__).resolve().parent/'geometry';OUT.mkdir(exist_ok=True)
def edge(p):
    c=Part.BSplineCurve();c.interpolate(p);return c.toShape()
def wire(r,beta,chord,phase=0,base=1.2,thick=2.4):
    w=chord*math.cos(math.radians(beta))/r;h=chord*math.sin(math.radians(beta))
    sides=[]
    for sign in (1,-1):
        p=[]
        for j in range(25):
            s=j/24;a=phase+(s-.5)*w
            z=base+h*(1-s)+1.2*math.sin(math.pi*s)+sign*thick/2
            p.append(V(r*math.cos(a),r*math.sin(a),z))
        sides.append(p)
    a,b=sides
    return Part.Wire([edge(a),Part.makeLine(a[-1],b[-1]),edge(b[::-1]),Part.makeLine(b[0],a[0])])
def solid(wires):
    skin=Part.makeLoft(wires,False,True)
    caps=[Part.makeRuledSurface(w.Edges[0],w.Edges[2].reversed()) for w in (wires[0],wires[-1])]
    s=Part.makeSolid(Part.makeShell(skin.Faces+[f for c in caps for f in c.Faces]))
    if s.Volume<0:s.reverse()
    assert s.isValid()
    return s
def hub():return Part.makeCylinder(22,11.4).fuse(Part.makeCylinder(12,22,V(0,0,-22)))
def finish(name,s):
    s=s.removeSplitter()
    assert s.isValid() and len(s.Solids)==1,(name,len(s.Solids))
    mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.10,AngularDeflection=.15,Relative=False)
    mesh.transform(App.Matrix(.001,0,0,0,0,.001,0,0,0,0,.001,0,0,0,0,1))
    assert mesh.isSolid()
    mesh.write(str(OUT/(name+'.stl')))
    d=App.newDocument(name);o=d.addObject('PartDesign::Feature',name);o.Shape=s;d.recompute();d.saveAs(str(OUT/(name+'.FCStd')))
    print(name,s.Volume,s.BoundBox.ZMin,s.BoundBox.ZMax,mesh.CountFacets,flush=True)
    return dict(name=name,valid_solid=True,solids=len(s.Solids),volume_mm3=s.Volume,z_min_mm=s.BoundBox.ZMin,z_max_mm=s.BoundBox.ZMax,triangles=mesh.CountFacets)
reports=[]
# Four tubercled blades: 1.5 mm radial chord modulation over outer 60% span.
ws=[]
for i in range(61):
    r=21+51*i/60;x=(r-21)/51
    beta=45-20*x;c=(35/math.sin(math.pi/4))*(1-x)+(18/math.sin(math.radians(25)))*x
    if x>.4:
        u=(x-.4)/.6;c+=1.5*math.sin(math.pi*u)**2*math.sin(2*math.pi*(r-(21+.4*51))/8)
    phase=math.radians(18*math.sin(math.pi*x)-10*x)
    ws.append(wire(r,beta,c,phase))
blade=solid(ws).cut(Part.makeCylinder(22.6,50,V(0,0,11.4)))
s=hub()
for a in (0,90,180,270):
    b=blade.copy();b.rotate(V(),V(0,0,1),a);s=s.fuse(b)
reports.append(finish('tubercled',s))
# Corrected production loops; historical toroidal5 meshes are obsolete.
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'print_petg_12'))
from toroidal_geometry import make_fan
reports.append(finish('toroidal5_final',make_fan()))
(OUT/'candidate_geometry.json').write_text(json.dumps(dict(scope='Generic cambered sections. Old toroidal5 cases are obsolete; remesh toroidal5_final.',parts=reports),indent=2)+'\n')
