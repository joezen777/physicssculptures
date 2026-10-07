import math,json
from pathlib import Path
def sweep(lam=0):
    values=[]
    for j in range(3600):
        u=[math.cos(j*math.pi/1800+i*2*math.pi/3)-lam for i in range(3)]
        values.append(sum((1.4 if v>=0 else .4)*v*abs(v) for v in u))
    return dict(min=min(values),mean=sum(values)/len(values),max=max(values))
s=sweep()
assert abs(s['min']-.3)<1e-8 and abs(s['max']-1.2)<1e-8 and abs(s['mean']-.75)<1e-8
rows=[]
for name,a,r in [('existing',math.pi*476e-6,.108),('60x100',.006,.16),('80x120',.0096,.18),('100x150',.015,.2)]:
    for w in (3,5,8):
        q=.5*1.225*w*w
        rows.append(dict(name=name,area_cm2=a*1e4,radius_mm=r*1000,wind_m_s=w,torque_mNm={k:q*a*r*v*1000 for k,v in s.items()},drive_N=q*a*1.4,return_N=q*a*.4))
data=dict(note='Unvalidated normal-component model; assumed driving/return coefficients 1.4/0.4, air density 1.225 kg/m3',static=s,running_lambda_0p2=sweep(.2),cases=rows,required_cm2_at_10mNm_180mm={str(w):.01/(.5*1.225*w*w*.18*.3)*1e4 for w in (3,5,8)})
Path(__file__).with_suffix('.json').write_text(json.dumps(data,indent=2))
print(json.dumps(data,indent=2))
