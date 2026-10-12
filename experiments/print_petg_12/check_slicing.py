"""Run geometry-only slice checks; do not send generated G-code to a printer."""
from pathlib import Path
import json,subprocess,os,re,concurrent.futures
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"output"
CACHE=Path.home()/".cache/angularmomflyer/slicer"
EXE=CACHE/"root/usr/bin/prusa-slicer"
env=os.environ.copy();env["LD_LIBRARY_PATH"]=str(CACHE/"root/usr/lib/x86_64-linux-gnu")
rows=json.loads((OUT/"parts.json").read_text())
def check(row):
    path=CACHE/(row["id"]+"_check.gcode")
    args=[str(EXE),"--load",str(ROOT/"slicer_check.ini"),"--export-gcode","--center","110,110","--output",str(path)]
    if row["support"]!="None":args+=["--support-material"]
    args+=[str(OUT/"stl"/row["file"])]
    r=subprocess.run(args,env=env,capture_output=True,text=True)
    result=dict(id=row["id"],exit_code=r.returncode,supports=row["support"]!="None",warnings=r.stderr.strip())
    if r.returncode==0:
        text=path.read_text();result["layers"]=text.count(";LAYER_CHANGE")
        result["extrusion_moves"]=sum(1 for line in text.splitlines() if line.startswith("G1 ") and " E" in line and (" X" in line or " Y" in line))
        result["filament_mm"]=re.findall(r"; filament used \[mm\] = ([\d.]+)",text)
        assert result["layers"]>0 and result["extrusion_moves"]>0
    print(result,flush=True)
    return result
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(check,rows))
(OUT/"slice_validation.json").write_text(json.dumps(dict(status="PASS" if all(r["exit_code"]==0 for r in results) else "FAIL",nozzle_mm=.4,layer_mm=.2,line_width_mm=.45,results=results,scope="Toolpath generation only; not a calibrated machine profile. G-code retained outside the print package."),indent=2))
