"""Generate reproducible controls, comparisons and a 3D preview in runs/demo."""
from dataclasses import replace
from pathlib import Path
import json
import numpy as np
from gyro_sim import Config, simulate


def main():
    out = Path("runs/demo")
    out.mkdir(parents=True, exist_ok=True)
    base = Config(duration=3)
    cases = {
        "supported_spinning": base,
        "supported_stopped": replace(base, rotor_rpm=0),
        "free_spinning": replace(base, mode="free", gravity=0),
        "free_stopped": replace(base, mode="free", gravity=0, rotor_rpm=0),
        "free_alternating": replace(base, mode="free", gravity=0, alternating=True),
        "free_fall": replace(base, mode="free", duration=1),
    }
    results = {}
    summaries = {}
    for name, c in cases.items():
        results[name], summaries[name] = simulate(c, out/name)
        print(name, summaries[name], flush=True)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(13, 5), constrained_layout=True)
    for name, label in (("free_spinning", "Spinning rotors"),
                        ("free_stopped", "Stopped rotors"),
                        ("free_alternating", "Alternating rotors")):
        rows = results[name]
        t = [r["time"] for r in rows]
        ax[0].plot(t, [(r["ring_z"]-rows[0]["ring_z"])*1000 for r in rows],
                   label=label)
        ax[1].plot(t, [(r["com_z"]-rows[0]["com_z"])*1000 for r in rows],
                   label=label)
    ax[0].set_title("Ring alone can move vertically")
    ax[1].set_title("Whole-machine center of mass stays put")
    ax[1].set_ylim(ax[0].get_ylim())
    for a in ax:
        a.set_xlabel("Time (s)")
        a.set_ylabel("Height change (mm)")
        a.grid(alpha=.2)
        a.legend()
    fig.suptitle("Free assembly, gravity off | initial spin, then coast")
    fig.savefig(out/"comparison.png", dpi=140)
    plt.close(fig)
    (out/"validation.json").write_text(json.dumps(summaries, indent=2))

    import mujoco
    from PIL import Image, ImageDraw
    renderer = None
    frames = []
    camera = mujoco.MjvCamera()
    camera.distance, camera.azimuth, camera.elevation = 2.3, 120, -27
    camera.lookat[:] = [0, 0, 1.07]
    def frame(model, data):
        nonlocal renderer
        if renderer is None:
            renderer = mujoco.Renderer(model, height=600, width=800)
        renderer.update_scene(data, camera)
        im = Image.fromarray(renderer.render())
        draw = ImageDraw.Draw(im)
        draw.rectangle((0, 0, 800, 60), fill=(20, 28, 38))
        draw.text((16, 10), "GYROSCOPIC RING | SUPPORTED | 30 RPM carrier / 1200 RPM rotors",
                  fill="white")
        draw.text((16, 32), f"t = {data.time:.2f} s | ideal joints; no collisions; initial spin then coast",
                  fill=(150, 215, 235))
        frames.append(im)
    try:
        simulate(base, frame_callback=frame)
    finally:
        if renderer:
            renderer.close()
    frames[0].save(out/"preview.png")
    frames[0].save(out/"preview.gif", save_all=True, append_images=frames[1:],
                   duration=40, loop=0)
    print(f"Demo files: {out.resolve()}")


if __name__ == "__main__":
    main()
