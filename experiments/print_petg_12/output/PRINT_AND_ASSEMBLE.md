# PETG / 1.2 mm nozzle print prototype

This is the first separate-parts print set for the four-level fan tunnel: three flowerpots with fan floors, optional curved wind-sail arms, and a guarded top fan. Use the files in this folder rather than the earlier modular-fan-tunnel draft. This kit uses 24 mm AF male connectors and a 116 mm module pitch; it is not interchangeable with the older 16 mm / 88 mm parts.

## Start here

1. Print C01 and C02, one each, and check them with the actual 608 and 604 bearings.
2. Print one P07 planet gear and one P08 retainer to check tooth quality, nut fit and the removable bearing seat.
3. Print the remaining quantities listed in print_manifest.csv. The suffix in each STL name is the TOTAL required quantity, not a plate containing that many copies.
4. Follow the linear assembly order below. The labeled exploded image uses the same P01-P19 part IDs as the files.

Every STL is one separate, closed part. Dimensions are millimeters. Import at 100% scale. Files are already resting at Z=0 in the intended print orientation; center each part on the bed. The largest individual footprint is 192 x 192 mm, leaving room for a 4 mm brim on the specified 220 x 220 mm bed. The assembled sails extend beyond that footprint but print as separate arms and cups.

This is a fit-test prototype. Nominal CAD and slicer checks do not replace a physical bearing-fit trial, load test or airflow test. The top guard has not been certified for children's access or impact resistance.

## Print settings and fit

Material: PETG. Nozzle: 1.2 mm. The toolpath check used 0.4 mm layers, 1.32 mm nominal extrusion width, Arachne perimeters, three perimeters, six top/bottom layers, 30% gyroid infill and a 4 mm brim. A conservative 5 mm3/s flow ceiling was used for inspection; calibrate the actual hotend and filament rather than assuming a large nozzle permits high flow.

The inspection configuration uses 240 C nozzle / 80 C bed as provisional values. Use the filament manufacturer's temperature range and a suitable PETG bed-release method for your actual build surface. The supplied slicer_check.ini is an inspection configuration, NOT a tested Ender start/end G-code profile. No machine-ready G-code is included.

C01 has 22.2, 22.4 and 22.6 mm holes, left to right along its long edge. C02 has 12.2, 12.4 and 12.6 mm holes in the same order. Production bearing pockets are nominally 22.4 and 12.4 mm. Bearings should seat without splitting the housing; screw-on retainers provide axial capture. Correct flow/hole compensation and reprint the coupon if the middle hole does not fit. Do not scale the whole assembly to correct bearing fit.

The coarser gears use module 2, 72 ring teeth, 36 sun teeth and 18 planet teeth. Both rows remain staggered. Truncated addenda give approximately 1.56-1.64 mm external tooth-tip widths, sufficient to retain a toolpath with this nozzle in the checked slicer. The speed ratio remains -2 per stage. This tooth form still needs a physical mesh and wear trial.

Walls, fan blades and grille rings are generally 3.6 mm or thicker; some local bearing lips and nut-pocket margins are thinner. Small inner-race spacers are specified as STEEL TUBE rather than thin printed tubes. There are no printed bearings or printed load-bearing axle threads.

## Supports and finishing

Use the support/orientation columns of print_manifest.csv. The pot/fan bodies, top fan, cup undersides, sail-arm undersides and some sun-housing/flange overhangs need supports. These STLs are not a support-free release.

The supplied orientation places the pot upright with its male connector downward; keep the bearing seat and nut pockets clear of support scars. The sun socket, ring halves, collars, base and shroud are supplied inverted where that gives a better bed face. Inspect support placement before printing; do not fill bearing pockets or captive-nut slots unnecessarily. Remove support and strings fully from the airflow path and tooth rows.

Deburr the hex connectors, bolt holes and tooth edges. Do not force binding gears with the wind sails. Metal tube ends must be square and burr-free. Target the listed spacer lengths within about 0.1 mm for the first fit trial, then confirm free rotation and end play in the actual assembly.

## Purchased parts

See hardware_bom.csv for exact quantities. Bearings, fasteners, threaded rod and steel spacers are purchased parts, not STLs.

- 11 x 608 bearings (8 x 22 x 7 mm); 9 x 604 bearings (4 x 12 x 4 mm).
- 1 x M8 threaded steel rod, cut to 468 mm, deburred; 9 x M8 hex nuts and 1 x M8 acorn nut.
- 9 x M4 x75 planet-axle bolts, 18 x M4 axle nuts and 9 x M4 washers of approximately 7 mm OD.
- 24 x M3 x16 socket-head screws for the eight 608 retainers, plus 9 x M3 x20 socket-head screws for the three split sun housings; 33 x M3 nuts total.
- 27 x M2.5 x16 screws and 27 x M2.5 nuts for the planet retainers.
- 18 x M4 x20 socket-head bolts for ring halves/collars, plus 3 x M4 x20 for the sail hub.
- 6 x M4 x10 BUTTON-HEAD screws for the recessed sail-arm roots. Do not replace them with taller heads or longer shafts without checking the clearances.
- 3 x M4 x25 socket-head cup bolts and 3 x M4 washers of approximately 9 mm OD.
- 6 x M4 x16 socket-head guard bolts.
- 54 x M4 nuts total, INCLUDING the 18 axle nuts already listed above.
- Steel tube ID8.2 / OD12: 12.5 mm x1; 32 mm x1; 15 mm x3; 5.9 mm x3; 11 mm x3; 44.6 mm x3; 21 mm x1.
- Steel tube ID4.2 / OD6: 37.2 mm x9 and 10 mm x9.

The main shaft and planet bolts remain stationary. Bearings rotate around clamped inner races; the threaded stock is not intended as a rotating journal. Tighten against the metal spacer/inner-race stack gently and confirm free rotation. The plastic housings and caps must not be crushed to remove end play.

## Linear assembly order

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

Every required purchased component is shown separately in the exploded image: 295 bearings, fasteners, washers and steel spacer/shaft pieces alongside 59 printed assembly parts. Gray hardware is labeled by specification, count at that location, and joint. Enlarged planet_joint_labeled.png and cup_joint_labeled.png views show the two small connection stacks in detail. The M8 rod is offset beside the base at its actual 468 mm length; the much taller exploded layout is not a shaft-cutting dimension. Threads and fastener details are simplified. The numbered assembly sequence above specifies insertion and tightening order.

## Design and verification references

604 and 608 boundary dimensions: SKF rolling-bearing catalog, https://cdn.skfmediahub.skf.com/api/public/0901d196809a65c0/pdf_preview_medium/0901d196809a65c0_pdf_preview_medium.pdf

Nozzle/profile guidance: Prusa Knowledge Base, https://help.prusa3d.com/article/creating-profiles-for-different-nozzles_127540 and https://help.prusa3d.com/article/layers-and-perimeters_1748

Reports in this folder record closed STL meshes, bed envelopes, sampled gear phases, nominal assembly clearances, bearing insertion paths, screw-head/shaft envelopes and toolpath generation. They do not establish aerodynamic performance or a physical safety rating.

## Rebuild from source

From WSL Ubuntu, run python3 experiments/print_petg_12/launch.py --slice-check. This uses the bundled FreeCAD runtime and the local PrusaSlicer cache. The render window closes automatically. To regenerate only the CAD views and labeled image, use --render-only.
