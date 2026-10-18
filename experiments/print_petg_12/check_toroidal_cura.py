from pathlib import Path
import subprocess,json
root=Path('/mnt/c/Program Files/UltiMaker Cura 5.8.1')
repo=Path(__file__).resolve().parents[2];out=repo/'experiments/print_petg_12/output/toroidal5_final'
def win(p):return subprocess.check_output(['wslpath','-w',str(p)],text=True).strip()
defs=root/'share/cura/resources/definitions';print(defs.exists(),flush=True)
settings={'layer_height':.25,'layer_height_0':.25,'machine_nozzle_size':.6,'xy_offset':0,'line_width':.66,'wall_line_width':.66,'wall_line_width_0':.66,'wall_line_width_x':.66,'skin_line_width':.66,'infill_line_width':.66,'wall_line_count':4,'top_layers':5,'bottom_layers':5,'infill_sparse_density':30,'infill_line_distance':2.2,'support_enable':'false','adhesion_type':'none','meshfix_union_all':'true','meshfix_union_all_remove_holes':'false','machine_width':220,'machine_depth':220,'machine_height':250,'machine_center_is_zero':'true','material_print_temperature':240,'material_bed_temperature':80,'speed_print':30,'speed_wall':25,'speed_wall_0':20,'speed_wall_x':25,'speed_topbottom':25,'speed_layer_0':15,'speed_travel':120,'machine_gcode_flavor':'RepRap (Marlin)','machine_start_gcode':'','machine_end_gcode':'','roofing_layer_count':0,'flooring_layer_count':0}
args=[str(root/'CuraEngine.exe'),'slice','-m4','-j',win(defs/'fdmprinter.def.json')]
for k,v in settings.items():args+=['-s',f'{k}={v}']
args+=['-e0','-j',win(defs/'fdmextruder.def.json'),'-s','machine_nozzle_size=0.6','-s','material_diameter=1.75','-l',win(out/'P17_top_fan_B_integrated_supports_print-1x.stl'),'-o',win(out/'cura_inspection_only.gcode')]
r=subprocess.run(args,capture_output=True,text=True);(out/'cura_engine.log').write_text(r.stdout+'\n'+r.stderr);print(r.returncode, r.stderr[-2500:])
(out/'cura_settings.json').write_text(json.dumps(settings,indent=2))

assert r.returncode==0

import hashlib
log=r.stdout+'\n'+r.stderr
report={'engine':'CuraEngine 5.8.1','exit_code':r.returncode,'nozzle_mm':.6,'layer_mm':.25,'horizontal_expansion_mm':0,'cad_offset_applied_to':'P17 hub/casing features only','supported_stl_sha256':hashlib.sha256((out/'P17_top_fan_B_integrated_supports_print-1x.stl').read_bytes()).hexdigest(),'warnings':[x for x in log.splitlines() if '[warning]' in x],'errors':[x for x in log.splitlines() if '[error]' in x]}
(out/'cura_engine_validation.json').write_text(json.dumps(report,indent=2)+'\n')
assert not report['errors']
