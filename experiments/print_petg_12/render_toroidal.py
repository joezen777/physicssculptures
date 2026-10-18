from pathlib import Path
import numpy as np,trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.colors import to_rgb
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'output/toroidal5_final'
fan=trimesh.load_mesh(OUT/'P17_top_fan_B_print-1x.stl');sup=trimesh.load_mesh(OUT/'P17_toroidal5_supports_only.stl')
fig=plt.figure(figsize=(14,8))
def draw(ax,mesh,color,alpha=1):
 light=np.array([-.3,-.5,.8]);light/=np.linalg.norm(light)
 shading=.45+.55*np.clip(mesh.face_normals@light,0,1)
 colors=np.array(to_rgb(color))[None,:]*shading[:,None]
 ax.add_collection3d(Poly3DCollection(mesh.triangles,facecolors=colors,edgecolors='none',alpha=alpha))
def setup(ax,title,elev=26,azim=-55):
 ax.set(xlim=(-90,90),ylim=(-90,90),zlim=(-2,100));ax.set_box_aspect((180,180,102));ax.view_init(elev,azim);ax.set_axis_off();ax.set_title(title,fontsize=12)
ax=fig.add_subplot(221,projection='3d');draw(ax,fan,'#e3a34a');setup(ax,'Final P17: five closed-loop pairs')
ax=fig.add_subplot(222,projection='3d');draw(ax,fan,'#e3a34a');setup(ax,'Top view — 144 mm swept diameter',90,-90)
ax=fig.add_subplot(223,projection='3d');draw(ax,sup,'#519aaa');draw(ax,fan,'#e3a34a');setup(ax,'Separate supported STL — removable blue combs',12,-65)
ax=fig.add_subplot(224,projection='3d');draw(ax,fan,'#e3a34a')
g=trimesh.load_mesh(OUT/'P185_print-1x.stl');g.vertices[:,1]*=-1;g.vertices[:,2]=86-g.vertices[:,2]
# Cutaway uses triangle-centre selection for visual inspection only.
keep=np.flatnonzero(g.triangles_center[:,1]>0);g=g.submesh([keep],append=True);draw(ax,g,'#82919f',.45)
gr=trimesh.load_mesh(OUT/'P19_curved_guard_grille_print-1x.stl');gr.apply_translation([0,0,86]);draw(ax,gr,'#82919f',.3)
setup(ax,'Raised P185 shroud + unchanged P19 (cutaway)',15,-60)
fig.suptitle('Toroidal5 print release | PETG · 0.6 mm nozzle · 0.25 mm layers',fontsize=16)
fig.tight_layout();fig.savefig(OUT/'toroidal5_print_preview.png',dpi=170)
