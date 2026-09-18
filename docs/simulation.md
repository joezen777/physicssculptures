# Initial implementation

The clarified sketch has four horizontal satellite disks, with their axles running along the upward rods. Each rod has a ball joint at the carrier. The initial model implements this topology in MuJoCo, with a native interactive viewer and reproducible headless runs.

## Architecture
gyro_sim.py generates MJCF with explicit inertial properties, initializes spin, integrates motion, measures quantities and exposes a CLI/native viewer. make_demo.py runs controls and produces comparison plots and a rendered preview. tests/test_physics.py checks force conventions, conserved momentum/energy, ballistic motion, response to known external torque, and time-step convergence.

No separate web backend is needed for this first experiment. The selected engine is free and open source and runs locally in WSL2 Ubuntu.

## Physics and conventions
SI units are used internally. User RPM inputs are converted to radians per second. Rotor RPM is relative to its rod, and rod joints initially have zero relative angular velocity. Rods initially lean radially outward. This initialization implies a specific initial angular momentum, which can differ between control cases; controls are not equal-energy comparisons.

Free mode subtracts the initial center-of-mass velocity from the root translation so total linear momentum starts at zero. All diagnostics include all massive bodies. Angular momentum is evaluated about the complete center of mass in world coordinates. Uniform gravity contributes zero torque about that center.

The supported mode force sensor reports the parent-to-child force. The reported value is rotated to world coordinates to obtain the external support force acting on the assembly; a static weight test verifies the convention.

The physics engine's kinematic/dynamic fields are refreshed before measurements. Total energy includes gravitational potential. Free-mode conservation diagnostics account for gravitational linear impulse and ballistic center-of-mass displacement.

The visual ring and spokes are schematic; the explicit mass/inertia model is a uniform annulus and excludes independent spoke/hub mass. This initial model has no central drive assembly. Initial spin avoids incorrectly injecting momentum through a world-attached motor. A later self-contained drive must include the hub and equal/opposite motor reactions.

## Limitations
No contact, joint stops, bearing friction, flexible members, aerodynamic lift, rotor imbalance or mechanical stress model. Only the staged supported experiment has motor control. Passing through the ground or another part is expected in this idealization. Supported motion cannot establish free-flight lift. Larger speeds require new convergence tests. Results are not fabrication instructions.

## References
- https://mujoco.readthedocs.io/en/stable/python.html
- https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html
- https://mujoco.readthedocs.io/en/latest/computation/

## Staged startup and reset correction

The native supported viewer now starts paused in staged mode. R and all preset keys reset time, positions, velocities, motor controls and preparation constraints and pause the experiment. SPACE starts/resumes. Experiment is the controller used by both the viewer and regression tests, so the R-then-SPACE test exercises the same event handler and stepping logic.

Initial velocities are zero in staged mode. Temporary equality constraints hold the ring angle and weld each rod to the ring at its configured pose. Torque-limited rotor servos ramp their relative spin speed using a smoothstep target over 2 seconds, followed by a 0.5-second hold. At release the preparation constraints deactivate and rotor motor torques become zero. A ground-referenced ring motor ramps its speed target over 2 seconds and continues regulating it afterward. No prescribed position or velocity overwrites are used during stepping.

The small-wheel motors are off after release because an ideal ball-mounted rod cannot transmit an axial reaction couple into the ring. Maintaining relative motor speed on a freely counter-rotating rod is not equivalent to maintaining inertial flywheel spin. A different physical bearing/motor support model would be needed to assert that behavior.

The reaction path during preparation is through fixtures and the supported ring to the ground. This is a preparation fixture experiment, not an isolated machine. A free-mode staged request is rejected rather than silently applying a world-referenced drive. Coasting free-flight experiments and their conservation tests are unchanged.

Controller torques are held constant over each RK4 time step; the integrated mechanical dynamics remain torque-driven. The ring and rotor motors have respective 20 Nm and 1 Nm torque limits. Coasting diagnostics report energy drift; staged runs report energy change but leave relative energy drift null because motors and fixture transients exchange energy.

Additional CSV columns report phase, ring RPM and all four rotor-relative RPM values. Viewer text shows current phase and measured speeds. At t=2.5 s the fixtures release; soft constraint compliance and finite motor gains imply small tracking deviations.
