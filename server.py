"""Local dashboard. Physics stays in Python/MuJoCo; Three.js displays body poses."""
from contextlib import asynccontextmanager
from dataclasses import asdict
from collections import deque
from pathlib import Path
from threading import Event, RLock, Thread
import time
import mujoco
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from gyro_sim import Config, Experiment, sample
from flight import flight_config

ROOT = Path(__file__).resolve().parent


class Lab:
    def __init__(self):
        self.lock = RLock()
        self.experiment = Experiment(Config(startup="staged"))
        self.initial_com_z=float(self.experiment.data.subtree_com[1,2])
        self.revision = 1
        self.history = deque(maxlen=240)
        self.error = None
        self.stop = Event()

    def run(self):
        while not self.stop.is_set():
            start = time.monotonic()
            with self.lock:
                try:
                    e = self.experiment
                    before = e.data.time
                    e.tick(.04)
                    mujoco.mj_forward(e.model, e.data)
                    if any(w.number for w in e.data.warning):
                        raise RuntimeError("Numerical warning: pause and lower speed or reset.")
                    if not e.paused and e.data.time > before:
                        self.history.append(sample(e.model, e.data, e.c))
                except Exception as exc:
                    self.error = str(exc)
                    self.experiment.paused = True
            self.stop.wait(max(0, .04-(time.monotonic()-start)))

    def state(self):
        with self.lock:
            e = self.experiment
            row = sample(e.model, e.data, e.c)
            return {
                "revision": self.revision, "paused": e.paused, "error": self.error,
                "initial_com_z":self.initial_com_z,
                "config": asdict(e.c), "metrics": row, "history": list(self.history),
                "body_positions": e.data.xpos.tolist(), "body_quaternions": e.data.xquat.tolist(),
                "mass_kg": float(e.model.body_subtreemass[1]),
            }

    def geometry(self):
        with self.lock:
            m = self.experiment.model
            return {"revision": self.revision, "bodies": [
                mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY,i) or str(i) for i in range(m.nbody)],
                "geoms": [{"type": int(m.geom_type[i]), "body": int(m.geom_bodyid[i]),
                           "size": m.geom_size[i].tolist(), "pos": m.geom_pos[i].tolist(),
                           "quat": m.geom_quat[i].tolist(), "color": m.geom_rgba[i].tolist(),
                           "name": mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_GEOM,i) or ""}
                          for i in range(m.ngeom) if m.geom_type[i] != mujoco.mjtGeom.mjGEOM_PLANE]}

    def configure(self, patch):
        with self.lock:
            fields = set(Config.__dataclass_fields__)
            if set(patch)-fields:
                raise ValueError("Unknown configuration field")
            config = asdict(self.experiment.c) | patch
            # API is used locally, but validate types before calling the physics engine.
            for name, f in Config.__dataclass_fields__.items():
                value=config[name]
                if f.type is bool and type(value) is not bool:
                    raise ValueError(f"{name} must be boolean")
                if f.type is float and (isinstance(value,bool) or not isinstance(value,(float,int))):
                    raise ValueError(f"{name} must be numeric")
                if f.type is str and not isinstance(value,str):
                    raise ValueError(f"{name} must be text")
            new = Experiment(Config(**config))
            self.experiment = new
            self.initial_com_z=float(new.data.subtree_com[1,2])
            self.revision += 1
            self.history.clear()
            self.error = None


lab = Lab()


@asynccontextmanager
async def lifespan(app):
    worker=Thread(target=lab.run, daemon=True)
    worker.start()
    yield
    lab.stop.set()
    worker.join(timeout=3)


app = FastAPI(lifespan=lifespan)


@app.get("/api/state")
def state():
    return lab.state()


@app.get("/api/model")
def model():
    return lab.geometry()


@app.post("/api/preset/{name}")
def preset(name: str):
    if name not in ("flight", "no-air", "original"):
        raise HTTPException(404, "Unknown preset")
    c = Config(startup="staged") if name == "original" else flight_config(name == "flight")
    lab.configure(asdict(c))
    return lab.state()


@app.post("/api/config")
def configure(patch: dict):
    try:
        lab.configure(patch)
    except (ValueError, TypeError) as exc:
        raise HTTPException(422, str(exc)) from exc
    return lab.state()


@app.post("/api/action/{action}")
def action(action: str):
    with lab.lock:
        if action == "toggle":
            lab.experiment.handle_key(32)
        elif action == "reset":
            lab.experiment.handle_key(82)
            lab.initial_com_z=float(lab.experiment.data.subtree_com[1,2])
            lab.history.clear()
            lab.error = None
        else:
            raise HTTPException(404, "Unknown action")
    return lab.state()


dist=ROOT/"web"/"dist"
if dist.exists():
    app.mount("/assets",StaticFiles(directory=dist/"assets"),name="assets")


@app.get("/")
def index():
    if not (dist/"index.html").exists():
        raise HTTPException(503,"Build the frontend: cd web && npm install && npm run build")
    return FileResponse(dist/"index.html")
