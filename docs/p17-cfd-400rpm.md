# P17 fixed-speed 3D CFD screening at 400 RPM

## Scope and interpretation

This experiment solves three-dimensional incompressible Navier–Stokes flow around explicit rotor surfaces using OpenCFD OpenFOAM v1912, maintained build 260127. It is an isolated-rotor, steady multiple-reference-frame (MRF), laminar screening calculation. This is computational screening, not experimentally validated fan performance. No physical airflow measurements are available.

The imposed speed is 400 RPM (41.887902 rad/s), with the negative-z rotation sense matching the original P17 blades. Tip speed at radius 72 mm is 3.016 m/s. Air density is 1.225 kg/m³ and kinematic viscosity is 1.5e-5 m²/s. All geometries have the same nominal 144 mm swept diameter.

The three large wind sails are NOT solved in this experiment. A 10-knot wind does not uniquely determine shaft speed. Fixing 400 RPM gives a fair aerodynamic comparison at one speed; the required torque must ultimately be matched to the sails and drivetrain. The guard, tower, rod and downstream gearbox obstructions are excluded. Results therefore describe an isolated rotor rather than the complete assembled machine.

## Explicit geometry

- Original: original P17 blade surfaces extracted from the source FreeCAD assembly, translated into rotor coordinates. Small hub holes and pockets filled to simplify meshing; outer blade geometry retained.
- Scimitar: existing 40 mm candidate prototype blade geometry, with the same filled-hub simplification.
- Tubercled: four generic cambered blades, pitch 45° to 25°, nominal chord giving a 35 mm root and 18 mm tip vertical projection. A windowed 1.5 mm sinusoidal chord modulation over the outer 60% span represents the tubercles, with an 8 mm wavelength. The skin is 2.4 mm axially. This is a representative implementation, not a measured or optimized biological profile.
- Toroidal: five pairs of generic cambered arms, 47.5° root to 22° tip pitch, with a connected outer loop. The two arms have 36° azimuth separation and up to 18 mm vertical separation, connected by an outward-curving cap reaching 72 mm radius. Skin is 2 mm axially. This is one explicit interpretation of the broad concept, not a unique toroidal design.

Candidate sections are simple cambered shells, not digitized Goe 417, Eiffel 335 or Eppler 420 coordinates. Geometric pitch is not aerodynamic angle of attack: the latter depends on the solved local velocity. Closed loops do not eliminate all vorticity, and tubercles do not guarantee improved efficiency. The comparison applies only to the actual generated surfaces. Geometry generators and STL surfaces are in `experiments/cfd400/`.

## Numerical setup

- Cartesian domain: 400 × 400 × 500 mm, centered on the rotor origin.
- All six outer faces: zero gauge pressure, pressure-inlet/outlet velocity, no imposed freestream.
- Rotating MRF cell zone: radius 82 mm, z = -35 to +55 mm. Rotor surface velocity is imposed by the MRF correction.
- snappyHexMesh: 10 mm base cells, 2.5 mm near-rotor region, 1.25 mm surface refinement for coarse cases, 0.625 mm surface refinement for the finer original case. No prism boundary layers. Thin-feature and viscous-load resolution are limitations.
- SIMPLE steady solver, limited linear-upwind momentum discretization, relaxed pressure and velocity. Iteration number is not elapsed physical time.
- Mesh-quality checks must pass before the solver starts.
- Laminar closure is a screening assumption at this low-speed operating point, not evidence that all separated flow is steady or laminar. Transient and transition/turbulence-model sensitivity remain unresolved.

## Reported quantities

Downward signed volumetric flux is sampled through a fixed 144 mm diameter disk at z = -40 mm. There are 576 equal-area samples (12 radial rings × 48 azimuths), interpolated from the CFD velocity field. `Q = -mean(Uz) * pi * 0.072²`. Positive reported flow is downward; backflow subtracts from the total. This is a defined downstream disk flux, not a standardized ducted fan test or the entire entrained plume. The same absolute plane is used for every design.

Aerodynamic torque is the pressure plus viscous moment about the shaft integrated over the rotor wall. Required shaft power is resisting torque × 41.887902 rad/s. Mechanical bearing and gear losses are excluded.

A numerical screening flag requires the run to finish, less than 2% torque range over its final 100 iterations, less than 2% flow range over the final three samples, and final initial equation residuals below 1e-3. These are declared screening tolerances, not a certification or experimental validation criterion. A successful executable exit alone does not establish convergence. Two mesh levels provide a sensitivity check, not a formal grid-convergence study.

## Reproduction

All work runs in WSL2 Ubuntu. Cases and large field files are stored on the Linux filesystem at `~/.cache/angularmomflyer/cfd400/`, outside OneDrive and Git. See the experiment README for commands. Compact histories and results are retained in the repository. The original coarse mesh was generated with Ubuntu OpenFOAM v1912.200626; all flow solves use the maintained OpenCFD build. Remaining meshes use the maintained build.
