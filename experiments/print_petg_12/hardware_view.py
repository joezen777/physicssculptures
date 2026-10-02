"""Purchased hardware for the complete exploded assembly; threads simplified."""
import math,json
from collections import Counter
import FreeCAD as App,Part
from FreeCAD import Vector as V
def complete_hardware(doc,scene,out):
    scene=[dict(s) for s in scene]
    for o in list(doc.Objects):
        if o.Name.startswith("AddedHardware"):doc.removeObject(o.Name)
    def xy(r,a):return r*math.cos(math.radians(a)),r*math.sin(math.radians(a))
    def ring(ro,ri,h):return Part.makeCylinder(ro,h).cut(Part.makeCylinder(ri,h))
    def hexnut(af,h,bore):
        r=af/math.sqrt(3);v=[V(r*math.cos(j*math.pi/3),r*math.sin(j*math.pi/3),0) for j in range(6)]
        return Part.Face(Part.makePolygon(v+[v[0]])).extrude(V(0,0,h)).cut(Part.makeCylinder(bore,h))
    def add(spec,role,shape,p,axis=V(0,0,1),stage=-1):
        shape.Placement=App.Placement(V(*p),App.Rotation(V(0,0,1),axis))
        o=doc.addObject("PartDesign::Feature","AddedHardware"+str(len(scene)))
        o.Label=spec+" | "+role;o.Shape=shape
        o.addProperty("App::PropertyString","PartID");o.PartID=spec
        c=o.Shape.BoundBox.Center
        scene.append(dict(name=o.Name,key=spec,spec=spec,role=role,stage=stage,order=0,hardware=True,center=list(c)))
    def nut(size,role,p,stage=-1,axis=V(0,0,1)):
        af,h={2.5:(5,2),3:(5.5,2.4),4:(7,3.2)}[size]
        add("M"+str(size)+" nut",role,hexnut(af,h,size/2),p,axis,stage)
    def bolt(size,length,role,p,stage=-1,axis=V(0,0,1),button=False):
        hr,hh={2.5:(2.25,2.5),3:(2.75,3),4:(3.5,4)}[size]
        if button:hr,hh=3.8,2.2
        s=Part.makeCylinder(size/2,length).fuse(Part.makeCylinder(hr,hh,V(0,0,-hh)))
        s=s.cut(Part.makeCylinder(size*.42,hh*.6,V(0,0,-hh)))
        add("M"+str(size)+" x"+str(length)+(" button screw" if button else " screw"),role,s,p,axis,stage)
    def pattern(size,length,role,r,angles,z,nutz,stage,up):
        axis=V(0,0,1 if up else -1)
        for a in angles:
            x,y=xy(r,a);bolt(size,length,role+" screws",(x,y,z),stage,axis)
            nut(size,role+" nuts",(x,y,nutz),stage)
    pattern(3,16,"base retainer",17.5,[0,120,240],-38.6,-27,-1,True)
    pattern(4,20,"sail hub",25,[30,150,270],-6,-24,-1,False)
    for a in [0,120,240]:
        for r in [29,39]:
            x,y=xy(r,a-18*math.sin(math.pi*(r-24)/84))
            bolt(4,10,"arm root screws",(x,y,-8.6),button=True,axis=V(0,0,-1))
            nut(4,"arm root nuts",(x,y,-18))
        x,y=xy(108,a);v=V(-math.sin(math.radians(a)),math.cos(math.radians(a)),0)
        p=V(x,y,-9)
        bolt(4,25,"cup screws",list(p-v*3),axis=v)
        add("M4 washer OD9","cup washers",ring(4.5,2.1,.8),list(p+v*14),v)
        nut(4,"cup nuts",list(p+v*14.8),axis=v)
    for level in range(3):
        b=116*level
        pattern(3,16,"pot retainer",17.5,[0,120,240],b+15,b,level,False)
        pattern(3,16,"sun retainer",17.5,[60,180,300],b+46.4,b+58.8,level,True)
        pattern(3,20,"sun join",17.5,[0,120,240],b+53.4,b+68.8,level,True)
        pattern(4,20,"ring collar",90,range(0,360,60),b+96,b+80,level,False)
        for a in [0,120,240]:
            x,y=xy(54,a)
            for h in [10,130,250]:
                dx,dy=xy(10.5,h)
                bolt(2.5,16,"planet retainer screws",(x+dx,y+dy,b+90),level,V(0,0,-1))
                nut(2.5,"planet retainer nuts",(x+dx,y+dy,b+76),level)
    pattern(3,16,"top retainer",17.5,[0,120,240],363,348,3,False)
    pattern(4,16,"guard",82,range(0,360,60),386,374,3,False)
    for s in scene:
        if not s.get("hardware"):continue
        if "role" in s:continue
        key=s["key"];z=s["center"][2];level=s["stage"];b=116*level
        if key in ("H608","H604"):
            s["spec"]=key[1:]+" bearing"
            if key=="H604":role="planet bearing"
            elif level==-1:role="base bearing"
            elif level==3:role="top bearing"
            else:role={1:"pot bearing",5:"lower sun bearing",7:"upper sun bearing"}[s["order"]]
        elif key=="M8_rod":s["spec"]="M8 rod L468";role="main rod"
        elif key=="M8_acorn":s["spec"]="M8 acorn nut";role="top acorn"
        elif key=="M8_nut":
            s["spec"]="M8 nut"
            role=("base lower nut" if z<-55 else "base upper nut") if level==-1 else ("top shaft nut" if level==3 else ("carrier lower nut" if z-b<35 else "carrier upper nut"))
        elif key=="M4x75":
            s["spec"]="M4 x75 axle bolt";role="planet axle"
            o=doc.getObject(s["name"]);x,y=s["center"][:2]
            o.Shape=o.Shape.fuse(Part.makeCylinder(3.5,4,V(x,y,b+22)))
        elif key=="M4_nut":s["spec"]="M4 nut";role="planet lower nut" if z-b<50 else "planet upper nut"
        elif key=="M4_washer":s["spec"]="M4 washer OD7";role="planet washer"
        elif key.startswith("T4_"):
            s["spec"]="Tube ID4.2 OD6 L"+key[3:];role="planet lower spacer" if "37" in key else "planet upper spacer"
        elif key.startswith("T8_"):
            length=float(key[3:]);s["spec"]="Tube ID8.2 OD12 L"+format(length,"g")
            role={12.5:"base lower spacer",32:"base upper spacer",15:"pot upper spacer",5.9:"carrier upper spacer",11:"sun inner spacer",44.6:"interstage spacer",21:"top spacer"}[length]
        else:raise ValueError(key)
        s["role"]=role
    counts=Counter(s["spec"] for s in scene if s.get("hardware"))
    expected={"608 bearing":11,"604 bearing":9,"M8 rod L468":1,"M8 nut":9,"M8 acorn nut":1,
        "M4 x75 axle bolt":9,"M3 x16 screw":24,"M3 x20 screw":9,"M3 nut":33,
        "M2.5 x16 screw":27,"M2.5 nut":27,"M4 x20 screw":21,"M4 x10 button screw":6,
        "M4 x25 screw":3,"M4 x16 screw":6,"M4 nut":54,"M4 washer OD7":9,"M4 washer OD9":3}
    for length,count in [(12.5,1),(32,1),(15,3),(5.9,3),(11,3),(44.6,3),(21,1)]:
        expected["Tube ID8.2 OD12 L"+format(length,"g")]=count
    expected.update({"Tube ID4.2 OD6 L37.2":9,"Tube ID4.2 OD6 L10":9})
    assert dict(counts)==expected,(counts,expected)
    (out/"exploded_hardware_validation.json").write_text(json.dumps(dict(status="PASS",hardware_instances=sum(counts.values()),printed_instances=sum(not s.get("hardware",False) for s in scene),counts=dict(sorted(counts.items())),scope="Every required purchased item represented; simplified unthreaded hardware geometry."),indent=2))
    return scene
