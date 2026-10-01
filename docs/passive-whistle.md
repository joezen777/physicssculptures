# Passive radial whistle workbench

Open http://localhost:8767 after running `bash launch_whistle.sh` in WSL Ubuntu.
Build with the existing Node/Vite environment: `cd web && npm run build`.
The independent FastAPI server is `whistle_server.py`; it does not modify the original flywheel server on port 8766.

## What the results say

The requested starting geometry does not self-cycle in the tested A, B, C or D configurations. A, B and D decay to an equilibrium at about **28.97 mm** travel. C moves to the outer stop. Switching a latch or snapping a conservative spring does not remove centrifugal force.

At 600 rpm and a 100 mm outer radius, a 5 g piston experiences **0.493 N at the inner position and 1.974 N at the outer position**. Rim speed is 6.283 m/s and free-stream dynamic pressure is 24.18 Pa. With 60% recovery and the default inlet/outlet areas, closed pressure is 11.607 Pa, producing just **0.00131 N** on a 12 mm piston.

A tuned pressure-dump example does cycle in this simplified model:

| Parameter | Tuned example |
|---|---:|
| Radius / RPM | 100 mm / 600 rpm |
| Piston mass / diameter | 2 g / 40 mm |
| Available stroke | 40 mm |
| Spring constant | 7.934959 N/m |
| Inward preload | 0.481675 N |
| Static / kinetic friction | 0.005 / 0.003 N |
| Damping | 0.025 N s/m |
| Inlet / bypass / leakage area | 20 / 400 / 2 mm² |
| Open / close / return detection | 0.85 / 0.15 / 0.16 of stroke |
| Acoustic endpoints / tube diameter | 25–65 mm / 40 mm |
| Measured repeating pitch range | approximately 2011 → 1208 Hz |
| Cycle frequency | approximately 0.4213 Hz |
| Falling sweep duration | approximately 2.03 s |
| Peak speed / centrifugal force | approximately 0.115 m/s / 0.742 N |

The example completed **25 returns during a 60-second run**. Its cycle frequency changed by less than 1% with half-size timesteps. The pressure-work, dissipated-energy and effective-energy change agree within 20 microjoules in the tested 16-second run. A no-pressure-source control does not cycle.

These decimal spring values are model settings, **not manufacturing precision recommendations**. At 24-second dwells, tested speeds 599, 599.5, 599.75, 600, 600.25, 600.5 and 601 rpm cycled. 595 rpm did not move, 598 rpm was unresolved/transient, 602 rpm reached equilibrium, and 605 rpm reached the outer stop. This brackets a narrow window; it does not establish exact continuous boundaries.

The primary module of the example keeps cycling during the prescribed second-piston faults. With the stuck or 5% extra-mass fault, the second module records zero returns versus six for the primary in 16 seconds. That does not mean the second module cycles. Each module's return count is reported separately. Peak sampled imbalance in the 16-second trials was approximately:

| Opposing piston | Imbalance |
|---|---:|
| Nominally identical | numerical zero |
| Stuck at initial position | 0.269 N |
| Valve trip 5% of stroke late | 0.235 N |
| 5% greater friction | 0.224 N |
| 5% greater mass | 0.311 N |

## Mechanics and geometry

All solver quantities are SI. UI dimensions are converted from mm, mm² and g.

The cylinder radius is the **outer piston travel limit**, not the starting radius. Thus
`r = R - travel + x`. Invalid geometries that cross the shaft or put the initial acoustic mouth beyond it are rejected. The scoop is fixed at the rim and feeds the inner side through a duct; its speed is omega*R. The piston-local speed omega*r is also recorded.

The radial equation is
`m*xdd = m*omega²*r + Fspring + A*p + Fgravity + Ffriction - b*xdot + Fcontact`.

For the linear spring:
`Fspring = -preload - k*(x-x_rest)`.
With constant pressure, effective linear stiffness is `k - m*omega²`. Positive effective stiffness normally leads to equilibrium with damping. Negative effective stiffness may drive the piston into a stop.

The bistable option uses a smooth double-well potential. Let `a=0.35*travel`, `z=(x-0.5*travel)/a`, and `B=1.5*sqrt(3)*snap_force`. Then
`Fspring = B*(z-z³)-preload` and
`U = B*a*(z⁴/4-z²/2)+preload*x`.
The barrier control sets the maximum restoring force of the unbiased well. Snapping changes position through numerical integration; there is no artificial position or energy jump.

Static friction holds the piston until breakaway; kinetic friction opposes sliding. Damping is viscous. The solver uses a semi-implicit velocity/position update and an implicit, coupled pneumatic pressure/velocity solve. Maximum timestep defaults to 0.5 ms and is reduced for high stiffness or low mass. End stops are perfectly inelastic unilateral constraints, with impulse-derived contact forces. Peak contact force is timestep-dependent; impact speed is the more transferable diagnostic.

For a horizontal shaft, radial gravity is periodic with rotor angle. Any maintained motion in this case is explicitly classified as rotation-forced, not an autonomous oscillation. Tangential Coriolis guide reactions are included in the optional dynamic shaft-reaction estimate; their contribution to seal friction is not modeled.

## Passive modes and energy accounting

- **A:** spring plus the constant recovered-air source and leakage. No switched bypass.
- **B:** the bypass opens at the outer trip and closes at the inner position. Pressure changes by integrating the pneumatic state; position is never reset.
- **C:** the conservative bistable spring. A bypass can optionally be coupled to its travel thresholds. Without a changing energy source it usually settles, snaps once, or hits a stop.
- **D:** a latch holds at the inner catch until net outward force exceeds static friction plus the latch threshold. At the outer trip it enters return/catch mode. Releasing a latch supplies no inward force. The same spring must produce the actual return. An optional bypass changes the pressure forces.
- **D + stationary cam:** adds an explicit passive connection to a nonrotating frame. A unilateral moving cam envelope enforces a smooth inward return during the selected part of each revolution. Cam work is estimated and reported. This is **rotation-forced cycling**, never reported as autonomous self-cycling. It consumes external shaft work and can create severe contact loads. This is a conceptual contact profile, not a designed cam follower.

The drive maintaining constant RPM supplies energy externally; no internal active controls are used. The constant centrifugal field is conservative in the rotating frame. Its cycle work is zero for a closed radial excursion. Measured positive pressure work can sustain B; hysteresis by itself is not an energy source.

Reported effective energy is
`E = 0.5*m*v² + U_spring - 0.5*m*omega²*r²`.
Pressure work, dissipation and cam work are accumulated. The energy comparison is meaningful for vertical-shaft runs without external cam contact. Horizontal gravity introduces additional periodic work, so those diagnostics are not a closed energy audit.

## Pneumatics and acoustics

NASA's [dynamic pressure definition](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/dynamic-pressure/) gives `q=0.5*rho*(omega*R)²`. The source is `Ps=C_recovery*q`, not q itself. The [drag equation](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/drag-coefficient/) estimates `D=Cd*q*A_inlet` and shaft power `D*omega*R`.

The inlet and outlet flows are linearized from an orifice relation at Ps:
`G = C_flow*A*sqrt(2/(rho*max(Ps,1 Pa)))`.
`Qin=Gin*(Ps-p)`, `Qout=Gout*p`, where the open bypass adds outlet area.
Chamber compliance is `C=V/(gamma*Patm)`, with gamma=1.4 and atmospheric pressure 101325 Pa.
The integrated equation is `C*pdot = Qin-Qout-A*xdot`.
The implicit coupling prevents tiny air compliance from creating an unstable explicit pressure step. Compression can temporarily raise chamber pressure above recovered source pressure; this is not extra source energy.

The bypass is an **ideal pressure-balanced, massless valve**: actuation travel/work, cracking pressure, delay and stiction are not included. That is a significant optimistic assumption, especially because the tuned quasi-static margins are only about **2.3 mN**. Real seal friction, guide side loads, leakage, flow separation, co-rotation of ambient air, and manifold losses may eliminate the model's window.

Quarter-wave resonance is `f=c/[4*(L+0.6*tube_radius)]`, using the [UNSW closed/open pipe model and end correction](https://newt.phys.unsw.edu.au/jw/flutes.v.clarinets.html). Length interpolates between the selected acoustic endpoints using actual piston travel. If the endpoint difference does not equal physical stroke, a mechanical linkage or equivalent cavity arrangement would be required. Independently chosen piston and acoustic tube diameters imply a stepped piston or coupled chamber; they are not a fully resolved CAD geometry.

The alternative [Helmholtz approximation](https://phys.unsw.edu.au/jw/Helmholtz.html) is
`f=c/(2*pi)*sqrt(A_neck/(V_cavity*L_neck_eff))`, with a combined neck correction of 1.45 neck radii. It is appropriate for a compact cavity and narrow neck rather than a long uniform pipe. Neither acoustic option solves the aeroacoustic jet/labium feedback, excitation threshold, mode locking, overblowing, vent-dependent acoustic impedance, or loudness. Web Audio plays an explicitly labeled resonance-only sine tone, including at states where a real whistle may be silent.

## Analysis, sweeps, optimization and balance

The playback renders stored solver samples at their actual timestamps and stops at the end. It never loops a transient to manufacture apparent oscillation.

A return is measured only after the piston crosses the outer threshold and subsequently crosses the return threshold inward. Cycling requires at least four late return events, reasonably stable periods and a recent event. Smaller sustained oscillations require late extrema, stable periods and nondecaying late amplitude. Transients remain unresolved instead of being called sustained. Pitch ranges in summaries use the last 35% of the run; whole-run startup extrema are also exported. Classification describes finite-window evidence, not indefinite stability.

The RPM test is a 21-point ascending **stepped dwell sweep**, carrying position, velocity, pressure, valve and latch state. It is not a continuous acceleration ramp. Each dwell uses the configured duration. Horizontal gravity/cam angle restarts per dwell, so phase-sensitive sweeps need a future continuous-angle ramp model. Discrete RPM points can miss narrow operating windows. Full pitch/rate/equilibrium/sweep-time/imbalance results accompany the colored operating map.

The bounded design search tests 54 combinations in mode B, varying mass, diameter, stroke, inlet, vent and switching positions. Spring rate and preload are analytically centered between the open and closed force curves for each geometry. User friction, damping and recovery remain fixed. The search uses vertical shafts and two nominally balanced modules, then independently halves the timestep and tests a 5% friction mismatch. It does not create active resets or silently reduce friction. Absence of a candidate is not an impossibility proof; returned candidates are ideal-model hypotheses, not print-ready designs.

For evenly spaced pistons, the first mass moment is `sum(m_i*r_i*e_i)`. Its magnitude divided by total moving-piston plus centered-rotor mass gives COM offset. Its magnitude multiplied by omega² gives rotating imbalance. A second estimate includes radial acceleration and tangential Coriolis terms. Fixed housing geometry is assumed balanced. Axial couple imbalance, spring mass, moving air, bearing compliance, vibration resonance and rotor structural strength are omitted.

Acceleration, impact velocity, spring/piston force and imbalance are compared with adjustable screening thresholds. Defaults (100 g, 1 m/s impact, 10 N spring/piston force, 5 N imbalance) are illustrative flags, not allowable stresses or a safety certification. Pressure/low-Mach and source-power model limits are also flagged.

## Prototype implications

The original small-bore design is not supported by the tested force balance. Promising changes are a larger pressure area, a much lighter sabot, lower measured seal friction, and a pressure-balanced bypass. Even then, the fixed spring requires close RPM matching. A stationary return cam is a more explicit energy path but adds a stator connection and contact design; it is not a rotor-only self-oscillator.

Before making a rotating prototype, measure a nonrotating module's breakaway/sliding force, whistle leakage, required jet speed and valve actuation work. Use those measured values in the workbench. A printed housing on the Ender 3 V2 can be considered for that fixture, with a smooth replaceable bore/liner and a characterized metal spring. No printer-specific fits, supports, rotor wall thicknesses or resin/filament strength claims are provided because there is no validated rotating CAD part here.

## Reproduction and checks

Run `python -m unittest discover -s tests -p test_whistle.py -v` in the existing Python environment.
Fourteen tests cover geometry validation, static friction, position-dependent centrifugal load, analytic spring equilibrium, conservative bistability, failed resets, pressure dumping, acoustic formulas, paired balance, cam classification, high-RPM flags, cycling energy, timestep convergence, source-off control and API validation.

`experiments/whistle_lab/validate.py` repeats the baseline, example, fault, narrow RPM, 60-second and bounded-search studies and writes JSON under ignored `runs/whistle/`.

Chromium verification covered initial physics results, tuned-example loading, playback, Web Audio controls, CSV export, narrow-screen overflow and absence of JavaScript errors. Both the original dashboard and the new entry point build through Vite.

A compact checked result snapshot is committed in `docs/passive-whistle-results.json`.
