# P15/P16 sail screening - 2026-10-07

P14 and all production CAD/STLs are unchanged. These are concepts, not print-ready replacements or measured drag.

## Geometry and choices
Existing P16 is a shallow spherical cap (outer/inner radii 24/20.4 mm, clipped 10 mm below sphere center), not a hemisphere. Outer diameter is 43.63 mm; frontal reference area is 14.95 cm2. Inner opening is about 9.93 cm2; do not confuse reference frontal area with curved shell area. Tangential moment arm is 108 mm.

| Alternative P16 | Area per sail | Proposed P15 radius |
|---|---:|---:|
| Rounded-back C scoop 60 x 100 mm | 60 cm2 | 160 mm |
| Rounded-back C scoop 80 x 120 mm | 96 cm2 | 180 mm |
| Rounded-back C scoop 100 x 150 mm | 150 cm2 | 200 mm |
| Deep round/conical bucket, diameter 80 mm | 50.3 cm2 | 160-180 mm |
| Feathering paddle/louvers 80 x 120 mm | 96 cm2 gross | 180 mm |

Prefer the middle C scoop for an initial prototype. Dimensions are frontal envelopes, not developed sheet widths. Louvers may reduce return drag but require steel pivots, stops and reliable passive opening. A fixed flat panel has similar forward/reverse drag and is unsuitable by itself. Twisted scoops might smooth torque but require separate analysis.

Preserve the complete P15 root engagement and original two M4 x10 screw locations. Stretching its existing curve changes those locations. Reinforce only beyond the root; P14 remains a load limit. Use a keyed saddle to spread P16 load and resist rotation around its bolt. Check steel bolt grip length.

Check full swept clearances and table height. An 80 mm radial width at 180 mm radius has nominal inner edge 140 mm versus pot radius 96 mm; scoop depth/deflection still matter. A 150 mm tall sail centered at old elevation -9 mm extends below the base feet; raise its P15 attachment.

PETG provisional shell 2.4-3.6 mm with rim/saddle ribs, subject to load tests. Print arm flat with continuous layers along its length, preserving root thickness. Print scoop upright with saddle supports as necessary. Historical output uses a 1.2 mm nozzle inspection profile; repository setup specifies 0.2 mm. Slice for the actual installed nozzle. No new mesh, structural or slicer validation is claimed.

## Model and handoff
F=0.5 rho U_relative^2 Cd A; torque uses tangential force times radius. All three arms drive/brake simultaneously. Arbitrary-angle startup requires total torque above breakaway resistance at every angle. Running inertia can bridge a weak interval only while K(theta)=K(start)+integral(T_air-T_load)dtheta stays positive. Positive work over a whole turn does not alone guarantee startup.

sail_screening.py samples 3600 phases with normal-component drag:
u_i/U=cos(theta+2 pi i/3)-lambda; lambda=omega r/U.
T=0.5 rho U^2 A r sum(C_i (u_i/U) abs(u_i/U)).
Assume rho=1.225 kg/m3, driving C=1.4, returning C=0.4. These are NOT calibrated coefficients for existing or proposed sails. Crossflow, lift, wakes, support drag, pitching moments and Reynolds effects are omitted. Same coefficients isolate area/radius effects only.

At rest coefficient sum min/mean/max=0.30/0.75/1.20. Weak phase: 2(1.4)(0.5^2)-0.4=0.30.
At 5 m/s, torque before mechanical/fan losses:
| Sail | Weak/mean/strong torque, mN m |
|---|---|
| Existing at 108 mm | 0.74/1.85/2.97 |
| 60x100 at 160 mm | 4.41/11.03/17.64 |
| 80x120 at 180 mm | 7.94/19.85/31.75 |
| 100x150 at 200 mm | 13.78/34.45/55.13 |

80x120 at 5 m/s: separate face-on drive/reverse forces 0.206/0.0588 N, corresponding to 37.0/10.6 mN m. These face-on opposing positions do not occur simultaneously with three arms. Weak phase: two partial driving contributions total 18.5 against 10.6 mN m return, leaving 7.94. Reverse consumes 57% there versus 29% face-on.

At lambda=0.2 the same phase gives 2(1.4)(0.3^2)-0.4(1.2^2)=-0.324, a braking interval; inertia may bridge it. Static estimates do not predict running speed. If return C is 0.7, static weak torque is zero: area alone cannot ensure all-angle starting under this model.

## Area and actual hardware
A per sail >= T_breakaway/(0.5 rho U^2 r 0.30). Three arms already included.
For hypothetical 10 mN m resistance at 180 mm:
| Wind m/s | Area cm2 per sail | With 2x torque reserve |
|---|---:|---:|
| 3 | 336 | 672 |
| 5 | 121 | 242 |
| 8 | 47 | 94 |

Scale directly with measured resistance, inversely with radius and wind squared. The 80x120 option at 5 m/s supports only about 4 mN m resistance with 2x static reserve. Target wind, payload and actual resistance are unknown.

Stationary steel rod/axles/spacers do not count as rotating inertia. Rotating hardware and PETG do; soil/plants also matter. Weight affects bearing loading but is not directly braking torque about a vertical axis.

Speeds +1,-2,+4,-8 reflect resisting torque to input by absolute ratio, plus losses: 1 mN m at top fan requires at least 8 mN m input. Effective inertia sums I_j g_j^2 (top fan factor 64), including planets and moving hardware. Fan load depends on speed. For constant net acceleration from rest through 120 degrees in time t, T_net=2 I_effective (2 pi/3)/t^2, in addition to resistance. Real dynamics require integration.

## Measurements
Pull tangentially at known input radius on the fully assembled steel/PETG stack with intended payload. Sample peak breakaway force over multiple turns: T=F r. At 108 mm, 0.10 N means 10.8 mN m (10 g hanging mass approximately 10.6 mN m, allowing for cord/pulley effects). Measure running torque at intended speeds too. Measure individual sail forces at both faces and intermediate angles in known wind, subtracting fixture drag; then measure whole-rotor locked torque and startup at multiple angles to capture shielding.

## Sources
NASA drag equation: https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/drag-equation/
Pindado et al. (2012): https://pmc.ncbi.nlm.nih.gov/articles/PMC3386737/
Local build.py, output/parts.json, output/PRINT_AND_ASSEMBLE.md.
Research supports relative-wind/angle modeling, not our assumed coefficients or this drivetrain.

## Implemented retrofit (2026-10-11)
The 80 x 120 mm half-cylinder scoop and reinforced 180 mm arm are now in experiments/print_petg_12/output/sail_80x120. Print three of each. P14 and the original release are unchanged. The keyed saddle uses M4 x30 steel bolts; the original root screws remain M4 x10 button-head. See that folder's README, CAD assembly, validation reports and previews. This is a printable prototype; aerodynamic and structural performance still require physical testing.

### Krull aesthetic retained
P15 now uses a flowing swept-crescent outline and matching curved reinforcing spine instead of the straight retrofit strut. Preserve this Krull-inspired visual language in future wind-arm revisions. The P14 root interface, 180 mm sail lever and P16 scoop geometry are unchanged. Edges remain blunt for a functional PETG part.

## 0.4 mm nozzle check (2026-10-11)

The 80x120 retrofit was originally inspected with a 0.2 mm nozzle profile. The Ender now has a 0.4 mm nozzle, so finish_sail_80x120.py slices P15/P16 with the shared 0.4 mm inspection profile (0.2 mm layers, 0.45 mm lines), allowing supports on the part. The thinnest features are the 2.7 mm saddle cheeks and 3.2 mm scoop shell, at least six lines wide; the 4.5 mm bolt bore is unchanged. Both parts generate toolpaths without slicer warnings and reach their full 24 mm and 120 mm heights. Geometry is unchanged, so the STLs need no regeneration. Strength, fit and print quality remain physically untested.
