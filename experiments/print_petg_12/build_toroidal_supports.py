"""Removable, short contoured PETG ribs; all coordinates and STL units mm."""
from pathlib import Path
import json,math
import numpy as np,trimesh
from shapely.geometry import box,Point
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'output/toroidal5_final'
rotor=trimesh.load_mesh(OUT/'P17_top_fan_B_print-1x.stl',process=True)
assert rotor.is_watertight and rotor.is_winding_consistent
LAYER=.25;GAP=.5;DX=.5;WIDTH=1.32;PITCH=2.4;XY=.3
# Rays at the expanded support footprint corners bound the closest surfaces.
xs=np.arange(-72+DX/2,72,DX);ys=np.arange(-72,72.01,PITCH)
centers=np.array([(x,y) for y in ys for x in xs]);offset=np.array([[0,0],[-DX/2-XY,-WIDTH/2-XY],[DX/2+XY,-WIDTH/2-XY],[DX/2+XY,WIDTH/2+XY],[-DX/2-XY,WIDTH/2+XY]])
origins=np.c_[np.repeat(centers,5,axis=0)+np.tile(offset,(len(centers),1)),np.full(len(centers)*5,-1.)]
heights=[[] for _ in range(len(origins))]
for start in range(0,len(origins),1500):
 o=origins[start:start+1500];dirs=np.tile([0,0,1.],(len(o),1))
 loc,ray,tri=rotor.ray.intersects_location(o,dirs,multiple_hits=True)
 for point,idx in zip(loc,ray):heights[start+idx].append(float(point[2]))
 print('Rays',min(start+1500,len(origins)),'/',len(origins),flush=True)
for i,h in enumerate(heights):
 heights[i]=sorted(set(round(z,5) for z in h))
profiles={};rejected=0;interval_count=0
for idx,(x,y) in enumerate(centers):
 col=idx%len(xs);row=idx//len(xs)
 # Half-mm cut slots divide each fin into at most 7.5 mm removable pieces.
 if col%16==15 or math.hypot(x,y)<15.5:continue
 hh=heights[idx*5:idx*5+5];n=len(hh[0])
 if n<2 or n%2 or any(len(h)!=n for h in hh):rejected+=1;continue
 for k in range(0,n,2):
  if k and math.hypot(x,y)<23.5:continue # no supports in functional hub pockets
  top=math.floor((min(h[k] for h in hh)-GAP)/LAYER+1e-8)*LAYER
  bottom=0 if k==0 else math.ceil((max(h[k-1] for h in hh)+GAP)/LAYER-1e-8)*LAYER
  if top-bottom<1:continue
  profiles.setdefault((row,col//16,k),[]).append(box(x-DX/2,bottom,x+DX/2,top));interval_count+=1
meshes=[];components=[];bed_groups={};bed_footprints={}
for (row,segment,k),rects in profiles.items():
 profile=unary_union(rects)
 polys=[profile] if profile.geom_type=='Polygon' else list(profile.geoms)
 for polygon in polys:
  # Add a low removable foot to ribs which start on the bed.
  m=trimesh.creation.extrude_polygon(polygon,WIDTH,engine='earcut')
  # profile XY represents physical XZ; extrusion is physical Y.
  m.vertices=m.vertices[:,[0,2,1]];m.vertices[:,1]+=ys[row]-WIDTH/2;m.invert()
  assert m.is_watertight and m.volume>0
  if polygon.bounds[1]<1e-8:
   xmin,zmin,xmax,zmax=polygon.bounds
   bed_groups.setdefault(segment,[]).append(m)
   bed_footprints.setdefault(segment,[]).append(box(xmin,ys[row]-.8,xmax,ys[row]+.8))
  else:meshes.append(m)
  components.append({'y':float(ys[row]),'span_x_mm':float(polygon.bounds[2]-polygon.bounds[0]),'bottom_mm':float(polygon.bounds[1]),'top_mm':float(polygon.bounds[3]),'between_blades':k>0})
# Thin base strips tie bed-supported ribs into removable combs.
for segment,ribs in bed_groups.items():
 xmin=-72+segment*8;xmax=xmin+7.5
 footprint=unary_union(bed_footprints[segment]).buffer(.45,join_style=2).intersection(box(xmin,-74,xmax,74)).difference(Point(0,0).buffer(14.8))
 polys=[footprint] if footprint.geom_type=='Polygon' else list(footprint.geoms)
 bases=[trimesh.creation.extrude_polygon(p,.5,engine='earcut') for p in polys if p.area>.01]
 meshes.append(trimesh.boolean.union(ribs+bases,engine='manifold'))
assert meshes and all(m.is_watertight for m in meshes)
support=trimesh.util.concatenate(meshes)
# Exact mesh clearance trimming catches curvature between sampled rays.
protected=[rotor]
for dz in [-GAP,GAP]:
 m=rotor.copy();m.apply_translation([0,0,dz]);protected.append(m)
keepout=trimesh.boolean.union(protected,engine='manifold')
support=trimesh.boolean.difference([support,keepout],engine='manifold')
assert support.is_watertight
intersection=trimesh.boolean.intersection([rotor,support],engine='manifold')
assert abs(intersection.volume)<1e-4,intersection.volume
support.export(OUT/'P17_toroidal5_supports_only.stl')
trimesh.util.concatenate([rotor,support]).export(OUT/'P17_top_fan_B_integrated_supports_print-1x.stl')
# Three compact bridge coupons, identical ribs, 1/2/3-layer release gaps left to right.
coupons=[]
for j,gap in enumerate([.25,.5,.75]):
 parts=[]
 def block(size,pos):
  b=trimesh.creation.box(size);b.apply_translation(pos);parts.append(b)
 x=j*30
 block([24,12,.5],[x,0,.25]);block([2,12,10],[x-11,0,5]);block([2,12,10],[x+11,0,5]);block([24,12,1],[x,0,10.5])
 for y in [-4.8,-2.4,0,2.4,4.8]:block([18,WIDTH,10-gap],[x,y,(10-gap)/2])
 coupons.append(trimesh.boolean.union(parts,engine='manifold'))
trimesh.util.concatenate(coupons).export(OUT/'C03_PETG_support_release_025_050_075.stl')
report=dict(status='PASS_GEOMETRY_ONLY',physically_tested=False,nozzle_mm=.6,layer_mm=LAYER,nominal_vertical_gap_mm=GAP,expanded_xy_check_mm=XY,rib_width_mm=WIDTH,rib_pitch_mm=PITCH,max_rib_segment_mm=max(x['span_x_mm'] for x in components),support_mesh_groups=len(meshes),support_rib_segments=len(components),rotor_support_overlap_mm3=float(abs(intersection.volume)),between_blade_components=sum(x['between_blades'] for x in components),support_volume_mm3=float(support.volume),support_intervals=interval_count,part_volume_mm3=float(rotor.volume),notes='Short ribs, disconnected from rotor by release gaps. Bed-supported ribs joined into peelable base combs; remove all pieces through loop openings. Gap performance must be calibrated with coupon. Do not split/drop STL shells onto the bed.',components=components)
(OUT/'support_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('Supports generated:',len(meshes),'components',flush=True)

# Bind generated verification to the exact mesh files.
import hashlib
p=OUT/'support_validation.json';j=json.loads(p.read_text());j['input_stl_sha256']={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in OUT.glob('*.stl')};p.write_text(json.dumps(j,indent=2)+'\n')
