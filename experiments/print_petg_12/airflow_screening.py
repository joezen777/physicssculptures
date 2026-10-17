"""Uncalibrated steady-state screening, not CFD or physical measurements."""
import math, json
from pathlib import Path

RHO=1.225
WIND=10*1852/3600
NU=1.5e-5
ROOT=.022
CHORD=.018
N=160

def bisect(f, lo, hi):
    assert f(lo)*f(hi)<=0
    for _ in range(65):
        mid=(lo+hi)/2
        if f(mid)>0: lo=mid
        else: hi=mid
    return (lo+hi)/2

def sail_coeff(lam, phases=720):
    vals=[]
    for j in range(phases):
        vs=[math.cos(2*math.pi*j/phases+i*2*math.pi/3)-lam for i in range(3)]
        vals.append(sum((1.4 if v>=0 else .4)*v*abs(v) for v in vs))
    return min(vals),sum(vals)/phases,max(vals)

def rotor(radius, blades=6, twisted=False, lift_scale=1, cd0=.06, n=N):
    # Solve at omega=1 rad/s; forces scale as omega^2, induced velocity as omega.
    area=math.pi*(radius**2-ROOT**2)
    dr=(radius-ROOT)/n
    def forces(vi):
        thrust=torque=0
        for j in range(n):
            r=ROOT+(j+.5)*dr
            beta=math.radians(35-20*(r-ROOT)/(radius-ROOT) if twisted else 22)
            phi=math.atan2(vi,r)
            alpha=beta-phi
            cl=lift_scale*math.sin(2*alpha)
            cd=cd0+2*math.sin(alpha)**2
            q=.5*RHO*(r*r+vi*vi)*blades*CHORD*dr
            thrust+=q*(cl*math.cos(phi)-cd*math.sin(phi))
            torque+=q*(cl*math.sin(phi)+cd*math.cos(phi))*r
        return thrust,torque
    vi=bisect(lambda v:forces(v)[0]-2*RHO*area*v*v,0,radius)
    thrust,torque=forces(vi)
    assert 0 < thrust*vi <= torque
    return dict(vi=vi,thrust=thrust,torque=torque,area=area)

def run():
    sails=[('original cups',math.pi*476e-6,.108),('80x120 scoops',.0096,.18)]
    variants=[('P17 six flat blades',6,False),('four twisted flat-section blades',4,True),('six twisted flat-section blades',6,True)]
    lam_free=bisect(lambda l:sail_coeff(l)[1],0,1)
    rows=[]
    for polar,scale,cd in [('nominal',1,.06),('lower lift / higher drag',.7,.12),('higher lift / lower drag',1.3,.04)]:
        lower=rotor(.060,lift_scale=scale,cd0=cd)
        for variant,b,twist in variants:
            top=rotor(.072,b,twist,scale,cd)
            for name,a,r in sails:
                factor=.5*RHO*WIND**2*a*r
                static=[v*factor for v in sail_coeff(0)]
                for eta in (.6,.8,1.):
                    # eta is aggregate transmission efficiency for geared loads.
                    k=lower['torque']*(1+(2**3+4**3)/eta)+top['torque']*8**3/eta
                    for friction in (0,.002,.005,.010):
                        def balance(w):
                            return factor*sail_coeff(w*r/WIND)[1]-friction-k*w*w
                        if balance(0)<=0: w=0.
                        else: w=bisect(balance,0,lam_free*WIND/r)
                        wt=8*w
                        power=top['torque']*wt**3
                        v=top['vi']*wt
                        flow=top['area']*v
                        rows.append(dict(sails=name,variant=variant,polar=polar,transmission_efficiency=eta,
                            input_friction_mNm=friction*1000,
                            startup='all phases under assumed breakaway=running friction' if static[0]>friction else 'phase dependent' if static[2]>friction else 'no static phase',
                            input_rpm=w*30/math.pi,top_rpm=wt*30/math.pi,
                            top_disk_axial_m_s=v,top_flow_L_s=flow*1000,top_flow_CFM=flow*2118.88,
                            top_shaft_W=power,top_thrust_N=top['thrust']*wt*wt,
                            tip_chord_Re=CHORD*math.hypot(wt*.072,v)/NU,
                            ideal_same_power_flow_L_s=(top['area']*(power/(2*RHO*top['area']))**(1/3)*1000 if power else 0),
                            balance_residual_Nm=balance(w),static_min_mean_max_mNm=[x*1000 for x in static]))
    # Numerical checks: phase quadrature, radial convergence and equilibrium.
    assert max(abs(x-y) for x,y in zip(sail_coeff(0),(.3,.75,1.2)))<1e-10
    coarse=rotor(.072,n=80); fine=rotor(.072,n=320)
    convergence={key:abs(coarse[key]/fine[key]-1) for key in ('vi','thrust','torque')}
    assert max(convergence.values())<.001
    assert all(abs(x['balance_residual_Nm'])<1e-10 for x in rows if x['input_rpm']>0)
    data=dict(wind_knots=10,wind_m_s=WIND,free_running_tip_speed_ratio=lam_free,
        limitations='Uncalibrated analytical screening. No physical measurements, CFD, measured polars, wake coupling, crosswind effects, or startup dynamics.',
        convergence_relative=convergence,cases=rows)
    out=Path(__file__).with_suffix('.json')
    out.write_text(json.dumps(data,indent=2)+'\n')
    selected=[x for x in rows if x['polar']=='nominal' and x['transmission_efficiency']==.8 and x['input_friction_mNm']==2]
    print(json.dumps(dict(wind=WIND,convergence=convergence,selected=selected),indent=2))
if __name__=='__main__': run()

