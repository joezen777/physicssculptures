# Hardware sprues — resin fit prototypes

These are the screws, bolts, nuts, washers and tube spacers from the turbine hardware list, arranged on removable sprues. They are the requested **hardware kit**, not the turbine's plastic housings, gears or fans.

Target: Photon Mono M5s with Anycubic ABS-Like Resin Pro 2. Every item has a raised 12-point size label on the nearby sprue frame. Letters are embossed 0.8 mm above the tag, not etched.

The files provide **274 hardware pieces in the bill-of-material quantities**, plus eight calibration pieces on H00. Resin fasteners and spacers are for fit and assembly trials; use the original metal hardware for running or loading the turbine. The files do not give resin the strength, stiffness or wear resistance of the steel parts.

## Print H00 first

H00 contains one short screw and matching nut for each thread size: M2.5, M3, M4 and M8. Print, wash, dry and post-cure this sheet with the intended resin process, then check that each nut starts and runs freely. Check against purchased hardware too if mixing resin and metal.

Threads are actual modeled right-hand helices, using the nominal coarse pitches:
- M2.5: 0.45 mm
- M3: 0.50 mm
- M4: 0.70 mm
- M8: 1.25 mm

The truncated 60-degree thread approximation includes a prototype fit allowance: external surfaces are offset inward by 0.025 mm radially; female thread cavities are offset outward by 0.075 mm. This gives a nominal 0.10 mm radial allowance. These are not tolerance-class-certified fasteners. Exposure and cure shrinkage still need calibration; no global model scaling is applied.

Start calibration at 0.025 mm layers to resolve the small M2.5/M3 threads. Use the resin manufacturer's profile for the actual bottle/color and tune exposure on the printer. If H00 binds, correct the process or regenerate the thread allowance before printing the entire kit. Do not force small resin threads.

## Sheet quantities

The filename suffix is the number of copies of the **whole sprue sheet**. It is not the number of individual pieces on that sheet. Multiple small sheets may be arranged on one build plate after checking clearance.

| Sheet | Contents of one sheet | Sheet copies | Hardware total |
|---|---|---:|---:|
| H00 | Four short test screws + four nuts | 1 | 8 calibration pieces |
| H01 | M2.5 x16 screws x9 | 3 | 27 |
| H02 | M3 x16 screws x8 | 3 | 24 |
| H03 | M3 x20 screws x9 | 1 | 9 |
| H04 | M4 x20 screws x7 | 3 | 21 |
| H05 | M4 x10 low button-head screws x6 | 1 | 6 |
| H06 | M4 x25 screws x3 | 1 | 3 |
| H07 | M4 x16 screws x6 | 1 | 6 |
| H08 | M4 x75 fully threaded axle bolts x3 | 3 | 9 |
| H09 | M2.5 nuts x9 | 3 | 27 |
| H10 | M3 nuts x11 | 3 | 33 |
| H11 | M4 nuts x18 | 3 | 54 |
| H12 | M8 nuts x9 | 1 | 9 |
| H13 | M8 acorn nut x1 | 1 | 1 |
| H14 | OD7 washers x9 and OD9 washers x3 | 1 | 12 |
| H15 | ID8.2 / OD12 spacers, assorted lengths | 1 | 15 |
| H16 | ID4.2 / OD6 spacers: L37.2 x9 and L10 x9 | 1 | 18 |

H15 contains lengths 12.5 x1, 32 x1, 15 x3, 5.9 x3, 11 x3, 44.6 x3 and 21 x1, all in millimeters.

The 54 M4 nuts already include the 18 axle nuts. Do not add 18 more.

## Reading the embossed labels

- M3x16: nominal thread size and under-head screw length.
- M4x10 B: the low button-head arm screw; head height is 2.2 mm.
- M4 N: M4 nut.
- M8 CAP: the acorn nut.
- W7 / W9: washer outside diameter, with 4.2 mm bore and 0.8 mm thickness.
- 8.2/12x44.6: tube ID 8.2 mm, OD 12 mm, length 44.6 mm.
- 4.2/6x10: tube ID 4.2 mm, OD 6 mm, length 10 mm.

Font: DejaVu Sans Bold, 12-point equivalent nominal CAD text height of 4.233 mm. All labels are on the sacrificial frame so the hardware itself stays identifiable without adding text to its mating surfaces.

## Slicing and removing sprues

1. Import at 100% in millimeters and retain the supplied orientation.
2. Center the sheet on the 218 x123 x200 mm bed.
3. The 2.4 mm frame starts at Z=0; label pads are 2.6 mm thick. Hardware is lifted 6 mm and attached through 0.7 mm sacrificial necks.
4. The sprue connections are not a complete resin support solution. Inspect the sliced layers and add supports where needed, especially under head, washer and tube end faces.
5. Keep support contacts and sprue trimming away from thread flanks, drive sockets and tube bores. Existing sprue contacts are placed on head faces, nut end faces, washer faces or tube end faces.
6. Clip each connection carefully and finish the remaining nub. Do not twist a long screw or thin tube off the frame.
7. Wash and post-cure per the resin maker's instructions. Inspect threads, sockets and spacer ends after curing.
8. Use only light finger assembly for these fit prototypes. Long resin axle bolts and thin resin spacers are not substitutes for loaded steel shafts and spacer stacks.

## Still purchased

- 11 x 608 bearings.
- 9 x 604 bearings.
- 1 x M8 threaded steel main rod, 468 mm long.

These are not included as resin copies. The main rod cannot fit the M5s as one piece, and it has not been redesigned into a segmented shaft.

## Checks and files

All sheets are checked for valid connected Manifold solids, closed one-component STL meshes, build-volume fit, exact hardware counts and raised-label size. Screw/nut CAD engagement is checked at three rotational positions for all four thread sizes. These tests do not establish physical thread fit or load capacity.

- sprue_manifest.csv / .json: sheet quantities, item sizes and dimensions.
- validation.json: CAD and quantity checks.
- hardware_sprues_preview.png: sheet index.
- embossed_labels_detail.png: screw threads and raised-label close-up.
- spacers_detail.png: tube spacer close-up.
- original_hardware_bom.csv: the source hardware list.

The earlier plastic-body sprues remain in the separate resin_sprue_sheets folder. This folder is resin_hardware_sprues.

## References

- [Accu metric coarse thread dimensions](https://www.accu.co.uk/p/117-iso-metric-thread-dimensions)
- [Anycubic M5s build-volume specification](https://store.anycubic.com/blogs/3d-printing-guides/anycubic-photon-mono-m5s-vs-photon-mono-m5)
- [Anycubic ABS-Like Resin Pro 2](https://store.anycubic.com/products/abs-like-resin-pro-2)

Rebuild from WSL with python3 experiments/resin_hardware_sprues/launch.py. FreeCAD closes automatically after rendering.

The FreeCAD document contains the exact mesh geometry arranged for viewing. Thread geometry is generated analytically in mesh_build.py (48 angular samples, 64 for M8; 24 axial steps per pitch). Mesh simplification tolerance is 0.002 mm. No screw, nut, washer or tube is split into separate assembly pieces.
