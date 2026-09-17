# Gyroscopic ring experiment: initial design

## Objective and status
Explore a rotating annular carrier with elevated satellite flywheels on ball-mounted rods. Determine satellite motion, carrier reaction forces, and whether any apparent rise represents translation of the complete assembly. This is a research and experiment specification, not a completed or validated simulation. The supplied sketch appeared black in the conversation; geometry is inferred from the verbal description.

## Software decision
Recommend MuJoCo with Python for the first rigid-body model: open-source Apache 2.0 licensing, native Python bindings, ball/hinge/free joints, and gyroscopic dynamics. Project Chrono is a credible alternative, particularly for more elaborate mechanical systems. Use FreeCAD/OpenSCAD for eventual printable geometry. FreeCAD's prescribed assembly animation alone does not establish force-driven gyroscopic behavior. A STEP viewer is for inspecting geometry.

Sources:
- https://github.com/google-deepmind/mujoco
- https://mujoco.readthedocs.io/en/latest/computation/
- https://mujoco.readthedocs.io/en/stable/modeling.html
- https://projectchrono.org/faq/
- https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Assembly_CreateSimulation.md
- https://openscad.org/about.html

## Physics
A fast rotor has angular momentum approximately L = I_spin * omega along its axle. Changing that direction requires torque, tau = dL/dt. This can produce precession and nutation, not an absolute prohibition on tipping or translation. A spinning wheel can still be lowered bodily.

Orbiting a rotor does not by itself require its spin axis to turn: axis direction, center-of-mass offsets, and constraints determine the torque. Centripetal force is inward in an inertial frame; centrifugal force is a useful apparent force only in the rotating frame. An ideal ball joint permits rotation and transmits force but no couple. A force applied below the rotor center of mass can nevertheless exert torque about that center.

The ring may experience instantaneous upward forces, rocking, and changes in height while other components move oppositely. Internal forces cancel for the complete assembly:
M * acceleration_of_center_of_mass = sum_of_external_forces.
In free flight without aerodynamic forces, vertical center-of-mass acceleration is -g. With gravity disabled and no external forces, center-of-mass velocity is constant. A ground-mounted drive or support is an external force/torque path. Contact can also supply an impulse; a hop is not sustained free-flight thrust.

## Proposed model
- Rigid annular carrier, central hub, and relative revolute bearing.
- Several identical rods mounted on spherical joints around the ring.
- Each rod carries a separate rotor on an axle hinge.
- Provisional interpretation: each rotor axle follows its rod; awaiting user clarification.
- All masses, inertia tensors, dimensions, rod inclinations, spin directions and speeds remain configurable; no physical dimensions are asserted yet.
- First use initial spin and coast, avoiding hidden energy or momentum inputs from prescribed velocities. Later internal motors must include reaction on their mounting bodies.
- Begin with rigid bodies, ideal bearings, no aerodynamic forces, and no collisions. Add joint limits, friction and contact explicitly in subsequent fidelity steps.

## Experiments and validation
1. Single gyroscope: apply a known torque, verify angular-momentum response and precession.
2. Ground-supported carrier: measure mount reaction and satellite tilt; support forces cannot count as free-flight lift.
3. Free assembly with gravity off: monitor total linear/angular momentum, energy and complete center of mass.
4. Free assembly with gravity on: compare full center of mass with its ballistic trajectory, separately from ring height.
5. Controls: stopped satellite rotors, reversed spin, alternating spin, and ring-only rotation.
6. Repeat with smaller time steps and compare integrators. Select integration settings based on conservation and convergence, not visual plausibility. Compare torque-free energy and momentum before introducing damping or motors.
7. Plot total center-of-mass height, carrier height, satellite tilt, external force/impulse, and conservation residuals.

## Interface direction
Start with the physics engine's 3D viewer and reproducible Python runs. A later game-like interface can expose ring RPM, rotor RPM, masses, rod length, tilt, damping, support mode, pause/reset and force arrows. Use React/Vite/MUI with a Python FastAPI backend if a custom browser UI is needed.
