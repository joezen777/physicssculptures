# 400 RPM isolated-rotor CFD

Run in WSL Ubuntu from the repository root. No cloud service is used. See `docs/p17-cfd-400rpm.md` for assumptions and output definitions.

## Runtime

The calculation uses locally unpacked OpenCFD OpenFOAM v1912.260127-1 from the official Noble repository, not a system installation. `foam_runtime.py` defines the runtime paths. The official package index is https://dl.openfoam.com/repos/deb/dists/noble/main/binary-amd64/Packages.gz . Packages `openfoam1912` and `openfoam1912-common` are unpacked under `~/.cache/angularmomflyer/openfoam/maintained/`. The original Ubuntu v1912 mesher was used for the original coarse mesh; its flow solver had a SHA1 stream error and was replaced by the maintained build.

Runtime dependencies are unpacked with `apt-get download` and `dpkg-deb -x` into `~/.cache/angularmomflyer/openfoam/root/`: libopenmpi3t64, libptscotch-7.0, libscotch-7.0, libfftw3-double3, libboost-system1.83.0, libhwloc15, libevent-core-2.1-7t64, libevent-pthreads-2.1-7t64, libpmix2t64, libnl-3-200, libnl-route-3-200, libmunge2, openmpi-bin and openmpi-common. No administrator privileges were used. The maintained build's `lib/dummy` directory supplies the unused optional KaHIP decomposition library; the cases run serially.

## Generate and run

The checked-in STL surfaces are in metres. Geometry generators use the repository's FreeCAD models and the FreeCAD bundled Python runtime; do not run them with plain system Python. They simplify hub pockets and generate representative candidate shapes as documented.

```bash
python3 experiments/cfd400/setup_case.py original
python3 experiments/cfd400/run_case.py ~/.cache/angularmomflyer/cfd400/original_coarse
# Repeat for scimitar, tubercled, toroidal5.
python3 experiments/cfd400/setup_case.py original --fine
python3 experiments/cfd400/run_case.py ~/.cache/angularmomflyer/cfd400/original_fine
python3 experiments/cfd400/summarize.py --save
```

The generator refuses to overwrite an existing case. `run_case.py` remeshes and overwrites its stage logs; use `--solve-only` only for a deliberate solve of an existing checked mesh. Do not rerun an active case. Large mesh/field data stay in the Linux cache; compact results and source are committed. The `.foam` file can be opened with a compatible ParaView reader.

`plot_geometry.py` uses NumPy and Matplotlib. The local plotting environment is `~/.cache/angularmomflyer/cfd-venv/`.

No score should be treated as a reliable winner if the flow has not numerically settled or mesh sensitivity can change the ranking. In particular, solver iterations are not physical-time samples and cannot be averaged as a transient simulation.
