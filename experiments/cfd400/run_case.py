from pathlib import Path
import os,subprocess,sys,json,time
case=Path(sys.argv[1]).resolve()
from foam_runtime import BIN,ENV
env=ENV
steps=['blockMesh','snappyHexMesh','checkMesh','topoSet','simpleFoam']
results=[]
if '--solve-only' in sys.argv:steps=['simpleFoam']
for cmd in steps:
    args=[str(BIN/cmd),'-case',str(case)]
    if cmd=='snappyHexMesh':args+=['-overwrite']
    t=time.time()
    with (case/('log.'+cmd)).open('w') as log:
        r=subprocess.run(args,env=env,stdout=log,stderr=log)
    results.append(dict(command=cmd,returncode=r.returncode,seconds=time.time()-t))
    (case/'run_status.json').write_text(json.dumps(results,indent=2))
    print(cmd,r.returncode,time.time()-t,flush=True)
    if r.returncode:raise SystemExit(r.returncode)
    if cmd=='checkMesh' and 'Mesh OK.' not in (case/'log.checkMesh').read_text():
        raise RuntimeError('Mesh did not pass checkMesh; solver not started.')
