# Collar, hemisphere ball joint, centrifugal latch and propeller models

## Geometry and motion
The user confirmed radial inward/outward tilt: each collar's revolute bearing axis is tangent to the donut. The alternate ball mount retains three rotational freedoms, with a hemisphere tilt stop. Collars have a +/-90 degree hinge stop. Ball stops use a spatial distance constraint between the rod tip and a point one rod length above the mount: d <= sqrt(2)*L. This is exactly cos(tilt) >= 0 and does not restrict axial twist as a quaternion angle limit would.

Both mounts sit on top-side pedestals with height rotor_radius + 45 mm. This gives the whole rotor clearance above the donut top even at a horizontal stick orientation. Solver stops are compliant and can have small numerical penetration, so tests allow less than 0.5 degree overshoot. The collar annulus, bearing shaft and socket shapes are schematic, not manufacturing CAD.

Cross braces rotate 45 degrees away from the four hinge locations and sit 35 mm below the ring center plane. Ring, shafts and rotors have collision geometry enabled. Cosmetic bearing housings, preparation pedestals and plungers do not use contact; the pin/hole interaction is an ideal latch, not a resolved contact/jamming simulation. The reference floor remains non-colliding. Geometry separation and contact checking are not certification of a printable mechanism.

## Passive latch
Each mount has a 15 g sliding plunger moving radially outward. Its spring has 0.06 N inward preload, 12 N/m stiffness, 0.025 N s/m damping and 4 mm release travel by default. The slider has a lower stop at zero and an upper stop at 12 mm (or twice the release travel if larger). Its mass includes a plunger counterweight centered at the specified body origin.

The engine computes inertial loading of the pin from the actual rotating assembly. No timer or direct RPM comparator releases it. A weld constraint holds the rod exactly upright until its own pin displacement reaches the release travel, then the weld deactivates. Release is latched until reset; the spring cannot reinsert a pin into an arbitrarily rotated hole.

The displayed estimate is the steady-rotation force balance:
omega_release = sqrt((preload + stiffness * travel) / (pin_mass * (pin_radius + travel))).
pin_radius = ring_radius + 35 mm.
Default estimated release is approximately 38.7 RPM. Acceleration, damping, gravity in tilted configurations and constraint forces can change the actual event time.

Outward withdrawal is commonly described using centrifugal force in the rotating frame; the inertial-frame explanation is the spring providing centripetal acceleration until it cannot retain the pin. This is a passive centrifugal latch, not an electrically powered solenoid. Pin shear, friction at the loaded hole, wear, spring packaging and re-engagement hardware are not modeled.

## Startup and motor reaction
Staged supported runs start at rest. Small rotors ramp over 2 s, hold another 0.5 s, then the ground-mounted donut motor starts its 2 s ramp. With latches enabled, the small mounts remain upright until their pins retract; their release is no longer tied to donut motor start.

Small motors now continue regulating relative rotor-to-housing speed after release, allowing meaningful shared speed targets. Torques are internal to each rotor/housing pair. A ball-mounted housing can counter-rotate because it cannot transmit an axial couple through an ideal ball joint. Bearing-relative RPM is therefore different from inertial rotor RPM; both are recorded, and propeller loads use inertial spin. The free-housing discrete motor gain is bounded using its axial inertia and the time step.

In free-flight mode the experiment starts pre-spun and coasts, with no ground drive. Its initial total linear momentum is zero. The plunger masses and spring forces are included in the complete assembly.

## Propellers
A selectable propeller replaces each disk with a two-blade rigid shape and rectangular-bar inertia. The dashboard preset uses 120 mm radius, 30 g mass, 8000 RPM, alternating handedness/rotation. Flywheel preset uses 90 mm radius, 350 g mass, 1200 RPM. Changing rotor type therefore changes both geometry and mass explicitly; it is not an equal-inertia comparison.

External aerodynamic loads on each rotor use:
T = pitch_sign * Ct * rho * n * abs(n) * D^4
Q = -Cq * rho * n * abs(n) * D^5
where n is inertial axial revolutions per second, D is diameter, and loads follow the rotor's current axis. Drag opposes spin. Alternating rotors use matching opposite blade handedness so normal commanded rotation gives downward airflow for every propeller. Reversing a given propeller's actual rotation reverses its thrust in this simplified model.

Defaults Ct=0.10, Cq=0.01 and rho=1.225 kg/m^3 are illustrative. The model assumes static air coefficients and omits inflow variation, blade flexibility, interaction between wakes, ground effect and CFD. Coefficients require measurement for a particular propeller. Airflow arrows indicate direction only. Propeller thrust is an external momentum exchange with air, not gyroscopic propulsion. Ballistic/conservative diagnostics are disabled where their assumptions do not apply.

## Validation
Mechanism regression tests cover speed-dependent pin release, a stronger spring remaining locked, collar-axis direction and brace offset, ball hemisphere stops with unrestricted twist, motor startup/reset, static support load, free-flight invariants, thrust proportional to speed squared, alternating-propeller thrust direction, and total linear impulse from aerodynamic forces. All four joint/rotor combinations are exercised.

## Sources
- MuJoCo constraints and integration: https://mujoco.readthedocs.io/en/latest/computation/
- MuJoCo spatial tendon limits: https://mujoco.readthedocs.io/en/stable/XMLreference.html
- NASA propeller momentum explanation: https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/propeller-thrust/
- NASA thrust coefficient scaling: https://ntrs.nasa.gov/api/citations/20120015977/downloads/20120015977.pdf
