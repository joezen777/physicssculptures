from pathlib import Path
import re,json,hashlib
import numpy as np,trimesh
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
out=Path(__file__).resolve().parent/'output/toroidal5_final'
support=trimesh.load_mesh(out/'P17_toroidal5_supports_only.stl');rotor=trimesh.load_mesh(out/'P17_top_fan_B_print-1x.stl')
engine=json.loads((out/'cura_engine_validation.json').read_text())
assert engine['exit_code']==0 and engine['supported_stl_sha256']==hashlib.sha256((out/'P17_top_fan_B_integrated_supports_print-1x.stl').read_bytes()).hexdigest()
levels=[10,25,35,45];paths={v:[] for v in levels};xyz=np.zeros(3);e=0;layer=-1
for line in (out/'cura_inspection_only.gcode').read_text().splitlines():
 if line.startswith(';LAYER:'):layer=int(line.split(':')[1])
 if line.startswith('G92 E'):e=float(line[5:]);continue
 if not line.startswith(('G0 ','G1 ')):continue
 vals={k:float(v) for k,v in re.findall(r'([XYZE])(-?[0-9.]+)',line)};prev=xyz.copy();ne=vals.get('E',e)
 for i,k in enumerate('XYZ'):xyz[i]=vals.get(k,xyz[i])
 if ne>e and np.linalg.norm(xyz[:2]-prev[:2])>0.01:
  for v in levels:
   if abs(xyz[2]-v)<.01:paths[v].append([prev[:2].copy(),xyz[:2].copy()])
 e=ne
fig,axs=plt.subplots(2,2,figsize=(12,12));report=[]
for ax,v in zip(axs.flat,levels):
 seg=np.array(paths[v]);mid=seg.mean(axis=1);pts=np.c_[mid,np.full(len(mid),v-.125)]
 ins=support.contains(pts);part=rotor.contains(pts)
 ax.add_collection(LineCollection(seg[~ins],colors='#b78529',linewidths=.35));ax.add_collection(LineCollection(seg[ins],colors='#1687ab',linewidths=.55))
 outer=ins&(np.linalg.norm(mid,axis=1)>50);counts=np.histogram(np.mod(np.arctan2(mid[outer,1],mid[outer,0]),2*np.pi),bins=np.linspace(0,2*np.pi,6))[0]
 report.append(dict(z_mm=v,support_extrusion_segments=int(ins.sum()),outer_support_segments_by_72degree_sector=counts.tolist(),total_segments=len(seg)))
 assert ins.sum()>0 and all(counts>0),(v,'Supports absent in an outer sector')
 ax.set(xlim=(-76,76),ylim=(-76,76),aspect='equal',title=f'Cura 5.8.1 Z={v} mm; blue = built-in support paths');ax.grid(alpha=.15)
fig.tight_layout();fig.savefig(out/'cura_support_toolpaths.png',dpi=150)
(out/'cura_toolpath_validation.json').write_text(json.dumps({'status':'PASS_SAMPLED_SUPPORT_TOOLPATHS','engine':'CuraEngine 5.8.1','physically_tested':False,'engine_exit_code':engine['exit_code'],'engine_warnings':engine['warnings'],'supported_stl_sha256':hashlib.sha256((out/'P17_top_fan_B_integrated_supports_print-1x.stl').read_bytes()).hexdigest(),'samples':report},indent=2))
print(report)
