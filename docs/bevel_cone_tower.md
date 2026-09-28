# Ice-cream cone bevel variant

A separate experiment in `experiments/bevel_cones`; the original spur tower is unchanged.

## Geometry and mechanism

Three slender shells by default taper from 28 mm diameter at the bearing boss to 110 mm at the rim over 100 mm height. A small truncated tip is necessary for the 8 mm rod and 608 bearing, so these cannot end in a literal sharp point. Stages are spaced 170 mm apart.

Each stage has two opposed 24-tooth bevel gears and three equal radial bevel pinions spaced 120 degrees apart. Module 2, 45-degree pitch cones and a common pitch apex describe a miter differential with its carrier fixed. The lower cone drives the lower bevel through six pitched fan blades; the upper bevel drives the next cone through a 16 mm AF male / 16.4 mm AF female hex. A stationary three-post frame holds the radial axles above the cone rim. This avoids a stationary axle passing through a rotating shell.

With the carrier fixed, the upper side gear rotates at the same speed in the opposite direction: bottom +1, middle -1, upper +1, fan -1 in the three-stage draft. This variant intentionally gives up the spur version's 3:1 multiplication to demonstrate the bevel layout. Unequal or compound gears require a new common-apex and shaft-angle design; simply changing a bevel diameter is insufficient.

## Tooth construction

The tooth flanks use the spherical-involute geometry from FreeCAD Gears / pygears, with interpolated curves and ruled conical lofts. This is not a spur profile pasted onto a taper. Two spherical bands span cone distances 25 to 29.3 mm and 29.7 to 34 mm; the outer band is offset half a tooth (7.5 degrees). Spherical boundaries keep both mating gears' row divisions at the same distance from the common apex. A root web joins the bands. Backlash input is 0.18 mm per gear.

Sources:
- [FreeCAD Gears](https://github.com/looooo/freecad.gears), selected GPL-3.0-or-later modules vendored with license and pinned commit in vendor/PROVENANCE.md.
- [KHK gear dimensions](https://khkgears.net/gear-knowledge/gear-technical-reference/calculation-gear-dimensions/), bevel pitch cones and intersecting shafts.
- [KHK miter technical information](https://khkgears.net/pdf/miter-tech.pdf), axial thrust and assembly considerations.

## Draft limitations and printing

This is a visual/kinematic CAD draft, not a print release. The 608 shapes show the 8 x 22 x 7 mm envelope. Nominal bearing seats are 22.2 mm diameter and 7.2 mm long. Retaining collars, axial bearing support, gear mounting shoulders, fasteners and a complete load path still need engineering. Gravity alone cannot reliably retain bevel gears against their axial separating forces. The animation prescribes the intended ratio; it is not a contact dynamics simulation.

Start with a single low-speed hand-turned mesh coupon, not the whole tower. For the Ender 3 V2 with 0.2 mm nozzle, use a tough material such as PETG for initial fit exploration, print separate gears and housings, and orient the gear axis vertically where possible. The spherical band ends and internal seats need a support/orientation trial. Resin detail can be explored with ABS Pro 2 but tooth toughness and support marks must be tested. Clearances remain starting values, not verified printer tolerances.

## Files and regeneration

Run `python3 experiments/bevel_cones/launch.py` in WSL Ubuntu to regenerate and open the model in FreeCAD. Outputs include the native FCStd, full STEP, full/cutaway renders, gear detail and checks.json. The live controls switch the cone walls between full and cutaway and pause/resume rotation.

Solid validity and sampled tooth-overlap checks are recorded by the builder. They do not constitute a full interference sweep or mechanical qualification.

## Repeating fan modules

Each cone is open around its central bearing boss and has six 22-degree pitched fan spokes at its rim, replacing the plain drive spokes. Adjacent modules use opposite blade handedness because their rotations reverse. These are conceptual fan paddles, not aerodynamic airfoils. The small cone throat and gears restrict flow; useful turbine efficiency has not been demonstrated. The stack is straight and rigid, not a flexible snake. Set BEVEL_STAGES from 1 to 6 when launching to vary the visual stack; arbitrary physical stack height is not qualified. Each additional level needs its own fixed pinion supports and axial retention.

The male hex insertion length is 10 mm to clear the preceding upper bearing. The radial support arms have a 9 x 12 mm cross-section around an 8.2 mm axle hole, leaving a continuous solid around the hole. Validation requires every modeled component to be a single solid.

## Verification of the three-stage draft

All 60 native components are valid single solids; the exported STEP reloads as 60 valid solids. Twenty-four tooth-overlap checks across four input angles and three pinions reported zero overlap. Twenty-seven selected static component pairs, including fan/pinion and hex/bearing clearances, reported zero overlap. See output/checks.json and output/verification.json. These are sampled checks, not a full motion or structural qualification.
