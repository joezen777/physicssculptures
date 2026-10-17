# P17S scimitar prototype: 144 mm swept diameter, 40 mm blade limit

This is an experimental printable candidate, not a demonstrated performance upgrade or a strength-qualified rotor. Production P17 and the existing print package remain unchanged.

## Package

- P17S_print-1x.stl: three-blade scimitar rotor with original hub/connector.
- P18S_print-1x.stl: replacement guard shroud, 32 mm taller.
- scimitar_40mm.FCStd: CAD assembly with raised P19 grille reference.
- P17S.step and P18S.step: parts in assembly coordinates.
- validation.json: solid/mesh validity, retained hub interface, clearance and geometry.
- airflow_screening.json: explicitly unvalidated analytical comparison.
- inspection_0p2mm.ini and slice_validation.json: geometry-only slicer inspection.
- Preview PNGs: rotor, top, side and guard fit.

Print one of each STL. Reuse the existing P19 grille and top bearing/retainer. Do not mix the extended shroud with the original top spacer.

## Hardware and installation

Use a 500 mm end-to-end M8 threaded rod in the modeled base location (bottom z=-68 mm, top z=432 mm). Replace the old top steel spacer (ID 8.2 mm, OD 12 mm, length 21 mm) with a 53 mm steel spacer from z=359 to z=412. Keep the bearing and fan at their original elevations. Raise the grille, its captured top nut and acorn arrangement 32 mm. Reuse the six M4 x16 grille fasteners at the new flange elevation. Verify actual rod engagement and acorn internal depth on the hardware used; modeled envelopes are not hardware measurements.

The shroud extends from z=340 to412; the raised grille begins at412. The fan blade envelope is z=348 to386.8, leaving 25.2 mm vertical clearance. Nominal shroud inner radius76 minus rotor radius72 gives4 mm radial clearance. Bearing-cap clearance comes from relief to radius 22.6 above local z=11.4; original cap outer radius22 gives0.6 mm nominal radial clearance.

Before powered use, rotate through complete turns by hand and check the printed bearing fit, cap, shaft and housing. Balance the completed rotor and verify that support removal has not damaged roots. Use the guard during low-speed comparative tests.

## Geometry choices

Three swept, cambered shells, with matched clockwise/negative-pitch hand to original P17. Swept diameter 144 mm; stationary bounding-box width is less because only three sectors exist. Blade vertical envelope 38.8 mm, below the 40 mm limit. Including the existing 22 mm downward connector, total part height 60.8 mm.

Root geometric pitch 50 degrees transitions to 22 degrees by radius 31 mm and remains 22 degrees toward the tip. This is geometric pitch, not angle of attack. Sweep advances near midspan and retreats toward the outer edge. Angular chord extent is capped at 118 degrees so neighboring 120-degree sectors remain separated; the envelope and tip lip further limit outer chord.

The blade is a specifically defined cambered shell, NOT an exact Eppler420 section. Mean-surface camber is 1.2 mm*sin(pi*s) in the axial direction; axial skin thickness 2.4 mm gives a smaller normal thickness at steep pitch. This printable compromise has no measured airfoil polar. The outer 1.6 mm radial band incorporates a 10 mm downward lip with overlap into the shell. Geometric projection limits and a gradual base rise keep the lip inside the height envelope. Buried roots reach radius 21 mm to bond into the existing hub.

Calculated projected annular solidity is 0.7854; developed chord-area solidity is 0.8582, excluding lips and measured above radius 22.6 mm. This specifies what 'solidity' means and meets the requested >0.75 criterion. The broad root reaches approximately 37 mm above the original blade reference, rather than prescribing a disconnected high scoop. Section stations and curve interpolation are fully defined in scimitar_geometry.py and build_scimitar.py.

## Calculation

At10 knots with only the three large 80x120 mm sails at 180 mm radius, input friction 2 mN m, and aggregate geared efficiency 0.8:

| Rotor | Nominal calculated RPM | Nominal calculated flow |
|---|---:|---:|
| Original P17 |417|5.92 L/s|
| P17S, hypothetical additional lip-drag coefficient 0-0.05 |369-381|7.10-7.33 L/s|

The nominal analytical improvement is about20-24%. This is NOT a measured gain and NOT a trustworthy performance interval. Independent blade strips with surrogate Cl=scale*sin(2*alpha), Cd=Cd0+2*sin(alpha)^2 do not resolve high-solidity cascade interference, exact camber, sweep, winglets, tip vortices, swirl, floor-to-floor wake interaction or wind crossflow. These omissions could erase the apparent improvement. The model grants no extra lift benefit for camber or winglets. Three surrogate polar cases are saved, with hypothetical added lip drag; neither is calibrated. Compare this rotor physically with original P17 under identical wind and payload before calling it better.

Checks enforce positive induced power below shaft power and numerical torque balance. No CFD, physical airflow, structural, fatigue or startup test has been performed. Fan inertia increases substantially: CAD rotor volume is 51.99 cm3, about 66 g if fully solid PETG at 1.27 g/cm3, before print voids. Startup dynamics were not simulated.

## Print guidance

Use PETG on the Ender 3 V2/Sprite Pro with the actual 0.2 mm nozzle. The inspection profile uses 0.12 mm layers, 0.22 mm extrusion width, five perimeters and supports everywhere. Rotor STL has its connector end on the bed; support the broad undersides and tip lips. Keep support scars away from bearing bores and nut seats, and remove support completely from the blade gaps. The narrow gaps make removal an explicit physical print-trial concern. Shroud STL is upright and needs flange support. Both parts fit within a 220 mm bed with the specified 6 mm brim.

Temperature 240 C and bed 80 C in the inspection profile are starting inspection values, not a calibrated filament/machine recipe. Generated G-code remains outside the package and is not for direct printer execution. No resin alternative is qualified here. First inspect fit and support removability on a print before any sustained operation.

## Rebuild in WSL Ubuntu

Use launch_scimitar.py from this directory's parent. It runs the bundled FreeCAD Python builder, analytical screening, GUI previews, nozzle-specific slicing and ZIP packaging. FREECAD_APP can override the existing local runtime. Sources and package are committed separately from production; no full production rebuild is needed.

Slicer inspection completed successfully for both parts with no warnings; counts in slice_validation.json are layer-change markers including support events, not unique physical heights. Preview images were visually inspected.
