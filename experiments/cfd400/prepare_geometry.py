from pathlib import Path
import FreeCAD as App,Part,MeshPart,json
from FreeCAD import Vector as V
ROOT=Path(__file__).resolve().parents[1]/'print_petg_12'
OUT=Path(__file__).resolve().parent/'geometry';OUT.mkdir(exist_ok=True)
src=App.openDocument(str(ROOT/'output/print_prototype.FCStd'))
scene=json.loads((ROOT/'output/scene.json').read_text())
shape=src.getObject(next(x['name'] for x in scene if x['key']=='P17')).Shape.copy()
shape.translate(V(0,0,-348))
def export(name,s):
    # Aerodynamically irrelevant small hub bores/fastener pockets filled for meshing.
    s=s.fuse(Part.makeCylinder(22,11.4)).fuse(Part.makeCylinder(6.3,22,V(0,0,-22))).removeSplitter()
    assert s.isValid() and len(s.Solids)==1
    mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
    mesh.transform(App.Matrix(.001,0,0,0,0,.001,0,0,0,0,.001,0,0,0,0,1))
    assert mesh.isSolid()
    mesh.write(str(OUT/(name+'.stl')))
    print(name,mesh.CountFacets,flush=True)
export('original',shape)
sc=App.openDocument(str(ROOT/'output/scimitar_40mm/scimitar_40mm.FCStd'))
s=sc.getObject('P17S').Shape.copy();s.translate(V(0,0,-348))
export('scimitar',s)
