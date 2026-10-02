# Resin sprue sheets — Photon Mono M5s

Material: Anycubic ABS-Like Resin Pro 2. Each STL is one connected sprue sheet, with the part IDs raised on the disposable frame beside the parts.

## Print these files

Use the R01–R19 STL files in this folder. The filename suffix is the number of copies of the **complete sheet**, not the number of loose parts. For example, R07 contains nine P07 planet gears; print that sheet once. R09 contains one P09 ring half; print that sheet six times.

Together the sheets provide all 59 production pieces and the two bearing-fit coupons. The parts keep the same P01–P19 and C01–C02 IDs as the existing assembly guide and exploded image. Bearings, steel spacers, shaft, bolts, nuts and washers remain purchased hardware.

| Sheet | Parts on one sheet | Print sheets |
|---|---|---:|
| R01 | P01 ×8 | 1 |
| R02 | P02 ×1 | 2 |
| R03 | P03 ×1 | 1 |
| R04 | P04 ×1 | 3 |
| R05 | P05 ×3 | 1 |
| R06 | P06 ×1 | 3 |
| R07 | P07 ×9 | 1 |
| R08 | P08 ×9 | 1 |
| R09 | P09 ×1 | 6 |
| R10 | P10 ×1 | 2 |
| R11 | P11 ×1 | 1 |
| R12 | P12 ×1 | 1 |
| R13 | P13 ×1 and P14 ×1 | 1 |
| R14 | P15 ×3 | 1 |
| R15 | P16 ×3 | 1 |
| R16 | P17 ×1 | 1 |
| R17 | P18 ×1 | 1 |
| R18 | P19 ×1 | 1 |
| R19 | C01 ×1 and C02 ×1 | 1 |

## Labels and sprue construction

- **12-point lettering**, using a nominal CAD text height of 4.233 mm (12 × 25.4 / 72), DejaVu Sans Bold.
- Letters project **0.8 mm above** their label plaques. These are embossed solids, not etched recesses.
- Each individual part has its own ID on the adjacent frame.
- The open frame and runners are 2.4 mm thick. Parts start 6 mm above the build plane.
- Sacrificial stems taper to 0.9 mm diameter connections. Trim these carefully; do not twist a finished part off the frame.
- The frame is a disposable carrier, not a part of the finished turbine.

## Slicer preparation

1. Print the R19 coupon sheet first, using the same resin, exposure and post-cure workflow intended for the gears.
2. Import each sheet in millimeters at **100% scale** and retain its exported orientation. Center it on the bed.
3. Use the Photon Mono M5s profile (218 × 123 × 200 mm), with an ABS-Like Resin Pro 2 profile for the actual resin color. Start calibration at 0.05 mm layers. Exposure, lift/retract and support strengths must be calibrated on the machine.
4. **Add and inspect final resin supports.** The built-in sprue stems hold the kit together; they are not a complete overhang/island support solution. Inspect every layer, including the fan blades, upper tooth row, pot wall, ring and grille. Add supports to sacrificial runners where practical and use non-mating faces for additional contacts.
5. Keep support contacts off bearing-seat cylinders, hex fit faces and active gear flanks. Clean all nut pockets and through holes.
6. R02/R03 are 198 mm tall including their 6 mm sprue lift. They have only **2 mm of height left** in the 200 mm envelope. Do not let auto-lift or a thick added raft push the sheet beyond the printer's build volume. The frame already starts at Z=0; check the complete sliced plate, including any added raft.
7. R02/R03 should be printed individually. Retain the supplied edge-on orientation and confirm adequate supports along the growing shell and fan blades. Large solid parts and long stems need careful support planning.
8. Keep the modeled openings clear for draining and washing. The files retain their original solid walls and open passages; no new sealed hollow cavities were introduced. Do not auto-hollow the hubs or base without designing drainage and inspecting the resulting internal cavities.
9. Wash, remove supports/sprues, finish contact marks, dry and post-cure according to the resin maker's instructions. Check the coupons after the same post-cure treatment.
10. Check 608 and 604 bearing fits, then print and test the geared parts before committing to the large sheets. Use local compensation/recalibration if necessary; do not scale the whole kit to change bearing fit.

The parts alone use about **2.39 liters of solid resin**, before coupons, sprues, additional supports and process waste. The manifest records CAD volume per sheet; actual resin consumption will be higher.

## Dimensions and assembly

The functional parts are 1:1 copies of the PETG prototype's CAD geometry, remeshed for resin. Only orientation, position and removable sprues were added. No global shrinkage percentage is baked in. Bearing pockets remain 22.4 mm and 12.4 mm nominal; test C01/C02 first.

Use [the numbered assembly guide](ASSEMBLY_GUIDE.md), [the complete exploded image](assembly_reference.png), and [the purchased hardware list](hardware_bom.csv). The image retains its original PETG title; it is an assembly reference for the same geometry. Use this README for resin printing.

## Verification and scope

The generator checks each sheet's CAD solid, closed STL mesh, connected-component count, complete kit quantities, 12-point label metadata, and build-volume envelope. The STL files are **unsliced**, and additional resin supports are required. These checks do not establish exposure calibration, support reliability, dimensional accuracy after curing, or mechanical durability in resin. No physical resin print has been tested yet.

Files:
- sprue_manifest.csv — sheet quantities, included part IDs, dimensions and resin volumes.
- sprue_manifest.json — detailed placements, raised-label and sprue connection data.
- validation.json — geometry and quantity check results.
- sprue_sheets_preview.png — visual index of the sheets.
- embossed_labels_detail.png — close view of the actual raised CAD lettering.

## References

- [Anycubic M5s build-volume specification](https://store.anycubic.com/blogs/3d-printing-guides/anycubic-photon-mono-m5s-vs-photon-mono-m5)
- [Anycubic ABS-Like Resin Pro 2](https://store.anycubic.com/products/abs-like-resin-pro-2)

Regenerate from WSL using the bundled FreeCAD Python runtime with experiments/resin_sprues/launch.py. The generator reads the original CAD without changing the PETG STLs.
