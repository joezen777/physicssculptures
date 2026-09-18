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
No contact, joint stops, bearing friction, flexible members, aerodynamic lift, motor control, rotor imbalance or mechanical stress model. Passing through the ground or another part is expected in this idealization. Supported motion cannot establish free-flight lift. Larger speeds require new convergence tests. Results are not fabrication instructions.

## References
- https://mujoco.readthedocs.io/en/stable/python.html
- https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html
- https://mujoco.readthedocs.io/en/latest/computation/
