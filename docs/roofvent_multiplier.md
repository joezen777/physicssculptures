# Roof-vent-style wind input for the flowerpot multiplier

The active wind-input variant is in `experiments/roofvent_multiplier`. It supersedes the wooden-blade/candle exploration as the working direction. Both the original flowerpot model and the separate bevel variant remain preserved.

## Interpretation and layout

The user's roof-turbine-vent reference is interpreted as a vertical-axis rotor: the vanes travel around a horizontal circle while the shaft stays vertical. This keeps the existing gear stack upright. A horizontal-axis propeller would require a different input transmission.

Twelve scoop-like vanes form a barrel around the lowest pot. Their cross-sections curve circumferentially and sweep from smaller end diameters to a larger middle diameter, with a modest twist up the height. Each vane is a loft through six polygonal sections. This is a geometric concept, not a tested airfoil.

- Vane height: 100 mm, from z=8 to z=108.
- Maximum outer diameter: approximately 224 mm.
- Nominal vane thickness: 1.6 mm measured radially.
- Two end bands and one middle torque band connect the vanes.
- Three internal torque arms connect the middle band to the lowest pot cap.
- The lower pot retains six 12 mm floor intake openings, a 608 seat and an accessible 56 mm manual drive flange.
- The fixed shaft and internal carriers supply reaction torque; no external support posts are added.

Commercial roof turbine vents use curved vanes, bearings and internal bracing, but their specifications do not transfer to this model. Visual reference:
https://www.lomanco.com/vents/whirlybirds/

## Kinematics and available power

Rotor and lowest ring turn together. With the internal carriers fixed, the first center gear/next pot rotates at -3 times rotor speed and the final output at +9 times rotor speed. Ideally the final torque is one ninth of input torque; real losses reduce output power.

The wind power crossing a rotor's projected area is 0.5*rho*A*v^3. For an illustrative 0.224 x 0.100 m area and rho=1.225 kg/m3, that is about 0.37 W at 3 m/s and 1.72 W at 5 m/s, BEFORE aerodynamic conversion and bearing/gear losses. These are incident wind-energy figures, not predicted shaft output or starting torque. No power coefficient or self-starting wind speed has been established.

The original output fan is retained as a visible output/load. For an initial physical wind test it should be removable so that unloaded and loaded startup can be compared. A commercial roof ventilator is designed primarily for ventilation; attaching a geared load changes its behavior. This model is not a certified roof fitting or rainproof ventilator.

## Fabrication and checks

The barrel is an assembly, not a single printable piece. Individual vanes can be oriented separately. The 219 mm middle band is too close to the Ender 3 V2 bed limit for a practical brim/clearance margin: split the bands and spider into keyed bolted sectors before producing a print release. Blade root fastening, axial retention, balancing, fatigue and gust loads remain unresolved. PETG is a candidate for low-speed indoor fit trials; material and orientation need coupon testing.

FreeCAD's cutaway removes the front half of the cage and pots to reveal the gear train. Full-housing mode restores them. The animation prescribes gear ratios and is not an airflow simulation.

Run `python3 experiments/roofvent_multiplier/launch.py` in WSL. The output directory contains the native FCStd, full/cutaway STEP files, renders and checks. Run validate.py with the bundled FreeCAD Python environment for selected mesh, clearance and STEP round-trip checks.

## Verification

All 68 full-assembly components passed the builder solid-validity check. The native cutaway contains 63 nonempty components; five front vanes are wholly removed by the section. Four sampled gear poses and 33 selected cutaway clearance pairs passed. The cutaway STEP reload is valid and matches native volume to a relative error of 2.2556272142351226e-08. This does not establish aerodynamic performance.

The full exterior image is produced by render_full.FCMacro after the main build, using the exported full STEP in a temporary FreeCAD instance.
