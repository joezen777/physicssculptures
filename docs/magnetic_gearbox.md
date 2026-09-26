# Magnetic gearing and the useful number of stages

## How many multiplications?

There is no universal maximum count of gear stages. For ideal 4:1 stages with a
stationary reaction member, G = 4^N:

| Stages | Nominal ratio | Output at assumed 300 RPM shell |
|---:|---:|---:|
| 1 | 4 | 1,200 RPM |
| 2 | 16 | 4,800 RPM |
| 3 | 64 | 19,200 RPM |
| 4 | 256 | 76,800 RPM |
| 5 | 1,024 | 307,200 RPM |
| 6 | 4,096 | 1,228,800 RPM |

The final columns are arithmetic, not achievable-speed claims. In a free cylinder:

    omega_out = omega_reaction + 4^N (omega_shell - omega_reaction)

Changing the number of stages changes the rotor inertia and the motion of the reaction
drum. The previous three-stage free-drum multiplier cannot be reused for more stages.
A larger ratio may produce a LOWER actual output speed for a given available energy.
A simple output-only inertia J is reflected at the input as G^2 J. Each additional
4:1 stage multiplies that contribution by 16. For a finite drop, the system may hit
the ground before spinning up appreciably.

With a restrained reaction member, output torque is approximately input torque times
the product of stage efficiencies divided by G. Even an assumed 98% per stage gives
about 88.6% overall after six stages. That percentage is illustrative, not measured
for either CAD model. The more important limits can be torque, inertia, rotor stress,
bearing speed, slip and heat. A 25 mm radius rotor at the arithmetic six-stage speed
would have a rim speed of about 3.22 km/s: the ratio calculation alone is plainly
insufficient for a usable design.

No maximum useful stage count is established for this experiment. Start by comparing
one, two and three stages after obtaining the fin torque-versus-speed curve, magnetic
pull-out torque, rotor stress limits and loss model. Adding more stages now would
multiply an assumed input speed, not predict a better device.

## Contactless magnetic variant

The FreeCAD magnetic.FCMacro creates a separate model; the original toothed version
remains available. The cylinder and six pitched upper fins are retained. Each of the
three magnetic stages contains:

- Inner rotor: 4 pole pairs, represented by 8 alternating red/cyan magnetic sectors.
- Outer reaction rotor: 12 pole pairs, represented by 24 alternating magnetic sectors.
- Intermediate input rotor: 16 steel flux-modulating pieces, represented in gray.
- A nominal 2 mm radial vacuum gap on each side of the modulator.

Nominal radial dimensions in millimetres are: inner magnets 23-26, modulators 28-31,
outer magnets 33-36, outer back iron 36-39. Active axial length is 10 mm. The inner
rotor drives the next stage's modulator holder. The first holder attaches to the shell.
All outer rotors attach to the shared, independently rotating reaction drum.

For synchronous motion, the magnetic-gearing relation is:

    p_inner * omega_inner + p_outer * omega_outer
        = (p_inner + p_outer) * omega_modulator

With the chosen counts:

    omega_inner = 4 omega_modulator - 3 omega_outer

This preserves the previous cascade equation, including the need for a reaction
member. Permanent magnets transfer torque and energy; they do not supply continuous
energy or hold the reaction drum stationary.

The displayed phase is illustrative. The code imposes the synchronous relation;
it does not calculate magnetic force, torque, stable phase lag or pull-out torque.
Electromagnetic finite-element analysis is needed to establish these properties.
The wide gaps were chosen to make the concept visible, not optimized for torque.
Inter-stage magnetic leakage, end effects, saturation, demagnetization, magnet
retention, laminations and thermal design have not been resolved.

The supplied inertia calculation assumes polymer supports at 1,240 kg/m3, permanent
magnets at 7,500 kg/m3, steel at 7,800 kg/m3 and modulator material at 7,650 kg/m3.
The concept mass is 1.3044 kg. At an assumed 300 RPM shell, the calculation gives
a reaction speed of 304.64 RPM and a bottom speed of only 7.89 RPM in the free case.
The high-inertia inner magnet rotors substantially change the dynamics: this first
layout is NOT an improvement in free-fall speed. Holding the reaction member fixed
would restore the nominal 19,200 RPM, provided magnetic torque capacity is adequate.
A useful optimization must reduce rotor inertia and resolve the reaction mechanism
before adding stages.

These are illustrative. It assumes synchronous lock, zero initial spin, no losses,
and external torque applied only to the shell. Replacing gears with magnets changes
mass and inertia, so the toothed model's free-drum RPM result does not transfer.

## Why contactless is not lossless

Magnetic gearing removes tooth contact. Eddy currents and hysteresis can still heat
magnetic material; torque ripple and losses remain. Bearings are a separate design
problem. Magnetic bearings could remove normal rolling contact, but stable support
requires a suitable complete design, often active sensors, control and electrical
power, plus touchdown provisions. Passive permanent magnets alone do not provide
unconditionally stable static suspension in all directions.

The CAD does not contain a validated magnetic bearing system. Vacuum reduces
windage but also removes convective cooling. Increasing speed increases demands on
magnet retention and rotor containment. Magnetic coupling can lose synchronism when
its torque capacity is exceeded. Such slip interrupts the assumed gearing relation.

For a printed demonstrator, reuse the original low-speed printer/material guidance.
Print nonmagnetic holders only, with separate magnet pockets and positive retention
after a proper mechanical design. This concept does not specify a magnet grade,
pocket tolerance, adhesive or high-speed retention sleeve and is not a print release.

## Use

In WSL Ubuntu:

    DROP_RENDER=1 ~/Applications/freecad-experiment/squashfs-root/AppRun experiments/drop_gearbox/magnetic.FCMacro

This generates magnetic_output/magnetic.FCStd, full and cutaway STEP files, two
preview PNGs, a physics JSON and 72 frames. The FreeCAD controls switch between
restrained reaction, ideal free reaction, and locked co-rotation. No field solve is
performed. STEP files do not contain animation or magnetization vectors.

## References

- Gardner et al., magnetic gear geometry and synchronous equations:
  https://cpb-us-e2.wpmucdn.com/labs.utdallas.edu/dist/9/93/files/2021/09/PM-Materials.pdf
- NASA measurements illustrate that magnetic gearbox efficiency is not 100% and
  depends on operating point:
  https://ntrs.nasa.gov/citations/20190032574
- NASA magnetic-bearing technology assessment:
  https://www.nasa.gov/centers-and-facilities/nesc/magnetically-levitated-space-mechanisms/

Verification passed for all 186 solids, sector counts, radial gaps, the inertia
matrix and cutaway STEP roundtrip volume. See magnetic_output/verification.json.

Use python3 experiments/drop_gearbox/launch.py --magnetic --viewer to open the
magnetic STEP in Open STEP Viewer. Use --magnetic --render without --viewer to
rebuild and animate the magnetic version in FreeCAD.
