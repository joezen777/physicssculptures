from pathlib import Path
import sys, os
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
os.chdir(ROOT)
Path('runs/whistle').mkdir(parents=True,exist_ok=True)
from whistle import *
from whistle_server import clean
from pathlib import Path
import json
out={}
out["baseline"]={mode:simulate(Config(mode=mode),False)["summary"] for mode in "ABCD"}
c=example_config()
out["candidate"]=simulate(c,False)
out["faults"]={fault:simulate(replace(c,fault=fault),False)["summary"] for fault in ("none","stuck","late","friction","mass")}
out["fine_rpm"]=[]
for rpm in (595,598,599,599.5,599.75,600,600.25,600.5,601,602,605):
 s=simulate(replace(c,rpm=rpm,duration=24),False)["summary"]
 out["fine_rpm"].append({"rpm":rpm,**s})
out["long_run"]=simulate(replace(c,duration=60),False)["summary"]
out["optimization"]=optimize(Config(),54)
Path('runs/whistle/validation.json').write_text(json.dumps(clean(out),indent=2))
print('Long-run',out["long_run"]["cycle_hz"],out["long_run"]["reset_count"])
print('Candidate late pitch',out["candidate"]["summary"]["pitch_min"],out["candidate"]["summary"]["pitch_max"])
print('Faults',[(k,v["self_cycles"],v["peak_imbalance"]) for k,v in out["faults"].items()])
print('RPM',[(z["rpm"],z["behavior"],z["self_cycles"]) for z in out["fine_rpm"]])
print('Search',len(out["optimization"]["candidates"]),out["optimization"]["tested"])
