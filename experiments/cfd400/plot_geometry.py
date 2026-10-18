from pathlib import Path
import struct,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
ROOT=Path(__file__).resolve().parent
fig=plt.figure(figsize=(14,8))
for i,name in enumerate(['original','scimitar','tubercled','toroidal5']):
    data=(ROOT/'geometry'/(name+'.stl')).read_bytes()
    n=struct.unpack_from('<I',data,80)[0]
    if len(data)==84+50*n:
        triangles=np.array([struct.unpack_from('<12f',data,84+50*j)[3:] for j in range(n)]).reshape(-1,3,3)*1000
    else:
        verts=[list(map(float,l.split()[1:])) for l in data.decode().splitlines() if l.strip().startswith('vertex')]
        triangles=np.array(verts).reshape(-1,3,3)*1000
    for row in range(2):
        ax=fig.add_subplot(2,4,i+1+4*row,projection='3d')
        poly=Poly3DCollection(triangles,facecolors='#66aacc',edgecolors='#37758a',linewidths=.06,alpha=1)
        ax.add_collection3d(poly);ax.set(xlim=(-75,75),ylim=(-75,75),zlim=(-25,42))
        ax.set_box_aspect((150,150,67));ax.view_init(elev=90 if row==0 else 20,azim=-65)
        ax.set_title(name.replace('toroidal5','Toroidal: 5 pairs').capitalize());ax.set_axis_off()
fig.suptitle('Actual CFD surfaces | 144 mm diameter | generic candidate sections',fontsize=16)
fig.tight_layout();fig.savefig(ROOT/'geometry'/'comparison.png',dpi=160)
