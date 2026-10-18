# Toroidal5 production top assembly

Selected for appearance. No proven aerodynamic ranking. Revised 2026-10-18.

Production files: experiments/print_petg_12/output/toroidal5_final and output/stl. Sources: toroidal_geometry.py, build_toroidal.py, build_toroidal_supports.py, integrate_toroidal.py. See the release README for assembly and Cura settings.

Checks: single watertight rotor, Euler characteristic -16 (five loops plus four mounting holes), original hub interface preserved within radius20.9 mm,144 mm swept diameter,4 mm radial clearance,27.4 mm grille clearance. P185/P18 is72 mm tall, flange-down. Existing P19 is reusable at z412; replace21 mm top steel spacer with53 mm and use500 mm end-to-end M8 rod. Lower sails unchanged.

The previous return loft was nearly zero volume and silently discarded one arm per pair during fusion. Single-solid and watertight checks missed this. Revised radial-vertical return sections are normal to the azimuthal path, with volume and topology assertions. Old toroidal5 CFD geometry/results do not represent this release; future runs must use toroidal5_final, remesh, and establish convergence. No CFD was run.

The user reported prior integrated supports absent in Cura5.8.1 preview under raised wings. Ribs were widened from0.66 to1.32 mm at2.4 mm pitch, regenerated beneath both arms and returns. Short removal sections use0.5 mm nominal vertical clearance and a0.5 mm bed comb. Expanded-footprint sampling plus exact trimming prevents rotor overlap. Coupons compare0.25/0.5/0.75 mm release gaps.

PrusaSlicer generation passed for four print choices. CuraEngine5.8.1 completed for the supported fan at0.6 mm nozzle /0.25 mm layers. Extrusion-midpoint checks found supports in all five outer sectors at four heights. The original Cura profile was unavailable, so the precise omission cause remains unconfirmed. Cura retained an overlapping-face warning on fine triangulation; the STL is watertight and the warning is recorded. Removal, clean undersides, strength, balance and airflow remain physically unvalidated.

Historical full-assembly validation/images retain a top-part override. Main CAD and production package are updated by targeted integration without rebuilding lower components.
