# Falling finned cylinder with three planetary speed-increasing stages

## What this experiment represents

This is a kinematic CAD concept, not a qualified drop device or vacuum vessel.
The illustrative envelope is 98 mm diameter by 221 mm high, with six upper
fins extending to approximately 138 mm diameter. Fins have a 30 degree pitch.
There are three coaxial stages at z = 174, 118 and 62 mm. Each has:

- A 72-tooth internal ring attached to a common independently rotating reaction drum.
- Three 24-tooth planets at equal 120 degree spacing and 24 mm orbit radius.
- A central 24-tooth sun.
- Module 1 mm, nominal 20 degree pressure angle, 6 mm face width.
- A carrier driven by the preceding sun; the first carrier is driven by the outer shell.

The balanced layout is nominal: manufacturing errors, bearings and flexible modes
would still require static and dynamic balancing. Three-planet assembly is compatible
because (72 + 24) / 3 = 32 is an integer. Ring and planet phases are included.
The tooth flanks use sampled involutes, with simplified roots and no production backlash.

Blue parts are the wind-driven shell and carriers. Purple parts are the independent
reaction assembly, including the ring gears and lower flywheel. Green gears are planets.
Gold parts are suns and output shafts. The cutaway removes the front half of the outer
shell for inspection; the full STEP retains the full shell.

## The missing constraint: a reaction member

Rotation of a rigid shell alone does not automatically drive internal gears relative
to that shell. A second degree of freedom is required. In this concept it is an
independently supported reaction drum. Inertia gives it a transient reaction, but does
not hold its angular velocity at zero. Vacuum does not supply reaction torque.
An off-axis gravity weight would not give a stationary reference about the vertical
axis, and a freely falling pendulum is not a useful gravity reference.

The FreeCAD controls provide three cases:

1. **Restrained reaction:** ring drum held stationary by an external restraint.
   Useful to illustrate gearing, but not the freely falling sealed-cylinder case.
2. **Free reaction:** lossless spin-up from rest; only the shell receives external torque.
   The reaction drum responds according to the model's generalized inertia.
3. **Locked:** every member rotates together. There is no speed increase.

A sustained high ratio relative to the ground would need a separately characterized
reaction mechanism, such as an independently air-coupled rotor or stator. That changes
the exterior design and torque model; it is not implicitly supplied by this drawing.

## Gear equations

For each stage, Willis' relation is:

    Ns * (omega_sun - omega_carrier)
        + Nr * (omega_ring - omega_carrier) = 0

Thus omega_sun = 4 omega_carrier - 3 omega_reaction.
After three stages sharing the reaction member:

    omega_bottom = omega_reaction + 64 (omega_shell - omega_reaction)
                 = 64 omega_shell - 63 omega_reaction

These can be RPM or radians/second as long as the units are consistent.
A stationary reaction member would give:

| Shell RPM | Stage 1 RPM | Stage 2 RPM | Bottom RPM |
|---:|---:|---:|---:|
| 100 | 400 | 1,600 | 6,400 |
| 300 | 1,200 | 4,800 | 19,200 |
| 600 | 2,400 | 9,600 | 38,400 |
| 1,000 | 4,000 | 16,000 | 64,000 |

These are conditional ratios, not predicted falling speeds. With the reaction
held stationary, ideal output torque is input torque divided by 64; gear losses
reduce it further. Gears trade torque for speed and do not create power.

The animation preserves these ratios and planet rolling kinematics.
The ideal view displays shell rotation at 1 degree/second: 1,800 times slower
than a 300 RPM shell. Planet centers orbit with their carriers; planet absolute
spin is 2 omega_carrier - omega_sun because both gears have 24 teeth.
STEP files are static geometry. The FreeCAD macro supplies the animation.

## Free-drum dynamics and energy

The build integrates inertia from full CAD solids before cutting the shell away.
Illustrative material densities are 1,240 kg/m3 for general components and
7,800 kg/m3 for shafts, reaction rods and flywheel. Fins and rods include their
radial parallel-axis terms. Planets include both orbital and spin inertia.
These material choices are inertia assumptions, not a high-speed build specification.

For generalized coordinates q = [theta_shell, theta_reaction], each central rotating
body contributes J [a,b]^T [a,b] to inertia matrix M when its speed is
a omega_shell + b omega_reaction. Planet orbital motion contributes mass*r^2
with the carrier's coefficients; planet spin contributes its own polar inertia.
Axisymmetry and three equally spaced planets make this M independent of phase.

    T = 1/2 q_dot^T M q_dot
    M q_double_dot = [torque_on_shell, 0]

Starting at rest, with no friction or load, the conserved generalized reaction
momentum gives omega_reaction / omega_shell = -M12/M22.
This is a conserved generalized momentum, not a claim that the drum itself
conserves angular momentum independently of the gears. The generated physics.json
contains the matrix and resulting speed ratios. The final illustrative mass is
0.7823 kg. At shell 300 RPM, the free reaction member turns at 268.8 RPM, and the
stage outputs are approximately 393.7, 768.3 and 2,266.7 RPM. Bearings, seals and real tooth
friction would change the dynamics. This is a simplified constrained rigid-body model.

For a drop through height h in still air, with no stored energy or initial spin,
rotational energy cannot exceed m*g*h. The calculator uses the appropriate equivalent
inertia to derive a generous energy ceiling, assigning all available gravitational
energy to rotation. Actual translation, wake losses and friction reduce it.
Increasing ratio increases reflected rotor inertia quadratically, so gear ratios
cannot give unlimited speed from finite energy.

## Why drop height and vacuum do not determine RPM

The cylinder falls through external air; its fins extract energy from that airflow.
Only its interior is taken to be evacuated. If the outside were also vacuum, the
fins would not start rotation from rest. Internal vacuum reduces windage but leaves
bearing friction, gear contact losses, material stress, rotor imbalance and heating.

An aerodynamic calculation needs mass, drop height, measured or computed axial drag,
and the fin torque as a function of fall speed and spin speed. For a specified
drag coefficient and area, the usual terminal-speed estimate is:

    v_terminal = sqrt(2*m*g / (rho_air * Cd * A))

But fin torque versus rotation is a separate function; terminal fall speed does not
determine spin RPM. The drawing's flat fins are a concept, not an aerodynamically
validated turbine. Vertical stability and tumbling have not been simulated.

## Mechanical and printing scope

The CAD indicates shaft paths and reaction supports, but does not detail rolling
bearings, keys, retaining hardware, pressure-rated endcaps, seals, lubrication,
or rotor containment. The partial shell is a visualization only. The full-shell
export is also not a certified evacuated structure: buckling under external
atmospheric pressure must be evaluated separately.

For a low-speed hand-turned educational prototype, use Ender 3 V2 / Sprite Pro /
0.2 mm nozzle with PLA for initial gears and carriers. Print gear faces flat,
start with 0.10 mm layers, and trial 0.15–0.25 mm flank clearance and 0.2–0.3 mm
diametral journal clearance using coupons. Those clearances are NOT incorporated
into this zero-backlash concept model. Print the shell vertically in sections,
with fins separately so supports do not damage gear or journal surfaces.
Use metal pins and real bearings for a functional prototype. ABS Pro 2 resin on the
Photon Mono 5s may improve tooth detail for a static demonstrator, but is not a
qualified high-speed rotor material. No supplied file is a high-speed print release.

## Files and reproduction

From the repository in Ubuntu:

    python3 experiments/drop_gearbox/launch.py --rebuild --render
    ~/Applications/freecad-experiment/squashfs-root/AppRun python experiments/drop_gearbox/make_preview.py
    python3 experiments/drop_gearbox/calculate.py --shell-rpm 300 --height 100
    python3 experiments/drop_gearbox/launch.py --viewer

The first command requires a Linux FreeCAD GUI and a display. FREECAD_APP can
override the portable executable path. The animation controls stay open.
Generated files are in experiments/drop_gearbox/output. Omit --rebuild to reopen
the existing model and animate immediately. The saved FCStd alone contains geometry;
run animate.FCMacro to display the playback controls.

## References

- Planetary gear kinematics: university lecture on the Willis method:
  https://wm.pollub.pl/fcp/6PREgARcJNScXKxEMUA9DAmltVyVUFDFqUVJWa3VBeQN0fWRfMR0fQWpmExhaRFBAElI5HhwxF0l2Aw0HTWB1CA/_users/code_JKh06FhwPOSoQHxEoAloNWz4jWyVZ/strona_katedry/pracownicy/jedlinski/tmm_wyklad_3_eng_student.pdf
- NASA drag equation:
  https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/drag-equation/
- NASA falling-object equations:
  https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/flight-equations-with-drag/

## Verification performed

All 50 modeled solids pass CAD validity checks. The cutaway STEP was independently
reloaded and its aggregate volume matched the FreeCAD model within 1 ppm. Checks
also cover six-fin radial balance, all nine planet orbit radii, positive kinetic
energy, and conserved free-reaction generalized momentum. Three sampled relative
gear phases have less than 0.0001 mm3 tooth intersection (sampled-flank numerical
error). This is not a full interference sweep or a stress/bearing analysis.
See output/verification.json and output/validation.json.

To repeat the CAD verification with the installed portable runtime:

    PYTHONPATH=~/Applications/freecad-experiment/squashfs-root/usr/lib ~/Applications/freecad-experiment/squashfs-root/AppRun python experiments/drop_gearbox/validate.py
