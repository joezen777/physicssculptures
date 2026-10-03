from pathlib import Path
import json,FreeCAD,Part,MeshPart
from FreeCAD import Vector as V
root=Path(__file__).resolve().parent
labels=json.loads((root/"label_request.json").read_text())
data={}
for label in labels:
    shapes=[Part.makeFace(w,"Part::FaceMakerBullseye").extrude(V(0,0,.9)) for w in Part.makeWireString(label,"/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",12*25.4/72,0) if w]
    s=Part.makeCompound(shapes);b=s.BoundBox;s.translate(V(-b.XMin,-b.YMin,-b.ZMin))
    mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.015,AngularDeflection=.15,Relative=False)
    v,f=mesh.Topology
    data[label]=[[(p.x,p.y,p.z) for p in v],f]
(root/"label_meshes.json").write_text(json.dumps(data))
