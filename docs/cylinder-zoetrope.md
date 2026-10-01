# Cylindrical brick relay zoetrope

The interactive fragment is in experiments/cylinder-zoetrope.html. It runs without network requests or a backend and is intended for the conversation visualization renderer.

## Geometry and timing

Four rows each contain 24 fixed silhouette poses on the outside of an opaque cylinder. A canvas orthographic projection compresses each figure horizontally by the cosine of its angle and hides the rear hemisphere. This is a conceptual surface drawing, not a manufactured 3D model.

Each drawing's phase is (-column / 24 - row * 0.75) modulo one. Over the first three quarters of a cycle its brick moves from 4 units above the row origin to 92 units below it; row origins are 96 units apart. At transfer, the upper row's final brick position coincides with the lower row's initial position. Only the receiving row owns the brick at the boundary. The remaining quarter-cycle returns empty hands upward. Bricks enter above the top and leave below the bottom; this is an open relay, not a closed material loop.

Rotation advances at rpm / 60 turns per second. The sampled view evaluates the cylinder at floor(turns * 24) / 24 turns, holding the last captured image between samples. Therefore sample frequency = 24 * rpm / 60; the default 30 rpm gives 12 samples/second and a two-second action cycle. The drawings themselves do not change in time. Sampling replaces one drawing with the next at each viewing position.

The continuous view uses the same static artwork with continuous angular motion. Browser refresh can itself alias the rotation, and this simplified renderer does not model motion blur, exposure duration, slit optics, lighting, or perceptual persistence. The sampled view deliberately uses held images rather than flashing the screen. A physical build needs synchronized shutter/slit/strobe sampling to reproduce the effect.

Unwrapped view shows 14 adjacent drawings of each row; it does not animate. Pause and Next pose support inspecting individual transfer positions. Reduced-motion users start paused.

## References

- https://kellyegan.net/2014/3d-printed-zoetrope/ — construction example and flashes per rotation.
- https://www.sarahkushner.com/pdf/uist-zoetrope-abstract.pdf — strobe-synchronized cylindrical animation.

## Validation

Chromium in WSL: rendered and visually inspected the cylinder; verified frame stepping changes pixels, pause state, all three views, speed-to-sample-frequency updates, and no JavaScript errors. Verified no root horizontal overflow at a 360px viewport. No physical optical experiment has been performed.
