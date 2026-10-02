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
