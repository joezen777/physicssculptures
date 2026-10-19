"""Mesh-based checks, geometric airflow proxy, render, and PETG slicing."""
from pathlib import Path
import hashlib,json,os,subprocess
import numpy as np,trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.colors import to_rgb
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'output/p19_rain'
report={'physical_tested':False,'mesh':{},'airflow':{}}
meshes={}
for name in ['P19','P19C']:
    m=trimesh.load_mesh(OUT/(name+'_rain.stl'));meshes[name]=m
    assert m.is_watertight and m.is_winding_consistent and m.volume>0
    assert len(m.split())==1
    report['mesh'][name]={'watertight':True,'consistent_winding':True,
        'components':1,'dimensions_mm':m.extents.tolist(),'volume_mm3':float(m.volume)}
m=meshes['P19']
# Vertical rays through the six annular overlaps locate actual mesh slot walls.
curtains=[]
for r in [32.25,39.75,47.25,54.75,62.25,70.125]:
    n=720;t=(np.arange(n)+.37)*2*np.pi/n
    origins=np.column_stack([r*np.cos(t),r*np.sin(t),np.full(n,40)])
    hit,idx,_=m.ray.intersects_location(origins,np.tile([0,0,-1],(n,1)),multiple_hits=True)
    gaps=[]
    for i in range(n):
        z=np.sort(hit[idx==i,2])
        # Closed manifold gives pairs of material intervals from bottom up.
        assert len(z)%2==0,(r,i,z)
        values=[z[j+1]-z[j] for j in range(1,len(z)-1,2) if z[j]>9]
        gaps.append(max(values,default=0))
    gaps=np.array(gaps)
    curtains.append({'radius_mm':r,'open_fraction':float(np.mean(gaps>.1)),
      'minimum_open_gap_mm':float(gaps[gaps>.1].min()),
      'area_mm2':float(gaps.sum()*r*2*np.pi/n)})
area=sum(c['area_mm2'] for c in curtains)
report['airflow']={'method':'720 mesh rays per cylindrical overlap curtain; sum clear vertical gaps times arc length',
 'curtains':curtains,'total_curtain_area_mm2':area,
 'relative_to_annulus_24_to_76':area/(np.pi*(76**2-24**2)),
 'limitation':'Geometric side-slot proxy, not discharge coefficient or fan performance. Turns, pillars and wetting cause losses.'}
assert min(c['minimum_open_gap_mm'] for c in curtains)>3
# Verify actual upward roof triangles drain toward gutter ends. Exclude rims/posts.
v=m.triangles_center;n=m.face_normals
sel=(v[:,2]>10.95)&(v[:,2]<21.5)&(np.hypot(v[:,0],v[:,1])>25)&(np.hypot(v[:,0],v[:,1])<75)&(n[:,2]>.7)&(n[:,2]<.999)
# Roof gradients from mesh triangle normals; radial downhill component should be positive.
r=np.hypot(v[sel,0],v[sel,1]);radial=(n[sel,0]*v[sel,0]+n[sel,1]*v[sel,1])/(r*n[sel,2])
report['drainage']={'gutter_drop_mm':67*.075,'gutter_slope':.075,
 'roof_radial_downhill_gradient_min':float(radial.min()),
 'roof_radial_downhill_gradient_max':float(radial.max()),
 'roof_triangles_checked':int(sel.sum()),
 'angular_rise_from_gutter_to_sector_midpoint_mm':2.4,
 'limitations':'Checks gravity drainage of designed surfaces. Surface tension, print texture, wind-driven rain and splash require physical testing.'}
assert radial.min()>0
# Measure actual gutter centerline descent from mesh, not only design constants.
sample_r=np.linspace(26,87.5,124);drops=[]
for theta in np.radians(np.arange(30,360,60)):
 origins=np.column_stack([sample_r*np.cos(theta),sample_r*np.sin(theta),np.full(len(sample_r),40)])
 hits,ids,_=m.ray.intersects_location(origins,np.tile([0,0,-1],(len(sample_r),1)),multiple_hits=True)
 heights=np.array([hits[ids==i,2].max() for i in range(len(sample_r))])
 slopes=-np.diff(heights)/np.diff(sample_r)
 assert slopes.min()>.07
 drops.append(float(slopes.min()))
report['drainage']['mesh_gutter_centerline_min_outward_slopes']=drops
report['drainage']['excluded_flat_surfaces']='Original mounting rim, bolt lands and small central cap crown can retain a water film; no enclosing lip on crown.'
# Covered central bore: vertical rays over bore and bearing radius strike the cap.
t=np.linspace(0,2*np.pi,120,endpoint=False)
origins=np.vstack([np.column_stack([r*np.cos(t),r*np.sin(t),np.full(len(t),40)]) for r in [0,4.3,8,11]])
hit,ids,_=meshes['P19C'].ray.intersects_location(origins,np.tile([0,0,-1],(len(origins),1)),multiple_hits=True)
assert len(np.unique(ids))==len(origins)
report['center_cover']={'vertical_rain_rays_intercepted':len(origins),'bearing_radius_checked_mm':11,'wind_driven_spray_excluded':False}
# Render actual mesh and radial cut to expose the labyrinth.
fig=plt.figure(figsize=(15,10),facecolor='#f4f6f8')
def draw(ax,mesh,color):
    light=np.array([-.3,-.5,.8]);light/=np.linalg.norm(light)
    shade=.45+.55*np.clip(mesh.face_normals@light,0,1)
    ax.add_collection3d(Poly3DCollection(mesh.triangles,facecolors=np.array(to_rgb(color))[None,:]*shade[:,None],edgecolors='none',antialiased=False))
def setup(ax,title,elev,azim):
    ax.set(xlim=(-90,90),ylim=(-90,90),zlim=(0,42));ax.set_box_aspect((180,180,60));ax.view_init(elev,azim);ax.set_axis_off();ax.set_title(title)
ax=fig.add_subplot(221,projection='3d',computed_zorder=False);draw(ax,m,'#4d91a6');draw(ax,meshes['P19C'],'#e1a846');setup(ax,'Assembled rain-shedding grille',32,-65)
ax=fig.add_subplot(222,projection='3d',computed_zorder=False);draw(ax,m,'#4d91a6');draw(ax,meshes['P19C'],'#e1a846');setup(ax,'Six petal gutters between bolt holes',90,-90)
ax=fig.add_subplot(223,projection='3d',computed_zorder=False);cut=m.submesh([np.flatnonzero(m.triangles_center[:,1]>0)],append=True);draw(ax,cut,'#4d91a6');draw(ax,meshes['P19C'],'#e1a846');setup(ax,'Visual half-section: discrete pillars, open louver slots',8,-90)
ax=fig.add_subplot(224)
section=trimesh.intersections.mesh_plane(m,plane_origin=[0,0,0],plane_normal=[0,1,0])
for line in section:ax.plot(line[:,0],line[:,2],color='#256879',lw=1)
section=trimesh.intersections.mesh_plane(meshes['P19C'],plane_origin=[0,0,0],plane_normal=[0,1,0])
for line in section:ax.plot(line[:,0],line[:,2],color='#c18b27',lw=1)
ax.set(xlim=(0,90),ylim=(0,30),xlabel='Radius (mm)',ylabel='Height above mounting plane (mm)',title='Exact mesh section through bolt axis');ax.set_aspect('equal');ax.grid(alpha=.2)
fig.suptitle('P19 rain-shedding replacement | original 176 mm mounting rim | removable center cap',fontsize=16)
fig.tight_layout();fig.savefig(OUT/'P19_rain_review.png',dpi=160);plt.close(fig)
report['input_stl_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('*.stl')}
(OUT/'mesh_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
