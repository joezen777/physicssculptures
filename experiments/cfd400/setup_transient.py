"""Transient frozen-rotor sensitivity cases; not sliding-mesh validation."""
from pathlib import Path
import argparse,shutil,re,json,math
BASE=Path.home()/'.cache/angularmomflyer/cfd400'
p=argparse.ArgumentParser();p.add_argument('design');p.add_argument('--rpm',type=int,default=400);p.add_argument('--seconds',type=float,default=1.5);p.add_argument('--fine',action='store_true');args=p.parse_args()
src=BASE/(args.design+('_fine' if args.fine else '_coarse'))
dst=BASE/(args.design+('_fine' if args.fine else '')+f'_transient_{args.rpm}')
if dst.exists():raise SystemExit(f'Refusing to overwrite {dst}')
assert 'Mesh OK.' in (src/'log.checkMesh').read_text()
for name in ['system','constant']:shutil.copytree(src/name,dst/name)
# Start from rest, not an unconverged steady field.
shutil.copytree(src/'0',dst/'0')
for p in (dst/'0').iterdir():
 if p.name not in ['U','p']:p.unlink()
p=dst/'constant/MRFProperties';p.write_text(re.sub(r'omega [^;]+;',f'omega {-args.rpm*2*math.pi/60:.12g};',p.read_text()))
p=dst/'system/fvSchemes';p.write_text(p.read_text().replace('default steadyState;','default backward;').replace('bounded Gauss linearUpwind','Gauss linearUpwind'))
header='FoamFile {version 2.0;format ascii;class dictionary;object fvSolution;}\n'
(dst/'system/fvSolution').write_text(header+'''solvers {
p {solver GAMG;tolerance 1e-8;relTol .05;smoother GaussSeidel;}
pFinal {$p;relTol 0;}
U {solver smoothSolver;smoother symGaussSeidel;tolerance 1e-8;relTol .05;}
UFinal {$U;relTol 0;}
}
PIMPLE {nOuterCorrectors 2;nCorrectors 2;nNonOrthogonalCorrectors 1;momentumPredictor yes;}
relaxationFactors {equations {".*" 1;}}
''')
p=dst/'system/controlDict';s=p.read_text().replace('application simpleFoam;','application pimpleFoam;').replace('endTime 1000;deltaT 1;',f'endTime {args.seconds};deltaT 0.0001;adjustTimeStep yes;maxCo 0.7;maxDeltaT 0.001;').replace('writeControl timeStep;writeInterval 250;','writeControl adjustableRunTime;writeInterval 0.15;').replace('writeControl timeStep;writeInterval 10;','writeControl timeStep;writeInterval 1;').replace('writeControl timeStep;writeInterval 50;','writeControl adjustableRunTime;writeInterval 0.015;')
p.write_text(s)
(dst/'constant/dynamicMeshDict').write_text('FoamFile {version 2.0;format ascii;class dictionary;object dynamicMeshDict;}\ndynamicFvMesh staticFvMesh;\n')
(dst/'case.foam').touch()
(dst/'experiment.json').write_text(json.dumps(dict(design=args.design,rpm=args.rpm,seconds=args.seconds,mesh=str(src),initial_state='rest',method='transient laminar frozen-rotor MRF, not sliding mesh'),indent=2)+'\n')
print(dst)
