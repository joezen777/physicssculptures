"""Confirm the coarse-nozzle external wall paths retain radial engraving detail."""
from pathlib import Path
import re,json,math,argparse,subprocess,os
ROOT=Path(__file__).resolve().parent;OUT=ROOT.parent/"pot_zoetrope/output"
CACHE=Path.home()/".cache/angularmomflyer/slicer"
def measure(path):
    x=y=z=0.;kind="";dips=0;outer=0;layers=set()
    for line in path.open():
        if line.startswith(";TYPE:"):kind=line.strip()[6:]
        if not line.startswith(("G0 ","G1 ")):continue
        words={a:float(b) for a,b in re.findall(r"([XYZE])([-+\d.]+)",line.split(";")[0])}
        x=words.get("X",x);y=words.get("Y",y);z=words.get("Z",z)
        if kind!="External perimeter" or "E" not in words or not ("X" in words or "Y" in words):continue
        local_z=z-22
        if not 20<local_z<66:continue
        inset=60+.35*local_z-math.hypot(x-110,y-110)
        if .4<inset<1.8:outer+=1
        if .95<inset<1.65:dips+=1;layers.add(round(z,3))
    return dict(recess_path_moves=dips,recess_path_layers=len(layers),outer_wall_moves=outer)
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--baseline",action="store_true");parser.add_argument("--slice",action="store_true");args=parser.parse_args()
    if args.slice:
        env=os.environ.copy();env["LD_LIBRARY_PATH"]=str(CACHE/"root/usr/lib/x86_64-linux-gnu")
        for key,name in [("P02","P02_pot_fan_A_print-2x.stl"),("P03","P03_pot_fan_B_print-1x.stl")]:
            command=[str(CACHE/"root/usr/bin/prusa-slicer"),"--load",str(ROOT/"slicer_check.ini"),"--export-gcode","--center","110,110","--support-material","--output",str(CACHE/(key+"_check.gcode")),str(ROOT/"output/stl"/name)]
            result=subprocess.run(command,env=env,capture_output=True,text=True)
            assert result.returncode==0,(key,result.stderr,result.stdout[-2000:])
            print("Sliced "+key,flush=True)
    rows={key:measure(CACHE/(key+"_check.gcode")) for key in ["P02","P03"]}
    target=OUT/("engraving_slice_baseline.json" if args.baseline else "engraving_slice_detail_check.json")
    if not args.baseline:
        baseline=json.loads((OUT/"engraving_slice_baseline.json").read_text())["parts"]
        for key,d in rows.items():
            assert d["recess_path_moves"]>baseline[key]["recess_path_moves"]+100,(key,d,baseline[key])
            assert d["recess_path_layers"]>=10,(key,d)
        result=dict(status="PASS",parts=rows,baseline=baseline,scope="External wall toolpaths include radial recess detail; physical print fidelity untested.")
    else:result=dict(parts=rows,scope="Unengraved P02/P03 toolpaths before artwork was added.")
    target.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
