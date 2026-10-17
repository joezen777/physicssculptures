# Three-fan comparison at 10 knots: conditional screening

2026-10-17. Only the current three large 80 x 120 mm sails at 180 mm radius are used. Top diameter is 144 mm; the guard is assumed adjusted for the 40 mm blade envelope. Original P17 is retained as a control.

## Result

| Candidate | Calculated RPM | Calculated flow, L/s | Flow relative to P17 |
|---|---:|---:|---:|
| Toroidal proxy, 5 pairs | 359 | 8.05 | 136% |
| Toroidal proxy, 4 pairs | 370 | 7.69 | 130% |
| Tubercled proxy, 4 blades | 363 | 7.68 | 130% |
| Scimitar prototype | 378 | 7.28 | 123% |
| Original P17 | 417 | 5.92 | 100% |

The five-pair toroidal proxy has the highest nominal flow among the selected representative cases. Its nominal advantage over the scimitar is 10.6%; over the tubercled proxy it is 4.9%. These differences are conditional, not established performance gains. Four-pair toroidal and tubercled cases differ by less than 0.1%.

This is NOT a resolved toroidal or tubercle simulation. The blade-strip proxy cannot establish the claimed vortex effects. The toroidal result primarily reflects adding lifting-strip area and its torque load. The tubercled result primarily reflects a different chord/pitch distribution, not demonstrated stall control. Do not choose a production design based on these values alone.

## Does the ranking survive uncertainty?

| Candidate | Flow envelope, L/s |
|---|---:|
| Toroidal proxy, 5 pairs | 6.68-8.88 |
| Toroidal proxy, 4 pairs | 6.38-8.50 |
| Tubercled proxy, 4 blades | 6.39-8.52 |
| Scimitar prototype | 6.12-7.95 |

These are deterministic stress envelopes while holding the nominal wind, sail coefficients, drivetrain efficiency and friction FIXED. Independent design-specific lift factors 0.8/1/1.2, drag multipliers 0.75/1/1.5 and extra-feature drag coefficients 0/0.01/0.05 are hypothetical discrepancy tests, not measured error bounds or probability distributions. Tubercles have no separate lumped feature drag in this model, so their feature-drag cases are duplicates.

All candidates can lead when their favorable discrepancy case is compared with unfavorable cases for the others. That is a counterexample to robustness within this test set, not a probability that any one design wins. The intervals overlap substantially. The calculation therefore does NOT establish which rotor is actually best.

A wider common-environment grid additionally uses three common polar cases, aggregate drivetrain efficiencies 0.6/0.8/1.0 and input friction 0/2/5 mN m. The saved CSV has 2916 rows (some duplicate tubercle rows as noted). No statistical confidence is implied.

## Explicit sectional assumptions for the two new concepts

These are geometries of analytical blade strips, not mechanically validated 3D solids. Topology, interference, hub attachment, sweep surfaces, shell strength, balance and printability of the two new concepts have not been validated or exported as STLs.

### Toroidal proxy

- Analyze 3, 4 and 5 pairs (6, 8 and 10 lifting strips). Four pairs is the representative default; five pairs is separately included in the full uncertainty comparison.
- Active strip radius 22.6-68 mm. The 68-72 mm outer region represents the closing loop; it contributes only an assumed tangential drag load in this reduced model.
- Root geometric pitch 47.5 degrees, linearly falling to 22 degrees at the end of the lifting strip.
- Root chord 33/sin(47.5 degrees) = approximately 44.8 mm, allowing a nominal 2 mm axial wall within a 35 mm root section envelope; chord linearly falls to 18 mm.
- Model the bridge as an 18 x 4 mm surface per pair with two wetted sides, acting at 70 mm radius. This is a drag-area placeholder, NOT a geometric or aerodynamic solution of the loop.
- A separate 27-case geometry grid varies pair count 3/4/5, chord scale 0.8/1/1.2 and tip pitch 18/22/26 degrees. The 1.2x chord cases exceed the root-height limit (41.6 mm including the wall) and are explicitly marked sectional_height_limit_pass=false; they are not used in the nominal ranking. The other cases pass this sectional height check only, not a full 3D fit check.
- No Goettingen/Eiffel airfoil polar, closed-loop vortex interaction or special efficiency benefit is assumed. Larger chord cases must not be called feasible designs without a 3D clearance/height check.

Nominal flows for 3/4/5 pairs are 7.18/7.69/8.05 L/s, with corresponding RPM 384/370/359. Finite-blade/loop interference could change this trend.

### Tubercled proxy

- Four blades, active radii 22.6-72 mm.
- Geometric pitch linearly decreases from 45 degrees to 25 degrees.
- Chord linearly decreases from 35/sin(45 degrees) = 49.5 mm to 18/sin(25 degrees) = 42.6 mm. The quoted heights are interpreted as chord projections, not solid airfoil thickness.
- Outer 60% span has a trial 1.5 mm leading-edge sinusoid with 8 mm wavelength, smoothly tapered to zero at both ends. Only local chord variation is represented.
- The model does not resolve the counter-rotating vortices, spanwise sweep or stall-delay mechanism.
- A smooth-edge control using the same mean chord/pitch distribution gives 7.6805 L/s, versus 7.6804 L/s with the geometric modulation (-0.0009%). This tiny change is NOT evidence of a beneficial tubercle effect.

### Scimitar and original P17

Scimitar radial chord/pitch comes from the implemented scimitar_geometry.py. The nominal lip-drag coefficient is 0.01. The new comparison reproduces the earlier nominal scimitar flow within 0.01%. The original P17 uses its earlier 22 mm root model; new concepts share a 22.6 mm root clearance. This small area difference is explicitly retained rather than changing the established control.

## Equations and operating point

Use air density 1.225 kg/m3, kinematic viscosity 1.5e-5 m2/s and wind 10 knots = 5.14444 m/s. The three-sail average torque curve is the existing uncalibrated normal-component model with forward/reverse drag coefficients 1.4/0.4. Nominal aggregate geared efficiency is 0.8 and input-referred friction is 2 mN m.

Each strip uses relative speed sqrt((omega*r)^2 + vi^2), inflow angle phi=atan2(vi,omega*r), alpha=geometric_pitch-phi, Cl=lift_scale*sin(2*alpha), Cd=Cd0+2*sin(alpha)^2. Axial and tangential forces are resolved to thrust and torque. Solve integrated thrust=2*rho*A*vi^2 for uniform induced velocity. Extra loop/lip drag is added to torque only; no invented lift bonus is added.

These common analytic force laws are NOT calibrated airfoil polars for the proposed high-camber sections, especially around Reynolds numbers of only a few thousand. In the five-pair toroidal proxy, local Reynolds numbers are approximately 3022-3745; the tubercled proxy gives 3328-7900. Camber, thickness and strong separation could substantially alter results.

The coupled torque balance includes lower fan floors at speed ratios 1, 2 and 4, and the top rotor at 8. RPM is solved, not held at 415. Flow means annular area times uniform modeled induced velocity at the top plane. It is neither far-wake velocity nor the sum of floor flows.

The model omits blade interactions, swirl, actual tip losses, vertical loop-induced flow, tubercle vortices, stack wakes, grille losses, wind crossflow, speed-dependent friction and startup inertia. It cannot produce a reliable pressure-flow curve or directional-throw ranking. The objective here is free axial volume flow under this simplified drive model.

## Validation performed

- Every rotor case satisfies positive induced power no greater than shaft power.
- Positive operating-point residuals against the direct sail torque calculation are below 1e-8 N m.
- 120 versus 480 radial strips changes nominal RPM/flow by less than 0.001%.
- Earlier scimitar nominal flow is reproduced within 0.01%.
- These are numerical/model consistency checks, NOT validation against experiments.

## Reproduce

From the repository root in WSL Ubuntu:

    python3 experiments/print_petg_12/compare_fan_concepts.py

Output: results.json, sensitivity.csv in experiments/print_petg_12/output/three_fan_comparison. Only the standard library is needed. No paid APIs or GPU models were used.

## Evidence and next decision

MIT reports reduced noise and comparable thrust at similar power for tested toroidal drone propellers, not a universal efficiency gain or elimination of all vortices:
https://www.ll.mit.edu/partner-us/available-technologies/toroidal-propeller-0

The cited tubercle study distinguishes pre-stall, post-stall and deep-stall performance at Re=20,000. It does not validate our much smaller rotor's chosen modulation:
https://www.sciencedirect.com/science/article/pii/S0960148122014823

To resolve the ranking, specify complete 3D surfaces for the other two designs and use a validated unsteady 3D flow model or guarded comparative physical tests measuring RPM, torque and integrated axial flow under identical wind and payload. Include the original P17 and a smooth-edge four-blade control. The present result motivates testing five-pair toroidal and four-blade axial candidates; it does not justify discarding the existing scimitar prototype or declaring a winner.
