"""Two removable Krull wind-arm joints; run with bundled FreeCAD Python."""
from pathlib import Path
import math,json,hashlib
import FreeCAD as App,Part,MeshPart
from FreeCAD import Vector as V
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output/arm_joint_variants';OUT.mkdir(exist_ok=True)
for name in ['validation.json','installation_validation.json','render_complete.txt','slice_validation.json','release_summary.json']:(OUT/name).unlink(missing_ok=True)
src=App.openDocument(str(ROOT/'output/print_prototype.FCStd'))
scene=json.loads((ROOT/'output/scene.json').read_text())
def original(key):return src.getObject(next(r['name'] for r in scene if r['key']==key)).Shape.copy()
old=original('P15');oldhub=original('P14')
newdoc=App.openDocument(str(ROOT/'output/sail_80x120/P15_P16_sail_80x120.FCStd'))
sail=newdoc.getObject('P16').Shape.copy()
def box(x,y,z,dx,dy,dz):return Part.makeBox(dx,dy,dz,V(x,y,z))
def cyl(r,h,x,y,z,axis=V(0,0,1)):return Part.makeCylinder(r,h,V(x,y,z),axis)
def rotated(s,deg):
    s=s.copy();s.rotate(V(),V(0,0,1),deg);return s
def moved(s,x=0,y=0,z=0):
    s=s.copy();s.translate(V(x,y,z));return s
def edge(points,z):
    c=Part.BSplineCurve();c.interpolate([V(x,y,z) for x,y in points]);return c.toShape()
def strip(a,b,z,h):
    w=Part.Wire([edge(a,z),Part.makeLine(V(*a[-1],z),V(*b[-1],z)),edge(b,z).reversed(),Part.makeLine(V(*b[0],z),V(*a[0],z))])
    return Part.Face(w).extrude(V(0,0,h))
def oldstrip(r0,r1,width,z,h):
    a=[];b=[]
    for i in range(49):
        r=r0+(r1-r0)*i/48
        angle=math.radians(-18*math.sin(math.pi*(r-24)/84))
        for pts,sign in [(a,-1),(b,1)]:
            t=angle+sign*width/(2*r);pts.append((r*math.cos(t),r*math.sin(t)))
    return strip(a,b,z,h)
def saddle():
    s=box(169,-53,-17,22,8,24)
    return s.fuse(box(169,-49,-17,2.7,9,16)).fuse(box(188.3,-49,-17,2.7,9,16))
sailhole=cyl(2.25,40,180,-60,-9,V(0,1,0))
sail_head_clear=cyl(4.7,27,180,-80,-9,V(0,1,0))
# Temporary: U-shaped lower cradle installed from BELOW and closing cap from ABOVE.
# 22 mm exterior around a nominal 12 mm original arm; 0.4 mm clearance per face.
cradle=oldstrip(76,100,22,-16,10.4).common(box(60,-40,-30,38,80,60))
cradle=cradle.fuse(box(98,-9,-21,22,16.4,3.6))
cradle=cradle.fuse(box(98,-7.4,-21,22,4,24.4))
body=strip([(116,-18),(134,-54),(155,-68),(174,-60),(180,-53)],
           [(116,-3.4),(138,-30),(155,-44),(169,-47),(180,-45)],-12,6)
cradle=cradle.fuse(body).fuse(saddle()).fuse(box(114,-9,-15,12,5.6,9))
rib=strip([(127,-35),(146,-56),(163,-58),(174,-55)],
          [(127,-31),(146,-52),(163,-54),(174,-51)],-12,10)
cradle=cradle.fuse(rib)
plan_clear=oldstrip(74,110,12.8,-12.4,60)
tab_clear=box(99.6,-3.4,-17.4,16.8,6.8,60)
cradle=cradle.cut(plan_clear).cut(tab_clear)
cap=oldstrip(76,100,22,-5.6,3.2)
cap=cap.fuse(box(98,3.4,-17.4,22,4,20.8)).fuse(box(98,-3.4,-.6,22,10.8,4))
cap=cap.fuse(box(92,-10,-5.6,7.4,8,9))
# Downward-open cap pockets allow installation without sliding along the arm.
cap=cap.cut(oldstrip(74,110,12.8,-50,44.4)).cut(box(99.6,-3.4,-50,16.8,6.8,49.4))
oldhole=cyl(2.25,50,108,-25,-9,V(0,1,0))
cradle=cradle.cut(oldhole).cut(sailhole).cut(sail_head_clear).cut(box(97.8,-10,-5.8,1.9,6.8,9.5)).removeSplitter()
cap=cap.cut(oldhole).removeSplitter()
# Permanent: closed socket with two lateral through-bolts, external washers/nuts.
def hexagon(af,h,z):
    r=af/math.sqrt(3);p=[V(r*math.cos(i*math.pi/3),r*math.sin(i*math.pi/3),z) for i in range(6)]
    return Part.Face(Part.makePolygon(p+[p[0]])).extrude(V(0,0,h))
hub=cyl(30,12,0,0,-18).cut(hexagon(36.6,12,-18))
socket=box(36,-12,-23,42,24,17).fuse(box(28,-12,-18,12,24,12))
socket=socket.cut(box(38,-6.3,-20.3,41,12.6,11.6))
for x in [49,65]:socket=socket.cut(cyl(3.15,40,x,-20,-14.5,V(0,1,0)))
for a in [0,120,240]:hub=hub.fuse(rotated(socket,a))
for a in [30,150,270]:
    t=math.radians(a);hub=hub.cut(cyl(2.25,20,25*math.cos(t),25*math.sin(t),-24))
hub=hub.removeSplitter()
tongue=box(38.4,-6,-20,43.6,12,11)
blade=strip([(80,-6),(96,-39),(122,-65),(151,-70),(174,-60),(180,-53)],
            [(80,6),(99,-11),(128,-40),(151,-45),(169,-47),(180,-45)],-12,6)
arm=tongue.fuse(blade).fuse(saddle())
rib=strip([(96,-31),(119,-52),(146,-61),(169,-55)],
          [(96,-27),(119,-48),(146,-57),(169,-51)],-12,10)
arm=arm.fuse(rib)
# Underside gusset spreads the depth transition at the mouth of the socket.
p=[V(78.3,-4,-20),V(100,-4,-12),V(100,-4,-9),V(78.3,-4,-9)]
arm=arm.fuse(Part.Face(Part.makePolygon(p+[p[0]])).extrude(V(0,8,0)))
for x in [49,65]:arm=arm.cut(cyl(3.15,40,x,-20,-14.5,V(0,1,0)))
arm=arm.cut(sailhole).cut(sail_head_clear).removeSplitter()
parts={'T15_extension':cradle,'T15_closing_cap':cap,'S14_side_access_hub':hub,'S15_side_access_arm':arm}
checks=[]
def clear(name,a,b):
    v=a.common(b).Volume
    assert v<1e-4,(name,v)
    checks.append(dict(check=name,overlap_mm3=v))
for key,s in parts.items():
    assert s.isValid() and len(s.Solids)==1,(key,s.isValid(),len(s.Solids))
clear('Temporary cradle versus installed arm',cradle,old)
clear('Temporary cap versus installed arm',cap,old)
clear('Temporary cradle versus cap',cradle,cap)
clear('Temporary extension versus scoop',cradle,sail)
clear('Permanent tongue versus socket',arm,hub)
clear('Permanent arm versus scoop',arm,sail)
for dz in [-45,-25,-12,-4,0]:clear('Cradle upward installation '+str(dz),moved(cradle,z=dz),old)
for dz in [30,15,5,0]:
    clear('Cap downward installation '+str(dz),moved(cap,z=dz),old)
    clear('Cap versus cradle during installation '+str(dz),moved(cap,z=dz),cradle)
for dx in [0,5,15,30,45]:
    clear('Side arm radial withdrawal '+str(dx),moved(arm,x=dx),hub)
# Check bolt shanks and 9 mm OD washer seats are clear of the moving parts.
for x in [49,65]:
    shank=cyl(2,35,x,-12.8,-14.5,V(0,1,0))
    clear('Side bolt shank versus hub '+str(x),shank,hub)
    clear('Side bolt shank versus tongue '+str(x),shank,arm)
    sleeve=cyl(3,24,x,-12,-14.5,V(0,1,0)).cut(cyl(2.1,24,x,-12,-14.5,V(0,1,0)))
    clear('Steel compression sleeve versus hub '+str(x),sleeve,hub)
    clear('Steel compression sleeve versus tongue '+str(x),sleeve,arm)
# Hardware seat and insertion envelopes. Washers are annuli; head/nut are conservative cylinders.
for label,xx,yy,zz,grip,objects in [('temporary',108,-7.4,-9,14.8,[cradle,cap]),('side49',49,-12,-14.5,24,[hub,arm]),('side65',65,-12,-14.5,24,[hub,arm]),('scoop_temp',180,-53,-9,21,[cradle,sail]),('scoop_side',180,-53,-9,21,[arm,sail])]:
    front=cyl(4.5,.8,xx,yy-.8,zz,V(0,1,0)).cut(cyl(2.1,.8,xx,yy-.8,zz,V(0,1,0)))
    head=cyl(3.5,4,xx,yy-4.8,zz,V(0,1,0))
    back=cyl(4.5,.8,xx,yy+grip,zz,V(0,1,0)).cut(cyl(2.1,.8,xx,yy+grip,zz,V(0,1,0)))
    nut=cyl(4.05,3.2,xx,yy+grip+.8,zz,V(0,1,0)).cut(cyl(2,3.2,xx,yy+grip+.8,zz,V(0,1,0)))
    for obj in objects:
        for name,steel in [('front washer',front),('head',head),('back washer',back),('nut',nut)]:clear(label+' '+name,steel,obj)
# Whole assembly: radial/vertical broad-phase and shared-rotation reduction.
existing=[(r['key'],src.getObject(r['name']).Shape,getattr(src.getObject(r['name']),'SpeedRatio',0)) for r in scene if r['key'] not in ('P14','P15','P16')]
for label,objects,includehub in [('temporary',[cradle,cap],oldhub),('side_access',[hub,arm],None)]:
    if includehub:
        for s in objects:clear(label+' versus retained P14',s,includehub)
    for i,s in enumerate(objects):
        for deg in range(0,360,30):
            test=rotated(s,deg)
            for key,other,ratio in existing:
                if ratio==1 and deg:continue
                other=rotated(other,ratio*deg) if ratio else other
                if not test.BoundBox.intersect(other.BoundBox):continue
                clear(label+' part '+str(i)+' angle '+str(deg)+' versus '+key,test,other)
        if label=='temporary':
            for a in [120,240]:
                for other in [cradle,cap,old,sail]:clear(label+' neighbour',s,rotated(other,a))
        elif i==1:
            for a in [120,240]:
                for other in [arm,sail]:clear(label+' neighbour',s,rotated(other,a))
# Horizontal driver/wrench approach to both side-bolt positions, from both sides.
for x in [49,65]:
    for sign in [-1,1]:
        tool=cyl(5.5,60,x,sign*24,-14.5,V(0,sign,0))
        for key,other,ratio in existing:
            if tool.BoundBox.intersect(other.BoundBox):clear('Tool access '+str(x)+' '+str(sign)+' '+key,tool,other)
        for a in [120,240]:clear('Tool versus neighbouring arm',tool,rotated(arm,a))
doc=App.newDocument('ArmJointVariants')
manifest=[]
for key,s in parts.items():
    o=doc.addObject('PartDesign::Feature',key);o.Shape=s
    printshape=s.copy()
    # Closing cap upside-down on its long curved roof; support local tab features.
    if key=='T15_closing_cap':printshape.rotate(V(),V(1,0,0),180)
    bb=printshape.BoundBox;printshape.translate(V(-bb.XMin,-bb.YMin,-bb.ZMin))
    bb=printshape.BoundBox
    assert bb.XLength<212 and bb.YLength<212 and bb.ZLength<240
    m=MeshPart.meshFromShape(Shape=printshape,LinearDeflection=.08,AngularDeflection=.12,Relative=False)
    assert m.isSolid(),key
    qty=1 if key.startswith('S14') else 3
    file=key+'_print-'+str(qty)+'x.stl';m.write(str(OUT/file))
    manifest.append(dict(id=key,file=file,quantity=qty,size_mm=[bb.XLength,bb.YLength,bb.ZLength],volume_mm3=s.Volume,triangles=m.CountFacets,closed_mesh=True))
# Original references included hidden in native document to make the handshake inspectable.
for name,s in [('Original_P15',old),('Original_P14',oldhub),('Reference_P16',sail)]:
    o=doc.addObject('PartDesign::Feature',name);o.Shape=s
doc.recompute();doc.saveAs(str(OUT/'arm_joint_variants.FCStd'))
report=dict(status='PASS',parts=manifest,checks=checks,root_socket_overlap_mm=39.6,temporary_overlap_nominal_mm=32,
            side_joint_clearance_per_face_mm=.3,temporary_clearance_per_face_mm=.4,
            collision_sample_step_deg=30,physical_testing=False,scope='Nominal CAD, sampled paths and tool envelopes; not stress or fatigue qualification.')
(OUT/'validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(dict(status='PASS',parts=manifest,check_count=len(checks)),indent=2))
