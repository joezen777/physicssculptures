"""Passive radial whistle: lumped mechanics and low-Mach pneumatic model, SI internally."""
from dataclasses import dataclass, asdict, replace
from math import pi, sin, cos, sqrt, exp, isfinite
import numpy as np

G = 9.80665
ATM = 101325.0

@dataclass
class Config:
    mode: str = "A"
    shaft: str = "vertical"
    spring: str = "linear"
    acoustic: str = "quarter"
    radius_mm: float = 100
    rpm: float = 600
    mass_g: float = 5
    piston_mm: float = 12
    travel_mm: float = 75
    spring_k: float = 30
    preload_n: float = .2
    spring_rest_mm: float = 0
    static_n: float = .005
    kinetic_n: float = .003
    damping: float = .025
    rho: float = 1.225
    inlet_mm2: float = 8
    drag_cd: float = 1.1
    recovery: float = .6
    vent_mm2: float = 80
    leak_mm2: float = 2
    flow_cd: float = .65
    tube_mm: float = 12
    length_min_mm: float = 25
    length_max_mm: float = 100
    sound_speed: float = 343
    neck_mm: float = 3
    neck_length_mm: float = 6
    valve_open: float = .9
    valve_close: float = .1
    reset_threshold: float = .1
    latch_n: float = .02
    snap_n: float = .05
    use_dump: bool = False
    stator_cam: bool = False
    cam_return_fraction: float = .25
    modules: int = 1
    fault: str = "none"
    rotor_mass_g: float = 250
    initial_fraction: float = 0
    max_g: float = 100
    max_impact: float = 1
    max_force: float = 10
    max_imbalance: float = 5
    duration: float = 16
    dt: float = .0005

    def validate(self):
        choices = {"mode": ("A","B","C","D"), "shaft": ("vertical","horizontal"),
                   "spring": ("linear","bistable"), "acoustic": ("quarter","helmholtz"),
                   "fault": ("none","stuck","late","friction","mass")}
        for name, values in choices.items():
            if getattr(self,name) not in values:
                raise ValueError(f"{name}: choose one of {values}")
        for name in ("use_dump","stator_cam"):
            if type(getattr(self,name)) is not bool:
                raise ValueError(f"{name} must be boolean")
        bounds = {
            "radius_mm":(50,300),"rpm":(0,3000),"mass_g":(1,100),"piston_mm":(5,40),
            "travel_mm":(10,200),"spring_k":(0,500),"preload_n":(0,50),
            "spring_rest_mm":(-200,200),"static_n":(0,10),"kinetic_n":(0,10),
            "damping":(0,20),"rho":(.1,2),"inlet_mm2":(0,2000),
            "drag_cd":(0,3),"recovery":(0,1),"vent_mm2":(0,5000),
            "leak_mm2":(0,1000),"flow_cd":(.05,1),"tube_mm":(5,40),
            "length_min_mm":(5,300),"length_max_mm":(10,500),"sound_speed":(250,400),
            "neck_mm":(1,20),"neck_length_mm":(1,100),"valve_open":(.05,1),
            "valve_close":(0,.95),"reset_threshold":(0,.9),"latch_n":(0,50),
            "snap_n":(.0001,50),"cam_return_fraction":(.05,.8),
            "rotor_mass_g":(10,10000),"initial_fraction":(0,1),
            "max_g":(1,10000),"max_impact":(.01,30),"max_force":(.001,10000),
            "max_imbalance":(.001,10000),"duration":(2,60),"dt":(.00001,.001)}
        for name,(lo,hi) in bounds.items():
            v=getattr(self,name)
            if isinstance(v,bool) or not isinstance(v,(int,float)) or not isfinite(v) or not lo<=v<=hi:
                raise ValueError(f"{name} must be finite and between {lo} and {hi}")
        if self.modules not in (1,2,4,6,8,12) or type(self.modules) is not int:
            raise ValueError("modules must be 1, 2, 4, 6, 8 or 12")
        if self.travel_mm>=self.radius_mm:
            raise ValueError("Travel must be smaller than rotor radius; the piston cannot cross the shaft.")
        if self.valve_close>=self.valve_open or self.reset_threshold>=self.valve_open:
            raise ValueError("Closing and reset positions must be below the opening position.")
        if self.kinetic_n>self.static_n:
            raise ValueError("Kinetic friction cannot exceed static friction.")
        if self.length_max_mm<=self.length_min_mm:
            raise ValueError("Maximum acoustic length must exceed minimum length.")
        if self.length_min_mm>self.radius_mm-self.travel_mm:
            raise ValueError("Minimum acoustic length must fit between the mouth and initial piston radius.")
        if self.stator_cam and self.mode!="D":
            raise ValueError("The stationary cam option belongs to mode D.")
        return self

    @property
    def omega(self): return self.rpm*2*pi/60
    @property
    def stroke(self): return self.travel_mm/1000
    @property
    def radius(self): return self.radius_mm/1000
    @property
    def r0(self): return self.radius-self.stroke
    @property
    def area(self): return pi*(self.piston_mm/2000)**2

def spring_force(c,x):
    if c.mode=="C" or c.spring=="bistable":
        a=.35*c.stroke
        z=(x-.5*c.stroke)/a
        # Smooth double-well potential, with calibrated force barrier.
        return c.snap_n*1.5*sqrt(3)*(z-z**3)-c.preload_n
    return -c.preload_n-c.spring_k*(x-c.spring_rest_mm/1000)

def spring_energy(c,x):
    if c.mode=="C" or c.spring=="bistable":
        a=.35*c.stroke; z=(x-.5*c.stroke)/a
        return c.snap_n*1.5*sqrt(3)*a*(z**4/4-z*z/2)+c.preload_n*x
    return .5*c.spring_k*(x-c.spring_rest_mm/1000)**2+c.preload_n*x

def frequency(c,x):
    length=(c.length_min_mm+(c.length_max_mm-c.length_min_mm)*x/c.stroke)/1000
    if c.acoustic=="quarter":
        effective=length+.6*c.tube_mm/2000
        return c.sound_speed/(4*effective),length
    area=pi*(c.neck_mm/2000)**2
    neck=c.neck_length_mm/1000+1.45*c.neck_mm/2000
    volume=pi*(c.tube_mm/2000)**2*length
    return c.sound_speed/(2*pi)*sqrt(area/(volume*neck)),length

def pneumatic(c,x,opened):
    speed=c.omega*c.radius
    q=.5*c.rho*speed**2
    source=c.recovery*q
    # Secant linearization of subsonic orifice flow at the recovered pressure.
    conductance=c.flow_cd*sqrt(2/(c.rho*max(source,1.0)))*1e-6
    gi=conductance*c.inlet_mm2
    go=conductance*(c.leak_mm2+(c.vent_mm2 if opened else 0))
    volume=c.area*(c.length_min_mm/1000+x)
    compliance=volume/(1.4*ATM)
    return source,gi,go,compliance,q

class Module:
    def __init__(self,c,index=0):
        self.c=c
        self.index=index
        self.mass=c.mass_g/1000*(1.05 if index==1 and c.fault=="mass" else 1)
        self.friction_scale=1.05 if index==1 and c.fault=="friction" else 1
        self.x=c.initial_fraction*c.stroke; self.v=0.; self.p=0.
        self.open=False; self.latched=c.mode=="D" and not c.stator_cam
        self.returning=False; self.high_seen=False; self.cycles=[]
        self.max_impact=0.; self.peak_v=0.; self.peak_fc=0.; self.peak_spring=0.
        self.pressure_work=0.; self.source_work=0.; self.dissipation=0.; self.cam_work=0.
        self.snap_events=0; self.last_well=self.x>.5*c.stroke
        self.initial_energy=self.energy()
        self.forces={"fc":self.mass*c.omega**2*(c.r0+self.x),"spring":spring_force(c,self.x),"air":0.,"friction":0.,"damping":0.,"gravity":0.,"stop":0.}
        self.accel=0.; self.max_stop=0.

    def energy(self):
        c=self.c
        return .5*self.mass*self.v*self.v+spring_energy(c,self.x)-.5*self.mass*c.omega**2*(c.r0+self.x)**2

    def step(self,t,h):
        c=self.c; oldx=self.x; oldv=self.v
        hi=min(.99,c.valve_open+(.05 if self.index==1 and c.fault=="late" else 0))
        dump=c.mode=="B" or (c.mode in ("C","D") and c.use_dump)
        if dump:
            if not self.open and self.x>=hi*c.stroke: self.open=True
            elif self.open and self.x<=c.valve_close*c.stroke: self.open=False
        if c.mode=="D" and not c.stator_cam:
            if self.x>=hi*c.stroke: self.returning=True
            if self.returning and self.x<=c.reset_threshold*c.stroke and self.v<=0:
                self.latched=True; self.returning=False
        ps,gi,go,comp,q=pneumatic(c,self.x,self.open)
        den=comp+h*(gi+go)
        pfree=(comp*self.p+h*gi*ps)/den
        fc=self.mass*c.omega**2*(c.r0+self.x)
        fs=spring_force(c,self.x)
        grav=-self.mass*G*sin(c.omega*t+self.index*2*pi/c.modules) if c.shaft=="horizontal" else 0.
        applied=fc+fs+grav+c.area*pfree
        # Static complementarity: no motion until breakaway force is exceeded.
        static=c.static_n*self.friction_scale
        kinetic=c.kinetic_n*self.friction_scale
        if self.latched and applied>static+c.latch_n:
            self.latched=False
        stuck=(self.index==1 and c.fault=="stuck") or self.latched
        if abs(oldv)<1e-9 and abs(applied)<=static:
            v=0.; ff=-applied
        elif stuck:
            v=0.; ff=0.
        else:
            sign=1 if (oldv if abs(oldv)>1e-9 else applied)>0 else -1
            ff=-kinetic*sign
            v=(self.mass*oldv+h*(applied+ff))/(self.mass+h*c.damping+h*h*c.area*c.area/den)
            if oldv*v<0:
                if abs(applied)<=static: v=0.; ff=-applied
                else:
                    ff=-kinetic*(1 if applied>0 else -1)
                    v=h*(applied+ff)/(self.mass+h*c.damping+h*h*c.area*c.area/den)
        x=oldx+h*v; stop=0.
        if stuck: x=oldx
        if x<0 or x>c.stroke:
            self.max_impact=max(self.max_impact,abs(v))
            bound=0. if x<0 else c.stroke
            stop=-self.mass*v/h
            self.dissipation+=.5*self.mass*v*v
            x=bound; v=0.
        if c.mode=="D" and c.stator_cam and c.rpm>0:
            phase=(c.omega*(t+h)/(2*pi)+self.index/c.modules)%1
            start=1-c.cam_return_fraction
            if phase>=start:
                u=(phase-start)/c.cam_return_fraction
                cap=c.stroke*(1-3*u*u+2*u**3)
                wall_v=-c.stroke*6*u*(1-u)*c.rpm/60/c.cam_return_fraction
                if x>cap:
                    impact=max(0,v-wall_v); self.max_impact=max(self.max_impact,impact)
                    impulse=self.mass*(wall_v-v)
                    stop+=impulse/h
                    self.cam_work+=impulse*wall_v
                    self.dissipation+=.5*self.mass*(v-wall_v)**2
                    x=cap; v=wall_v
        if stuck: stop=-(fc+fs+grav+c.area*pfree)
        actual_v=(x-oldx)/h
        self.p=(comp*self.p+h*(gi*ps-c.area*actual_v))/den
        self.x=x; self.v=v; self.accel=(v-oldv)/h
        fa=c.area*self.p
        self.pressure_work+=fa*(x-oldx)
        self.source_work+=ps*gi*(ps-self.p)*h
        self.dissipation+=(kinetic*abs(actual_v)+c.damping*actual_v**2)*h
        self.peak_v=max(self.peak_v,abs(v)); self.peak_fc=max(self.peak_fc,fc)
        self.peak_spring=max(self.peak_spring,abs(fs)); self.max_stop=max(self.max_stop,abs(stop))
        self.forces={"fc":fc,"spring":fs,"air":fa,"friction":ff,"damping":-c.damping*v,"gravity":grav,"stop":stop}
        if x>=hi*c.stroke: self.high_seen=True
        if self.high_seen and x<=c.reset_threshold*c.stroke and v<=0:
            self.cycles.append(t+h); self.high_seen=False
        well=x>.5*c.stroke
        if well!=self.last_well: self.snap_events+=1; self.last_well=well

def stable_cycles(times,duration):
    late=[t for t in times if t>=duration*.35]
    if len(late)<4: return False,0.
    periods=np.diff(late)
    mean=float(np.mean(periods))
    recent=times[-1]>=duration-1.5*mean
    return bool(recent and np.std(periods)/mean<.15),1/mean if recent else 0.

def analyze(c,rows,mods,h):
    a=np.array([r["x"] for r in rows]); v=np.array([r["v"] for r in rows])
    times=np.array([r["t"] for r in rows]); late=a[times>=c.duration*.65]
    m=mods[0]; reset,rate=stable_cycles(m.cycles,c.duration)
    moved=float(np.ptp(a))>max(1e-5,.005*c.stroke)
    late_span=float(np.ptp(late)) if len(late) else 0
    settled=late_span<max(1e-5,.003*c.stroke) and max(abs(v[-min(50,len(v)):]))<.002
    # Peak-to-peak evidence, rather than classifying variance as self oscillation.
    maxima=[]; minima=[]
    for i in range(1,len(a)-1):
        if a[i]>a[i-1] and a[i]>=a[i+1]: maxima.append((times[i],a[i]))
        if a[i]<a[i-1] and a[i]<=a[i+1]: minima.append((times[i],a[i]))
    late_peaks=[z for z in maxima if z[0]>.35*c.duration]
    sustained=False
    if len(late_peaks)>=5 and late_span>.01*c.stroke:
        periods=np.diff([z[0] for z in late_peaks])
        peaks=np.array([z[1] for z in late_peaks])
        half=late[len(late)//2:]
        sustained=bool(np.std(periods)/max(np.mean(periods),1e-10)<.15 and
                       np.ptp(half)>.85*late_span and abs(peaks[-1]-peaks[0])<.1*late_span and
                       times[-1]-late_peaks[-1][0]<1.5*np.mean(periods))
        if sustained and not reset: rate=1/float(np.mean(periods))
    endstop=settled and a[-1]>.995*c.stroke
    if reset: behavior="RESET CYCLING"
    elif sustained: behavior="SUSTAINED OSCILLATION"
    elif endstop: behavior="END-STOP"
    elif not moved: behavior="NO MOTION"
    elif settled: behavior="DAMPED OSCILLATION" if len(maxima)+len(minima)>=3 else "STATIC EQUILIBRIUM"
    elif len(maxima)+len(minima)>=3: behavior="DECAYING / UNRESOLVED"
    else: behavior="TRANSIENT / UNRESOLVED"
    forced=c.shaft=="horizontal" or c.stator_cam
    if (reset or sustained) and forced: behavior="ROTATION-FORCED CYCLING"
    peak_imb=max(r["imbalance_n"] for r in rows)
    maxg=max(r["g_load"] for r in rows)
    warnings=[]
    if maxg>c.max_g: warnings.append(f"Radial acceleration {maxg:.1f} g exceeds screening limit {c.max_g:g} g.")
    if max(z.max_impact for z in mods)>c.max_impact: warnings.append("Piston/cam impact speed exceeds the selected screening limit.")
    if max(z.peak_fc for z in mods)>c.max_force or max(z.peak_spring for z in mods)>c.max_force:
        warnings.append("Piston or spring load exceeds the selected screening limit.")
    if peak_imb>c.max_imbalance: warnings.append("Imbalance exceeds the selected screening limit.")
    if c.omega*c.radius/c.sound_speed>.3: warnings.append("Tip Mach number exceeds 0.3: incompressible airflow approximation is unreliable.")
    if any(r["pressure"]<-ATM*.2 or r["pressure"]>ATM*.2 for r in rows):
        warnings.append("Pressure exceeds the small-signal pneumatic model range.")
    ps,gi,go,_,q=pneumatic(c,0,False)
    _,_,gopen,_,_=pneumatic(c,0,True)
    pcl=ps*gi/(gi+go) if gi+go else 0.
    pop=ps*gi/(gi+gopen) if gi+gopen else 0.
    xs=np.linspace(c.valve_close*c.stroke,c.valve_open*c.stroke,80)
    outward=[m.mass*c.omega**2*(c.r0+x)+spring_force(c,x)+c.area*pcl-c.static_n for x in xs]
    inward=[-m.mass*c.omega**2*(c.r0+x)-spring_force(c,x)-c.area*pop-c.static_n for x in xs]
    if reset:
        reason="Repeated full-stroke returns are measured in the late-time solution."
        if forced: reason+=" Motion is rotation-forced, not autonomous self-oscillation."
    elif not moved: reason="Breakaway force does not exceed static friction or the latch threshold."
    elif endstop: reason="Outward load drives the piston to its outer stop; no completed return cycle."
    elif settled: reason="The system settles. A constant centrifugal field and a passive spring do not replenish dissipated cycle energy."
    else: reason="The observation window does not establish sustained cycling; extend the run or inspect the transients."
    if not reset and c.mode=="B":
        if max(inward)<=0: reason="After venting, centrifugal load prevents spring-driven return throughout the valve stroke."
        elif min(outward)<=0: reason="Closed-valve pressure cannot carry the piston through the full opening stroke against spring and friction."
        elif min(inward)<=0: reason="The spring cannot complete the return through the valve stroke after venting."
        elif not m.open: reason="The piston has not reached the valve-opening position; pressure/flow and transient motion limit triggering."
    if not reset and c.mode in ("C","D") and not c.use_dump and not c.stator_cam:
        reason+=" A snap or latch alone does not remove centrifugal force or provide cyclic energy."
    drag=c.drag_cd*q*c.inlet_mm2*1e-6
    power=drag*c.omega*c.radius
    source_power=sum(z.source_work for z in mods)/c.duration
    if source_power>c.modules*power*1.2+1e-6:
        warnings.append("Pneumatic source power exceeds the scoop drag-power estimate; source model needs refinement.")
    freqs=[r["frequency"] for r in rows]
    down_times=[]
    # Time spent going from the reset threshold to the high valve position.
    begun=None
    for r in rows:
        if r["x"]<=c.reset_threshold*c.stroke: begun=r["t"]
        if begun is not None and r["x"]>=c.valve_open*c.stroke:
            down_times.append(r["t"]-begun); begun=None
    pitch_late=[r["frequency"] for r in rows if r["t"]>=c.duration*.65]
    pitch_min=min(pitch_late);pitch_max=max(pitch_late)
    return {
        "behavior":behavior,"screening":"MECHANICALLY UNSAFE" if warnings else "NO SCREENING LIMIT EXCEEDED",
        "moved":moved,"settled":bool(settled),"reset_count":len(m.cycles),"self_cycles":bool(reset and not forced),
        "module_cycle_counts":[len(z.cycles) for z in mods],
        "all_modules_cycle":all(stable_cycles(z.cycles,c.duration)[0] for z in mods),
        "maintained":bool(reset or sustained),"forced":forced,"cycle_hz":rate if reset or sustained else 0.,
        "equilibrium_mm":float(a[-1]*1000) if settled or not moved else None,
        "late_span_mm":late_span*1000,"pitch_min":pitch_min,"pitch_max":pitch_max,
        "observed_pitch_min":min(freqs),"observed_pitch_max":max(freqs),
        "sweep_seconds":float(np.mean(down_times[-5:])) if down_times else None,
        "peak_velocity":max(z.peak_v for z in mods),"peak_impact":max(z.max_impact for z in mods),
        "peak_fc":max(z.peak_fc for z in mods),"peak_spring":max(z.peak_spring for z in mods),
        "peak_stop_force":max(z.max_stop for z in mods),"max_g":maxg,"peak_imbalance":peak_imb,
        "peak_com_mm":max(r["com_mm"] for r in rows),"reason":reason,"warnings":warnings,
        "closed_pressure":pcl,"open_pressure":pop,"outward_margin":min(outward),"return_margin":min(inward),
        "source_power_w":source_power,"scoop_drag_power_w":c.modules*power,
        "pressure_work_j":sum(z.pressure_work for z in mods),"cam_work_j":sum(z.cam_work for z in mods),
        "dissipation_j":sum(z.dissipation for z in mods),
        "effective_energy_change_j":sum(z.energy()-z.initial_energy for z in mods),
        "dt":h,"run_seconds":c.duration,"cycle_times":m.cycles,
        "sound_note":"Resonance-only sonification. Jet/labium onset, loudness and mode-locking are not predicted.",
        "geometry_note":"Independent acoustic length endpoints imply a linkage ratio if their difference differs from piston stroke."
    }

def simulate(c,include_rows=True,initial=None,progress=None):
    c.validate()
    mods=[Module(c,i) for i in range(c.modules)]
    if initial:
        for m,state in zip(mods,initial):
            m.x,m.v,m.p,m.open=state[:4]
            if len(state)>4: m.latched,m.returning=state[4:6]
            m.initial_energy=m.energy()
    stiff=max(c.spring_k, c.mass_g/1000*c.omega**2, c.snap_n/max(c.stroke,1e-6)*60 if c.mode=="C" or c.spring=="bistable" else 0.,1.)
    h=min(c.dt,.07*sqrt(c.mass_g/1000/stiff))
    n=int(np.ceil(c.duration/h));h=c.duration/n
    stride=max(1,int(.01/h));rows=[];next_sample=0
    for i in range(n+1):
        t=i*h
        if progress and i%2000==0: progress(i/n,f"Integrating {t:.1f} / {c.duration:g} s")
        if i==next_sample or i==n:
            m=mods[0]; f,length=frequency(c,m.x)
            ux=uy=rx=ry=0.
            for j,z in enumerate(mods):
                a=2*pi*j/c.modules
                moment=z.mass*(c.r0+z.x)
                ux+=moment*cos(a);uy+=moment*sin(a)
                rad=z.mass*(z.accel-c.omega**2*(c.r0+z.x));tan=2*z.mass*c.omega*z.v
                rx+=rad*cos(a)-tan*sin(a);ry+=rad*sin(a)+tan*cos(a)
            moment=sqrt(ux*ux+uy*uy)
            row={"t":t,"x":m.x,"v":m.v,"pressure":m.p,"frequency":f,"length":length,
                 **m.forces,"open":m.open,"latched":m.latched,
                 "g_load":c.omega**2*(c.r0+m.x)/G,
                 "imbalance_n":c.omega**2*moment,"dynamic_reaction_n":sqrt(rx*rx+ry*ry),
                 "com_mm":1000*moment/(c.rotor_mass_g/1000+sum(z.mass for z in mods)),
                 "positions":[z.x for z in mods],"masses":[z.mass for z in mods],
                 "local_speed":c.omega*(c.r0+m.x),"inlet_speed":c.omega*c.radius}
            rows.append(row);next_sample=i+stride
        if i<n:
            for z in mods:z.step(t,h)
    summary=analyze(c,rows,mods,h)
    return {"config":asdict(c),"summary":summary,"rows":rows if include_rows else [],
            "final":[[m.x,m.v,m.p,m.open,m.latched,m.returning] for m in mods]}

def sweep(c,count=21,progress=None):
    c.validate()
    out=[];initial=None
    for i,rpm in enumerate(np.linspace(0,c.rpm,count)):
        run=simulate(replace(c,rpm=float(rpm)),False,initial)
        initial=run["final"]
        out.append({"rpm":float(rpm),**run["summary"]})
        if progress:progress((i+1)/count,f"RPM dwell {i+1}/{count}: {rpm:.0f}")
    return {"config":asdict(c),"points":out,"max_rpm":c.rpm,"dwell_seconds":c.duration,
            "method":"Ascending stepped sweep; each RPM dwells for the selected run duration and carries piston position, velocity, pressure and valve state. Not a continuous acceleration ramp."}

def optimize(c,budget=54,progress=None):
    c.validate()
    # Search the passive pressure-dump hypothesis; never modify friction to obtain a win.
    candidates=[];tested=0;rejected=0
    combos=[(m,d,s) for m in (1.,2.,5.) for d in (20.,30.,40.) for s in (10.,20.,40.)]
    for j in range(budget):
        mass,dia,stroke=combos[j%len(combos)]
        if stroke>=c.radius_mm-c.length_min_mm: stroke=max(10,c.radius_mm-c.length_min_mm-1)
        if stroke>=c.radius_mm: continue
        trial=replace(c,mode="B",spring="linear",stator_cam=False,use_dump=False,
            mass_g=mass,piston_mm=dia,travel_mm=stroke,tube_mm=dia,
            length_max_mm=c.length_min_mm+stroke,inlet_mm2=20 if j<len(combos) else 60,
            vent_mm2=400 if j<len(combos) else 800,leak_mm2=c.leak_mm2,
            valve_open=.85 if j<len(combos) else .9,valve_close=.15 if j<len(combos) else .1,
            reset_threshold=.16 if j<len(combos) else .11,
            spring_rest_mm=0,initial_fraction=0,modules=2,fault="none",shaft="vertical")
        ps,gi,go,_,_=pneumatic(trial,0,False)
        _,_,gv,_,_=pneumatic(trial,0,True)
        pcl=ps*gi/(gi+go) if gi+go else 0
        pop=ps*gi/(gi+gv) if gi+gv else 0
        span=trial.area*(pcl-pop)
        residual=span*.1/trial.stroke
        k=mass/1000*c.omega**2+residual
        preload=mass/1000*c.omega**2*trial.r0+trial.area*(pcl+pop)/2-residual*trial.stroke/2
        if k>500 or preload<0 or preload>50:
            rejected+=1;continue
        trial=replace(trial,spring_k=k,preload_n=preload)
        run=simulate(trial,False);tested+=1
        s=run["summary"]
        if s["self_cycles"] and not s["warnings"]:
            # Independent finer-step confirmation and a specified manufacturing mismatch.
            fine=simulate(replace(trial,dt=trial.dt/2),False)["summary"]
            if fine["self_cycles"] and abs(fine["cycle_hz"]-s["cycle_hz"])<.05*max(s["cycle_hz"],1e-6):
                mismatch=simulate(replace(trial,fault="friction"),False)["summary"]
                candidates.append({"config":asdict(trial),"summary":s,"fine_cycle_hz":fine["cycle_hz"],
                                   "friction_fault_imbalance":mismatch["peak_imbalance"],
                                   "friction_fault_cycles":mismatch["all_modules_cycle"],
                                   "score":s["pitch_max"]/s["pitch_min"]/(1+s["peak_velocity"])})
        if progress:progress((j+1)/budget,f"Design {j+1}/{budget}: {len(candidates)} confirmed")
    candidates.sort(key=lambda z:z["score"],reverse=True)
    return {"config":asdict(c),"candidates":candidates[:8],"tested":tested,"rejected":rejected,
            "note":"Bounded pressure-dump search, fixed user friction/damping/recovery. Candidates use a vertical shaft, two nominally balanced modules and tuned linear springs. Failure to find one is not a proof of impossibility; successful models are not print-ready designs."}

def example_config():
    """Analytically balanced seed, verified numerically; not a fabrication specification."""
    c=Config(mode="B",modules=2,mass_g=2,piston_mm=40,travel_mm=40,
             tube_mm=40,length_max_mm=65,inlet_mm2=20,vent_mm2=400,
             valve_open=.85,valve_close=.15,reset_threshold=.16)
    ps,gi,go,_,_=pneumatic(c,0,False)
    _,_,gv,_,_=pneumatic(c,0,True)
    pcl=ps*gi/(gi+go); pop=ps*gi/(gi+gv)
    residual=c.area*(pcl-pop)*.1/c.stroke
    return replace(c,spring_k=c.mass_g/1000*c.omega**2+residual,
                   preload_n=c.mass_g/1000*c.omega**2*c.r0+c.area*(pcl+pop)/2-residual*c.stroke/2)
