# Stackable cone turbine tower - first FreeCAD draft

## Intent and adopted layout

This is a standing, hand-testable tower, separate from the earlier falling-device
experiments. Two cone housings stack along a stationary 8 mm shaft. A six-paddle
fan couples to the top. Every active gear surface has two straight-tooth rows,
with the second row shifted by half a tooth pitch. This is a staggered two-row
layout, not herringbone.

The first draft deliberately uses cylindrical involute gear bands INSIDE conical
housings. Actual conical/bevel tooth surfaces have not been generated. This choice
makes the requested tooth staggering, hex stacking and split inserts reviewable
with a standard, checkable gear mesh.

Each stage contains:
- One cone with an independently supported rotating bearing seat.
- A removable 72-tooth internal ring, split into two semicircular keyed inserts.
- A 24-tooth central output gear and hub, with a female hex socket.
- Three 24-tooth gears equally spaced on fixed axles.
- A stationary carrier clamped to the central shaft.
- A separate three-tab retaining cap.
- Simplified 608 bearings, axle spacers and an 8 mm stationary shaft.

Each center gear drives the cone immediately above through a 16 mm across-flats
male hex fitting into a 16.4 mm AF socket. The final center gear drives the fan.
The hex transmits torque; it is not intended to establish bearing preload or carry
the entire tower weight.

## Dimensions and tooth layout

| Item | Draft value |
|---|---|
| Gear module | 1.5 mm |
| Pressure angle | 20 degrees |
| Teeth per row: ring / center / planet | 72 / 24 / 24 |
| Row width and center relief gap | 4.0 mm / 0.4 mm |
| Total gear face width | 8.4 mm |
| Second-row angular offset: ring / center / planet | 2.5 / 7.5 / 7.5 degrees |
| Planet center radius | 36 mm |
| Stage spacing | 88 mm |
| Cone body outside diameter | 84 mm bottom, 132 mm top |
| Cap outside diameter | 135 mm |
| Base outside diameter | 164 mm |
| Bearing envelope | 608: 8 x 22 x 7 mm |
| Nominal bearing pocket | 22.2 mm diameter, 7.2 mm deep |
| Male / female hex AF | 16.0 / 16.4 mm |
| Rotating-hub clearance bore around stationary spacers | 12.5 mm |

Teeth are sampled involutes with simplified roots, not a production cutter-generated
profile. External teeth are thinned by 0.12 mm at the pitch circle; internal spaces
are widened by 0.12 mm. Two external members or an external/internal pair therefore
provide about 0.24 mm nominal circumferential backlash at the pitch circle.

The 0.4 mm middle gap leaves the outer tooth rows separated but connected through
their root bodies. Both mating gears have the appropriate half-tooth row offset.
The layout does not rely on staggered teeth to locate or retain axles.

## Motion and reaction torque

The carrier is fixed to the stationary shaft. For each stage:

    Ns * omega_sun + Nr * omega_ring = 0
    omega_sun = -3 * omega_ring
    omega_planet = 3 * omega_ring

The body and ring rotate together through three keys. The center gear and the cone
above rotate together through the hex coupling. Relative to bottom-cone rotation,
the middle cone rotates -3 times as fast and the top fan +9 times as fast.

If the fan drives the stack, the bottom output is nine times slower and rotates in
the same direction as the fan. Ideal torque increases ninefold; real bearing and
gear losses reduce that. Two stages do not multiply power. No aerodynamic prediction
of fan power or starting torque is made.

The three planet centers remain fixed; these are orbit-free planetary-layout idlers.
The central shaft and its anchored base supply the reaction torque. Carrier collars
show a split and M3 clearance hole, but the clamp fasteners and final shaft restraint
are not yet detailed.

## Assembly concept

1. Anchor the central shaft and slide on the lower cone and its bearing.
2. Install the stationary carrier with its three 8 mm axle pins.
3. Add inner-race spacers, the central gear assembly and the three intermediate gears.
4. Fit the two ring segments around the gear cluster with their row phases aligned.
5. Seat the three ring keys in the cone collar pockets.
6. Install the retaining cap; its ledge captures the ring without clamping its teeth.
7. Add the next stationary spacer and cone, inserting its male hex into the socket.
8. Repeat for the second stage and fan.

The segmented ring allows access around the assembled gear cluster. The insertion
sequence still needs a physical fit test. No claim is made that all parts can yet be
assembled in exactly this sequence without adjustment.

## Bearings, compression and retention

The cone bearing inner race is on the fixed shaft and its outer race sits in the
rotating cone. Each central output hub has two spaced 608 seats. Each of the three
intermediate gears has one 608 seat on its own fixed 8 mm pin.

Stationary spacers contact the bearing inner rings. Rotating hubs have a 12.5 mm
clearance bore where needed so they do not rub on the 12 mm OD spacers. Bearings
carry rotor weight; gear teeth are not intended as the stack's axial support.

Bearing geometry is an envelope-correct visual approximation with balls and races,
but no cage, seals or dynamic ball motion. The metal axle pins, central rod,
spacers and bearings are reference hardware, not printed parts.

## Printing scope and unresolved items

This is a FIRST DRAFT, not a validated set of ready-to-print moving parts.

Preferred first prototype: Ender 3 V2 / Sprite Pro / 0.2 mm nozzle. Use PLA for
low-speed gear fit trials and PETG for cap flexures and cone housings. Start with
0.10 mm layers. The largest part is 164 mm diameter. Print gear faces flat.
The staggered second tooth row creates overhangs; test bridging/support removal,
or split rows into keyed printable halves if necessary. Print the fan separately.
Do not use brittle resin for untested snap fingers.

Outstanding work:
- Bearing-fit coupons; 22.2 mm is a starting allowance, not a guaranteed fit.
- Positive axial retention of bearings and intermediate gears.
- Snap-finger deflection, insertion chamfers, fatigue and dimensional coupons.
- Final clamp hardware and shaft anchoring.
- Full all-part interference and assembly-path testing.
- Tooth root strength, wear, startup friction, usable airflow and output loading.
- Clearances under deflection and print-induced eccentricity.

The cap has three rectangular retaining ledges and mating collar pockets to show
the intended attachment. It still needs a lead-in ramp and validated flexure sizing.
Gravity seats components, but a completed mechanism also needs positive retention.
No STL production release is supplied at this stage.

## Files and reproduction

From WSL Ubuntu:

    python3 experiments/stacking_cones/launch.py --render
    ~/Applications/freecad-experiment/squashfs-root/AppRun python experiments/stacking_cones/make_preview.py
    python3 experiments/stacking_cones/launch.py --viewer

The build opens FreeCAD with playback and full-housing/cutaway controls. It saves:
- output/tower_draft.FCStd: editable grouped cutaway assembly.
- output/tower_full.step: full static geometry.
- output/tower_cutaway.step: static cutaway geometry.
- output/tower_overview.png and gear_detail.png.
- output/checks.json and motion.json.
- output/tower_animation.gif after running make_preview.py.

The animation represents imposed gear kinematics, not contact dynamics or airflow.
Numeric properties in DesignParameters document dimensions; edit the macro and
regenerate to change geometry. Native Part features are editable placements/shapes.

## References

Staggered half-pitch two-section gears have precedent; this does not validate this
specific printed design:
https://patents.google.com/patent/US4679459A/en

General tooth-profile reference:
https://khkgears.net/involute-tooth-form/

## Verification completed

All 53 modeled components pass native solid validity checks. Four sampled rotations
show zero tooth-intersection volume for the center/planet and ring/planet pairs.
Sixteen selected spacer, carrier, cap and hex-joint clearance pairs have zero solid
intersection at the saved assembly pose. The cutaway STEP reloads as 149 valid
solids and matches native component volume to about 0.026 parts per million.
The portable animation contains 60 distinct-time frames with verified geometry
motion. See output/checks.json and output/verification.json.

Repeat the independent geometry check using:

    PYTHONPATH=~/Applications/freecad-experiment/squashfs-root/usr/lib ~/Applications/freecad-experiment/squashfs-root/AppRun python experiments/stacking_cones/validate.py
