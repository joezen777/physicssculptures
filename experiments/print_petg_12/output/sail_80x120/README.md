# Larger wind-sail retrofit: P15 / P16
Print **3 of each STL**, at 100% scale in millimeters. Each file contains one part.

- P15_arm_180mm_print-3x.stl: Krull-inspired swept crescent arm with a curved reinforcing spine, original P14 root and screw holes, and keyed sail saddle.
- P16_scoop_80x120mm_print-3x.stl: 80 mm wide, 120 mm tall half-cylinder scoop, 3.2 mm shell and reinforced rims.
- P15_P16_sail_80x120.FCStd: editable replacement geometry in assembly coordinates.
- assembly_with_sails.FCStd: full assembly preview with replacements.

P14 is unchanged. These replace only P15/P16; keep the original files for comparison. Approximate swept diameter is 440 mm. The scoop bottom is 32 mm above the original base-foot bottom. Frontal area is 96 cm2 per sail; its nominal tangential force lever is 180 mm.

## Hardware and assembly
Reuse the six M4 x10 BUTTON-HEAD root screws and nuts at P14.
Use **three M4 x30 steel socket-head bolts**, three OD9 M4 washers and three M4 nuts for the scoops (one set per scoop). The longer bolts replace the original M4 x25 cup bolts.

Fit each P15 root to P14 with its original two screws. Seat the rectangular P16 boss between the P15 cheeks (0.30 mm clearance each side). Insert the M4 x30 bolt from behind the arm, through the 4.5 mm bore. Fit washer and nut inside the scoop. Keep all openings in the same tangential direction as shown in sails_detail.png. Tighten just enough to seat the PETG; the saddle cheeks resist twisting. Check bolt protrusion and free rotation manually.

The bolt's printed grip is approximately 21 mm at the bore; the washer/nut stack is about 4 mm, leaving roughly 5 mm of thread with an M4 x30 bolt. Actual hardware dimensions must be checked.

## PETG printing
Files are already oriented and rest at Z=0. P15 prints horizontally with support beneath its raised arm/root and tabs. P16 prints upright on its bottom rim, with support under its mounting boss and overhanging features. Enable supports everywhere where needed, not only from the bed. Keep supports out of screw bores and root recesses where practical.

The included 0.2 mm nozzle / 0.12 mm layer profile is for geometry inspection, matching the repository's listed Ender nozzle. It is NOT a calibrated printer profile. Use your actual installed nozzle and tested PETG temperatures/flow. Allow a brim; inspect the slicer preview. No machine-ready G-code is supplied. Remove supports and deburr the bores; do not scale parts to correct fit.

## Verification and limits
See validation.json and slice_validation.json. Checks cover valid single solids, closed meshes, exact root preservation, P14 fit, arm/scoop fit, inter-arm separation and 10-degree sampled rotation against the existing CAD assembly. The original assembly's supplemental hardware illustrations are not a complete fastener collision certification for this retrofit.
P14's original STL hash is recorded. Full structure, fatigue, PETG creep, gust loading and physical aerodynamic performance are not verified. Larger sails increase load on the unchanged hub. Test at low wind first and resolve rubbing/binding before use.

The prior theoretical torque comparison is in docs/print_petg_12_sail_options.md. Coefficients were assumed, not measured; these STLs do not establish the predicted performance.

## Rebuild
From WSL Ubuntu with the existing FreeCAD runtime:
env PYTHONPATH=$HOME/Applications/freecad-experiment/squashfs-root/usr/lib $HOME/Applications/freecad-experiment/squashfs-root/AppRun python experiments/print_petg_12/build_sail_80x120.py
python3 experiments/print_petg_12/finish_sail_80x120.py
