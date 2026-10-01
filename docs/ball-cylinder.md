# Ball bouncing down tilted rectangles

experiments/ball-cylinder.html is a second cylindrical zoetrope proof of concept, preserving the brick relay separately. It uses the same 24-sector projection and sampled rotation described in cylinder-zoetrope.md.

Each fixed sector contains five narrow rectangular platforms with alternating tilt (+/-0.36 radians), staggered left/right by 14 drawing units. One ball occupies a fixed pose in each sector. The phase is (-sector / 24) modulo one. One revolution represents four downward bounces; six captured poses describe each bounce.

For bounce stage k and fractional progress u, the ball follows linear horizontal interpolation between successive contact centers and vertical position y = y_contact(k) + 84*u - 180*u*(1-u). This produces a short rise after impact followed by an accelerating descent. Contact centers include the radius offset along the platform normal. Platforms and balls are all fixed artwork; only the cylinder angle changes. The sampled view holds captures at one-sector angular increments.

This is prescribed animation, not a rigid-body collision solver: bounce energy is not calculated, and the bottom-to-top loop reset is intentional. It demonstrates apparent descending motion on a rotating cylindrical surface, not a mechanism that returns a real ball upward. Surface projection omits motion blur, lighting optics, and physical construction constraints.

The view selector compares sampled motion, continuous rotation, and a static unwrapped strip of 14 adjacent drawings. The default 30 rpm gives 12 captured poses per second and a two-second descent loop. The renderer holds frames without flashing. Reduced-motion users start paused.

Validation: Chromium in WSL; visual screenshot inspection; pose stepping changes the image and 24 steps return to the same image; all three views; speed update; 320/360/736px layouts without horizontal overflow; no JavaScript errors. Physical optical behavior has not been experimentally verified.
