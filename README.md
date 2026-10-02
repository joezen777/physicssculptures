# Flywheel Lab

**Latest print files:** [1.2 mm PETG STL set](experiments/print_petg_12/output/stl) and [labeled exploded guide](experiments/print_petg_12/output/exploded_assembly_labeled.png).

**Resin sprue sheets:** [Photon Mono M5s / ABS-Like Pro 2 kit](experiments/print_petg_12/output/stl/resin_sprue_sheets) with raised 12-point part IDs. [Sheet index](experiments/print_petg_12/output/stl/resin_sprue_sheets/sprue_sheets_preview.png). Add final resin supports in the slicer.

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

## Falling cylinder / planetary gearbox experiment

A separate FreeCAD study explores a fin-driven shell, three symmetric 4:1 planetary
stages, and an independent reaction drum. Includes full and cutaway STEP exports,
a slowed animation, and conditional RPM / energy calculations. See
[the design and physics notes](docs/drop_gearbox.md).

The [magnetic variant study](docs/magnetic_gearbox.md) adds contactless concentric
magnet rotors, speed-ratio limits and a separate FreeCAD/STEP/animation set.

## Stackable cone tower draft

A separate standing tower study implements two-row staggered teeth on every gear,
split keyed ring inserts, 608 bearing seats, stationary carriers and hex stacking
couplings. See [the first-draft notes](docs/stacking_cone_tower.md).

## Bevel cone variant

See [the pointed cone / bevel gear draft](docs/bevel_cone_tower.md) for the separate FreeCAD experiment.

## Flowerpot bottom input

[Bottom drive and wooden blade concept](docs/flowerpot_bottom_input.md), retaining the two-stage multiplier.

## Active wind-input variant

[Roof-vent rotor with flowerpot multiplier](docs/roofvent_multiplier.md) is the earlier wind-input study.

## Four-level circular-sail tower

[Simple bottom sails, all-608 axles, and 2x stages](docs/simple_sail_tower.md) is the earlier four-level draft.

## Modular fan tunnel

[Full-wall pots with fan floors and a removable sail add-on](docs/modular_fan_tunnel.md) is the earlier concept revision; the printable PETG prototype is below.

## PETG prototype for a 1.2 mm nozzle

The current print set is in [experiments/print_petg_12/output/stl](experiments/print_petg_12/output/stl). Each filename includes its total print quantity. Print the two fit coupons first.

- [Labeled exploded assembly image](experiments/print_petg_12/output/exploded_assembly_labeled.png)
- [Print settings, supports and full assembly guide](experiments/print_petg_12/output/PRINT_AND_ASSEMBLE.md)
- [Printed-part quantities](experiments/print_petg_12/output/print_manifest.csv)
- [604 bearing / P04 axle detail](experiments/print_petg_12/output/planet_joint_labeled.png)
- [P16 cup / P15 arm detail](experiments/print_petg_12/output/cup_joint_labeled.png)
- [Purchased bearings, spacers and fasteners](experiments/print_petg_12/output/hardware_bom.csv)
- [FreeCAD assembly](experiments/print_petg_12/output/print_prototype.FCStd)
- [Complete print package ZIP](experiments/print_petg_12/print_package_PETG_1p2mm.zip)

Use this kit as a complete set; its coarser teeth, larger hex couplings and taller module spacing do not match the earlier draft. Physical PETG fit and airflow still need testing.

### Linear assembly order

1. Print and inspect the coupons, then all P01-P19 parts in their filename quantities. Clean support, nut slots and bearing seats. Sort A-pitch pots P02 for levels 1 and 3, B-pitch pot P03 for level 2, and B-pitch top fan P17.
2. Load three M3 nuts into the underside pockets of each pot hub and the top fan hub. Insert one 608 from above into each hub. Attach one P01 retainer to each with three M3 x16 screws. These are four of the eight P01 caps.
3. For each of the nine P07 planet gears, load three M2.5 nuts from below, insert one 604 from above, and fit P08 with three M2.5 x16 screws. The cap's small projecting collar goes into the bearing counterbore.
4. Prepare each of the three sun assemblies. Slide three M3 nuts into the radial slots of P06. Insert its upper 608 through the open bottom face.
5. Load three M3 nuts into P05's side slots. Insert its lower 608 from below. Place an 11 mm ID8.2/OD12 steel spacer between the two bearing inner races and bring P05 and P06 together.
6. Join each P05/P06 pair using three M3 x20 screws through P05's RECESSED head pockets. Seat these heads completely before installing the bottom bearing cap.
7. Fit a P01 under each sun assembly with three M3 x16 screws. Rotate this cap 60 degrees relative to the housing-join screw pattern so its holes align with the other three holes. These use three more P01 caps.
8. Load the M3 nuts into P13's side slots, insert its lower 608 from below, and attach the final P01 with three M3 x16 screws.
9. Fit an M8 nut into the underside hex pocket of base P12. Thread in the 468 mm rod, leaving about 2 mm below the base's central bottom face, within the feet recess. Tighten another M8 nut against the top of the base.
10. Slide the 12.5 mm ID8.2/OD12 spacer over the rod. Lower the P13 base-drive assembly until its lower bearing's inner race rests on that spacer.
11. If using sails, preload six M4 nuts into the underside arm-root pockets of P14. Fit each P15 into its curved root pocket and use two recessed M4 x10 button-head screws per arm.
12. Fit one P16 cup to each arm's upright end tab. Pass an M4 x25 screw from the recessed back of the tab through the cup boss; fit the OD9 washer and nut from inside the cup. All cup openings must face the same tangential sense around the rotor.
13. Load three M4 nuts into P13's outward-opening flange slots. Slide P14 over P13's external hex and secure it using three M4 x20 bolts. Omit P14-P16 and their fasteners if testing without wind sails.
14. Slide the 32 mm ID8.2/OD12 spacer down the rod. Lower the first P02 pot and engage its male hex with P13's socket.
15. Add a 15 mm ID8.2/OD12 spacer above the pot bearing. Thread an M8 nut onto the rod until it seats against that spacer. Lower P04 over this nut so its underside hex pocket captures it; secure P04 with a second M8 nut above.
16. Install three M4 x75 bolts upward through P04. Secure each bolt to the carrier with an M4 nut above the carrier. Slide a 37.2 mm ID4.2/OD6 spacer onto each stationary bolt.
17. Add the 5.9 mm ID8.2/OD12 spacer above the carrier's upper M8 nut. Lower one prepared sun assembly onto the central rod.
18. Lower the three prepared P07/P08 planet assemblies onto the outer bolts and mesh them with the sun. Align both staggered tooth rows. Add a 10 mm ID4.2/OD6 spacer above each 604 inner race, then an OD7 washer and an M4 nut. Snug the nuts against the inner-race stack without binding the gear.
19. Load six M4 nuts into the outward-facing slots under the pot's upper flange. Fit two P09 ring halves SIDEWAYS around the planets, rotating the second identical half 180 degrees. Align both tooth rows before seating the halves.
20. Fit P10 over the ring halves and fasten the collar, ring halves and pot together using six M4 x20 bolts. The collar has recessed screw-head access above each mounting pad. Align the halves concentrically and check free mesh before final tightening.
21. Hand-turn the bottom adapter. Confirm that the sun reverses direction and turns twice as fast as the pot. Resolve any rubbing or binding before adding another level.
22. Add a 44.6 mm ID8.2/OD12 spacer above the first sun's upper bearing. Lower P03 for level 2 and engage its male hex with the sun socket.
23. Assemble level 2 in this order: 15 mm center spacer, lower M8 nut, P04, upper M8 nut, three M4 axle bolts and their lower nuts, three 37.2 mm axle spacers, 5.9 mm center spacer, prepared sun, three prepared planets, three 10 mm axle spacers with washers/nuts, two P09 halves and P10 with six M4 x20 bolts. Hand-check rotation.
24. Add the next 44.6 mm center spacer and lower the second P02 for level 3. Assemble its carrier, spacers, sun, planets and ring halves in the same order as level 2, but use the shorter P11 terminal collar instead of P10.
25. Add the final 44.6 mm center spacer. Lower the prepared P17 top fan and engage its male hex with the third sun socket.
26. Add the 21 mm center spacer above the top fan bearing. Thread the ninth ordinary M8 nut onto the rod until it seats against that spacer.
27. Load six M4 nuts into the underside flange pockets of shroud P18. Lower the shroud around the top fan. Lower grille P19 over the central M8 nut so its hex pocket captures the nut.
28. Join P19 to P18 with six M4 x16 bolts. Fit the M8 acorn nut at the top of the rod and confirm the rod end fits inside it without bottoming out.
29. Hand-turn the input through several revolutions. Confirm speeds +1, -2, +4 and -8, clear fan/guard gaps, non-rubbing air collars and free bearings. Fix each fault before applying wind or a motor.
