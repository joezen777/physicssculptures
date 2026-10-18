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
- SIMPLE steady solver, limited linear-upwind momentum discretization, relaxed pressure and velocity. Initial relaxation factors were pressure 0.2 / velocity 0.4; they were reduced to 0.1 / 0.2 during startup to investigate stability. Approximate switch iterations are recorded in `experiments/cfd400/relaxation_change.json`. Iteration number is not elapsed physical time.
- Mesh-quality checks must pass before the solver starts.
- Laminar closure is a screening assumption at this low-speed operating point, not evidence that all separated flow is steady or laminar. Transient and transition/turbulence-model sensitivity remain unresolved.

## Reported quantities

Downward signed volumetric flux is sampled through a fixed 144 mm diameter disk at z = -40 mm. There are 576 equal-area samples (12 radial rings × 48 azimuths), interpolated from the CFD velocity field. `Q = -mean(Uz) * pi * 0.072²`. Positive reported flow is downward; backflow subtracts from the total. This is a defined downstream disk flux, not a standardized ducted fan test or the entire entrained plume. The same absolute plane is used for every design.

Aerodynamic torque is the pressure plus viscous moment about the shaft integrated over the rotor wall. Required shaft power is resisting torque × 41.887902 rad/s. Mechanical bearing and gear losses are excluded.

A numerical screening flag requires the run to finish, less than 2% torque range over its final 100 iterations, less than 2% flow range over the final three samples, and final initial equation residuals below 1e-3. These are declared screening tolerances, not a certification or experimental validation criterion. A successful executable exit alone does not establish convergence. Two mesh levels provide a sensitivity check, not a formal grid-convergence study.

## Reproduction

All work runs in WSL2 Ubuntu. Cases and large field files are stored on the Linux filesystem at `~/.cache/angularmomflyer/cfd400/`, outside OneDrive and Git. See the experiment README for commands. Compact histories and results are retained in the repository. The original coarse mesh was generated with Ubuntu OpenFOAM v1912.200626; all flow solves use the maintained OpenCFD build. Remaining meshes use the maintained build.

## Completed steady screening: failed convergence

All five steady cases reached 1,000 iterations and exited normally, and all meshes passed checkMesh. None passed the declared numerical convergence criterion. The final three downstream-flow samples varied by approximately 39% (original coarse), 74% (original fine), 4.6% (scimitar), 22% (toroidal), and 41% (tubercled). The original coarse/fine flux even differed in sign. These are solver diagnostics, NOT physical fluctuation amplitudes or evidence of a winning design. Steady iteration averages cannot substitute for time averages. The complete histories, summary flags and compact logs/configuration archive are retained under `experiments/cfd400/results/`.

## Higher-speed and transient follow-up

The user requested a higher-speed final-gear alternative. The sensitivity matrix is 400, 600 and 800 RPM for the four explicit geometries, plus the finer original at 400 RPM. These are imposed speeds, not predictions of the wind-driven equilibrium. For unchanged input shaft speed, total speed-up ratios 8, 12 and 16 would produce those speeds from an assumed 50 RPM input; the final stage would change from 2:1 to 3:1 or 4:1 speed-up. Gear geometry and strength have not been redesigned.

For a speed-up ratio g, ideal output torque is input torque/g. Including efficiency eta, available output torque is eta*T_input/g before other losses. Changing gearing also changes the sail operating point under load. It cannot create shaft power. A coupled solution must intersect the sail/drivetrain available-torque curve with each fan's CFD torque curve; the present fixed-speed tests do not establish that intersection.

Under unchanged dimensionless fan coefficients, Q scales with RPM, torque with RPM squared, and power with RPM cubed. Relative to 400 RPM, ideal 600 RPM factors are 1.5 / 2.25 / 3.375; at 800 RPM they are 2 / 4 / 8. This similarity estimate would preserve rankings, so Reynolds-number, separation and efficiency changes are exactly what the independent CFD speed tests must investigate. This is not a replacement for the simulations. Source: [AMCA airflow fundamentals / affinity laws](https://www.amca.org/assets/resources/public/assets/uploads/FINAL-_Fundamentals_of_Airflow-_TCF-_AMCA__5.6.20.pdf).

The transient follow-up uses pimpleFoam, second-order backward time integration, adaptive maximum Courant number 0.7, two outer correctors and two pressure correctors, with one non-orthogonal correction. Initial conditions are rest. The existing MRF geometry stays frozen: this is an unsteady frozen-rotor screening approximation, not a sliding-mesh blade-passage simulation. Guard interactions, transition modelling and mesh/time-step sensitivity remain limitations. Target physical duration is 1.5 seconds (10 revolutions at 400 RPM). No ranking is acceptable solely because that duration was reached; time-window statistics and finer-mesh sensitivity must also be assessed.

The original coarse pilot completed 0.003 physical seconds in about 140 wall-clock seconds. This is only a timing/startup check, not a useful performance measurement. Linear extrapolation suggests roughly 19 hours per serial 1.5-second case, before changes in time step and CPU contention. Four cases can run concurrently. A bounded runner checkpoints and stops at its compute-time limit; unfinished cases remain explicitly unfinished and can resume from written fields.

### User-selected compute limit

The user selected **one hour total** for the transient comparison. The active batch was checkpointed and resumed with the deadline measured from its original start, also counting the 140-second pilot. The earlier 12-hour assumption is superseded. This limit is unlikely to permit statistically settled flow or the queued higher-speed sweep; partial results must not be used to rank designs.
