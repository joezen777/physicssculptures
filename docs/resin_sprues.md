# Resin sprue sheets

> Stale since 2026-10-10: these sheets predate the one-piece helical P06/P07/P09 gear revision in print_petg_12. Rebuild before printing the gear sheets.

Target: Anycubic Photon Mono M5s, 218 x 123 x 200 mm; Anycubic ABS-Like Resin Pro 2. The user requested sprue sheets with embossed 12-point part labels on the disposable skeleton.

## Geometry and layout

The new folder is nested in the existing STL directory: experiments/print_petg_12/output/stl/resin_sprue_sheets. The PETG STL files remain unchanged. The source is the saved FreeCAD assembly, with assembly rotations removed before applying resin sheet orientations. The fit coupons are regenerated from their original dimensions.

The 19 sheet types reproduce the full 59-piece production kit plus both coupons. Filename quantities specify complete sheet copies. Repeated small parts share sheets; the original large parts stay full-size. The pots fit edge-on at 215 x 114.4 x 198 mm including their frames. This leaves only 2 mm of extra Z clearance; the slicer must not silently add excess lift or raft thickness.

Frames use 2.4 mm rails and a 6 mm part lift. Each part is connected through sacrificial stems with 0.9 mm necks. Anchor selection uses downward-facing tessellation candidates and exact CAD ray intersections. Tall unsupported sprue stems are avoided; additional print supports are required. Gear sprue candidates use original lower end faces rather than active tooth flanks. The boolean union uses a 0.0001 mm tolerance, below print resolution.

Each individual part has an adjacent raised label. Bold type uses 12 x 25.4 / 72 = 4.233 mm nominal CAD font height and 0.8 mm positive emboss. Letters are fused solids in the STL, not artwork or recessed text.

## Printing and fit

This is an unsliced resin conversion, not a pre-supported print profile. Sprues organize and connect the kit; they do not guarantee that every blade, tooth, wall or grille island is supported. The README requires layer inspection and additional support placement.

Functional dimensions and bearing clearances are unchanged. Test C01/C02 after the intended post-cure workflow. No guessed global shrinkage compensation is applied. Purchased steel hardware is retained. Solid-wall construction introduces no new sealed hollow chambers, at the cost of about 2.39 liters of resin for production parts before sprues and supports.

## Verification and reproduction

Each exported sheet must be a valid connected CAD solid and a closed single-component mesh inside the printer envelope. Sheet contents times copy counts must match the original print manifest. The packager verifies STL hashes and label sizes, then verifies ZIP bytes against source files.

Run python3 experiments/resin_sprues/launch.py from WSL for the full build/render/package workflow. FreeCAD closes after rendering. Use --render-only to reuse existing geometry. Reports describe geometric checks; exposure, cured fit, support reliability and resin mechanical performance require physical trials.

Primary printer and resin references are linked in the sheet README.

Final export: 19 sheet STL files, 30 total sheet copies, 59 production pieces and two fit coupons. All sheets passed solid/mesh, quantity and bed-envelope checks. CAD resin volume including coupons and sprues is approximately 2.664 liters before additional supports and waste. Raised lettering was visually inspected in the native CAD render.
