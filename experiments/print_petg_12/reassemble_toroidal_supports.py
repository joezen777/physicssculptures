"""Pair the compensated P17 hub with the existing, unchanged PETG supports."""
from pathlib import Path
import hashlib,json
import trimesh

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output/toroidal5_final'
rotor=trimesh.load_mesh(OUT/'P17_top_fan_B_print-1x.stl',process=True)
support_path=OUT/'P17_toroidal5_supports_only.stl'
support=trimesh.load_mesh(support_path,process=True)
assert rotor.is_watertight and support.is_watertight
intersection=trimesh.boolean.intersection([rotor,support],engine='manifold')
assert abs(intersection.volume)<1e-4,intersection.volume
trimesh.util.concatenate([rotor,support]).export(
    OUT/'P17_top_fan_B_integrated_supports_print-1x.stl')

report=json.loads((OUT/'support_validation.json').read_text())
report.update(
    status='PASS_GEOMETRY_REUSED_SUPPORTS',
    part_volume_mm3=float(rotor.volume),
    rotor_support_overlap_mm3=float(abs(intersection.volume)),
    support_mesh_preserved=True,
    support_mesh_sha256=hashlib.sha256(support_path.read_bytes()).hexdigest(),
    supported_stl_sha256=hashlib.sha256(
        (OUT/'P17_top_fan_B_integrated_supports_print-1x.stl').read_bytes()
    ).hexdigest(),
    input_stl_sha256={
        name:hashlib.sha256((OUT/name).read_bytes()).hexdigest()
        for name in [
            'P17_top_fan_B_print-1x.stl',
            'P17_top_fan_B_integrated_supports_print-1x.stl',
            'P17_toroidal5_supports_only.stl',
            'C03_PETG_support_release_025_050_075.stl',
        ]
    },
    notes='Original supports-only STL and release coupon are unchanged; only the fan hub geometry changed.'
)
(OUT/'support_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('Reused support mesh; rotor overlap mm3:',intersection.volume,flush=True)
