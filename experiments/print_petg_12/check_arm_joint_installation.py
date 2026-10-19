"""Check the temporary clamp can be installed around an assembled original tower."""
from pathlib import Path
import json
import FreeCAD as App
from FreeCAD import Vector as V
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'output/arm_joint_variants'
src=App.openDocument(str(ROOT/'output/print_prototype.FCStd'))
doc=App.openDocument(str(OUT/'arm_joint_variants.FCStd'))
scene=json.loads((ROOT/'output/scene.json').read_text())
cradle=doc.getObject('T15_extension').Shape
cap=doc.getObject('T15_closing_cap').Shape
# Existing arm/hub and the rest of the tower remain; original small cups are removed.
obstacles=[(r['key'],src.getObject(r['name']).Shape) for r in scene if r['key']!='P16']
results=[]
def check(name,s,extra=None):
    for key,other in obstacles+([] if extra is None else extra):
        if not s.BoundBox.intersect(other.BoundBox):continue
        overlap=s.common(other).Volume
        assert overlap<1e-4,(name,key,overlap)
        results.append(dict(position=name,obstacle=key,overlap_mm3=overlap))
def offset(shape,x=0,z=0):
    s=shape.copy();s.translate(V(x,0,z));return s
# Enter horizontally into the gap ABOVE the base, 25 mm below final position.
# Do not try pushing it up through the stationary base.
for x in [60,40,20,0]:check('cradle under-arm entry x='+str(x),offset(cradle,x=x,z=-25))
for z in [-25,-15,-5,0]:check('cradle final lift z='+str(z),offset(cradle,z=z))
for z in [30,15,5,0]:check('cap lowered z='+str(z),offset(cap,z=z),[('new cradle',cradle)])
(OUT/'installation_validation.json').write_text(json.dumps(dict(status='PASS',checks=results,scope='Sampled nominal original-tower installation path, small cups removed. Actual hand/tool access and print tolerances need physical check.'),indent=2))
print('PASS: temporary cradle enters the gap above the base; cap lowers from above.')
