# Prototype validation, 2026-09-17

> Historical record: the collar/pin/propeller revision supersedes the original geometry and motor behavior. See [current mechanics](mechanisms.md), [dashboard](dashboard.md), and [current validation](validation-current.md).

Environment: WSL2 Ubuntu, Python 3.12.3, MuJoCo 3.13.0. Dependencies are installed in ~/.venvs/angularmomflyer on the Linux filesystem; installing the environment under the OneDrive repository was exceptionally slow and that attempt was stopped.

## Automated checks

All five tests passed:
- Static supported assembly reaction equals its weight (36.4932 N).
- Free assembly conserves momentum and energy with gravity disabled.
- Free assembly follows the ballistic center-of-mass trajectory with gravity.
- A known external torque changes angular momentum by its angular impulse.
- Smaller time steps converge for the initial trajectory.

The native viewer opened and ran for a three-second smoke check and exited successfully. Headless EGL rendering produced the 3D PNG and animated GIF. The initial rendered image and comparison plot were visually inspected.

## Demonstration results

Default geometry and initial conditions are documented in README.md. These figures are numerical results for an idealized model, not measurements of a physical device.

| Experiment | Simulated duration | Final ring height change | Maximum whole-center-of-mass error |
| --- | --- | --- | --- |
| Free, no gravity, spinning satellites | 3 s | +0.05887795 m | 1.14e-9 m |
| Free, no gravity, initially stopped satellites | 3 s | +0.19523635 m | 5.17e-9 m |
| Free, no gravity, alternating satellite spin | 3 s | +0.07963476 m | 2.29e-7 m |
| Free fall, spinning satellites | 1 s | -4.85187812 m | 1.14e-9 m |

The free-fall center of mass dropped 4.905 m after one second, as predicted by gravity. The ring moved relative to it. No net lift is indicated. Initially stopped satellites are free to start rotating through coupling; they are not locked.

All six demonstration cases completed without MuJoCo numerical warnings. Maximum relative total-energy drift among them was below 4.8e-8.

## Additional three-second convergence runs

Halving the step from 0.2 ms to 0.1 ms gave:
- Free, same spin: endpoint ring-height difference 2.05e-9 m; maximum endpoint axle-tilt difference 1.47e-6 degrees.
- Free, alternating spin: endpoint ring-height difference 1.61e-7 m; maximum endpoint axle-tilt difference 1.25e-5 degrees. Maximum center-of-mass error fell to 5.73e-8 m.
- Supported, same spin: maximum endpoint axle-tilt difference 1.78e-5 degrees.

Tiny center-of-mass residuals are numerical error, not predicted propulsion. These checks cover these configurations and time intervals only.

## Reproduction

Run the unittest command and make_demo.py documented in README.md. Additional convergence calculations are in validate_convergence.py. Generated trajectories, models, graphics, configuration summaries and convergence output are saved under runs/demo and excluded from source control.

## Staged startup correction

Eight tests now pass, including the original five and three new tests: the actual viewer controller's R-then-SPACE sequence, five-second staged time-step comparison, and rejection of a ground motor in free flight.

The reset regression checks that all velocities/time return to zero and remain unchanged while paused. One second after SPACE, the small wheels are around 600 RPM while the ring remains below 0.01 RPM. After 2.4 seconds all four wheels are within 1 RPM of 1200 while the ring remains below 0.01 RPM. Later the ring accelerates, all preparation constraints release and rotor motor controls are zero. Pausing and resetting again restores the preparation constraints.

The five-second staged run agrees with a half-step run within 0.03 RPM for ring speed and 0.1 degree for each axle tilt. Both complete with no numerical warnings. The corrected native viewer also passes its three-second launch/close smoke check.
