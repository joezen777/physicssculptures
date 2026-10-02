# Embossable bouncing-ball artwork for the flowerpots

## Target and delivered artwork

This uses the current modular fan tunnel shell in experiments/modular_fan_tunnel/build.FCMacro, cone_shape(): outside radii 60 and 84 mm over 58 mm axial height. It does not target the older 84/132 mm stacking cone. The collar above z=58 is excluded, as are the lowest wall regions that overlap the transition below.

Files are in experiments/pot_zoetrope/output:

- ball-cone-wrap-ccw.svg: taper-correct developed surface for counterclockwise rotation viewed from above.
- ball-cone-wrap-cw.svg: reversed animation frame order for clockwise rotation viewed from above.
- ball-uv-strip-ccw.svg and ball-uv-strip-cw.svg: rectangular angle/axial-height maps for CAD wrapping.
- cone-wrap-alignment-guide.svg: separate full-body outline; never include this in emboss geometry.
- dimensions.json and validation.json: dimensions and geometric checks.
- cone-wrap-preview.png: visual inspection of the counterclockwise developed artwork.

The SVGs use physical millimetre dimensions, black filled closed paths, no strokes, no clipping, no text geometry, no background shape, no external resources, and no SVG transforms. Each contains 24 frames, each with five platform shapes and one ball (144 paths total). Import the paths as geometry, not as a raster image. All black shapes represent raised areas.

## Mapping and dimensions

The rectangular UV strip is 452.389342 mm wide and 58 mm high: one full turn at the mid-height circumference. Its x coordinate maps to theta = 2*pi*x/width, increasing counterclockwise when viewed from above; y maps to z = 58-y. It is NOT a physical rectangular stencil for a tapered pot. Do not use the artwork bounding box for automatic fit-to-face scaling: preserve the SVG page coordinates, including margins.

The developed frustum uses slant length L = sqrt(58^2 + 24^2) = 62.769419 mm; q = 24/L; developed radius rho = r/q; sector angle = 2*pi*q = 137.646645 degrees. Its page is approximately 409.714610 by 163.005116 mm. For UV coordinates x,y, set r = 60 + 24*(58-y)/58 and phi = (x/width-0.5)*2*pi*q. The developed position is (rho*sin(phi), -rho*cos(phi)), translated to positive page coordinates. Thus the pattern closes around the taper without a mismatched seam. Polygonal mapping samples straight edges every 0.15 mm or less; balls have 96 polygon vertices.

Cone-wrap files must be conically wrapped/developed onto the shell, not simply extruded as a flat plane through it. For CAD software that offers cylindrical/UV surface mapping, use the UV strip with the explicit theta,z mapping above. Neither SVG by itself defines an emboss depth or changes the existing FreeCAD assembly.

The complete pattern has generous blank margins at the ends of each 15-degree angular cell. UV platforms are 4 by 1 mm, tilted +/-0.36 radians, with 1.6 mm diameter balls. Actual surface widths vary with taper: the UV horizontal scale is r/72. The tiny near-contact clearance is intentionally 0.35 mm in UV space to avoid tangent contours merging during CAD import.

## Animation and direction

One turn represents four descending bounces. The ball resets from bottom to top at the sequence boundary. This is a drawn animation, not a mechanical ball-return design. Every platform and ball stays fixed to the rotating shell.

With the bottom rotor moving counterclockwise from above, the default modular stack +1,-2,+4 uses CCW, CW, CCW artwork respectively. Reverse those choices if the bottom rotor turns clockwise. Mapping x in the opposite angular direction also reverses the required file choice.

For one captured pose per sample, sampling frequency is 24*abs(rpm)/60. A single shared strobe on the differently geared pots will skip different numbers of poses unless frame counts or sampling are redesigned. Ordinary continuous lighting does not guarantee the apparent bounce. Embossing also needs visible shading or contrasting color; use grazing illumination or color the raised faces for an optical trial. No physical optical performance is claimed.

## Emboss and printing intent

Start with 0.5 mm outward relief measured normal to the surface, fused into the shell with a small intersection. A small edge/underside chamfer around 0.15 mm is a candidate if it preserves the contours. Depth and edge treatment are CAD operations, not encoded by SVG fill.

For the existing Ender 3 V2 / Sprite Pro / 0.2 mm nozzle, PETG remains the pot-body trial material. Print the pot axis vertically at approximately 0.10 mm layers and test a small curved wall coupon first. Inspect the underside of outward relief for sagging; avoid support scars across the pattern and tune relief/chamfer if necessary. Feature separation, adhesion and contrast need a real print trial. Recheck rotor clearance and balance after adding relief; SVG validity alone does not qualify the turbine assembly.

## Reproduction and validation

Run in WSL Ubuntu:

    python3 experiments/pot_zoetrope/generate.py

The generator accepts --bottom-diameter, --top-diameter and --height for other outward-tapered pots; defaults match the current CAD. Regeneration overwrites SVGs and dimensions.json; regenerate validation and preview after changing dimensions. Preserve the page origin during import.

Default files passed XML parsing, 144-closed-path count, page containment, positive polygon area, polygon validity and all-pairs separation checks using Shapely. Minimum measured gap: approximately 0.37307 mm in developed artwork and 0.35043 mm in UV artwork. Chromium rendered the conical SVG for visual inspection. CAD wrapping, relief fusion, slicing and physical embossing have not been performed.
