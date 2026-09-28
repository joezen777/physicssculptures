# Four-level circular-sail tower

This separate variant is in `experiments/simple_sail_tower`. The user confirmed four levels total. The earlier roof-vent cage and bevel variants remain unchanged.

| Level | Function | Speed relative to wind rotor | Blade pitch |
|---|---|---|---|
| 1 | Three circular shallow wind cups, horizontal rotation | +1 | Tangential cup openings |
| 2 | Flowerpot with open fan floor | -2 | -22 degrees |
| 3 | Flowerpot with open fan floor | +4 | +22 degrees |
| 4 | Fan inside a stationary ring | -8 | -22 degrees |

## Simplification and gearing

Three circular, shallow cup sails replace the twelve-vane barrel. Cups are placed at 120 degrees on 102 mm radial arms and only appear at the bottom. The dishes provide a drag asymmetry; they are not flat disks with equal drag on both faces. Their wind-starting performance has not been calculated or measured.

Each gear stage now has 96 ring teeth, 48 sun teeth and three 24-tooth idlers, module 1.5, 20-degree pressure angle. Pitch radii are 72, 36 and 18 mm; idler centers are 54 mm from the main shaft. The dimensional identity 96 = 48 + 2*24 holds, and (96+48)/3 = 48 permits the three equally spaced idlers.

With the carrier fixed, sun speed = -(96/48)*ring speed = -2*ring speed. Each idler spins at +4*ring speed. Three gear stages connect four visible levels. Ideal unloaded speed ratios are 1, -2, +4, -8; the ideal top torque is input torque divided by eight. Fan loads and losses reduce available torque and can prevent startup. No gearing creates additional wind power.

Two staggered straight-tooth rows are retained on every gear: each row is 4 mm wide with a 0.4 mm gap and a half-tooth phase offset. These remain cylindrical gears inside flowerpot housings.

## All rotating axles use 608 bearings

The hardware envelope is 8 mm bore, 22 mm outside diameter, 7 mm width. There are twenty 608 bearings: nine for the idlers, nine for the three pot/output-hub assemblies, one extra bottom input bearing and one dedicated top fan bearing.

The bottom wind hub has two spaced 608 bearings at z=-20 and z=2 mm, giving 22 mm between bearing centers. The 8 mm central rod stays fixed. The cups, arms and lower pot rotate together through the outer-race housing. Stationary spacers contact the inner races; rotating passages have 12.5 mm bores around 12 mm OD spacers. Bearing pockets start at 22.2 mm diameter and 7.2 mm depth.

Bearings permit rotation but cannot guarantee motion in every wind or eliminate friction. Real bearing fit, shaft straightness, spacer lengths and axial retention must be verified. Do not clamp rotating and stationary races together. Final shoulders, collars, clamp screws and assembly retention remain draft; the animation does not prove a working physical mount.

The shaft must be anchored to the base and the internal carriers held stationary. There are no outer support posts. The tall 8 mm shaft and base still need wind-load, stiffness and stability checks.

## Fans and ring

The second and third pot floors are six-blade open rotors instead of solid floors. Their pitches alternate because their rotation directions alternate. The top fan has its own 608 and a stationary ring with overhead support spokes, leaving clearance to the rotating fan. All three fan pitches have the same intended axial pumping direction under the prescribed rotations.

These are pitched paddles, not qualified aerodynamic airfoils. Upward pumping, available flow and startup are not demonstrated. Gear clusters and housing throats obstruct the flow path and must be included in a physical test or flow analysis.

## Printing intent

Use the Ender 3 V2 / Sprite Pro / 0.2 mm nozzle for low-speed fit trials: PLA for isolated gear fit coupons, PETG for the cup/arm and housing prototypes. The 171 mm pot caps and 184 mm base fit within the nominal bed. Print the three cups and arms separately; the overall rotor span is larger than the bed. The pictured integral arms are a geometry concept and need a keyed/bolted split before release.

Print tooth faces flat and test the staggered-row overhangs. Fan floors and the stationary top ring/spider need an orientation/support trial or separate blade/housing parts before printing. A 22.2 mm pocket is not a guaranteed bearing fit. Resin may resolve gear details but must be evaluated for tooth and attachment toughness. No print-ready STL release is provided.

## Files and operation

Run `python3 experiments/simple_sail_tower/launch.py` in WSL Ubuntu. The FreeCAD controls animate the specified gear ratios and switch the pot housings between full and cutaway. Output includes native FCStd, full and cutaway STEP, full_view.png, cutaway.png, mesh checks and motion metadata.

Source references:
- SKF bearing catalogue (608 dimensions): https://cdn.skfmediahub.skf.com/api/public/0901d196807026e8/pdf_preview_medium/0901d196807026e8_pdf_preview_medium.pdf
- KHK internal gear technical information: https://khkgears.net/pdf/internal-tech.pdf

All checks are geometric samples, not a complete strength, airflow or assembly qualification.

## Verification

The saved model contains 87 valid components and 20 modeled 608 bearings. Four sampled mesh poses and 32 selected static clearance pairs passed with zero overlap. The cutaway STEP reload contains 247 valid solids and matches native volume with relative error 2.118662202814136e-11. See output/verification.json.
