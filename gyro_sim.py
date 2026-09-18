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
    rotor_ramp: float = 2.0
    rotor_hold: float = 0.5
    ring_ramp: float = 2.0
    gravity: float = 9.81
    ring_rpm: float = 30.0
    rotor_rpm: float = 1200.0
    tilt_deg: float = 8.0
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
                    "rotor_radius", "rotor_mass", "dt", "duration", "rotor_ramp", "ring_ramp"):
            if getattr(self, key) <= 0:
                raise ValueError(f"{key} must be positive")
        if self.startup not in ("coast", "staged") or self.rotor_hold < 0:
            raise ValueError("Invalid startup mode or hold duration")
        if self.startup == "staged" and self.mode != "supported":
            raise ValueError("Staged startup uses a ground-mounted motor; use --startup coast for free flight")
        if self.duration < self.dt:
            raise ValueError("duration must be at least one timestep")
        if self.mode not in ("free", "supported") or self.gravity < 0:
            raise ValueError("Invalid mode or negative gravity")
        if abs(self.tilt_deg) > 80:
            raise ValueError("Initial tilt must be between -80 and 80 degrees")


def element(parent, tag, **attrs):
    return ET.SubElement(parent, tag, {k: str(v) for k, v in attrs.items()})


def make_model(c):
    c.validate()
    root = ET.Element("mujoco", model="Gyroscopic ring laboratory")
    element(root, "compiler", angle="radian")
    option = element(root, "option", timestep=c.dt, gravity=f"0 0 {-c.gravity}",
                     integrator="RK4")
    element(option, "flag", energy="enable")
    defaults = element(root, "default")
    element(defaults, "geom", contype="0", conaffinity="0", rgba=".2 .65 .75 1")
    element(defaults, "joint", damping="0", armature="0")
    visual = element(root, "visual")
    element(visual, "global", offwidth="960", offheight="720")
    world = element(root, "worldbody")
    element(world, "light", pos="0 -2 4", dir="0 .3 -1")
    # Reference grid is visual only: no ground collisions in this experiment.
    element(world, "geom", type="plane", size="4 4 .1", rgba=".12 .15 .2 1")
    ring = element(world, "body", name="ring", pos="0 0 1")
    if c.mode == "free":
        element(ring, "freejoint", name="base")
    else:
        element(ring, "joint", name="base", type="hinge", axis="0 0 1")
        element(world, "geom", type="cylinder", pos="0 0 .5", size=".035 .5",
                rgba=".45 .5 .6 1")
    # Uniform annulus, with rectangular radial/vertical cross section.
    ri, ro, height = .84*c.radius, 1.10*c.radius, .035
    iz = .5*c.ring_mass*(ri*ri + ro*ro)
    ix = c.ring_mass*(3*(ri*ri + ro*ro) + height*height)/12
    element(ring, "inertial", pos="0 0 0", mass=c.ring_mass,
            diaginertia=f"{ix} {ix} {iz}")
    for j in range(64):
        a, b = 2*math.pi*j/64, 2*math.pi*(j+1)/64
        element(ring, "geom", type="capsule",
                fromto=f"{c.radius*math.cos(a)} {c.radius*math.sin(a)} 0 "
                       f"{c.radius*math.cos(b)} {c.radius*math.sin(b)} 0",
                size=".022", rgba=".16 .6 .7 1")
    element(ring, "site", name="support", size=".015")
    colors = [".98 .65 .2 1", ".4 .75 1 1", ".98 .4 .4 1", ".65 .5 1 1"]
    for j in range(4):
        a = j*math.pi/2
        x, y = c.radius*math.cos(a), c.radius*math.sin(a)
        element(ring, "geom", type="capsule", fromto=f"0 0 0 {x} {y} 0",
                size=".009", rgba=".3 .4 .45 1")
        rod = element(ring, "body", name=f"rod{j}", pos=f"{x} {y} 0")
        element(rod, "joint", name=f"ball{j}", type="ball")
        length, radius = c.rod_length, .008
        rod_ix = c.rod_mass*(3*radius*radius + length*length)/12
        rod_iz = .5*c.rod_mass*radius*radius
        element(rod, "inertial", pos=f"0 0 {length/2}", mass=c.rod_mass,
                diaginertia=f"{rod_ix} {rod_ix} {rod_iz}")
        element(rod, "geom", type="sphere", size=".025", rgba=".85 .88 .92 1")
        element(rod, "geom", type="capsule", fromto=f"0 0 0 0 0 {length}",
                size=radius, rgba=".85 .88 .92 1")
        rotor = element(rod, "body", name=f"rotor{j}", pos=f"0 0 {length}")
        element(rotor, "joint", name=f"spin{j}", type="hinge", axis="0 0 1")
        thickness = .018
        iz = .5*c.rotor_mass*c.rotor_radius**2
        ix = c.rotor_mass*(3*c.rotor_radius**2 + thickness**2)/12
        element(rotor, "inertial", pos="0 0 0", mass=c.rotor_mass,
                diaginertia=f"{ix} {ix} {iz}")
        element(rotor, "geom", type="cylinder", size=f"{c.rotor_radius} {thickness/2}",
                rgba=colors[j])
        element(rotor, "geom", type="box", pos=f"{c.rotor_radius/2} 0 .011",
                size=f"{c.rotor_radius/2} .006 .002", rgba=".12 .14 .19 1")
    if c.startup == "staged":
        # Temporary preparation fixtures carry reaction torque during spin-up.
        equalities = element(root, "equality")
        element(equalities, "joint", name="ring_hold", joint1="base",
                polycoef="0 0 0 0 0", solref=".002 1")
        theta = math.radians(c.tilt_deg)
        for j in range(4):
            a = j*math.pi/2
            quat = (math.cos(theta/2), -math.sin(a)*math.sin(theta/2),
                    math.cos(a)*math.sin(theta/2), 0)
            pose = (c.radius*math.cos(a), c.radius*math.sin(a), 0, *quat)
            element(equalities, "weld", name=f"rod_hold{j}", body1="ring",
                    body2=f"rod{j}", relpose=" ".join(map(str, pose)),
                    solref=".002 1")
        actuators = element(root, "actuator")
        element(actuators, "motor", name="ring_motor", joint="base",
                ctrllimited="true", ctrlrange="-20 20")
        for j in range(4):
            element(actuators, "motor", name=f"rotor_motor{j}", joint=f"spin{j}",
                    ctrllimited="true", ctrlrange="-1 1")
    if c.mode == "supported":
        sensors = element(root, "sensor")
        element(sensors, "force", name="support_force", site="support")
    xml = ET.tostring(root, encoding="unicode")
    model = mujoco.MjModel.from_xml_string(xml)
    return model, xml


def initial_data(model, c):
    d = mujoco.MjData(model)
    rate = c.ring_rpm*2*math.pi/60 if c.startup == "coast" else 0
    if c.mode == "free":
        d.joint("base").qvel[5] = rate
    else:
        d.joint("base").qvel[0] = rate
    for j in range(4):
        a = j*math.pi/2
        theta = math.radians(c.tilt_deg)
        # Radially outward tilt; quaternion in the ring's frame.
        d.joint(f"ball{j}").qpos[:] = [
            math.cos(theta/2), -math.sin(a)*math.sin(theta/2),
            math.cos(a)*math.sin(theta/2), 0]
        sign = -1 if c.alternating and j % 2 else 1
        d.joint(f"spin{j}").qvel[0] = sign*c.rotor_rpm*2*math.pi/60 if c.startup == "coast" else 0
    mujoco.mj_forward(model, d)
    mujoco.mj_subtreeVel(model, d)
    if c.mode == "free":
        # Remove initial whole-machine linear momentum, retaining the rotation.
        d.joint("base").qvel[:3] -= d.subtree_linvel[1]
        mujoco.mj_forward(model, d)
    return d



def startup_phase(c, t):
    if c.startup == "coast":
        return "COASTING - preset initial speeds"
    if t < c.rotor_ramp:
        return "1 / SMALL WHEELS SPINNING UP - ring and sticks held"
    if t < c.rotor_ramp + c.rotor_hold:
        return "2 / SMALL WHEELS READY - ring still held"
    if t < c.rotor_ramp + c.rotor_hold + c.ring_ramp:
        return "3 / RING ACCELERATING - ball joints released"
    return "4 / RING AT TARGET - small wheels coasting"


def drive(model, d, c):
    if c.startup != "staged":
        return
    release = c.rotor_ramp + c.rotor_hold
    held = d.time < release
    d.eq_active[:] = held
    d.ctrl[:] = 0
    if held:
        u = min(1., d.time/c.rotor_ramp)
        target = c.rotor_rpm*2*math.pi/60*(u*u*(3-2*u))
        for j in range(4):
            sign = -1 if c.alternating and j % 2 else 1
            error = sign*target - d.joint(f"spin{j}").qvel[0]
            d.actuator(f"rotor_motor{j}").ctrl[0] = np.clip(.15*error, -1, 1)
    else:
        u = min(1., max(0., (d.time-release)/c.ring_ramp))
        target = c.ring_rpm*2*math.pi/60*(u*u*(3-2*u))
        error = target-d.joint("base").qvel[0]
        d.actuator("ring_motor").ctrl[0] = np.clip(10*error, -20, 20)


def advance(model, d, c):
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
        zaxis = d.body(f"rod{j}").xmat.reshape(3, 3)[:, 2]
        result[f"tilt{j}_deg"] = float(np.degrees(np.arccos(np.clip(zaxis[2], -1, 1))))
    if c.mode == "supported":
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
                                 / max(abs(first["energy"]), 1e-12)) if c.startup == "coast" else None,
        "max_ballistic_com_error_m": max_com_error if c.mode == "free" else None,
        "max_linear_momentum_error_kg_m_s": max_p_error if c.mode == "free" else None,
        "max_angular_momentum_error_kg_m2_s": max_h_error if c.mode == "free" else None,
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
    if c.mode == "free":
        axes[0].plot(t, -.5*c.gravity*t*t, "--", label="Ballistic prediction")
    axes[0].set_ylabel("Height change (m)")
    axes[0].legend()
    for j in range(4):
        axes[1].plot(t, [r[f"tilt{j}_deg"] for r in rows], label=f"Rotor {j+1}")
    axes[1].set_ylabel("Axle tilt from vertical (deg)")
    axes[1].legend(ncol=4)
    if c.mode == "supported":
        axes[2].plot(t, [r["support_up_N"] for r in rows], label="Support force on assembly")
        axes[2].axhline((c.ring_mass+4*(c.rod_mass+c.rotor_mass))*c.gravity,
                       ls="--", color="gray", label="Weight")
        axes[2].set_ylabel("Upward force (N)")
        axes[2].legend()
    else:
        axes[2].plot(t, [r["energy"]-rows[0]["energy"] for r in rows])
        axes[2].set_ylabel("Energy drift (J)")
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
            p.add_argument(flag, action="store_true")
        elif field.name == "startup":
            p.add_argument(flag, choices=["coast", "staged"], default=None)
        elif field.name == "mode":
            p.add_argument(flag, choices=["supported", "free"], default=field.default)
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
