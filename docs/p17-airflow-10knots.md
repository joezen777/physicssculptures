# P17 airflow screening at 10 knots

Calculated 2026-10-17. These are uncalibrated analytical estimates, not airflow measurements or CFD. No replacement STL has been produced or validated.

## Result

10 knots = 5.14444 m/s = 18.52 km/h. With the implemented 80 x 120 mm scoops at a 180 mm lever radius, nominal assumptions give:

| Top rotor | Bottom RPM | Top RPM (magnitude) | Axial speed at rotor plane, m/s | Flow, L/s | Flow, CFM |
|---|---:|---:|---:|---:|---:|
| Existing P17, six flat blades | 52.1 | 417 | 0.401 | 5.92 | 12.55 |
| Trial four twisted flat-section blades | 54.0 | 432 | 0.355 | 5.24 | 11.11 |
| Trial six twisted flat-section blades | 52.6 | 421 | 0.402 | 5.93 | 12.57 |

Nominal means assumed aggregate transmission efficiency 0.8 and constant input-referred running friction 2 mN m. Neither has been measured. Twisted trials use linear 35-degree root to 15-degree tip pitch, 18 mm chord, same radius and hub. They are mathematical geometries, not optimized or printable designs. All use the same surrogate flat-section force law; a cambered airfoil is NOT tested here.

The four-blade trial moves about 11.5% less air despite its higher speed. The six-blade trial differs by only 0.1% in flow, far below model uncertainty. This does not support replacing P17 based on the earlier four-blade suggestion. It does not exclude better geometry after calibration.

For existing P17 with large scoops, sweeping transmission efficiency 0.6/0.8/1.0, friction 0/2/5/10 mN m, and three surrogate blade polar assumptions gives 236-472 RPM and 2.87-7.41 L/s (0.194-0.502 m/s). This is an assumption sensitivity envelope, NOT a confidence interval or guaranteed operating range. It excludes uncertainty in sail coefficients; stalls remain possible.

Original small cups produce only 0.785/1.963/3.142 mN m static minimum/mean/maximum torque at this wind. With the illustrative 2 mN m running resistance they have no positive mean steady operating solution, although individual starting angles can momentarily produce motion. Larger scoops give 8.403/21.008/33.613 mN m. Their weakest static phase exceeds 2 mN m but not 10 mN m.

## Reproducible calculation

Run in WSL Ubuntu from the repository root:

```sh
python3 experiments/print_petg_12/airflow_screening.py
```

The script writes airflow_screening.json containing 216 cases and numerical checks. It uses only the Python standard library. No GPU or external service is needed.

Geometry comes from build.py: lower fan floors at radius 60 mm, top radius 72 mm, six 18 mm chord rectangular blades, constant pitch magnitude 22 degrees. Exposed blade root is approximated as 22 mm (hub radius); original box starts at 21 mm and is fused into the hub. The 3.6 mm thickness is not resolved aerodynamically. Hub blockage is approximated with annular area pi*(R^2-0.022^2). Rotation direction alternates, with pitch hand preserving the intended axial pumping direction.

Sail torque follows sail_screening.py:
u_i/U = cos(theta + 2*pi*i/3) - omega*r/U.
T_input = 0.5*rho*U^2*A*r*sum(C_i*u_i/U*abs(u_i/U)).
Assumed forward/reverse coefficients 1.4/0.4 and rho=1.225 kg/m3. Average over 720 phases. These coefficients are not measured for either sail. This model's unloaded tip-speed ratio is 0.2412; using wind speed as sail tangential speed would overpredict RPM.

Each rotor is treated as an isolated open rotor with zero axial freestream. Integrate 160 radial strips with phi=atan2(v_i, omega*r), alpha=beta-phi, Cl=s*sin(2*alpha), Cd=Cd0+2*sin(alpha)^2. Nominal s=1, Cd0=0.06; sensitivity pairs (0.7,0.12) and (1.3,0.04). These analytic polars are explicit placeholders, not data for the printed blades. Match integrated axial force to T=2*rho*A*v_i^2; integrate tangential force times radius for shaft torque. Volume flow is A*v_i at the rotor plane, not wind speed or far-wake velocity.

Solve mean sail torque = input friction + sum(abs(g)*rotor_torque/efficiency) at g=1,2,4,8, with efficiency 1 for direct bottom load and the chosen aggregate efficiency for all geared loads. The efficiency parameter is not per gear stage. Lower fan loads are included, but their flows are not added: these fans share a flow path. Shaft power is torque*angular speed. Zero-speed outputs mean no positive averaged running equilibrium, not a simulated startup trajectory.

At the nominal larger-scoop P17 operating point, top shaft power is only 8.36 mW, thrust 5.82 mN, and tip chord Reynolds number about 3,800. Uncalibrated section forces at this Reynolds number are a major uncertainty. The ideal same-power actuator-disk reference is 9.06 L/s; it is not a forecast for another blade design or a bound on the interacting stack.

## Checks and limits

Passed static sail torque coefficient check (0.30/0.75/1.20), positive-running torque balance residual <1e-10 N m, and rotor induced-power <= shaft-power checks. Increasing radial resolution from 80 to 320 strips changes nominal rotor velocity/thrust/torque by at most 0.0038%. These check numerical consistency, not physical accuracy.

The model omits wake interaction between floors, swirl, tip losses, grille blockage, pots, wind crossflow at the top rotor, changing Reynolds-dependent polars, bearing speed dependence, sail shielding and arm drag. Constant running friction is not measured breakaway resistance. Phase-dependent acceleration and inertia are not simulated; a positive mean solution does not prove sustained running or startup. In particular, crosswind of 5.14 m/s around a rotor with predicted axial speed only 0.4 m/s could substantially change the result. For testing, direct the known wind at the sails and characterize any wind reaching P17.

## Physical validation still needed

1. With intended payload, measure breakaway torque over a full turn and running torque versus RPM. Use known lever radius times tangential force; separate bearing/gear drag from fan load where possible.
2. Apply measured 5.144 m/s wind at sail height; map its uniformity across the rotor. Record input and top RPM simultaneously after settling, and test startup from several angles. Record wind at top height too.
3. Measure the axial velocity component over equal-area samples across the output plane with a suitable low-speed directional probe. Subtract the fan-stopped background; integrate Q=sum(v_axial*A_cell), excluding blocked cells. A single center reading or nondirectional wind-speed reading cannot provide volume flow.
4. Repeat current and replacement rotors under the same wind, sail configuration, payload and measurement plane, with at least three runs. Compare flow, RPM and startup success. Independently drive each rotor at matched RPM to separate rotor performance from drivetrain effects.

## References

- Local docs/print_petg_12_sail_options.md and experiments/print_petg_12/build.py.
- NASA momentum/thrust explanation: https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/propeller-thrust/
- Pindado et al., On Cup Anemometer Rotor Aerodynamics: https://pmc.ncbi.nlm.nih.gov/articles/PMC3386737/

References support the modeling framework; neither validates our chosen coefficients or this assembly.
