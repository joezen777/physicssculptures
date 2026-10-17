"""Screening only: independent strips do not resolve high-solidity interference."""
import json,math
from pathlib import Path
from airflow_screening import rotor,bisect,sail_coeff,RHO,WIND
from scimitar_geometry import station
OUT=Path(__file__).resolve().parent/'output/scimitar_40mm'
OUT.mkdir(exist_ok=True)
A=math.pi*(.072**2-.0226**2)
def scimitar(scale,cd0,lip_cd):
    def forces(v):
        t=q=0.
        for j in range(200):
            r=.0226+(.072-.0226)*(j+.5)/200;dr=(.072-.0226)/200
            beta,w,h,_,_=station(r*1000);c=math.hypot(r*w,h/1000)
            phi=math.atan2(v,r);alpha=math.radians(beta)-phi
            cl=scale*math.sin(2*alpha);cd=cd0+2*math.sin(alpha)**2
            f=.5*RHO*(r*r+v*v)*3*c*dr
            t+=f*(cl*math.cos(phi)-cd*math.sin(phi))
            q+=f*(cl*math.sin(phi)+cd*math.cos(phi))*r
        # Hypothetical extra tangential drag on both sides of each tip lip.
        lip_area=3*2*.0712*station(71.2)[1]*.010
        q+=.5*RHO*.0712**3*lip_area*lip_cd
        return t,q
    v=bisect(lambda v:forces(v)[0]-2*RHO*A*v*v,0,.072)
    t,q=forces(v);assert 0<t*v<=q
    return dict(vi=v,torque=q,area=A)
rows=[]
free=bisect(lambda l:sail_coeff(l)[1],0,1)*WIND/.18
for name,scale,cd in [('low',.7,.12),('nominal',1,.06),('high',1.3,.04)]:
    lower=rotor(.06,lift_scale=scale,cd0=cd)
    for lip in (0,.01,.05):
        for label,top in [('original P17',rotor(.072,lift_scale=scale,cd0=cd)),
                          ('scimitar prototype',scimitar(scale,cd,lip))]:
            k=lower['torque']*(1+(8+64)/.8)+512*top['torque']/.8
            def balance(w):return .5*RHO*WIND**2*.0096*.18*sail_coeff(w*.18/WIND)[1]-.002-k*w*w
            w=bisect(balance,0,free);wt=8*w
            assert abs(balance(w))<1e-10
            rows.append(dict(design=label,polar=name,assumed_lip_drag_coefficient=lip,
                top_rpm=wt*30/math.pi,flow_L_s=top['area']*top['vi']*wt*1000,
                shaft_mW=top['torque']*wt**3*1000))
report=dict(status='UNVALIDATED SURROGATE, NOT CFD',assumptions='10 knots, three 80x120 sails, aggregate efficiency .8, input friction 2 mNm; no added camber or winglet lift benefit',
            limitations='No blade-to-blade interference, wake coupling, swirl, resolved camber, tip flow, or crosswind; lip drag coefficients hypothetical. No performance guarantee.',
            cases=rows)
(OUT/'airflow_screening.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps([r for r in rows if r['polar']=='nominal'],indent=2))
