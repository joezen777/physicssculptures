# 1.2 mm PETG prototype

The current separate-parts print release is in experiments/print_petg_12. It preserves the three fan-floor pots, optional curved sail attachment and stationary top grille.

The 1.5-module 96/48/24 draft teeth were replaced by 2-module 72/36/18 staggered teeth at the same pitch radii. Addenda are 0.8 module; nominal external tooth-tip widths are about 1.56 and 1.64 mm. The ratio remains -2 per stage. Stage pitch increased from 88 to 116 mm; male hex connectors increased from 16 to 24 mm AF.

Bearing access is now explicit: P01 caps open the pot, fan and base 608 seats; the sun hub splits into P05/P06 with a removable bottom cap; P08 opens each planet's 604 seat. Captive nut slots, screw-head recesses and metal fastener locations replace draft snap fits. Steel inner-race spacers and a fixed M8 rod provide axial support and carrier reaction. Printed parts are not modeled as threaded bearings.

The print set has 19 production part types plus two bearing-fit coupons. The largest print footprint is 192 mm; STL quantities are generated from assembly instances. Purchased hardware has its own BOM and is not exported as STL.

See [the assembly and printing guide](../experiments/print_petg_12/output/PRINT_AND_ASSEMBLE.md), [the exploded image](../experiments/print_petg_12/output/exploded_assembly_labeled.png), and the JSON verification reports in the output folder. Physical friction, wind startup, structural durability and child access are not validated by these CAD checks.

Final checks passed: 21 single-component closed STL meshes, all footprints within 192 mm; nominal assembly-pair checks across 159 CAD instances; ten sampled gear phases; seven bearing insertion corridors; terminal blade sweep; 96 small-fastener shaft/head envelopes; and PrusaSlicer toolpath generation for every STL using the 1.2 mm inspection settings. The package contains 59 production prints plus two calibration coupons.

## Complete purchased-hardware exploded view (2026-10-02)

The exploded illustration and FreeCAD document now include every required purchased item individually, including screw heads, nuts, washers, axle bolts, and both spacer diameters. The previous view hid small hardware and only listed it; that omission is corrected. The 59 printed assembly instances plus 295 purchased instances give 354 visible objects. Quantity checks are written to exploded_hardware_validation.json.

hardware_view.py supplements the original CAD scene with the 195 previously unrepresented screws, nuts, and cup washers. Geometry is simplified (no helical threads); existing planet axle shafts receive visible heads. The renderer adds these objects idempotently and saves both the assembled and exploded FreeCAD documents. All printing geometry and STL files remain unchanged, so the earlier slicing and mesh checks still apply. The original 159-instance collision report describes the earlier validation scope; this documentation update does not claim a new full collision analysis of all 354 objects.

The full poster includes hardware at each repeated joint plus enlarged cup-to-arm and planet-axle views. The main rod is offset next to the base at actual length; exploded spacing is illustrative. FreeCAD closes after rendering.

The packaging check independently reads hardware_bom.csv, matches every quantity against the annotation instances, verifies all 354 object names in the native exploded document, checks both joint-detail selections, and checks every ZIP entry against its source file. The launcher refreshes the ZIP after rendering.

## Helical gear revision for a 0.4 mm nozzle (2026-10-10)

**Fault in the first print.** The staggered two-row teeth formed a discrete herringbone: row 2 of each gear was offset half a tooth from row 1, separated by a 0.8 mm gap. Rows that are 4.8 mm tall cannot pass each other axially. In a FreeCAD sweep over a full planet tooth pitch in 0.1 degree steps, a planet row straddling both sun rows always overlapped the sun by at least 23.7 mm3; a continuous spur row cleared at 0 mm3. The sun and planets both mount axially (on the M8 rod and the M4 axle bolts), so assembly step 18 could not be performed as written. A forced planet meshes the wrong row, half a tooth out of phase, as seen in the printed fit. The ring was split into halves only so it could be fitted sideways around the rows. The nominal CAD checks validated the final meshed pose but never an assembly path.

**Why not herringbone.** Herringbone shares the same failure: an apex cannot pass axially through a one-piece mate, so sun, planets or ring would have to be split across the face. Herringbone also forces every mesh to the same axial position. Here the sun, three planets and ring are each located by separate stacks of printed parts, nuts and steel spacers. Over-constrained V-teeth would fight those tolerance stacks, causing end-load on the 604/608 bearings and wear. Herringbone works best when one member floats axially, which this layout does not provide.

**Chosen form.** Single-row 15 degree helical gears, module 2 transverse, with unchanged 72/36/18 teeth, 54 mm center distance and -2 ratio. Sun is right-hand; planets and ring are left-hand (external mates take opposite hands, internal mates the same hand). Helical teeth slide together axially while turning, tolerate axial misalignment like spur gears, and add an overlap ratio of 10.4 tan15 / (2 pi) = 0.44 to the transverse contact ratio of about 1.6. Axial thrust is tan15 = 0.27 times tooth force, which is small for wind/fan torques. At each idler planet the sun and ring thrusts oppose, leaving a small tilting couple on the axle bolt. The 0.4 mm nozzle restores full 1.0-module addenda in place of the 0.8-module truncation chosen for 1.2 mm lines.

**One-piece ring.** Each 192 mm ring fits the 220 mm Ender bed, as the pots do. A continuous helical ring is lowered over the planets and turns as it engages, so neither the split nor its dovetails remain. Its flange, bolt circle and outline are unchanged.

Renders: [mesh](../experiments/print_petg_12/output/helical_gear_mesh.png) and [ring being lowered over the planets](../experiments/print_petg_12/output/helical_ring_assembly.png).

**Compatibility.** Only P06, P07 and P09 change; all other STLs and the purchased-hardware BOM are unchanged. The kit is now 56 printed instances. validate.py adds an axial insertion check that lowers a planet into the sun and ring and the ring over a planet in steps from 12 mm to 0, each turned by its helix rate. All 21 STLs generate toolpaths with the 0.4 mm inspection profile.

The resin sprue sheets in experiments/resin_sprues were generated from the previous split-ring gears and are stale for P06, P07 and P09 until that project is rebuilt.
