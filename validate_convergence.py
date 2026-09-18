from dataclasses import replace
from pathlib import Path
import json
from gyro_sim import Config, simulate
Path("runs/demo").mkdir(parents=True, exist_ok=True)
report = {}
for mode, gravity, alternating in [("free",0,False), ("free",0,True), ("supported",9.81,False)]:
    c = Config(mode=mode, gravity=gravity, alternating=alternating, duration=3)
    coarse, a = simulate(c)
    fine, b = simulate(replace(c, dt=.0001))
    report[f"{mode}_alternating_{alternating}"] = {
        "coarse": a, "fine": b,
        "endpoint_ring_difference_m": abs(coarse[-1]["ring_z"]-fine[-1]["ring_z"]),
        "endpoint_tilt_difference_deg": max(abs(coarse[-1][f"tilt{i}_deg"]-fine[-1][f"tilt{i}_deg"]) for i in range(4))
    }
Path("runs/demo/convergence.json").write_text(json.dumps(report, indent=2))
for name, item in report.items():
    print(name, "ring delta", item["endpoint_ring_difference_m"], "tilt delta", item["endpoint_tilt_difference_deg"], "fine COM error", item["fine"]["max_ballistic_com_error_m"])
