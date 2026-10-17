"""Shared geometry, dimensions in mm; prototype, not a validated airfoil."""
import math
def station(r):
    beta=50-28*min(1,max(0,(r-21)/10))
    cap=36.4-10*max(0,min(1,(r-64)/6.4))
    width=min(math.radians(118),cap/(r*math.tan(math.radians(beta))))
    h=r*width*math.tan(math.radians(beta))
    base=1.2+10*max(0,min(1,(r-64)/6.4))
    sweep=math.radians(24*math.sin(math.pi*(r-21)/51)-12*(r-21)/51)
    return beta,width,h,base,sweep
RADII=[21,21.8,22.6,24,27,31,36,42,48,54,60,64,67,70.4,72]
THICKNESS=2.4
CAMBER=1.2
