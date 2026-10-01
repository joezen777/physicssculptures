"""Separate localhost-only workbench; does not change the existing flywheel server."""
from dataclasses import asdict, replace
from pathlib import Path
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from whistle import Config, simulate, sweep, optimize, example_config

ROOT=Path(__file__).resolve().parent
app=FastAPI(title="Passive whistle physics")
pool=ThreadPoolExecutor(max_workers=1)
jobs={}
lock=Lock()

def clean(value):
    if isinstance(value,np.generic): return value.item()
    if isinstance(value,dict): return {k:clean(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)): return [clean(v) for v in value]
    return value

@app.get("/api/defaults")
def defaults(): return asdict(Config())

@app.get("/api/example")
def example(): return asdict(example_config())

@app.post("/api/jobs")
def submit(body:dict):
    kind=body.get("kind","simulate")
    if kind not in ("simulate","sweep","optimize","compare","balance"):
        raise HTTPException(422,"Unknown experiment")
    try:c=Config(**body.get("config",{})).validate()
    except (ValueError,TypeError) as e:raise HTTPException(422,str(e)) from e
    with lock:
        if any(j["status"] in ("queued","running") for j in jobs.values()):
            raise HTTPException(409,"An experiment is already running; wait or cancel it.")
        key=uuid4().hex
        while len(jobs)>7: jobs.pop(next(iter(jobs)))
        jobs[key]={"status":"queued","progress":0,"message":"Starting numerical integration","cancel":False}
    def update(fraction,message):
        with lock:
            if jobs[key]["cancel"]: raise InterruptedError("Cancelled")
            jobs[key].update(progress=fraction,message=message)
    def work():
        with lock:jobs[key]["status"]="running"
        try:
            if kind=="simulate":result=simulate(c,progress=update)
            elif kind=="sweep":result=sweep(c,21,update)
            elif kind=="optimize":result=optimize(c,54,update)
            elif kind=="compare":
                result={"config":asdict(c),"modes":[]}
                for i,mode in enumerate("ABCD"):
                    z=simulate(replace(c,mode=mode,stator_cam=False,use_dump=False),False)
                    result["modes"].append({"mode":mode,"summary":z["summary"]})
                    update((i+1)/4,f"Mode {mode}")
            else:
                result={"config":asdict(c),"faults":[]}
                for i,fault in enumerate(("none","stuck","late","friction","mass")):
                    z=simulate(replace(c,modules=2,fault=fault),False)
                    result["faults"].append({"fault":fault,"summary":z["summary"]})
                    update((i+1)/5,f"Opposing-piston fault: {fault}")
            update(1,"Complete")
            with lock:jobs[key].update(status="complete",result=clean(result),kind=kind)
        except InterruptedError:
            with lock:jobs[key].update(status="cancelled",message="Cancelled")
        except Exception as e:
            with lock:jobs[key].update(status="failed",message=str(e))
    pool.submit(work)
    return {"id":key}

@app.get("/api/jobs/{key}")
def get_job(key:str):
    with lock:
        if key not in jobs:raise HTTPException(404,"Unknown experiment")
        return jobs[key]

@app.delete("/api/jobs/{key}")
def cancel(key:str):
    with lock:
        if key not in jobs:raise HTTPException(404,"Unknown experiment")
        jobs[key]["cancel"]=True
    return {"cancel_requested":True}

dist=ROOT/"web"/"dist"
if dist.exists():
    app.mount("/assets",StaticFiles(directory=dist/"assets"),name="assets")
    @app.get("/")
    def index():return FileResponse(dist/"whistle.html")

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app,host="127.0.0.1",port=8767)
