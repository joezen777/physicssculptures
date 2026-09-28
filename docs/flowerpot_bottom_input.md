# Flowerpot multiplier with bottom input

This separate variant in `experiments/flowerpot_input` returns to the original two-stage, fixed-carrier planetary layout. The previous bevel experiment remains preserved at `experiments/bevel_cones` (checkpoint fe86396).

## Changes

- Six 12 mm intake openings through the lower pot floor on a 27 mm radius.
- A 56 mm diameter finger-drive flange and connecting collar beneath the existing lower 608 seat. The flange rotates with the lower pot; the central 8 mm rod remains fixed.
- Base lowered to leave 12 mm below the drive flange, with an extended stationary inner-race spacer. This is an accessible manual input, not a finished motor coupling.
- Six 48 x 16 x 2 mm wooden blade placeholders, pitched 22 degrees, around the bottom pot rim. Root plates show attachment locations; screw capture, blade drilling, clamp strength and assembly fits remain unresolved.
- The original staggered teeth, split rings and 3:1 per-stage speed increase are retained.

Bottom +1 rotation gives middle -3 and top +9. The ideal top torque is one ninth of bottom input torque; power is not multiplied. Internal carriers must remain fixed to the anchored shaft. This version needs no outer posts, but is not support-free.

## Convection feasibility

Rising warm air can apply torque to pitched blades, but no self-starting or useful candle-driven output has been established for this draft. The printed rotors, multiple bearings, gear contact friction and output fan all consume the small available mechanical power. Thermal watts from burning wax cannot be treated as shaft watts.

NIST measured 77 +/- 9 W for a particular taper candle in its study; that is not a measured rating for the user's tea lights or a turbine power estimate:
https://www.nist.gov/publications/characterization-candle-flames

The wood blades in this model are for cold-air testing. No candle mount or validated heat path is included. USFA recommends keeping candles at least 12 inches from anything that burns:
https://www.usfa.fema.gov/prevention/home-fires/prevent-fires/candle/

A useful progression is to measure breakaway torque with hand input, test the unloaded blade rotor using cool airflow, then reconnect one gear stage and finally the second stage. A string tangent to the 28 mm input flange with a hanging mass m gives applied torque m*g*0.028 in N m (m in kg). One gram corresponds to about 0.275 mN m, before any test-fixture friction. This measures the torque needed; it does not predict candle torque.

Any later flame-driven experiment needs a separately designed noncombustible heat collector/rotor and thermal separation from printed components. Even a metal rotor does not establish that adjacent plastic temperatures are acceptable.

## Bearing and intake details

The lower cone retains its 22.2 mm diameter x 7.2 mm 608 pocket. The stationary spacer contacts the inner race; the rotating hub's 12.5 mm bore clears the spacer's 12 mm outside diameter. Positive axial retention and allowable axial load still need verification for the selected real bearing. A radial bearing alone does not define the complete vertical load path.

The intake holes expose part of the lower floor. They do not guarantee efficient through-flow: the gear cluster, upper floor and other components still obstruct the axial air path. The rim blades can instead be tested with an external upward airflow around the pot.

## Retained bevel variant

Its fan-spoke pitch alternates +22 / -22 / +22 degrees for +1 / -1 / +1 module rotation, and the top fan pitch follows its rotation sign. That makes their intended axial flow directions consistent, but the animation is kinematic, not an aerodynamic result.

The requested bottom inlet and 608-supported bottom-drive improvements are recorded for a later bevel revision. This turn implements bottom intake/drive changes in the flowerpot variant, which is the resumed design.

## Reproduction and scope

Run `python3 experiments/flowerpot_input/launch.py` in WSL Ubuntu. The builder opens FreeCAD with live animation and full/cutaway controls and saves FCStd, STEP, renders and sampled mesh checks in output/.

Run validate.py with the bundled FreeCAD Python environment to check the saved geometry. Printed fits, heat tolerance, rotor balance, blade retention and complete motion clearances are not qualified.

Superseded working direction: see roofvent_multiplier.md. The wooden-blade generator is retained as an intermediate concept; its rendered outputs are not versioned.
