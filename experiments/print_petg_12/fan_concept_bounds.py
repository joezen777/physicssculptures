"""Drive-budget and geometry checks; no candidate-specific aerodynamic prediction."""
import json, math
from pathlib import Path
from airflow_screening import WIND, RHO, NU, ROOT, rotor, sail_coeff, bisect

R=.072
AREA=math.pi*(R*R-ROOT*ROOT)
ETA=.8
FRICTION=.002
SAIL_AREA=.0096
SAIL_RADIUS=.18
lower=rotor(.06)
factor=.5*RHO*WIND**2*SAIL_AREA*SAIL_RADIUS
free=bisect(lambda l:sail_coeff(l)[1],0,1)*WIND/SAIL_RADIUS

def budget(w):
    sail=factor*sail_coeff(w*SAIL_RADIUS/WIND)[1]
    lower_input=lower['torque']*w*w*(1+(2**3+4**3)/ETA)
    # Torque referred through the 8:1 speed multiplier.
    top_torque=max(0,(sail-FRICTION-lower_input)*ETA/8)
    power=top_torque*8*w
    v=(power/(2*RHO*AREA))**(1/3) if power else 0
    return dict(top_rpm=8*w*30/math.pi,top_available_W=power,
                top_available_mNm=top_torque*1000,
                ideal_isolated_flow_L_s=AREA*v*1000)

at415=budget(415*math.pi/30/8)
sweep=[budget(free*i/400) for i in range(401)]
best=max(sweep,key=lambda x:x['top_available_W'])
# For fixed annular area ideal flow scales as aerodynamic figure of merit^(1/3).
conversion_examples=[dict(assumed_figure_of_merit=f,
    idealized_flow_at_415_L_s=at415['ideal_isolated_flow_L_s']*f**(1/3))
    for f in (.2,.4,.6,.8,1)]
omega=415*math.pi/30
geometry=dict(tip_speed_m_s=omega*R,
    tip_rotation_only_Re_for_40_to_80mm_chord=[omega*R*c/NU for c in (.04,.08)],
    three_blade_mean_chord_mm_for_0p75_annular_solidity=.75*AREA/(3*(R-ROOT))*1000,
    root_chord_mm_if_35mm_height_is_pitch_projection=35/math.sin(math.radians(45)),
    biomimetic_tip_chord_mm_if_18mm_height_is_pitch_projection=18/math.sin(math.radians(25)),
    root_geometric_45deg_alpha_with_baseline_0p401ms_inflow=45-math.degrees(math.atan2(.401,omega*ROOT)))
assert abs(geometry['tip_speed_m_s']-3.129026282975433)<1e-8
assert 0<at415['top_available_W']<=best['top_available_W']
data=dict(status='No physical experiment or resolved 3D CFD. No defensible aerodynamic ranking.',
    drive='Only three large 80x120 mm sails at radius 180 mm in 10 knots wind',
    assumptions=dict(aggregate_geared_efficiency=ETA,input_friction_Nm=FRICTION,
                     sail_forward_Cd=1.4,sail_reverse_Cd=.4),
    budget_at_415=at415,best_sampled_budget=best,geometry=geometry,
    hypothetical_conversion_examples=conversion_examples,
    candidates={k:dict(airflow_score=None,rpm=None,
        reason='Missing resolved geometry and validated force/torque behavior')
        for k in ('toroidal','scimitar','tubercled')})
Path(__file__).with_suffix('.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps(data,indent=2))
