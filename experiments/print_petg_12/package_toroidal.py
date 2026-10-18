from pathlib import Path
import zipfile,json,hashlib
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'output';R=OUT/'toroidal5_final'
cura=json.loads((R/'cura_toolpath_validation.json').read_text())
assert cura['supported_stl_sha256']==hashlib.sha256((R/'P17_top_fan_B_integrated_supports_print-1x.stl').read_bytes()).hexdigest()
for p in R.glob('*validation.json'):
 j=json.loads(p.read_text())
 for name,digest in j.get('input_stl_sha256',{}).items():
  assert hashlib.sha256((R/name).read_bytes()).hexdigest()==digest,(p,name)
for name,digest in json.loads((R/'integration_validation.json').read_text())['production_stl_sha256'].items():
 assert hashlib.sha256((OUT/'stl'/name).read_bytes()).hexdigest()==digest,name
allowed={'.stl','.step','.FCStd','.json','.md','.ini','.png'}
files=sorted(p for p in R.iterdir() if p.suffix in allowed)
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(R/'SHA256SUMS.txt').write_text('\n'.join(v+'  '+k for k,v in manifest.items())+'\n');files.append(R/'SHA256SUMS.txt')
focused=OUT/'toroidal5_final_print_package.zip'
with zipfile.ZipFile(focused,'w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,'toroidal5_final/'+p.name)
production=ROOT/'print_package_PETG_1p2mm.zip';temporary=production.with_suffix('.new.zip');prefix='fan_tunnel_PETG_1p2mm/'
replacements={}
with zipfile.ZipFile(production) as z:
 for n in z.namelist():
  rel=n.removeprefix(prefix);p=OUT/rel
  if p.is_file():replacements[n]=p
for name in ['P17_top_fan_B_integrated_supports_print-1x.stl','P185_print-1x.stl','C03_PETG_support_release_025_050_075.stl']:
 replacements[prefix+'stl/'+name]=OUT/'stl'/name
for p in files:replacements[prefix+'toroidal5_final/'+p.name]=p
with zipfile.ZipFile(production) as old,zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED) as new:
 for n in old.namelist():
  if n not in replacements:new.writestr(n,old.read(n))
 for n,p in replacements.items():new.write(p,n)
temporary.replace(production)
for path in [focused,production]:
 with zipfile.ZipFile(path) as z:assert z.testzip() is None
 print(path)
