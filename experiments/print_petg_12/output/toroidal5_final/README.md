# Toroidal5 selected top fan — revised PETG supports

Chosen for appearance, not as a proven aerodynamic winner. Units: mm.

P17's hub/casing alone includes -0.15 mm horizontal expansion as CAD geometry. The outside casing radius is 21.85 mm; the male drive hex is 23.7 mm AF; the axial bore is 12.9 mm diameter; the bearing pocket is 22.7 mm diameter; the three screw holes are 3.9 mm diameter; and the three nut traps are 6.1 mm AF. The P06 mating socket remains 24.6 mm AF, giving 0.45 mm nominal clearance per hex flat. Fan blades and the existing integrated support mesh are unchanged. Set Cura Horizontal Expansion to 0.00 mm to avoid applying compensation twice.

Print ONE fan: `P17_top_fan_B_integrated_supports_print-1x.stl` includes removable supports; `P17_top_fan_B_print-1x.stl` is the bare alternative. Keep the supplied orientation (hex drive down). Do not split the supported STL into objects or drop its shells individually onto the bed. Custom supports are ordinary model geometry: in Cura Preview they appear as walls/skin, not as Cura-generated support.

## Cura 5.8.1 / 0.6 mm nozzle / 0.25 mm layers

Select your existing calibrated printer and PETG profile, set nozzle 0.6 mm, layer AND initial layer 0.25 mm, line width 0.66 mm, four walls, five top/bottom layers, 30% infill. Disable Generate Support and adaptive layers. Leave Remove All Holes OFF. Use normal surface mode, no raft; no auto orientation. The supplied Prusa INI is NOT a Cura profile. `cura_settings.json` documents the separate engine inspection, not a machine-ready profile or G-code.

Revised support ribs are 1.32 mm thick, on 2.4 mm spacing, with short removal segments and bed combs. The nominal vertical release gap is 0.50 mm (two layers); local sloping surfaces and layer rounding increase it. Supports also occupy the passages beneath raised arms. Do not print an earlier downloaded copy with the same filename.

First print `C03_PETG_support_release_025_050_075.stl`: the three coupons use 0.25 / 0.50 / 0.75 mm gaps from left to right. Test PETG release and underside sag before committing to the fan. The coupon does not replace a complete fan print trial. If the 0.50 mm coupon fails, adjust the CAD gap and regenerate; Cura's Support Z Distance does not change built-in support geometry. Starting inspection speeds: outer wall 20, inner wall 25, first layer 15 mm/s. Use temperatures and cooling calibrated for your PETG.

Inspect Cura Layer Preview before printing: the bed combs and tall rib walls must appear under all five outer wings and within raised-arm passages. After cooling, cut/peel the base combs into sections and withdraw the short ribs through the openings. Remove every loose fragment, deburr, check balance and hand-rotate through a full revolution before operation. Support removal and print strength are not physically validated.

## Guard and hardware

`P185_print-1x.stl` is the finalized 72 mm tall P18 shroud/collar, oriented flange-down. It is also installed in production under `P18_top_guard_shroud_print-1x.stl`; print only one of these identical files. No supports are intended for this orientation.

Use the 500 mm end-to-end M8 rod and a top steel spacer ID8.2 / OD12 / length53 mm, replacing the former21 mm top spacer. P19 mounts 32 mm higher. Its shape is unchanged, so an existing `P19_curved_guard_grille_print-1x.stl` print can be reused. Reuse six M4x16 guard bolts; check actual nut engagement and acorn internal depth during assembly.

The fan sweeps144 mm; nominal guard radial gap4 mm; blade-to-grille vertical gap27.4 mm. The mounting interface matches the original inside radius20.9 mm. These are CAD clearances, not measured as-printed tolerances.

## Scientific status

The previous toroidal candidate had a degenerate return loft that silently lost one arm per pair. This release corrects that topology and verifies five closed passages. Old toroidal CFD meshes and any partial results do not represent this release. No validated airflow ranking exists. A future long analysis must remesh this finalized geometry and include convergence and physical measurement validation.

See geometry, support, slicing and integration JSON reports for the actual checks. Old full-assembly images/exploded files depict the prior top assembly and are superseded for these parts.

Cura engine verification completed at0.6 mm /0.25 mm with support paths in all five outer sectors at Z10,25,35,45 mm; see cura_support_toolpaths.png. Cura emitted an overlapping-face warning on fine triangulation. The mesh is watertight and model/support intersection volume is zero; the warning is retained in the report. The original failed Cura profile was not reproduced, so the exact cause of that omission remains unconfirmed.
