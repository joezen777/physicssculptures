# Modular flowerpot fan tunnel

This revision in `experiments/modular_fan_tunnel` corrects the module concept: every flowerpot, including the bottom one, has a complete outer wall and an open propeller floor. The earlier model opened in cutaway mode; this version opens and saves in the full-wall view.

## Repeating module and air passage

The default assembly has three flowerpot modules plus the terminal fan in a ring. The tooth counts and 2x stages are unchanged: 96-tooth internal ring, 48-tooth center gear, three 24-tooth idlers, module 1.5, all with two staggered rows.

Every pot has the same shell, fan-floor layout, 608 seat and 16 mm AF male stacking connector. The connector is 12 mm long and mates with a 16.4 mm AF socket. Fan handedness alternates because adjacent pots rotate in opposite directions. The default four visible levels turn at +1, -2, +4 and -8.

The pots previously had large open gaps between levels. New overlapping transition collars close those gaps in the intended air passage:
- Each inter-pot reducer rises 19 mm from the lower cap and overlaps the next pot by 4 mm.
- At its upper lip the reducer has a 63 mm inner radius versus approximately 61.66 mm outside radius on the next pot: about 1.34 mm nominal radial clearance.
- The final transition overlaps the stationary terminal fan ring with 2 mm nominal radial clearance.

These are noncontact clearance joints, not airtight seals. The pots rotate at different speeds and must not rub. The gear cluster still obstructs the flow path. This is a ducted-fan concept; net upward airflow, leakage, pressure loss and useful output remain untested. It is not a validated scientific wind tunnel.

## Bottom support and optional sails

The bottom pot is no longer a special closed-floor input pot. Its same male connector plugs into a separate base drive adapter. That adapter has the lower 608 seat and a 16.4 mm AF female socket; the pot supplies the upper 608 seat. The bearings are centered 24 mm apart (z=-22 and z=2 mm).

The adapter stays in place when sails are removed. Stationary inner-race spacers run from the base to the lower bearing and between bearings. Rotating bores clear the spacers. Bearing fit, axial retention and preload still require a physical assembly trial.

A separate three-arm sail assembly fits the adapter's 28 mm AF external hex with a 28.4 mm AF female collar. It is placed below the fan sweep. The three shallow circular cups and collar are grouped as SailAddon in FreeCAD and can be hidden with a dedicated control. The collar is an assembly-time add-on: fit it before the bottom pot. Positive removable retention/fasteners are not finalized; this is not a validated snap-on attachment.

The main shaft, pots, sun gears and wind-sail support retain 608 bearings (8 x 22 x 7 mm). Each planet uses a 604 bearing (4 x 12 x 4 mm), a 4 mm axle, a 12.2 mm pocket and a smaller inner-race spacer. The default model uses eleven 608 and nine 604 bearings. The original gear and shaft fixtures remain conceptual where clamp screws, retaining hardware and printed fits have not yet been detailed.

## More modules

Set TUNNEL_MODULES when launching to generate a different number of pots (1-8 is the current generator limit), with the terminal ring fan above them. The shell/interface repeats; alternate the fan handedness. The base adapter and terminal fan are end fittings rather than unique pot modules.

Repeatable geometry does not mean unlimited practical stack height. Each stage doubles speed, adds bearing and gear losses, and increases shaft/support demands. Useful height and startup depend on the real wind input, fan load, shaft stiffness and friction.

## Printing scope

This is a CAD draft, not print-ready hardware. For low-speed fit trials on the Ender 3 V2 with 0.2 mm nozzle, use PLA for gear coupons and consider PETG for housings, blades and attachments. Pot caps are 171 mm diameter, within the nominal bed. The overall sail span is larger: manufacture its cups/arms separately and add a qualified joining design. Fan floors, collars and snap features need print orientation/support and fit trials; 22.2 mm bearing pockets are starting allowances. No STL release is supplied.

## Files

- output/tower_draft.FCStd: main editable model, full walls by default.
- output/tower_cutaway.FCStd: explicitly labeled section model.
- output/tower_full.step: complete assembly.
- output/tower_without_sails.step: supported tower with no sail add-on.
- output/tower_cutaway.step: section geometry.
- full_view.png, without_sails.png and cutaway.png: corresponding previews.
- module_underside.png: isolated pot showing its fan floor and male connector.

Run `python3 experiments/modular_fan_tunnel/launch.py` in WSL Ubuntu. Builds close FreeCAD automatically after saving. Add `--keep-open` only for an interactive inspection session, then close it when finished. Controls toggle full/cutaway walls, sail visibility and animation. The animation prescribes gear ratios; it does not simulate wind or contact forces.

Previous four-level draft and bearing/gearing references: [simple_sail_tower.md](simple_sail_tower.md).

The base adapter has a 4.5 mm deep relief around its upper outside rim to clear the pitched blade roots. The standalone module underside preview shows the open fan floor without hiding the housing walls.

## Curved arms and top grille revision

Sail arms, stationary planet-carrier arms and the top guard spokes now use smooth curved radial paths. Threefold or sixfold repetition preserves nominal mass symmetry and endpoint positions. Fan blades and gear teeth remain unchanged. The slimmer planet axles require load/stiffness validation; gearing ratios are unchanged.

The top guard has six curved 5 mm wide spokes and ten concentric 2.5 mm wide rings, all 4 mm thick. Ring center radii run from 17 to 71 mm in 6 mm steps. Nominal radial openings are 3.5 mm between rings and 3.75 mm at the central hub. The grille underside is 18 mm above the blade reference plane; blade pitch consumes part of this clearance. This reduces access from above, but is not a certified child-safe guard: printed stiffness, probe access, retention, breakage and other assembly openings need physical evaluation. The added grille also changes airflow resistance.

604 envelope confirmed in the [SKF bearing catalog](https://cdn.skfmediahub.skf.com/api/public/0901d196807026e8/pdf_preview_medium/0901d196807026e8_pdf_preview_medium.pdf). Bearing pocket allowances remain draft printing tolerances, not production fits.

Detail previews: output/guard_detail.png, output/sails_detail.png and output/planets_detail.png. Run inspect_details.FCMacro to regenerate them; the inspection window closes automatically.

## Verification of curved-arm revision

Passed native solid validity, 604 envelopes and 4 mm axle dimensions, 65 selected static clearance pairs, all fan floors and walls, all six grille spokes and ten rings, and clearance from a full rotational blade envelope. Four sampled gear phases have no tooth overlap. STEP round-trip: 251 valid solids, relative volume error 2.38e-9. Bearing count is eleven 608 plus nine 604. These checks do not establish structural strength or child-safety compliance.
