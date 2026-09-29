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

All rotating axes retain 608 bearings (8 x 22 x 7 mm). The default model uses 20 bearings. The original gear and shaft fixtures remain conceptual where clamp screws, retaining hardware and printed fits have not yet been detailed.

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

## Verification

Saved-model checks passed: 91 components, 20 bearing assemblies, all three intact shells and open fan floors, 38 selected static clearance pairs, and four sampled gear phases. STEP round-trip contains 251 solids with relative volume difference 1.55e-11. These are geometric checks, not full-motion collision, structural or airflow qualification. Results are in output/verification.json.
