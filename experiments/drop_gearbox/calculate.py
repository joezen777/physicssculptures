"""Conditional RPM and gravity-energy ceilings, not an aerodynamic prediction."""
import argparse
import json
import math
from pathlib import Path

def speeds(shell_rpm, reaction_rpm, stages=3):
    return [reaction_rpm + 4**i*(shell_rpm-reaction_rpm) for i in range(stages+1)]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shell-rpm",type=float,default=300)
    parser.add_argument("--height",type=float,default=100)
    args=parser.parse_args()
    if args.height<0: parser.error("height must be nonnegative")
    p=json.loads((Path(__file__).parent/"output/physics.json").read_text())
    M=p["M"]; k=p["free_reaction_per_shell"]
    r=args.shell_rpm
    for mode,ratio in [("Ideal restrained reaction",0),("Free lossless reaction",k),("Locked co-rotation",1)]:
        print(mode)
        print("  reaction RPM:",round(ratio*r,3))
        print("  shell, stage 1, stage 2, stage 3 RPM:",[round(x,3) for x in speeds(r,ratio*r)])
    energy=p["mass_kg"]*9.80665*args.height
    for mode,ratio in [("Restrained",0),("Free",k)]:
        J=M[0][0]+2*ratio*M[0][1]+ratio*ratio*M[1][1]
        w=math.sqrt(2*energy/J) if J else 0
        print(f"{mode} gravity-only ceiling for {args.height:g} m: shell {w*30/math.pi:,.0f} RPM; bottom {abs(64-63*ratio)*w*30/math.pi:,.0f} RPM")
    print("Ceilings assign ALL m*g*h to rotation: unattainable with translation, drag and losses.")
    print("No drop-speed or shell-RPM prediction is made; aerodynamic torque data is required.")

if __name__=="__main__":
    main()
