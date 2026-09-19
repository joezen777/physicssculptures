# Current revision validation (2026-09-19)

Environment: WSL2 Ubuntu, Python 3.12.3, MuJoCo 3.13.0; Node 24.18.0, Vite 7.3.6. All execution occurred inside Ubuntu.

## Automated results
The complete suite passed: 16 tests in 57.344 seconds. Vite production build also passed. Reproducible commands are in README.md; final command output is saved locally in runs/final-tests.log and runs/final-build.log (generated output is ignored by Git).

Coverage includes:
- Conserved momentum/energy and ballistic center-of-mass motion for explicitly unforced, contact-free baseline configurations.
- Known external angular impulse, static support weight and time-step convergence.
- Reset followed by Start, all-zero stopped state, small rotors spinning before donut motion, pause retaining state and invalid free-flight ground-drive rejection.
- Each pin staying engaged below its centrifugal release threshold; actual travel-triggered release above it; stronger springs remaining engaged.
- Tangential collar hinge axes and cross-brace angular separation.
- Upper-hemisphere ball stops with unrestricted twist.
- All four combinations of collar/ball and flywheel/propeller staying finite over six-second staged runs; axle tilt stays below the test ceiling of 90.5 degrees.
- Propeller speed-squared thrust, correct thrust direction for alternating handedness, zero thrust at zero speed and whole-assembly momentum change matching aerodynamic impulse.
- API applying both speed settings together, reset/pause behavior, failed configuration preserving the old model, and propeller geometry selection.

An initial ball/propeller test exposed excessive soft-stop overshoot. The hemisphere stop now uses a tighter response and anticipatory limit margin; the regression passes. This remains a compliant numerical stop, not an infinitely rigid CAD contact.

Starlette emitted a test-client deprecation notice about httpx; it did not affect test outcomes or runtime service.

## Browser checks
The actual dashboard was checked in the Codex browser:
- Initial paused collar/flywheel model with both speed controls.
- Start/pause and four latch releases at the configured ring speed.
- Ball-joint selection, changing shared small-rotor target to 1800 RPM and ring target to 50 RPM, and Apply changes & reset returning to time zero.
- Propeller selection replacing disks with blades and aerodynamic UI indicators.
- Visual placement of collars, top-mounted ball sockets, elevated rotor clearance and braces offset from the mounts.
- Final rebuilt dashboard loaded successfully with whole-machine and ring displacement readouts.

The local server is bound to 127.0.0.1:8766. It was relaunched after the interrupted session, verified with HTTP 200, and left in a paused default collar/flywheel configuration.

## Limits
This validates implementation and selected numerical cases, not physical construction. Spring values and aerodynamic coefficients are illustrative. Pin/hole shear, binding and loaded friction are not resolved. Contact and stiff stops require new convergence studies for extreme parameter choices. No CAD, printable files, measured propeller calibration or rotor stress validation is claimed.

## Powered-flight extension — 2026-09-19

All 19 unittest cases passed in 70.249 seconds. Production Vite build passed.
Added tests verify positive whole-machine climb with air, ballistic/free
center-of-mass motion without air, external-force impulse accounting,
and absence of a world actuator or support constraint in powered flight.
The five-run benchmark and half-timestep comparison are documented in
[powered-flight.md](powered-flight.md). Browser verification confirmed
preset loading, start/pause, positive center-of-mass displacement,
tilt/thrust charts, and power/weight telemetry.

## Supported steering extension

All 21 unittest cases passed in 130.437 seconds. The new physics test tracks
(8°, 0°), then (−6°, 5°), within 0.7° on each axis after four seconds per
command. It checks support force equals weight, total angular momentum is
conserved within 1e-5 N·m·s, no root actuator exists, and no engine warnings occur.
The API test verifies live command validation without model replacement.

Browser testing confirmed Start, live target changes without a reset, and Pause.
At 43.44 seconds, the requested (−6°, 5°) lean measured (−6.13°, 5.11°),
with 51.8 N bearing support and unchanged whole-machine center-of-mass height.
