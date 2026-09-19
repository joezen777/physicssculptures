# Local dashboard

FastAPI (server.py) owns one Experiment and a background simulation worker. The worker integrates 40 ms of simulation per loop when running and pauses on numerical warnings. If computation is slower than wall time, simulation time advances more slowly; it is not advertised as exact real time.

API calls and integration share a lock. Applying configuration builds a replacement model before swapping, pauses it, clears history, and increments a model revision. An invalid configuration leaves the running model intact. Start/pause toggles without resetting; reset restores preparation state.

The browser uses React, Vite, MUI and Three.js. /api/model provides static geometry and body ownership. /api/state provides body poses, telemetry and a bounded history. Three.js renders those poses; it does not calculate the physics. Rendering/polling can visually alias high rotor speeds, so measured RPM is authoritative.

Two numeric fields/sliders set the small rotor group and donut target independently. Controls are draft values until Apply changes & reset. Joint and rotor options can be combined, giving four variants. The spring section provides preload, stiffness, plunger mass and release travel; release RPM is labeled as an estimate. The UI exposes paused/running state, preparation phase, RPM, latch state, pin displacement, tilt, mass or thrust.

Dependencies are bundled locally. No external fonts, remote scripts or CDN runtime resources are required. The backend binds only to localhost:8766. Use launch_lab.sh after npm build; launch.sh retains the optional MuJoCo native viewer.

Physical model details and limitations are in mechanisms.md. Browser controls do not silently change velocities during a run; applying changes starts a new experiment.

## Powered flight presets

POST /api/preset/flight, /api/preset/no-air, and /api/preset/original replace
the full configuration and pause at time zero. Flight uses free-body motion,
internal rotor motors and radial collar tilt servos. No-air retains those
motors, masses and targets but sets both aerodynamic coefficients to zero.
The flight preset disables passive pins and exposes a tilt target slider.
Telemetry includes weight and instantaneous net mechanical actuator power.
Selecting other joint/support modes disables incompatible tilt control.
