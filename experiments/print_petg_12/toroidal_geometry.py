"""Production toroidal-five geometry in mm; generic cambered sections."""
import math
import FreeCAD as App,Part
from FreeCAD import Vector as V

def cyl(r,h,z=0):return Part.makeCylinder(r,h,V(0,0,z))
def hexagon(af,h):
 r=af/math.sqrt(3);p=[V(r*math.cos(j*math.pi/3),r*math.sin(j*math.pi/3),0) for j in range(6)]
 return Part.Face(Part.makePolygon(p+[p[0]])).extrude(V(0,0,h))
def shifted(s,z):
 s=s.copy();s.translate(V(0,0,z));return s

def mounting_hub():
 s=cyl(22,11.4).cut(cyl(6.3,11.4)).fuse(shifted(hexagon(24,22).cut(cyl(6.3,22)),-22)).cut(cyl(11.2,8,4))
 for a in (0,120,240):
  x,y=17.5*math.cos(math.radians(a)),17.5*math.sin(math.radians(a))
  h=cyl(1.8,15,-2);h.translate(V(x,y,0));s=s.cut(h)
  n=hexagon(5.8,2.8);n.translate(V(x,y,0));s=s.cut(n)
 return s

def edge(points):
 c=Part.BSplineCurve();c.interpolate(points);return c.toShape()
def section(r,beta,chord,phase=0,base=1.8,thick=2.4):
 w=chord*math.cos(math.radians(beta))/r;h=chord*math.sin(math.radians(beta));sides=[]
 for sign in (1,-1):
  p=[]
  for j in range(33):
   u=j/32;a=phase+(u-.5)*w
   p.append(V(r*math.cos(a),r*math.sin(a),base+h*(1-u)+1.2*math.sin(math.pi*u)+sign*thick/2))
  sides.append(p)
 a,b=sides
 return Part.Wire([edge(a),Part.makeLine(a[-1],b[-1]),edge(b[::-1]),Part.makeLine(b[0],a[0])])
def solid(wires):
 skin=Part.makeLoft(wires,False,True)
 caps=[Part.makeRuledSurface(w.Edges[0],w.Edges[2].reversed()) for w in (wires[0],wires[-1])]
 s=Part.makeSolid(Part.makeShell(skin.Faces+[f for c in caps for f in c.Faces]))
 if s.Volume<0:s.reverse()
 assert s.isValid() and len(s.Solids)==1
 return s

def make_fan():
 arms=[]
 for arm in (0,1):
  ws=[]
  for i in range(25):
   r=21+49.2*i/24;x=(r-21)/49.2
   beta=47.5-25.5*x;c=33/math.sin(math.radians(47.5))*(1-x)+18*x
   # Thicker root for a 0.6 mm nozzle; taper to 2.4 mm axial shell.
   thick=2.4+1.2*max(0,1-x/.45)**2
   ws.append(section(r,beta,c,math.radians(12*math.sin(math.pi*x)+arm*36),base=1.8+18*x*arm,thick=thick))
  arms.append(solid(ws))
 # A radial-thickness return wall: cross-sections normal to its azimuthal path.
 # The previous cylindrical airfoil sections were parallel to that path and
 # generated a degenerate near-zero-volume loft; never reuse that CFD return.
 ws=[]
 for i in range(27):
  degrees=-8+52*i/26;a=math.radians(degrees)
  zc=1.8+9*math.sin(math.radians(22))+18*degrees/36
  lo=max(.5,zc-9);hi=zc+9
  pts=[V(r*math.cos(a),r*math.sin(a),z) for r,z in [(69.6,lo),(72,lo),(72,hi),(69.6,hi)]]
  ws.append(Part.makePolygon(pts+[pts[0]]))
 loop=Part.makeLoft(ws,True,False)
 assert loop.isValid() and loop.Volume>500
 joined=arms[0].fuse(loop).fuse(arms[1])
 assert len(joined.Solids)==1 and joined.Volume>sum(a.Volume for a in arms), 'Return must join and retain BOTH arms'
 pair=joined.cut(cyl(22.6,60,11.4)).removeSplitter()
 assert pair.isValid() and len(pair.Solids)==1
 s=mounting_hub()
 for a in (0,72,144,216,288):
  b=pair.copy();b.rotate(V(),V(0,0,1),a);s=s.fuse(b)
 s=s.removeSplitter();assert s.isValid() and len(s.Solids)==1
 return s

def make_shroud():
 s=cyl(79.6,66).cut(cyl(76,66)).fuse(shifted(cyl(88,6).cut(cyl(76,6)),66))
 for a in range(0,360,60):
  x,y=82*math.cos(math.radians(a)),82*math.sin(math.radians(a))
  h=cyl(2.25,9,65);h.translate(V(x,y,0));s=s.cut(h)
  n=shifted(hexagon(7.4,3.4),66);n.translate(V(x,y,0));s=s.cut(n)
 return s.removeSplitter()
