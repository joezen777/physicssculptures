"""Common uncalibrated strip/momentum screening. NO resolved loop/tubercle CFD."""
from pathlib import Path
import math,json,csv,itertools
from airflow_screening import RHO,WIND,sail_coeff,rotor,bisect
from scimitar_geometry import station
ROOT=.0226;TIP=.072
A=math.pi*(TIP**2-ROOT**2)
OUT=Path(__file__).resolve().parent/'output/three_fan_comparison'
OUT.mkdir(exist_ok=True)
# Interpolation accelerates drive balances; direct residual checked below.
FREE=bisect(lambda l:sail_coeff(l)[1],0,1)
TABLE=[sail_coeff(FREE*i/1000)[1] for i in range(1001)]
def sail(lam):
    x=max(0,min(1000,lam/FREE*1000));i=min(999,int(x))
    return TABLE[i]+(TABLE[i+1]-TABLE[i])*(x-i)
def sections(design,n=240,pairs=4,chord_scale=1,tip_pitch=22,amplitude=.0015):
    rows=[]
    upper=.068 if design=='toroidal' else TIP
    for i in range(n):
        r=ROOT+(upper-ROOT)*(i+.5)/n;dr=(upper-ROOT)/n
        x=(r-ROOT)/(upper-ROOT)
        if design=='scimitar':
            beta,w,h,_,_=station(r*1000);c=math.hypot(r*w,h/1000);b=3
        elif design=='tubercled':
            beta=45-20*x
            c=(.035/math.sin(math.radians(45)))*(1-x)+(.018/math.sin(math.radians(25)))*x
            # Explicit trial tubercle wavelength 8 mm, amplitude 1.5 mm.
            # Only geometric chord modulation is represented; NO vortex benefit.
            if x>.4:
                u=(x-.4)/.6
                c+=amplitude*math.sin(math.pi*u)**2*math.sin(2*math.pi*(r-(ROOT+.4*(TIP-ROOT)))/.008)
            b=4
        elif design=='toroidal':
            beta=47.5-(47.5-tip_pitch)*x
            # 2 mm axial wall allowance within 35 mm root height.
            c=(.033/math.sin(math.radians(47.5)))*(1-x)+.018*x
            b=2*pairs
        else:raise ValueError(design)
        rows.append((r,dr,c*chord_scale,math.radians(beta),b))
    return rows
def unit_rotor(design,lift=1,cd0=.06,lift_factor=1,drag_factor=1,
               feature_cd=.01,n=240,**geometry):
    if design=='toroidal_5pairs':
        design='toroidal';geometry['pairs']=5
    strips=sections(design,n=n,**geometry)
    # Added tangential drag only: loop/winglet benefit remains unresolved.
    if design=='scimitar':
        extra_area=3*2*.0712*station(71.2)[1]*.010
    elif design=='toroidal':
        # Two wetted sides of an 18x4 mm outer bridge per loop.
        extra_area=2*geometry.get('pairs',4)*.018*.004
    else:extra_area=0
    def forces(vi):
        t=q=0
        for r,dr,c,beta,b in strips:
            phi=math.atan2(vi,r);alpha=beta-phi
            cl=lift*lift_factor*math.sin(2*alpha)
            cd=drag_factor*(cd0+2*math.sin(alpha)**2)
            f=.5*RHO*(r*r+vi*vi)*b*c*dr
            t+=f*(cl*math.cos(phi)-cd*math.sin(phi))
            q+=f*(cl*math.sin(phi)+cd*math.cos(phi))*r
        feature_radius=.0712 if design=='scimitar' else .070
        q+=.5*RHO*feature_radius**3*extra_area*feature_cd*drag_factor
        return t,q
    vi=bisect(lambda v:forces(v)[0]-2*RHO*A*v*v,0,TIP)
    t,q=forces(vi)
    assert 0<t*vi<=q
    return dict(vi=vi,torque=q,thrust=t,area=A,
        developed_solidity=sum(b*c*dr for r,dr,c,beta,b in strips)/A,
        projected_solidity=sum(b*c*math.cos(beta)*dr for r,dr,c,beta,b in strips)/A,
        strips=strips)
def operating(top,lower,eta=.8,friction=.002):
    k=lower['torque']*(1+(8+64)/eta)+512*top['torque']/eta
    factor=.5*RHO*WIND**2*.0096*.18
    def balance(w):return factor*sail(w*.18/WIND)-friction-k*w*w
    w=bisect(balance,0,FREE*WIND/.18) if balance(0)>0 else 0
    residual=factor*sail_coeff(w*.18/WIND)[1]-friction-k*w*w
    assert abs(residual)<1e-8 or w==0
    omega=8*w
    result=dict(rpm=omega*30/math.pi,flow_L_s=top['area']*top['vi']*omega*1000,
        shaft_mW=top['torque']*omega**3*1000,
        thrust_mN=top.get('thrust',0)*omega**2*1000,
        input_rpm=w*30/math.pi,torque_residual_Nm=residual)
    if 'strips' in top:
        values=[math.degrees(beta-math.atan2(top['vi'],r)) for r,dr,c,beta,b in top['strips']]
        res=[math.hypot(r,top['vi'])*omega*c/1.5e-5 for r,dr,c,beta,b in top['strips']]
        result.update(alpha_min_max_deg=[min(values),max(values)],Re_min_max=[min(res),max(res)],
            developed_solidity=top['developed_solidity'],projected_solidity=top['projected_solidity'])
    return result
def main():
    designs=['scimitar','tubercled','toroidal','toroidal_5pairs']
    lower=rotor(.06)
    nominal={d:operating(unit_rotor(d),lower) for d in designs}
    nominal['original_P17']=operating(rotor(.072),lower)
    prior=json.loads((OUT.parent/'scimitar_40mm/airflow_screening.json').read_text())
    ref=next(x for x in prior['cases'] if x['design']=='scimitar prototype' and x['polar']=='nominal' and x['assumed_lip_drag_coefficient']==.01)
    assert abs(nominal['scimitar']['flow_L_s']/ref['flow_L_s']-1)<.0001
    pairs={str(p):operating(unit_rotor('toroidal',pairs=p),lower) for p in (3,4,5)}
    # Deterministic structural uncertainty stress test, not measured priors or probabilities.
    rows=[]
    for polar,lift,cd in [('low',.7,.12),('nominal',1,.06),('high',1.3,.04)]:
        low=rotor(.06,lift_scale=lift,cd0=cd)
        for design in designs:
            for lf,df,extra in itertools.product((.8,1,1.2),(.75,1,1.5),(0,.01,.05)):
                top=unit_rotor(design,lift=lift,cd0=cd,lift_factor=lf,drag_factor=df,feature_cd=extra)
                for eta,friction in itertools.product((.6,.8,1),(0,.002,.005)):
                    rows.append(dict(design=design,common_polar=polar,lift_factor=lf,drag_factor=df,
                        feature_drag_coefficient=extra,transmission_efficiency=eta,
                        input_friction_mNm=friction*1000,**operating(top,low,eta,friction)))
    # Hold common environment/drive fixed; vary ONLY design-specific model discrepancy.
    fixed=[x for x in rows if x['common_polar']=='nominal' and x['transmission_efficiency']==.8 and x['input_friction_mNm']==2]
    envelopes={d:{k:[min(x[k] for x in fixed if x['design']==d),max(x[k] for x in fixed if x['design']==d)]
                   for k in ('rpm','flow_L_s')} for d in designs}
    reversals={}
    for d in designs:
        best=max((x for x in fixed if x['design']==d),key=lambda x:x['flow_L_s'])
        opponents={other:min((x for x in fixed if x['design']==other),key=lambda x:x['flow_L_s']) for other in designs if other!=d}
        reversals[d]=dict(can_lead_under_stress_assumptions=all(best['flow_L_s']>x['flow_L_s'] for x in opponents.values()),
                         favorable_case=best,other_unfavorable_cases=opponents)
    convergence={}
    for d in designs:
        coarse=operating(unit_rotor(d,n=120),lower)
        fine=operating(unit_rotor(d,n=480),lower)
        convergence[d]={k:abs(coarse[k]/fine[k]-1) for k in ('rpm','flow_L_s')}
        assert max(convergence[d].values())<.005
    geometry=[]
    for p,c,tp in itertools.product((3,4,5),(.8,1,1.2),(18,22,26)):
        geometry.append(dict(pairs=p,chord_scale=c,tip_pitch=tp,
            sectional_height_limit_pass=(.033*c+.002<=.040),
            **operating(unit_rotor('toroidal',pairs=p,chord_scale=c,tip_pitch=tp),lower)))
    smooth_control=operating(unit_rotor('tubercled',amplitude=0),lower)
    result=dict(status='Unvalidated sectional proxies; NOT CFD, NOT physical measurements, NOT engineered toroidal/tubercled CAD',
        assumptions='Only three large 80x120 sails at 180 mm in 10 knots; nominal eta .8, input friction 2 mNm; common sinusoidal flat-section surrogate polar',
        nominal=nominal,toroidal_pair_counts=pairs,design_discrepancy_envelopes=envelopes,
        reversal_examples=reversals,convergence=convergence,toroidal_geometry_sweep=geometry,
        tubercled_smooth_edge_control=smooth_control,total_stress_cases=len(rows),
        conclusion='No robust physical ranking. Nominal ordering is conditional on independent strip proxies and selected geometry.')
    (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    with (OUT/'sensitivity.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    print(json.dumps(dict(nominal=nominal,pairs=pairs,envelopes=envelopes,
         reversal={k:v['can_lead_under_stress_assumptions'] for k,v in reversals.items()},
         convergence=convergence,cases=len(rows)),indent=2))
if __name__=='__main__':main()
