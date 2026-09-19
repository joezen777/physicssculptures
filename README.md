# Flywheel Lab

Local Python/MuJoCo physics with a React/MUI control panel and a Three.js 3D view. Choose radial collars or upper-hemisphere ball joints, solid flywheels or propellers, two shared speed targets, and a spring-loaded centrifugal release pin at each mount.

## Open the dashboard

Inside WSL2 Ubuntu, from this repository:

```bash
bash launch_lab.sh
```

Open http://localhost:8766 in your browser. The simulation starts paused.

1. Choose the joint and small rotor type.
2. Set **All four small rotors** and **Donut** speeds.
3. Click **Apply changes & reset**, then **Start**.
4. Inspect the lock count, pin retraction and tilt plots. Drag the model to orbit; scroll to zoom.
5. **Pause** preserves state. **Reset** returns to rest and re-engages every lock.

Changes in the panel are draft settings until applied. Reset in the run bar resets the current experiment; the Apply button applies draft settings and resets. Supported startup spins the small rotors first, then starts the donut. The latch releases only when its pin actually withdraws, not when a timer expires.

The default latch estimates a 38.7 RPM release speed. Try a 20 RPM donut target to keep it locked, then 60 RPM to release it. Increase spring preload or stiffness to raise the release speed. Values are illustrative, not spring or rotor fabrication specifications.

## Install/build

Keep Python dependencies on the Linux filesystem to avoid slow package operations in OneDrive. Use Node 24 (available under the user's WSL nvm installation) for the frontend.

```bash
python3 -m venv ~/.venvs/angularmomflyer
source ~/.venvs/angularmomflyer/bin/activate
python -m pip install -r requirements.txt
cd web
npm ci
npm run build
cd ..
bash launch_lab.sh
```

The server binds only to 127.0.0.1:8766. It serves the built frontend and simulation API; no cloud service or credentials are used. Node is needed to build, not to run the dashboard. The existing native viewer remains available through `bash launch.sh`, but configuration sliders and model selection are in the browser dashboard.

## Models

- **Collar:** tangent hinge axle; inward/outward tilt only, with +/-90-degree stops.
- **Ball:** tilt over the upper hemisphere, with unrestricted axial twist. Pedestals provide enough vertical clearance that the rotor does not hang below the donut top at horizontal tilt. Stops are compliant numerically.
- **Cross braces:** offset 45 degrees from mounts, below the ring.
- **Latch:** a real simulated slider mass, inward spring preload and stiffness, damping and travel stops. Each latch holds its stick upright until its own pin reaches the release travel. It stays released until reset.
- **Flywheel preset:** 90 mm rotor radius, 350 g each, 1200 RPM.
- **Propeller preset:** 120 mm radius, 30 g each, 8000 RPM, alternating spin and handedness. Downward airflow produces external thrust along the current rotor axis.
- **Propeller coefficients:** adjustable Ct and Cq in Environment & model. They are illustrative static-air coefficients, not measured propeller performance. Arrows indicate airflow direction, not a simulated wake.
- **Supported mode:** the ground bearing fixes donut position and axis. Its reactions cannot be interpreted as free-flight lift.
- **Free flight:** starts pre-spun and coasts with zero initial whole-machine linear momentum. No ground drive; the grid has no collisions. Gravity is optional.

Small speed targets and the main RPM readout refer to rotor speed relative to its housing. Ball-mounted housings can counter-rotate after unlocking; this can reduce inertial propeller spin and thrust. Aerodynamics uses actual inertial rotor spin. Solid flywheels have no aerodynamic thrust in this model.

Ring/rod/rotor collision geometry is enabled. Bearing housings and pins use ideal constraints rather than detailed contact; pin shear, jamming and re-engagement mechanics are not modeled. This is a physics prototype, not printable CAD.

## Headless experiments and checks

Activate the Python environment first:

```bash
python gyro_sim.py --startup staged --duration 7 --output runs/collar
python gyro_sim.py --joint-type ball --startup staged --duration 7 --output runs/ball
python gyro_sim.py --rotor-type propeller --rotor-radius .12 --rotor-mass .03 --rotor-rpm 8000 --alternating --startup staged --duration 7 --output runs/propeller
python gyro_sim.py --mode free --gravity 0 --output runs/free
python -m unittest discover -s tests -v
```

Each run saves XML, CSV, configuration/diagnostics JSON and a plot. Generated output is under runs/ and ignored by Git. Use --help for timing, dimensions, masses and spring parameters. Boolean options support --no-latch, --no-collisions and --no-joint-limits for controlled idealizations.

The conservation tests explicitly disable latches, contact, stops and aerodynamic loads. Powered, colliding or aerodynamic cases must not be judged against the old unforced energy/ballistic assumptions.

See [mechanical and scientific details](docs/mechanisms.md), [dashboard architecture](docs/dashboard.md) and [validation history](docs/validation.md). Earlier demo scripts and reports predate the new mechanism defaults; their exact historical numbers are not results for the current collar model.

## Powered lift experiment

In the dashboard, select **Load powered flight**, then **Start**. The preset uses
four powered propellers, a freely moving ring and internal collar tilt servos.
Use **Compare: air forces off** to run the same mechanism without aerodynamic forces.
Both presets start pre-spun and paused; reset restores that initial condition.
Adjust the collar target and rotor speeds, then apply changes and start again.

At three seconds the tilted propeller model rises 4.58 m; the no-air control
falls ballistically. See [powered-flight measurements and assumptions](docs/powered-flight.md).
Angular momentum changes orientation; air provides the external force.

## Supported gyroscope steering

Choose **Load supported gyro steering**, then Start. Adjust **Lean toward X/Y**
and press **Steer now · keep running** to steer without resetting.
The four powered collars redirect flywheel angular momentum; a balanced
spherical bearing supports the full weight. The default demonstration uses
a 3 RPM donut and alternating 3000 RPM flywheels.
See [design and controller limits](docs/supported-steering.md).
