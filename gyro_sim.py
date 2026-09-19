"""Four satellite gyroscopes on a rotating carrier; SI units throughout."""
from dataclasses import dataclass, asdict, replace
from pathlib import Path
import argparse
import csv
import json
import math
import time
import xml.etree.ElementTree as ET

import mujoco
import numpy as np


@dataclass
class Config:
    mode: str = "supported"
    startup: str = "coast"
    joint_type: str = "collar"
    rotor_type: str = "flywheel"
    joint_limits: bool = True
    collisions: bool = True
    latch: bool = True
    pin_mass: float = .015
    spring_preload: float = .06
    spring_k: float = 12.
    pin_travel: float = .004
    air_density: float = 1.225
    thrust_coefficient: float = .10
    torque_coefficient: float = .01
    steering: bool = False
    steer_x_deg: float = 8.
    steer_y_deg: float = 0.
    tilt_control: bool = False
    target_tilt_deg: float = 20.
    rotor_ramp: float = 2.0
    rotor_hold: float = 0.5
    ring_ramp: float = 2.0
    gravity: float = 9.81
    ring_rpm: float = 60.0
    rotor_rpm: float = 1200.0
    tilt_deg: float = 0.0
    radius: float = 0.4
    ring_mass: float = 2.0
    rod_length: float = 0.25
    rod_mass: float = 0.08
    rotor_radius: float = 0.09
    rotor_mass: float = 0.35
    alternating: bool = False
    dt: float = 0.0002
    duration: float = 3.0

    def validate(self):
        for key, value in asdict(self).items():
            if isinstance(value, (int, float)) and not math.isfinite(value):
                raise ValueError(f"{key} must be finite")
        for key in ("radius", "ring_mass", "rod_length", "rod_mass",
                    "rotor_radius", "rotor_mass", "dt", "duration", "rotor_ramp", "ring_ramp", "pin_mass", "spring_k", "pin_travel", "air_density"):
            if getattr(self, key) <= 0:
                raise ValueError(f"{key} must be positive")
        if self.joint_type not in ("collar", "ball") or self.rotor_type not in ("flywheel", "propeller"):
            raise ValueError("Invalid joint or rotor type")
        if min(self.spring_preload, self.thrust_coefficient, self.torque_coefficient) < 0:
            raise ValueError("Spring preload and aerodynamic coefficients must be nonnegative")
        if abs(self.ring_rpm) > 240 or abs(self.rotor_rpm) > 20000:
            raise ValueError("Speed outside supported experiment range")
        if self.startup not in ("coast", "staged", "powered") or self.rotor_hold < 0:
            raise ValueError("Invalid startup mode or hold duration")
        if self.startup == "staged" and self.mode != "supported":
            raise ValueError("Staged startup uses a ground-mounted motor; use --startup coast for free flight")
        if self.startup == "powered" and (self.mode != "free" or self.joint_type != "collar"):
            raise ValueError("Powered flight requires free mode and collar joints")
        if self.tilt_control and (self.startup != "powered" or self.latch):
            raise ValueError("Tilt control requires powered flight with pins disabled")
        if abs(self.target_tilt_deg) > 70:
            raise ValueError("Target tilt must be between -70 and 70 degrees")
        if self.duration < self.dt:
            raise ValueError("duration must be at least one timestep")
        if self.mode not in ("free", "supported", "pivot") or self.gravity < 0:
            raise ValueError("Invalid mode or negative gravity")
        if self.steering and (self.mode != "pivot" or self.joint_type != "collar" or self.rotor_type != "flywheel" or self.latch or self.startup != "coast"):
            raise ValueError("Steering needs pivot support, solid flywheels, collars, coast startup and no pins")
        if max(abs(self.steer_x_deg), abs(self.steer_y_deg)) > 15:
            raise ValueError("Steering target must be within 15 degrees per axis")
        if abs(self.tilt_deg) > 80:
            raise ValueError("Initial tilt must be between -80 and 80 degrees")


from mechanics import make_model, release_rpm, mount_height


def initial_data(model, c):
    d = mujoco.MjData(model)
    rate = c.ring_rpm*2*math.pi/60 if c.startup in ("coast", "powered") else 0
    if c.mode == "free":
        d.joint("base").qvel[5] = rate
    elif c.mode == "pivot":
        d.joint("base").qvel[2] = rate
    else:
        d.joint("base").qvel[0] = rate
    for j in range(4):
        a = j*math.pi/2
        theta = 0 if c.latch else math.radians(c.tilt_deg)
        if c.joint_type == "ball":
            d.joint(f"ball{j}").qpos[:] = [
                math.cos(theta/2), -math.sin(a)*math.sin(theta/2),
                math.cos(a)*math.sin(theta/2), 0]
        else:
            d.joint(f"tilt{j}").qpos[0] = theta
        sign = -1 if c.alternating and j % 2 else 1
        d.joint(f"spin{j}").qvel[0] = sign*c.rotor_rpm*2*math.pi/60 if c.startup in ("coast", "powered") else 0
    mujoco.mj_forward(model, d)
    mujoco.mj_subtreeVel(model, d)
    if c.mode == "free":
        # Remove initial whole-machine linear momentum, retaining the rotation.
        d.joint("base").qvel[:3] -= d.subtree_linvel[1]
        mujoco.mj_forward(model, d)
    return d



def startup_phase(c, t):
    if c.mode == "pivot":
        return "SUPPORTED STEERING - bearing carries weight; internal collar torques tilt the ring"
    if c.startup == "powered":
        return "POWERED FREE FLIGHT - internal motors; air supplies thrust"
    if c.startup == "coast":
        return "COASTING - preset initial speeds"
    if t < c.rotor_ramp:
        return "1 / SMALL WHEELS SPINNING UP - ring and sticks held"
    if t < c.rotor_ramp + c.rotor_hold:
        return "2 / SMALL WHEELS READY - ring still held"
    if t < c.rotor_ramp + c.rotor_hold + c.ring_ramp:
        return "3 / RING ACCELERATING - pins release only at sufficient speed"
    return "4 / SPEED CONTROL - inspect latch and tilt"


def rotor_load(model, d, c, j):
    body = model.body(f"rotor{j}").id
    axis = d.xmat[body].reshape(3,3)[:,2]
    velocity = np.zeros(6)
    mujoco.mj_objectVelocity(model, d, mujoco.mjtObj.mjOBJ_BODY, body, velocity, 0)
    n = float(np.dot(velocity[:3], axis)/(2*math.pi))
    pitch = -1 if c.alternating and j % 2 else 1
    diameter = 2*c.rotor_radius
    thrust = pitch*c.thrust_coefficient*c.air_density*n*abs(n)*diameter**4
    drag = -c.torque_coefficient*c.air_density*n*abs(n)*diameter**5
    return body, axis*thrust, axis*drag


def drive(model, d, c):
    release_time = c.rotor_ramp+c.rotor_hold
    # A released pin does not magically re-engage with a moving collar.
    if c.latch:
        for j in range(4):
            eq = model.equality(f"rod_hold{j}").id
            if d.joint(f"pin_slide{j}").qpos[0] >= c.pin_travel:
                d.eq_active[eq] = False
    if c.startup == "staged":
        held = d.time < release_time
        d.eq_active[model.equality("ring_hold").id] = held
        if not c.latch:
            for j in range(4):
                d.eq_active[model.equality(f"rod_hold{j}").id] = held
        d.ctrl[:] = 0
        u = min(1., d.time/c.rotor_ramp)
        target = c.rotor_rpm*2*math.pi/60*(u*u*(3-2*u))
        for j in range(4):
            sign = -1 if c.alternating and j % 2 else 1
            error = sign*target-d.joint(f"spin{j}").qvel[0]
            # Internal motor torques act equally and oppositely on rotor and housing.
            gain = .15
            eq = model.equality(f"rod_hold{j}").id
            if c.joint_type == "ball" and not d.eq_active[eq]:
                # A free ball-mounted housing has very little axial inertia.
                # Bound discrete servo gain to avoid numerically exciting its counterspin.
                housing_iz = .5*c.rod_mass*.008**2
                gain = min(gain, .5*housing_iz/c.dt)
            d.actuator(f"rotor_motor{j}").ctrl[0] = np.clip(gain*error, -1, 1)
        if not held:
            u = min(1., max(0., (d.time-release_time)/c.ring_ramp))
            target = c.ring_rpm*2*math.pi/60*(u*u*(3-2*u))
            error = target-d.joint("base").qvel[0]
            d.actuator("ring_motor").ctrl[0] = np.clip(10*error, -20, 20)
    if c.startup == "powered":
        for j in range(4):
            sign = -1 if c.alternating and j % 2 else 1
            error = sign*c.rotor_rpm*2*math.pi/60-d.joint(f"spin{j}").qvel[0]
            d.actuator(f"rotor_motor{j}").ctrl[0] = np.clip(.15*error, -1, 1)
            if c.tilt_control:
                u = min(1., d.time)
                target = math.radians(c.tilt_deg+(c.target_tilt_deg-c.tilt_deg)*u*u*(3-2*u))
                q = d.joint(f"tilt{j}")
                d.actuator(f"tilt_motor{j}").ctrl[0] = np.clip(4*(target-q.qpos[0])-.3*q.qvel[0], -2, 2)
    if c.steering:
        from steering import control
        control(model, d, c)
    if c.rotor_type == "propeller":
        # Aerodynamics is an external interaction with air, not gyroscopic lift.
        for j in range(4):
            body, force, torque = rotor_load(model, d, c, j)
            d.xfrc_applied[body,:3] = force
            d.xfrc_applied[body,3:] = torque


def advance(model, d, c):
    if c.rotor_type == "propeller" or c.steering:
        mujoco.mj_forward(model, d)
    drive(model, d, c)
    mujoco.mj_step(model, d)


class Experiment:
    """State shared by the native viewer and keyboard regression tests."""
    def __init__(self, config):
        self.c = replace(config)
        self.model, _ = make_model(self.c)
        self.data = initial_data(self.model, self.c)
        self.original_rpm = self.c.rotor_rpm
        self.paused = True

    def handle_key(self, key):
        if key == 32:
            self.paused = not self.paused
        elif key in (82, 49, 50, 51):
            if key != 82:
                self.c.rotor_rpm = 0 if key == 49 else self.original_rpm
                self.c.alternating = key == 51
            mujoco.mj_copyData(self.data, self.model, initial_data(self.model, self.c))
            self.paused = True

    def tick(self, seconds=1/60):
        if not self.paused:
            for _ in range(max(1, round(seconds/self.c.dt))):
                advance(self.model, self.data, self.c)


def sample(model, d, c):
    # mj_step leaves some derived fields at an intermediate state; refresh them.
    mujoco.mj_forward(model, d)
    mujoco.mj_subtreeVel(model, d)
    mass = float(model.body_subtreemass[1])
    com = d.subtree_com[1]
    momentum = mass*d.subtree_linvel[1]
    result = {"time": float(d.time), "ring_z": float(d.body("ring").xpos[2]),
              "com_x": float(com[0]), "com_y": float(com[1]), "com_z": float(com[2]),
              "energy": float(sum(d.energy)),
              "ring_rpm": float(d.joint("base").qvel[-1]*60/(2*math.pi)),
              "phase": startup_phase(c, d.time)}
    for axis, p, h in zip("xyz", momentum, d.subtree_angmom[1]):
        result[f"p_{axis}"] = float(p)
        result[f"h_{axis}"] = float(h)
    for j in range(4):
        result[f"rotor{j}_rpm"] = float(d.joint(f"spin{j}").qvel[0]*60/(2*math.pi))
        velocity = np.zeros(6)
        body_id = model.body(f"rotor{j}").id
        mujoco.mj_objectVelocity(model,d,mujoco.mjtObj.mjOBJ_BODY,body_id,velocity,0)
        axis = d.body(f"rotor{j}").xmat.reshape(3,3)[:,2]
        result[f"rotor{j}_inertial_rpm"] = float(np.dot(velocity[:3],axis)*60/(2*math.pi))
        zaxis = d.body(f"rod{j}").xmat.reshape(3, 3)[:, 2]
        ring_up = d.body("ring").xmat.reshape(3,3)[:,2]
        result[f"tilt{j}_deg"] = float(np.degrees(np.arccos(np.clip(np.dot(zaxis,ring_up), -1, 1))))
        result[f"pin{j}_mm"] = float(d.joint(f"pin_slide{j}").qpos[0]*1000) if c.latch else 0.
        result[f"locked{j}"] = bool(d.eq_active[model.equality(f"rod_hold{j}").id]) if (c.latch or c.startup == "staged") else False
    result["thrust_up_N"] = sum(rotor_load(model,d,c,j)[1][2] for j in range(4)) if c.rotor_type == "propeller" else 0.
    result["weight_N"] = mass*c.gravity
    result["motor_power_W"] = float(np.dot(d.actuator_force, d.actuator_velocity))
    result["release_rpm_estimate"] = release_rpm(c) if c.latch else 0.
    if c.mode == "pivot":
        normal = d.body("ring").xmat.reshape(3,3)[:,2]
        result["steer_x_deg"] = float(np.degrees(np.arctan2(normal[0], normal[2])))
        result["steer_y_deg"] = float(np.degrees(np.arctan2(normal[1], normal[2])))
        result["target_x_deg"] = c.steer_x_deg
        result["target_y_deg"] = c.steer_y_deg
    if c.mode in ("supported", "pivot"):
        # Parent-to-child force on the assembly, expressed in the sensor frame.
        force_local = d.sensor("support_force").data
        force_world = (d.site("support").xmat.reshape(3, 3) @ force_local)
        result["support_up_N"] = float(force_world[2])
    return result


def simulate(c, output=None, frame_callback=None):
    model, xml = make_model(c)
    d = initial_data(model, c)
    rows = [sample(model, d, c)]
    if frame_callback:
        frame_callback(model, d)
    stride = max(1, round(.01/c.dt))
    steps = round(c.duration/c.dt)
    for step in range(1, steps+1):
        advance(model, d, c)
        if step % stride == 0 or step == steps:
            rows.append(sample(model, d, c))
            if frame_callback and step % (stride*4) == 0:
                frame_callback(model, d)
    if any(w.number for w in d.warning):
        raise RuntimeError("MuJoCo reported numerical warnings; reduce timestep/speeds")
    first = rows[0]
    com0 = np.array([first[f"com_{a}"] for a in "xyz"])
    p0 = np.array([first[f"p_{a}"] for a in "xyz"])
    h0 = np.array([first[f"h_{a}"] for a in "xyz"])
    mass = float(model.body_subtreemass[1])
    max_com_error = max_p_error = max_h_error = 0.
    for row in rows:
        t = row["time"]
        expected_com = com0 + p0/mass*t + np.array([0, 0, -.5*c.gravity*t*t])
        expected_p = p0 + np.array([0, 0, -mass*c.gravity*t])
        max_com_error = max(max_com_error, float(np.linalg.norm(
            np.array([row[f"com_{a}"] for a in "xyz"]) - expected_com)))
        max_p_error = max(max_p_error, float(np.linalg.norm(
            np.array([row[f"p_{a}"] for a in "xyz"]) - expected_p)))
        max_h_error = max(max_h_error, float(np.linalg.norm(
            np.array([row[f"h_{a}"] for a in "xyz"]) - h0)))
    summary = {
        "config": asdict(c), "mujoco_version": mujoco.__version__, "total_mass_kg": mass,
        "energy_change_J": rows[-1]["energy"]-first["energy"],
        "relative_energy_drift": (max(abs(r["energy"]-first["energy"]) for r in rows)
                                 / max(abs(first["energy"]), 1e-12)) if c.startup == "coast" and not c.collisions and not c.joint_limits and c.rotor_type == "flywheel" and not c.latch else None,
        "max_ballistic_com_error_m": max_com_error if c.mode == "free" and c.rotor_type == "flywheel" else None,
        "max_linear_momentum_error_kg_m_s": max_p_error if c.mode == "free" and c.rotor_type == "flywheel" else None,
        "max_angular_momentum_error_kg_m2_s": max_h_error if c.mode == "free" and c.rotor_type == "flywheel" else None,
        "ring_height_change_m": rows[-1]["ring_z"]-first["ring_z"],
        "com_height_change_m": rows[-1]["com_z"]-first["com_z"],
        "numerical_warnings": 0,
    }
    if output:
        output = Path(output)
        output.mkdir(parents=True, exist_ok=True)
        (output/"model.xml").write_text(xml)
        (output/"summary.json").write_text(json.dumps(summary, indent=2))
        with (output/"trajectory.csv").open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        plot(rows, c, output/"measurements.png")
    return rows, summary


def plot(rows, c, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    t = np.array([r["time"] for r in rows])
    fig, axes = plt.subplots(3, 1, figsize=(9, 9), constrained_layout=True)
    for key, label in (("ring_z", "Ring"), ("com_z", "Whole-machine center of mass")):
        axes[0].plot(t, [r[key]-rows[0][key] for r in rows], label=label)
    if c.mode == "free" and c.rotor_type == "flywheel":
        axes[0].plot(t, -.5*c.gravity*t*t, "--", label="Ballistic prediction")
    axes[0].set_ylabel("Height change (m)")
    axes[0].legend()
    for j in range(4):
        axes[1].plot(t, [r[f"tilt{j}_deg"] for r in rows], label=f"Rotor {j+1}")
    axes[1].set_ylabel("Axle tilt from vertical (deg)")
    axes[1].legend(ncol=4)
    if c.mode == "supported":
        axes[2].plot(t, [r["support_up_N"] for r in rows], label="Support force on assembly")
        axes[2].axhline((c.ring_mass+4*(c.rod_mass+c.rotor_mass+(c.pin_mass if c.latch else 0)))*c.gravity,
                       ls="--", color="gray", label="Weight")
        axes[2].set_ylabel("Upward force (N)")
        axes[2].legend()
    else:
        axes[2].plot(t, [r["energy"]-rows[0]["energy"] for r in rows])
        axes[2].set_ylabel("Energy change (J)")
    axes[2].set_xlabel("Simulation time (s)")
    for ax in axes:
        ax.grid(alpha=.2)
    fig.suptitle(f"{c.mode.title()} | ring {c.ring_rpm:g} RPM | rotors {c.rotor_rpm:g} RPM"
                 f" | gravity {c.gravity:g} m/s2")
    fig.savefig(path, dpi=140)
    plt.close(fig)


def view(c, max_wall_seconds=None):
    import mujoco.viewer
    from queue import SimpleQueue
    experiment = Experiment(c)
    c, model, d = experiment.c, experiment.model, experiment.data
    keys = SimpleQueue()
    print("SPACE start/pause; R reset and pause; 1 stopped rotors; 2 spinning; 3 alternating.")
    print("Presets reset the experiment. Close the window to exit.")
    with mujoco.viewer.launch_passive(model, d, key_callback=keys.put,
                                     show_left_ui=False, show_right_ui=False) as viewer:
        viewer.cam.distance = 2.6
        viewer.cam.azimuth = 125
        viewer.cam.elevation = -25
        viewer.cam.lookat[:] = [0, 0, 1.05]
        launched = time.monotonic()
        while viewer.is_running() and (max_wall_seconds is None or time.monotonic()-launched < max_wall_seconds):
            start = time.monotonic()
            with viewer.lock():
                while not keys.empty():
                    experiment.handle_key(keys.get())
                experiment.tick()
                mujoco.mj_forward(model, d)
                if c.mode == "free":
                    viewer.cam.lookat[:] = d.subtree_com[1]
            rpm = d.joint("base").qvel[-1]*60/(2*math.pi)
            rotor_rpm = d.joint("spin0").qvel[0]*60/(2*math.pi)
            viewer.set_texts((None, mujoco.mjtGridPos.mjGRID_TOPLEFT,
                ("PAUSED - SPACE to start/resume" if experiment.paused else startup_phase(c, d.time))
                + f"\nTime {d.time:.2f}s | ring {rpm:.1f} RPM | wheel 1 {rotor_rpm:.0f} RPM"
                + "\nR = reset and pause | SPACE = start/pause", None))
            viewer.sync()
            time.sleep(max(0, 1/60-(time.monotonic()-start)))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--view", action="store_true")
    p.add_argument("--output", default="runs/latest")
    p.add_argument("--view-seconds", type=float, help="Auto-close viewer after this many wall seconds")
    for field in Config.__dataclass_fields__.values():
        flag = "--"+field.name.replace("_", "-")
        if field.type is bool:
            p.add_argument(flag, action=argparse.BooleanOptionalAction, default=field.default)
        elif field.name == "startup":
            p.add_argument(flag, choices=["coast", "staged", "powered"], default=None)
        elif field.name == "mode":
            p.add_argument(flag, choices=["supported", "free", "pivot"], default=field.default)
        else:
            p.add_argument(flag, type=field.type, default=field.default)
    args = vars(p.parse_args())
    viewer, output = args.pop("view"), args.pop("output")
    view_seconds = args.pop("view_seconds")
    if view_seconds is not None and (not math.isfinite(view_seconds) or view_seconds <= 0):
        p.error("--view-seconds must be finite and positive")
    if args["startup"] is None:
        args["startup"] = "staged" if viewer and args["mode"] == "supported" else "coast"
    c = Config(**args)
    try:
        if viewer:
            view(c, view_seconds)
        else:
            _, summary = simulate(c, output)
            print(json.dumps(summary, indent=2))
    except ValueError as exc:
        p.error(str(exc))


if __name__ == "__main__":
    main()
