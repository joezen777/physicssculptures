"""Reproducible powered-flight and matched no-air experiments."""
from dataclasses import replace
import json
from pathlib import Path
import numpy as np
import mujoco
from gyro_sim import Config, Experiment, advance, sample, rotor_load

def flight_config(air=True, **changes):
    c = Config(mode="free", startup="powered", joint_type="collar",
               rotor_type="propeller", latch=False, tilt_control=True,
               ring_mass=2.5, rotor_mass=.03, rotor_radius=.12,
               ring_rpm=30, rotor_rpm=8600, alternating=True, duration=3)
    if not air:
        c = replace(c, thrust_coefficient=0., torque_coefficient=0.)
    return replace(c, **changes)

def measure(c):
    e = Experiment(c)
    m,d = e.model,e.data
    first = sample(m,d,c)
    impulse = np.zeros(3)
    mass = m.body_subtreemass[1]
    max_tilt = 0.
    for _ in range(round(c.duration/c.dt)):
        mujoco.mj_forward(m,d)
        force = sum((rotor_load(m,d,c,j)[1] for j in range(4)), np.zeros(3))
        force[2] -= mass*c.gravity
        impulse += force*c.dt
        advance(m,d,c)
    last = sample(m,d,c)
    residual = np.array([last["p_"+a]-first["p_"+a] for a in "xyz"])-impulse
    return dict(duration=c.duration, dt=c.dt, air=bool(c.thrust_coefficient),
                target_tilt_deg=c.target_tilt_deg, mass_kg=float(mass),
                com_rise_m=last["com_z"]-first["com_z"],
                vertical_speed_m_s=last["p_z"]/mass,
                thrust_N=last["thrust_up_N"], weight_N=last["weight_N"],
                motor_power_W=last["motor_power_W"],
                tilts_deg=[last[f"tilt{j}_deg"] for j in range(4)],
                momentum_residual_Ns=float(np.linalg.norm(residual)),
                warnings=int(sum(x.number for x in d.warning)))

if __name__ == "__main__":
    results = {name: measure(c) for name,c in {
        "tilted": flight_config(),
        "upright": flight_config(target_tilt_deg=0),
        "no_air": flight_config(False),
        "no_air_no_gravity": flight_config(False, gravity=0),
        "half_timestep": flight_config(dt=.0001),
    }.items()}
    Path("runs").mkdir(exist_ok=True)
    Path("runs/flight-results.json").write_text(json.dumps(results,indent=2))
    print(json.dumps(results,indent=2))
