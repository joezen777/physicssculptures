# Krull arm-joint variants
Date: 2026-10-11. PETG printed components; steel fasteners and compression sleeves.
These are separate variants. Do not mix T15 extension parts with S14/S15 permanent parts.

## A. Temporary extension for installed ORIGINAL short P15 arms
Use this version if the original approximately 108 mm-radius arm and cup tab are already attached to P14 and cannot be removed. This does not fit the later full-length 180 mm P15 as an extension.
The original small cup and its side bolt must be removable. No root bolts, drilling or changes to the installed P14/P15 are required.

Print three T15_extension and three T15_closing_cap parts. Each STL contains one part.
Gray in the preview is the original arm/hub; blue is the lower cradle and crescent extension; orange is the closing cap. The gold P16 is the existing 80 x 120 mm scoop.

The lower cradle follows the old arm over approximately 32 mm of radial span, surrounds the old upright tab and connects to the swept crescent extension. The cap closes over the arm from above. Broad bottom, side and top bearing faces resist bending and twisting after their fit clearance is taken up. The old cup-hole bolt retains the assembly rather than being its only geometric load path. Clearance is nominally 0.4 mm per face; this is not a claim of equal pressure everywhere. Reject a fit that rocks excessively or requires force.

Assembly:
1. Support each old arm while removing the three small cups and their M4 side bolts; leave all P14 root screws alone. Then fit one extension at a time.
2. Hold the blue cradle approximately 25 mm below its final position and bring it inward from the side, through the gap ABOVE the base. Then raise it around the outer arm and tab. Do not try to push it upward through the stationary base.
3. Lower the orange cap from above. Align the old 4.5 mm cup hole with both new cheek holes.
4. Fit one M4 x25 steel bolt with an OD9 M4 washer under the head, then an OD9 washer and M4 nut on the opposite side. A prevailing-torque nut is suitable if its actual height fits the available thread; hold the head while tightening. Do not use tightening force to close a poor-fitting joint.
5. Attach the larger P16 scoop using the M4 x30 bolt with OD9 washers under both the head and nut.
6. Turn the full mechanism by hand and check the overlap, bolt access and scoop clearance before applying wind.

Per three-arm retrofit, root hardware unchanged:
- 3 M4 x25 joint bolts (the old cup bolts may be reused if undamaged).
- 6 OD9 M4 washers and 3 M4 nuts for the extension joints.
- 3 M4 x30 bolts, 6 OD9 washers and 3 M4 nuts for the large scoops.
- 3 unchanged P16 scoops: P16_scoop_80x120mm_print-3x.stl is included in each ZIP and remains in ../sail_80x120/. Reuse the large scoops if already printed.

The grip at the extension bolt is about 14.8 mm; two 0.8 mm washers and a 3.2 mm nut consume about 19.6 mm of its 25 mm length. Check actual purchased dimensions. The cap is a load-sharing structural part, not optional decoration.

The old short arm/root still carries the increased bending moment and wind torque. This temporary adapter cannot strengthen that already-printed root. Physical fatigue and gust capacity are untested.

## B. Permanent S14/S15 side-access socket
Print one S14_side_access_hub and three S15_side_access_arm parts.
This replaces P14 and P15 together; it is not a drop-in arm for the original P14.
P16 and the 180 mm nominal sail lever stay the same. The Krull swept-crescent arm outline is retained.

Each arm slides radially into a closed socket. Its tongue engages approximately 39.6 mm, with 0.3 mm clearance per face. The socket floor, roof and side walls distribute bending/twist reactions over the overlap; two lateral bolts at radial positions 49 and 65 mm retain each arm. The bolt heads and nuts face the sides, not the top/bottom. Both require horizontal tool access.

Two STEEL sleeves per arm, ID4.2 / OD6 / nominal length24 mm, go through the aligned 6.3 mm bores. These are purchased/cut hardware, not printed tubes. Their ends must be square, deburred and matched to the measured assembled joint width. The washers must bear on both sleeve ends: sleeves too short allow PETG compression; sleeves too long leave excessive joint play. Fit before final tightening. These sleeves limit bolt-clamping compression, not all PETG creep.

Assembly:
1. For a future rebuild, remove the old P14/P15 assembly. This is not the no-disassembly temporary solution.
2. Mount S14 on P13 using the existing three M4 x20 adapter bolts. The central hex and those three adapter-bolt locations are preserved. These adapter bolts retain their original orientation; only the two bolts per ARM were moved to side access.
3. Slide each S15 tongue into its radial socket until both holes align.
4. Insert two steel compression sleeves laterally.
5. Fit two M4 x35 bolts, each with an OD9 M4 washer under its head and another under its externally accessible nut.
6. Fit P16 using M4 x30 hardware with a washer under both head and nut as above. All scoop openings must face the same tangential sense.

Three-arm root-joint hardware:
- 6 M4 x35 steel socket-head bolts.
- 12 OD9 M4 washers.
- 6 M4 nuts (check actual nut height/thread engagement).
- 6 steel tube sleeves ID4.2 / OD6 / nominal length24 mm.
- Original three M4 x20 P14-to-P13 bolts/nuts reused.
Scoop hardware is additional, same as variant A.

Do not install M4 bolts in the oversized side bores without their sleeves. Do not glue the detachable overlap; it must remain serviceable.

## Printing and verification
PETG, actual installed nozzle. STLs are placed at Z=0 and oriented for inspection; supports are required. In particular, clean supports from temporary cradle faces and the permanent socket roof, bores and tongue. Do not scale for fit. Print one joint first and trial-fit it on an accessible spare/test arm if available before committing to all three.

The 0.2 mm nozzle / 0.12 mm layer inspection profile generates toolpaths but is not calibrated machine G-code. Choose a PETG profile suited to the actual printer/nozzle; inspect all supports and remove them without damaging the fit surfaces. Side arm tongues print flat for continuous layers along the load path. The hub's closed pockets require accessible removable support from their open ends.

installation_validation.json checks the sampled side-entry/lift path with the original tower assembled and the small cups removed. validation.json records single-solid/closed-mesh checks, installed-fit checks, sampled cap/cradle insertion paths, radial withdrawal, neighbouring-arm clearance, hardware/sleeve clearance and horizontal tool-access envelopes. Rotation was sampled every30 degrees; co-rotating shapes need only one relative check. Simplified tool envelopes are not a guarantee that every wrench fits. Full supplemental hardware, tolerances, physical strength, creep and fatigue remain unqualified.
Previews show simplified steel hardware without actual thread forms. The scoop-attachment bolts are not modeled in every overview.
Both variants preserve the original files in the earlier print folders.

## P04 settling is a separate issue
The current P04 design captures an M8 nut underneath, has another M8 nut above, and supports the stationary planet axles. The intended bearing clamping path uses steel spacers against stationary bearing INNER rings. These arm variants do not change P04 or establish the cause of its downward movement.

The reported symptom could involve nuts moving on the rod, movement of P04 around its captive nut, printed-part compression, incorrect spacer contact or some combination. Do not assume glue proves the underlying stack is correct. Gluing a loose interface may stop visible movement without preventing compression or excess bearing preload.

Before choosing a P04 repair, mark the nuts relative to the rod and carrier, measure the carrier height to a fixed reference, and observe which interface moves while turning by hand. Confirm steel spacers contact the intended inner-ring faces and do not rub shields/outer rings. Do not tighten further simply to eliminate motion if rotation becomes stiff. A permanent repair should positively locate the carrier and carry axial clamp loads through appropriate metal shoulders/spacers; its dimensions need the actual bearing/stack measurements.

References:
- Local docs/bearing-spacer-contact.md and original PRINT_AND_ASSEMBLE.md.
- SKF, Bearing preload: https://www.skf.com/binaries/pub12/Images/0901d1968065f1f4-Bearing-preload_tcm_12-299896.pdf
- SKF/Kaydon mounting guidance (higher preload increases friction torque): https://cdn.skfmediahub.skf.com/api/public/0901d1968053c10e/pdf_preview_medium/0901d1968053c10e_pdf_preview_medium.pdf
No P04 CAD modification or adhesive specification is included in this arm-joint release.

## Rebuild
env PYTHONPATH=$HOME/Applications/freecad-experiment/squashfs-root/usr/lib $HOME/Applications/freecad-experiment/squashfs-root/AppRun python experiments/print_petg_12/build_arm_joint_variants.py
env PYTHONPATH=$HOME/Applications/freecad-experiment/squashfs-root/usr/lib $HOME/Applications/freecad-experiment/squashfs-root/AppRun python experiments/print_petg_12/check_arm_joint_installation.py
python3 experiments/print_petg_12/finish_arm_joint_variants.py
python3 experiments/print_petg_12/package_arm_joint_variants.py
