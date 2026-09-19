# Supported gyroscope steering

Select **Load supported gyro steering**, press Start, change X/Y lean targets,
and press **Steer now · keep running**. This changes the command without
rebuilding or resetting the model. Other configuration changes use Apply/reset.

The new rig has a spherical central bearing at its center of mass. It permits
three rotational degrees of freedom and prevents translation of that bearing.
There is no motor on the central joint. Four internal rotor motors hold
alternating 3000 RPM; four torque-limited collar motors redirect their axes.
The donut initially rotates at 3 RPM and coasts. X/Y commands refer to the
world-frame normal direction, not individual rotating mounts. Heading is not
controlled.

Each short 40 mm shaft has a 390 g counterweight below its collar, balancing
the 350 g flywheel and 80 g shaft above. This keeps the center of mass at the
bearing as the collars move. Total modeled mass is 5.28 kg; support force is
51.7968 N at Earth gravity. The model has no aerodynamic lift.

## Controller

A proportional/derivative attitude controller requests transverse torque.
A regularized angular-momentum Jacobian maps that request to four gimbal
rates using rotor H = Izz × spin rate. Rates are limited to 0.7 rad/s; outward
commands stop beyond 65 degrees. A model-based inner velocity controller uses
the coupled mass matrix to compensate rotor/ring dynamics. Collar torque is
limited to 2 N·m, and rotor motor torque to 1 N·m. These are internal joint
actuators, not externally applied torques or prescribed motion.

The preset is tuned for slow donut rotation, alternating solid flywheels and
small attitude changes. Other speeds, large repeated commands, gimbal stops,
and loss of rotor speed can degrade control. This is not an all-attitude
stabilizer or a demonstrated mechanical efficiency advantage.

In a ten-second run with an 8° X command, X settled near 8.17° and Y near 0°.
The slight tracking offset is retained honestly rather than snapping geometry
to the requested pose. Steering redistributes angular momentum while the
bearing continues carrying the full weight. Ring height can change slightly
as it tilts around the bearing; center-of-mass height does not rise.

Counterweight and bearing contact geometry is illustrative. Counterweight
contacts are disabled; the model is not a clearance-validated fabrication
design. Motor/battery mass, bearing friction and structural flex are not
modeled separately.

MuJoCo's multibody dynamics and joint actuation:
https://mujoco.readthedocs.io/en/latest/computation/
