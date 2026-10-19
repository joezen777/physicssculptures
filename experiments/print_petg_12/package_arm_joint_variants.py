from pathlib import Path
import json,zipfile,hashlib
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'output/arm_joint_variants'
for file in ['validation.json','installation_validation.json','slice_validation.json']:
    assert json.loads((OUT/file).read_text())['status']=='PASS',file
assert (OUT/'render_complete.txt').exists()
scoop=ROOT/'output/sail_80x120/P16_scoop_80x120mm_print-3x.stl'
common=['README.md','validation.json','installation_validation.json','slice_validation.json','slicer_check_0p2mm.ini']
packages={
'temporary_extension_kit.zip':['T15_extension_print-3x.stl','T15_closing_cap_print-3x.stl','temporary_assembly.FCStd','temporary_assembled.png','temporary_joint_exploded.png'],
'side_access_hub_arm_kit.zip':['S14_side_access_hub_print-1x.stl','S15_side_access_arm_print-3x.stl','side_access_assembly.FCStd','side_access_assembled.png','side_joint_detail.png','side_joint_exploded.png']}
for filename,files in packages.items():
    with zipfile.ZipFile(OUT/filename,'w',zipfile.ZIP_DEFLATED) as z:
        for name in common+files:z.write(OUT/name,name)
        z.write(scoop,scoop.name)
        if filename.startswith('temporary'):
            selection='TEMPORARY RETROFIT: print 3 extensions + 3 closing caps. Keep installed original short P15 arms and P14. Remove small cups. Reuse already printed large P16 scoops or print 3 supplied scoops. Read README section A.\n'
        else:
            selection='PERMANENT REBUILD: print 1 S14 hub + 3 S15 arms. These replace P14 and P15 together. Use 6 steel compression sleeves, 6 M4x35 root bolts and side-access washers/nuts. Reuse large P16 scoops or print 3 supplied scoops. Read README section B.\n'
        z.writestr('START_HERE.txt',selection)
    with zipfile.ZipFile(OUT/filename) as z:
        assert z.testzip() is None
        for name in common+files:assert z.read(name)==(OUT/name).read_bytes()
        assert z.read(scoop.name)==scoop.read_bytes()
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'output/stl/P14_sail_hex_hub_print-1x.stl',ROOT/'output/stl/P15_curved_sail_arm_print-3x.stl',scoop]}
(OUT/'release_summary.json').write_text(json.dumps(dict(status='PASS',packages=list(packages),reference_sha256=hashes,physical_testing=False),indent=2))
# Only remove generated backups inside this variant output directory.
for p in OUT.glob('*.FCBak'):p.unlink()
print('PASS: both print packages verified against source files.')
