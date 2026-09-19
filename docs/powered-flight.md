# Powered flight and angular momentum

The powered-flight preset models a freely moving ring with four alternating-pitch propellers on radial collar hinges. Rotor motors and collar servos apply internal torques, with reaction torque on their parent bodies. There is no ground constraint, world motor, or upward force other than modeled propeller thrust. The donut coasts; maintaining its speed would require an additional counter-rotor or an external torque.

The assembly begins pre-spun at 30 RPM ring speed and 8600 RPM rotor-to-housing speed, with zero whole-machine linear momentum. Four torque-limited rotor motors maintain small-rotor speed. Four proportional/derivative servos ramp their tilt target from upright to 20 degrees in one second. The passive pins are disabled in this actively controlled experiment. Actual collar angles differ from the target under gyroscopic and orbital loads; this is not an exact position constraint or a flight stabilizer.

Mass is 2.94 kg: 2.5 kg assigned to the ring (including an assumed 0.5 kg power-system allowance), four 80 g rods and four 30 g propellers. Each propeller is 24 cm in diameter. Ct=0.1 and Cq=0.01 at air density 1.225 kg/m³ are illustrative, uncalibrated constants. Mechanical motor power is approximately 719 W; electrical input would be higher. Power is supplied by ideal internal motors without a battery discharge model.

## Measured results

Run `python flight.py` using the project virtual environment. The script saves measurements to `runs/flight-results.json`. At three seconds:

| Experiment | Center-of-mass height change | Final upward thrust |
| --- | ---: | ---: |
| Powered, 20° target tilt | +4.5800 m | 30.8405 N |
| Powered, upright target | +6.8178 m | 33.2954 N |
| Same mechanism, air forces off | −44.1450 m | 0 N |
| Air forces off, gravity off | approximately 0 m | 0 N |

Weight is 28.8414 N. All runs produced zero MuJoCo warnings. Halving the timestep from 0.2 ms to 0.1 ms changed the tilted climb by 0.000419 m. The three-second tilted run's change in total linear momentum agreed with integrated external force to 1.35e-8 N·s.

These are results of a static-coefficient aerodynamic model, not validated flight predictions. Inflow, forward-flight effects, wake interference, structural compliance, motor/battery sizing and active attitude stabilization are absent. The grid is not a collision floor, which permits a clean ballistic control experiment.

## Interpretation

Gyroscopic torques exchange angular momentum between rotors, mounts and ring. They can redirect orientation and therefore propeller thrust, but internal torques cannot accelerate the whole assembly's center of mass. Propellers generate external force by transferring momentum to air. Keeping the propellers upright provides more vertical thrust than tilting them; this model finds no additional lift from gyroscopic redirection.

NASA describes the momentum exchange underlying propeller thrust:
https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/propeller-thrust/

MuJoCo actuation and dynamics:
https://mujoco.readthedocs.io/en/stable/computation/index.html

This is an experiment model, not a printable high-speed rotor design.
