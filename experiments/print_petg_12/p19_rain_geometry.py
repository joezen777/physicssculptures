"""P19 rain-shedding grille; dimensions in mm, installed datum z=412."""
import math
import FreeCAD as App, Part
from FreeCAD import Vector as V

BANDS=[(24,33,12),(31.5,40.5,19),(39,48,12),(46.5,55.5,19),
       (54,63,12),(61.5,70.5,19),(69,77.5,12)]
def ann(ro,ri,h,z=0):
    return Part.makeCylinder(ro,h,V(0,0,z)).cut(Part.makeCylinder(ri,h,V(0,0,z)))
def halfwidth(r):
    return 2.2+2.8*math.sin(math.pi*max(0,min(1,(r-22)/66)))
def floor(r):
    return 7+(88-r)*.075
def xyz(r,t,z):
    return V(r*math.cos(t),r*math.sin(t),z)
def panel(points,thickness):
    # Closed triangulated sheet: independent triangular prisms avoid twisted faces.
    bits=[]
    for i in range(1,len(points)-1):
        p=[points[0],points[i],points[i+1]]
        bits.append(Part.Face(Part.makePolygon(p+[p[0]])).extrude(V(0,0,-thickness)))
    return bits[0].multiFuse(bits[1:]) if len(bits)>1 else bits[0]
def sector(ro,ri,z,a0,a1):
    pts=[xyz(r,t,z) for r,t in [(ri,a0),(ro,a0),(ro,a1),(ri,a1)]]
    return pts
def make_grille():
    base=ann(88,76,6).fuse(ann(22,4.3,12))
    r=13.5/math.sqrt(3)
    p=[xyz(r,j*math.pi/3,0) for j in range(6)]
    base=base.cut(Part.Face(Part.makePolygon(p+[p[0]])).extrude(V(0,0,6.8)))
    for a in range(6):
        t=a*math.pi/3
        base=base.cut(Part.makeCylinder(2.25,9,xyz(82,t,-1)))
    pieces=[base];roofs=[];gutters=[];columns=[]
    # Drain axes halfway between mounting holes: no screw access conflicts.
    for k in range(6):
        angle=math.radians(30+60*k)
        # Long narrow petal trench, an outward-sloping bed with low side lips.
        parts=[]
        for i in range(22):
            r0=21+i*67/22;r1=21+(i+1)*67/22
            w0=halfwidth(r0);w1=halfwidth(r1)
            def p(r,w,z):
                return V(r*math.cos(angle)-w*math.sin(angle),r*math.sin(angle)+w*math.cos(angle),z)
            parts.append(panel([p(r0,-w0,floor(r0)),p(r1,-w1,floor(r1)),
                                p(r1,w1,floor(r1)),p(r0,w0,floor(r0))],1.8))
            for sign in [-1,1]:
                parts.append(panel([p(r0,sign*w0,floor(r0)+.8),p(r1,sign*w1,floor(r1)+.8),
                                    p(r1,sign*(w1+.9),floor(r1)+.8),p(r0,sign*(w0+.9),floor(r0)+.8)],2.6))
        g=parts[0].multiFuse(parts[1:]);gutters.append(g);pieces.append(g)
        # Gutter feet land only on the hub and original outer mounting ring.
        for r in [21,77.5]:
            c=Part.makeCylinder(1.6,floor(r)-.2,xyz(r,angle,0))
            columns.append(c);pieces.append(c)
    for ri,ro,z in BANDS:
        for k in range(6):
            start=math.radians(30+60*k);end=start+math.pi/3
            # Ends project inside lips; open space underneath lets water enter gutter.
            a0=start+math.asin((halfwidth(ri)-.6)/ri)
            a1=end-math.asin((halfwidth(ri)-.6)/ri)
            strips=[]
            for j in range(16):
                pts=[]
                for r,u in [(ri,j/16),(ro,j/16),(ro,(j+1)/16),(ri,(j+1)/16)]:
                    edge=math.asin((halfwidth(r)-.6)/r)
                    t=start+edge+u*(math.pi/3-2*edge)
                    h=z-.10*(r-ri)+2.4*(1-abs(2*u-1))
                    pts.append(xyz(r,t,h))
                strips.append(panel(pts,1.6))
            roof=strips[0].multiFuse(strips[1:]);roofs.append(roof);pieces.append(roof)
            # Four separate narrow pillars per segment, leaving open sides.
            for r in [ri+1.7,ro-1.7]:
                edge=math.asin((halfwidth(r)-.6)/r)
                for t in [start+edge,end-edge]:
                    bottom=floor(r)-1.4
                    top=z-.1*(r-ri)
                    c=Part.makeCylinder(.9,top-bottom,xyz(r,t,bottom))
                    pieces.append(c);columns.append(c)
    shape=pieces[0].multiFuse(pieces[1:])
    assert shape.isValid() and len(shape.Solids)==1
    # Three radial cap screws. Blind pilot holes stay clear of the bearing bore.
    for k in range(3):
        t=math.radians(k*120)
        shape=shape.cut(Part.makeCylinder(1.25,5.2,xyz(22.1,t,9.5),V(-math.cos(t),-math.sin(t),0)))
    return shape,roofs,gutters,columns
def make_cap():
    # Clearance fit skirt; three M3x6 radial screws retain against wind lift.
    skirt=ann(23.8,22.25,6,6.5)
    # Revolved closed roof profile; >3 mm clearance above the installed acorn.
    pts=[V(23.8,0,12.5),V(10,0,27.5),V(0,0,27.5),
         V(0,0,25.9),V(9.3,0,25.9),V(22.25,0,12.5)]
    roof=Part.Face(Part.makePolygon(pts+[pts[0]])).revolve(V(),V(0,0,1),360)
    cap=skirt.fuse(roof).fuse(ann(22.3,20.6,.8,12))
    for k in range(3):
        t=math.radians(k*120)
        cap=cap.cut(Part.makeCylinder(1.7,5,xyz(25,t,9.5),V(-math.cos(t),-math.sin(t),0)))
    for k in range(6):
        notch=Part.makeBox(7,8.4,7.3,V(19,-4.2,6))
        notch.rotate(V(),V(0,0,1),30+60*k)
        cap=cap.cut(notch)
    return cap.removeSplitter()
