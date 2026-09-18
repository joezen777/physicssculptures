# Gyroscopic ring laboratory

A Python/MuJoCo experiment based on the four-flywheel sketch. Each rotor spins around its stick; the stick tilts freely at a ball joint on a rotating annular carrier.

## Install and run (WSL2 Ubuntu)

Run these commands inside Ubuntu, from this repository. Keep the virtual environment on the Linux filesystem to avoid slow package installation in OneDrive:

```bash
python3 -m venv ~/.venvs/angularmomflyer
source ~/.venvs/angularmomflyer/bin/activate
python -m pip install -r requirements.txt
python gyro_sim.py --view
```

After installation, launch directly with `bash launch.sh` (or `bash launch.sh --mode free --gravity 0`).

The native MuJoCo viewer needs a working WSLg display. Drag to orbit the camera and scroll to zoom. The viewer opens paused. SPACE starts or pauses; R resets to a paused initial state. 1 selects stopped satellite rotors, 2 selects spinning rotors, and 3 selects alternating spin directions; each selection resets and pauses. Press SPACE after R or a preset selection. These reset presets are separate experiments, not physical changes of momentum during a run. Close the window to exit.

## Supported viewer startup

The supported viewer defaults to a staged, motor-driven startup:
1. At reset, everything is stopped and paused.
2. Press SPACE: small wheels ramp up over 2 seconds while temporary preparation fixtures hold the ring and sticks.
3. Small wheels hold their target for 0.5 seconds; the ring stays stationary.
4. Fixtures release, small-wheel motors switch off, and the ring's ground-mounted motor ramps toward 30 RPM over 2 seconds.
5. The ring motor continues regulating speed; the small wheels coast.

The viewer displays phase, time, ring RPM and wheel 1 RPM. RPM targets are servo commands, so actual speeds have small tracking errors. Spin-up fixtures supply reaction torque; their preparation forces must not be interpreted as lift. After release, joints are free as before. Rods retain the configured initial tilt (8 degrees by default).

Use --rotor-ramp, --rotor-hold and --ring-ramp to adjust timing. --startup coast explicitly restores the original already-spinning experiment. Free-flight viewing defaults to coast; a staged ground motor is rejected in free mode.

## Reproducible experiments

```bash
# Staged startup matching the default viewer.
python gyro_sim.py --startup staged --duration 6 --output runs/staged

# Original ground-supported coasting experiment: inspect support reaction and gyro tilt.
python gyro_sim.py --output runs/supported

# Unconstrained assembly without gravity: distinguish internal motion from thrust.
python gyro_sim.py --mode free --gravity 0 --output runs/free

# Free fall: whole-machine center of mass must follow a ballistic trajectory.
python gyro_sim.py --mode free --output runs/fall

# Controls and numerical checks.
python gyro_sim.py --rotor-rpm 0 --output runs/stopped
python gyro_sim.py --alternating --output runs/alternating
python -m unittest discover -s tests -v
python validate_convergence.py

# Produce comparison charts and an animated view of the supported model.
MUJOCO_GL=egl python make_demo.py
```

Each run saves its model XML, trajectory CSV, configuration and numerical summary JSON, and measurement plot in its output directory. Generated output is ignored by Git. The demo also saves a validation report. Use --help for all parameters.

Defaults are illustrative, not a fabrication specification: 0.4 m carrier radius, 2 kg carrier, four 0.25 m rods of 0.08 kg each, and four 0.09 m-radius rotors of 0.35 kg each. Initial ring speed is 30 RPM and rotor speed relative to its rod is 1200 RPM. The initial 8-degree outward rod tilt makes the behavior easier to observe; use --tilt-deg 0 for upright rods.

## What this model does and does not establish

- Headless runs default to initial spin followed by coasting, with no active motors. The supported viewer defaults to staged startup as described above; motor-driven energy changes are not conservation errors.
- Rigid bodies with explicit idealized inertia tensors; ring inertia is a uniform annulus, rods and rotors are solid cylinders. Decorative geometry does not add mass.
- Supported mode pins the carrier center and axis to a frictionless vertical bearing; the bearing supplies external forces and may supply transverse torques. Its vertical reaction is not free-flight thrust.
- Free mode releases the entire carrier with its attached rotors in all six directions; it has no ground-mounted hub or drive. Initial total linear momentum is zero.
- Released ball joints and rotor bearings have no friction, stops, springs or damping. Temporary preparation fixtures are active only during staged spin-up.
- No collisions or aerodynamics. Parts can pass through each other and the reference floor; free fall continues through it. The floor is only a visual reference.
- A deliberately simplified carrier is used. Staged startup has an external ground drive and temporary fixtures, not a self-contained propulsion system. A finite-mass onboard hub/drive remains a future addition.
- RK4 with a 0.2 ms default time step is checked against smaller time steps. Higher RPM and different geometry require renewed convergence checks.
- Total center-of-mass motion is the lift criterion. Ring height alone can change as satellite masses move. At uniform gravity and with no other external forces, the whole machine falls with acceleration g.
- Rotors may look slow or reverse visually because rendering samples much slower than their spin; physics integration uses the smaller time step.

See [experiment rationale](docs/gyroscopic-ring-experiment.md) and [implementation notes](docs/simulation.md). This is a simulation prototype, not a high-speed rotor design approved for printing.

Recorded results: [validation report](docs/validation.md).
