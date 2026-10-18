"""Generate an isolated-rotor MRF CFD case at 400 RPM, SI units."""
from pathlib import Path
import math,json,os,shutil,argparse
ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('design');parser.add_argument('--fine',action='store_true')
args=parser.parse_args()
case=Path.home()/'.cache/angularmomflyer/cfd400'/ (args.design+('_fine' if args.fine else '_coarse'))
assert not case.exists(),str(case)+' already exists'
for d in ('0','constant/triSurface','system'): (case/d).mkdir(parents=True,exist_ok=True)
shutil.copy2(ROOT/'geometry'/(args.design+'.stl'),case/'constant/triSurface/fan.stl')
def write(path,body,cls='dictionary'):
    p=case/path
    p.write_text('FoamFile { version 2.0; format ascii; class '+cls+'; object '+p.name+'; }\n'+body+'\n')
write('system/blockMeshDict',"""convertToMeters 1;
vertices ((-.2 -.2 -.25)(.2 -.2 -.25)(.2 .2 -.25)(-.2 .2 -.25)
(-.2 -.2 .25)(.2 -.2 .25)(.2 .2 .25)(-.2 .2 .25));
blocks (hex (0 1 2 3 4 5 6 7) (40 40 50) simpleGrading (1 1 1));
edges ();
boundary (farfield {type patch; faces ((0 3 2 1)(4 5 6 7)(0 1 5 4)(1 2 6 5)(2 3 7 6)(3 0 4 7));});
mergePatchPairs ();
""")
level=4 if args.fine else 3
write('system/snappyHexMeshDict',f"""castellatedMesh true; snap true; addLayers false;
geometry {{
 fan.stl {{type triSurfaceMesh;name fan;}}
 nearRotor {{type searchableCylinder;point1 (0 0 -.035);point2 (0 0 .055);radius .085;}}
 wake {{type searchableCylinder;point1 (0 0 -.12);point2 (0 0 .12);radius .09;}}
}}
castellatedMeshControls {{
 maxLocalCells 2000000;maxGlobalCells 2500000;minRefinementCells 0;maxLoadUnbalance .1;nCellsBetweenLevels 3;
 features ();
 refinementSurfaces {{fan {{level ({level} {level});patchInfo {{type wall;}}}}}}
 resolveFeatureAngle 30;
 refinementRegions {{nearRotor {{mode inside;levels ((1E15 2));}}wake {{mode inside;levels ((1E15 1));}}}}
 locationInMesh (.15 .15 .15);allowFreeStandingZoneFaces true;
}}
snapControls {{
 nSmoothPatch 3;tolerance 1.5;nSolveIter 50;nRelaxIter 5;nFeatureSnapIter 10;
 implicitFeatureSnap true;explicitFeatureSnap false;multiRegionFeatureSnap false;
}}
addLayersControls {{
 relativeSizes true;layers {{}};expansionRatio 1.2;finalLayerThickness .3;minThickness .1;
 nGrow 0;featureAngle 60;nRelaxIter 3;nSmoothSurfaceNormals 1;nSmoothNormals 3;
 nSmoothThickness 10;maxFaceThicknessRatio .5;maxThicknessToMedialRatio .3;
 minMedialAxisAngle 90;nBufferCellsNoExtrude 0;nLayerIter 50;
}}
meshQualityControls {{
 maxNonOrtho 65;maxBoundarySkewness 4;maxInternalSkewness 4;maxConcave 80;
 minVol 1e-18;minTetQuality 1e-15;minArea -1;minTwist .02;minDeterminant .001;
 minFaceWeight .02;minVolRatio .01;minTriangleTwist -1;nSmoothScale 4;errorReduction .75;
}}
mergeTolerance 1e-6;
""")
write('system/topoSetDict',"""actions (
 {name rotorCells; type cellSet; action new; source cylinderToCell;
 sourceInfo {p1 (0 0 -.035);p2 (0 0 .055);radius .082;}}
 {name rotor;type cellZoneSet;action new;source setToCellZone;sourceInfo {set rotorCells;}}
);
""")
write('constant/MRFProperties',"""rotation {cellZone rotor;active yes;nonRotatingPatches (farfield);
origin (0 0 0);axis (0 0 1);omega -41.8879020479;}""")
write('constant/transportProperties','transportModel Newtonian;nu [0 2 -1 0 0 0 0] 1.5e-5;')
write('constant/turbulenceProperties','simulationType laminar;')
write('0/U',"""dimensions [0 1 -1 0 0 0 0];internalField uniform (0 0 0);
boundaryField {fan {type fixedValue;value uniform (0 0 0);}
farfield {type pressureInletOutletVelocity;value uniform (0 0 0);}}""",'volVectorField')
write('0/p',"""dimensions [0 2 -2 0 0 0 0];internalField uniform 0;
boundaryField {fan {type zeroGradient;}farfield {type fixedValue;value uniform 0;}}""",'volScalarField')
write('system/fvSchemes',"""ddtSchemes {default steadyState;}
gradSchemes {default cellLimited Gauss linear 1;}
divSchemes {default none;div(phi,U) bounded Gauss linearUpwind grad(U);div((nuEff*dev2(T(grad(U))))) Gauss linear;}
laplacianSchemes {default Gauss linear limited .5;}
interpolationSchemes {default linear;}
snGradSchemes {default limited .5;}
wallDist {method meshWave;}
""")
write('system/fvSolution',"""solvers {
p {solver GAMG;tolerance 1e-8;relTol .05;smoother GaussSeidel;}
U {solver smoothSolver;smoother symGaussSeidel;tolerance 1e-9;relTol .05;}
}
SIMPLE {nNonOrthogonalCorrectors 1;consistent yes;}
relaxationFactors {fields {p .1;}equations {U .2;}}
""")
sets=[]
for name,z in [('below',-.04),('above',.08)]:
    pts=[]
    for i in range(12):
        r=.072*math.sqrt((i+.5)/12)
        for j in range(48):
            theta=2*math.pi*(j+.5)/48
            pts.append(f'({r*math.cos(theta):.9f} {r*math.sin(theta):.9f} {z})')
    sets.append(name+' {type cloud;axis xyz;points ('+' '.join(pts)+');}')
write('system/controlDict',"""application simpleFoam;startFrom startTime;startTime 0;stopAt endTime;endTime 1000;deltaT 1;
writeControl timeStep;writeInterval 250;purgeWrite 2;writeFormat ascii;writePrecision 9;writeCompression off;
timeFormat general;timePrecision 6;runTimeModifiable true;
functions {
 loads {type forces;libs ("libforces.so");patches (fan);rho rhoInf;rhoInf 1.225;CofR (0 0 0);
 writeControl timeStep;writeInterval 10;log false;}
 velocitySamples {type sets;libs ("libsampling.so");interpolationScheme cellPoint;setFormat raw;
 fields (U p);writeControl timeStep;writeInterval 50;sets ("""+'\n'.join(sets)+""");}
}
""")
write('system/decomposeParDict','numberOfSubdomains 4;method scotch;')
(case/'case.foam').touch()
print(case)
