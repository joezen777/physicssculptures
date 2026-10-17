# Three 40 mm top-fan concepts: physics assessment

2026-10-17. Scope: 144 mm nominal diameter, adjusted guard, three large 80 x 120 mm sails at 180 mm radius, 10 knots wind. Objective: maximum useful axial volume flow on this drive, not maximum RPM. No old small-cup configuration is included.

## Result

No actual performance winner is established. The descriptions do not fully define blade surfaces, and the previous analytic rotor model cannot resolve the mechanisms distinguishing these concepts. Numerical airflow scores would require invented feature efficiencies. No candidate-specific CFD or physical test was performed.

| Concept | Supported conclusion | Main unresolved issue |
|---|---|---|
| Toroidal, 3-5 looped pairs | Closed loops can change tip-vortex losses and noise; no demonstrated advantage here | Loop interference, total section area, surface drag, section incidence and torque |
| Three high-solidity scimitar blades | Most straightforward first prototype to characterize; this is an engineering preference, not a performance rank | Stall and drag from high pitch, high solidity and winglets; drive RPM reduction |
| Four tubercled blades | Stall behavior can change with tubercles; no demonstrated airflow gain here | Tubercle amplitude/wavelength, Reynolds sensitivity, pre-stall losses and torque |

## Computed common constraints

Run: python3 experiments/print_petg_12/fan_concept_bounds.py

Outputs fan_concept_bounds.json. Standard-library-only calculation reuses the previous uncalibrated large-sail torque curve and lower-fan load model. Aggregate geared efficiency 0.8, input friction 2 mN m, sail Cd forward/reverse 1.4/0.4 remain assumed.

At 415 RPM, rotational tip speed is 3.129 m/s. With a 40-80 mm local chord, rotation-only tip Reynolds number is about 8,344-16,688, not the approximately 3,800 of the earlier 18 mm chord blade. Local root Reynolds numbers are lower. These estimates omit wind crossflow.

At 415 RPM the drive has about 8.64 mW and 0.199 mN m available at the top shaft after modeled lower-fan loads and losses. A scan of 401 speeds gives maximum available top power about 22.34 mW at 229 RPM. A redesigned rotor's torque curve must intersect this drive curve; 415 RPM cannot be imposed on all three designs. The maximum-power point need not maximize actual flow because aerodynamic efficiency varies with speed.

For the assumed isolated annular actuator disk, ideal flow Q=A*(P/(2*rho*A))^(1/3) is 9.16 L/s at the 415-RPM available power, or 12.57 L/s at the sampled maximum power. These are ideal reference ceilings under this model, not predictions for the three designs or bounds on the wind-exposed interacting stack. Unknown aerodynamic figure of merit f multiplies flow by f^(1/3). At 415 RPM, f=0.2-0.8 would produce 5.36-8.50 L/s. There is no evidence to assign a different f to each proposed concept.

## Geometry and terminology

Angle of attack is not geometric pitch. For an axial rotor alpha=beta-atan2(v_axial,omega*r), modified by camber and swirl. A nominal 45-degree root pitch with the old model's 0.401 m/s axial flow gives alpha about 22.25 degrees at r=22 mm and 415 RPM. A literal 45-50 degree angle of attack is a very different, separated-flow design condition. Do not use a linear attached-flow lift law there.

If 35 mm root height is the chord's vertical projection at 45 degrees, chord is about 49.5 mm. The biomimetic 18 mm tip height at 25 degrees similarly implies about 42.6 mm chord. If these dimensions instead mean section thickness or elevation offset, different surfaces result. Solidity must specify local versus disk-average and projected versus developed area: disk-average developed annular solidity 0.75 for three blades spanning r=22-72 mm requires mean chord about 73.8 mm. Overlap and section interference therefore matter; independent blade strips are not a validated predictor here.

The scimitar description mixes forward sweep in the title with a swept-back leading edge. Sweep can vary along the span, but the actual curve must be defined. Its 10 mm downturned lip also needs an explicit relationship to the 40 mm envelope. We assume the guard has been adjusted as requested; no fit failure is inferred.

Missing definitions include chord/twist/sweep distributions, exact section coordinates and thickness, camber changes, loop topology and sections, winglet shape, tubercle amplitude/wavelength, and intended outlet resistance. These are design choices that can be completed, but merely choosing them does not establish their aerodynamic performance.

## Evidence

MIT Lincoln Laboratory describes reduced tip-vortex drag effects and lower noise, with prototype thrust comparable at similar power on commercial quadcopters. It does not establish elimination of all vortices or a gain at this speed/Reynolds number:
https://www.ll.mit.edu/partner-us/available-technologies/toroidal-propeller-0
https://www.ll.mit.edu/sites/default/files/other/doc/2022-09/TVO_Technology_Highlight_41_Toroidal_Propeller.pdf

A numerical/experimental tubercle study covers Re=20,000 and distinguishes pre-, post-, and deep-stall behavior. Benefits cannot be assigned without geometry and operating-point matching:
https://www.sciencedirect.com/science/article/pii/S0960148122014823
Additional experimental dynamic-stall research operates at Re=33,000:
https://doi.org/10.1007/s00348-025-03981-7

The located Eppler 420 study is a 2D computational study whose abstract explicitly states that matching experimental reference data were unavailable, validating instead against another section before studying E420. The section name is not proof of suitability here:
https://sedici.unlp.edu.ar/handle/10915/105804

## Next meaningful experiment

Create fully specified surfaces and compare at equal available drive torque, allowing RPM to settle. Measure Q, shaft torque, RPM and startup in the same setup. Alternatively use geometry-resolved unsteady 3D simulation with convergence and experimental validation appropriate to these Reynolds numbers. Preserve the existing P17 as a control and include smooth-edge/no-winglet controls to isolate benefits of tubercles and winglets. The current blade-element model must not be presented as such a simulation.

No out-of-ten scores or candidate RPM/CFM estimates are reported because none are supported. Checks on common budget arithmetic passed. The first-prototype preference is the scimitar concept because its open-blade geometry is easier to specify and characterize; the aggressive root and winglet features remain unproven.
