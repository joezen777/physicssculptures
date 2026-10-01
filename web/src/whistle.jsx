import React,{useState,useEffect,useRef} from 'react';
import {createRoot} from 'react-dom/client';
import {ThemeProvider,createTheme,CssBaseline,Button,TextField,MenuItem,Accordion,AccordionSummary,AccordionDetails,Alert,LinearProgress,Chip,Switch,FormControlLabel} from '@mui/material';
import './whistle/style.css';

const theme=createTheme({palette:{mode:'dark',primary:{main:'#70d6b7'},background:{default:'#101719',paper:'#182326'}},typography:{fontFamily:'Inter, system-ui, sans-serif',button:{textTransform:'none'}}});
const fmt=(x,n=2)=>x==null?'—':Number(x).toLocaleString(undefined,{maximumFractionDigits:n});
const fields=[
 ['Geometry',[['radius_mm','Cylinder radius','mm',50,300],['mass_g','Piston mass','g',1,100],['piston_mm','Piston diameter','mm',5,40],['travel_mm','Available travel','mm',10,200],['rotor_mass_g','Centered rotor mass','g',10,10000],['initial_fraction','Initial travel fraction','',0,1,.01]]],
 ['Spring & contact',[['spring_k','Spring constant','N/m',0,500,.01],['preload_n','Inward preload','N',0,50,.001],['spring_rest_mm','Spring rest offset','mm',-200,200],['static_n','Static friction','N',0,10,.001],['kinetic_n','Kinetic friction','N',0,10,.001],['damping','Viscous damping','N s/m',0,20,.001],['snap_n','Over-center force barrier','N',.0001,50,.001]]],
 ['Air supply & bypass',[['rho','Air density','kg/m³',.1,2,.001],['inlet_mm2','Scoop inlet area','mm²',0,2000],['drag_cd','Scoop drag coefficient','',0,3,.01],['recovery','Pressure recovery','',0,1,.01],['vent_mm2','Open bypass area','mm²',0,5000],['leak_mm2','Whistle / leakage outlet','mm²',0,1000,.1],['flow_cd','Orifice flow coefficient','',.05,1,.01]]],
 ['Reset mechanism',[['valve_open','Valve opening / outer trip','stroke fraction',.05,1,.01],['valve_close','Valve closing position','stroke fraction',0,.95,.01],['reset_threshold','Return detection / latch catch','stroke fraction',0,.9,.01],['latch_n','Latch release force','N',0,50,.001],['cam_return_fraction','Cam return sector','turn fraction',.05,.8,.01]]],
 ['Acoustic cavity',[['tube_mm','Whistle tube diameter','mm',5,40],['length_min_mm','Minimum acoustic length','mm',5,300],['length_max_mm','Maximum acoustic length','mm',10,500],['sound_speed','Speed of sound','m/s',250,400],['neck_mm','Helmholtz neck diameter','mm',1,20,.1],['neck_length_mm','Helmholtz neck length','mm',1,100,.1]]],
 ['Numerics & screening',[['duration','Run / RPM dwell duration','s',2,60],['dt','Maximum integration step','s',.00001,.001,.00001],['max_g','Acceleration screening limit','g',1,10000],['max_impact','Impact-speed limit','m/s',.01,30,.01],['max_force','Piston / spring load limit','N',.001,10000,.1],['max_imbalance','Imbalance limit','N',.001,10000,.1]]]
];
const modes={A:'A · Simple spring',B:'B · Pressure dump',C:'C · Over-center spring',D:'D · Mechanical latch / cam'};
function download(name,value,type='application/json'){
 const blob=new Blob([typeof value==='string'?value:JSON.stringify(value,null,2)],{type});
 const url=URL.createObjectURL(blob), a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function Plot({rows,series,title,units,cursor}){
 const ref=useRef(),[w,setW]=useState(480),[hover,setHover]=useState(null);
 useEffect(()=>{const o=new ResizeObserver(([e])=>setW(Math.max(250,e.contentRect.width)));o.observe(ref.current);return()=>o.disconnect();},[]);
 const H=172,L=58,R=14,T=14,B=32;
 const values=rows.flatMap(r=>series.map(s=>r[s.key]*(s.scale||1)));
 let lo=Math.min(...values),hi=Math.max(...values);if(lo===hi){lo-=1;hi+=1;}const pad=(hi-lo)*.08;lo-=pad;hi+=pad;
 const xmax=rows.at(-1)?.t||1,xx=t=>L+t/xmax*(w-L-R),yy=v=>H-B-(v-lo)/(hi-lo)*(H-T-B);
 const colors=['#70d6b7','#f3bb75','#9dabff','#e58fa8','#91adb5'];
 const sample=hover==null?null:rows[Math.min(rows.length-1,Math.round(hover/xmax*(rows.length-1)))];
 return <div className="plot" ref={ref}><div className="plot-title">{title} <span>{units}</span></div>
 <svg width={w} height={H} role="img" aria-label={title+' over simulation time'}>
 {[0,.5,1].map(q=><g key={q}><line x1={L} x2={w-R} y1={yy(lo+q*(hi-lo))} y2={yy(lo+q*(hi-lo))} stroke="#334447"/><text x={L-8} y={yy(lo+q*(hi-lo))+4} textAnchor="end">{fmt(lo+q*(hi-lo),2)}</text></g>)}
 {[0,.5,1].map(q=><text key={q} x={xx(q*xmax)} y={H-12} textAnchor={q===0?'start':q===1?'end':'middle'}>{fmt(q*xmax,1)} s</text>)}
 {series.map((s,i)=><path key={s.key} d={rows.map((r,j)=>(j?'L':'M')+xx(r.t).toFixed(2)+','+yy(r[s.key]*(s.scale||1)).toFixed(2)).join(' ')} fill="none" stroke={colors[i]} strokeWidth="1.6"/>)}
 <line x1={xx(cursor)} x2={xx(cursor)} y1={T} y2={H-B} stroke="#d8e8e3" strokeDasharray="3 4" opacity=".55"/>
 {sample&&<line x1={xx(sample.t)} x2={xx(sample.t)} y1={T} y2={H-B} stroke="#fff"/>}
 <rect x={L} y={T} width={w-L-R} height={H-T-B} fill="transparent" onMouseMove={e=>{const b=e.currentTarget.ownerSVGElement.getBoundingClientRect();setHover(Math.max(0,Math.min(xmax,(e.clientX-b.left-L)/(w-L-R)*xmax)));}} onMouseLeave={()=>setHover(null)}/>
 </svg><div className="legend">{series.map((s,i)=><span key={s.key} style={{color:colors[i]}}>{s.label}{sample?' '+fmt(sample[s.key]*(s.scale||1),3):''}</span>)}{sample&&<span>at {fmt(sample.t,2)} s</span>}</div></div>;
}
function Cutaway({c,r}){
 const px=342+(r.length*1000)/(c.length_max_mm+8)*355,theta=c.rpm*2*Math.PI/60*r.t;
 const fmax=Math.max(.01,...['fc','spring','air','friction'].map(k=>Math.abs(r[k])));
 const arrow=(key,y,color,label)=>{
  const value=r[key],len=110*Math.abs(value)/fmax,sgn=value>=0?1:-1,start=522,end=start+sgn*len;
  return <g key={key}><text x="323" y={y+4} fill={color}>{label}</text><line x1={start} y1={y} x2={end} y2={y} stroke={color} strokeWidth="3"/>{len>2&&<path d={'M'+end+','+y+' l'+(-sgn*7)+',-4 v8 z'} fill={color}/>}<text x="715" y={y+4} textAnchor="end">{fmt(value,4)} N</text></g>;
 };
 let coil='M'+(px+12)+',153';const end=711;
 for(let i=1;i<=16;i++)coil+=' L'+(px+12+(end-px-12)*i/16)+','+(i===16?153:153+(i%2?9:-9));
 return <svg className="cutaway" viewBox="0 0 760 370" role="img" aria-label="True-state rotor end view and co-rotating radial cutaway showing piston, spring, inlet, bypass and forces">
 <text x="32" y="26" className="view-label">ROTOR END VIEW</text><circle cx="150" cy="157" r="104" fill="#223437" stroke="#547073"/><circle cx="150" cy="157" r="11" fill="#91adb5"/>
 {r.positions.map((x,i)=>{const a=theta+2*Math.PI*i/c.modules,rad=(c.radius_mm-c.travel_mm+x*1000)/c.radius_mm*99;return <g key={i}><line x1="150" y1="157" x2={150+101*Math.cos(a)} y2={157+101*Math.sin(a)} stroke="#789293" strokeWidth="6"/><circle cx={150+rad*Math.cos(a)} cy={157+rad*Math.sin(a)} r="7" fill={i===1&&c.fault!=='none'?'#f3bb75':'#70d6b7'}/></g>;})}
 <text x="150" y="289" textAnchor="middle">{fmt(c.rpm,0)} rpm · {c.shaft} shaft</text>
 <text x="150" y="311" textAnchor="middle">COM offset {fmt(r.com_mm,3)} mm</text>
 <text x="150" y="333" textAnchor="middle">Imbalance {fmt(r.imbalance_n,3)} N</text>
 <text x="323" y="26" className="view-label">RADIAL CUTAWAY · CO-ROTATING</text>
 <path d="M337 108 H720 V183 H337" fill="#10191b" stroke="#91adb5" strokeWidth="3"/>
 <rect x="342" y="112" width={Math.max(0,px-342)} height="67" fill="#70d6b7" opacity=".14"/>
 <line x1="342" y1="102" x2={px} y2="102" stroke="#70d6b7"/>
 <text x="521" y="87" textAnchor="middle">Air column {fmt(r.length*1000,1)} mm · {fmt(r.frequency,0)} Hz</text>
 <path d="M337 115 l-13 13 h24 z" fill="#f3bb75"/>
 <text x="323" y="213">Mouth / labium</text>
 <rect x={px-6} y="110" width="12" height="71" rx="2" fill="#70d6b7"/>
 <path d={coil} fill="none" stroke="#f3bb75" strokeWidth="2"/>
 <text x={px} y="239" textAnchor="middle">Sabot {fmt(r.x*1000,1)} / {c.travel_mm} mm</text>
 <path d="M730 55 H742 V63 H362 V110" stroke="#9dabff" strokeWidth="3" fill="none" strokeDasharray="7 4" strokeDashoffset={-r.t*15}/>
 <text x="729" y="48" textAnchor="end">Rim scoop → inlet duct</text>
 <path d={'M365 181 l'+(r.open?'20 17':'20 0')} stroke="#9dabff" strokeWidth="4"/>
 <text x="524" y="213">Bypass {r.open?'OPEN':'closed'} · {fmt(r.pressure,2)} Pa</text>
 {arrow('fc',274,'#70d6b7','Centrifugal')}
 {arrow('spring',300,'#f3bb75','Spring')}
 {arrow('air',326,'#9dabff','Air pressure')}
 {arrow('friction',352,'#e58fa8','Friction')}
 </svg>;
}
function App(){
 const [config,setConfig]=useState(null),[run,setRun]=useState(null),[job,setJob]=useState(null),[error,setError]=useState(''),[sweep,setSweep]=useState(null),[designs,setDesigns]=useState(null),[comparison,setComparison]=useState(null),[faults,setFaults]=useState(null);
 const [playing,setPlaying]=useState(false),[cursor,setCursor]=useState(0),[audioOn,setAudioOn]=useState(false),[speed,setSpeed]=useState(1);
 const audio=useRef(null),timeRef=useRef(0),jobRef=useRef(null);
 const set=(key,value)=>setConfig(c=>({...c,[key]:value}));
 async function start(kind,override){
  setError('');setPlaying(false);
  try{
   const res=await fetch('/api/jobs',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({kind,config:override||config})});
   const data=await res.json();if(!res.ok)throw Error(data.detail||'Request failed');
   jobRef.current=data.id;setJob({id:data.id,progress:0,message:'Integrating equations…',kind});
  }catch(e){setError(e.message);}
 }
 useEffect(()=>{fetch('/api/defaults').then(r=>r.json()).then(c=>{setConfig(c);start('simulate',c);}).catch(e=>setError(e.message));return()=>{audio.current?.ctx.close();};},[]);
 useEffect(()=>{
  if(!job?.id)return;
  let active=true;
  const timer=setInterval(async()=>{
   try{
    const res=await fetch('/api/jobs/'+job.id),data=await res.json();
    if(!active)return;
    if(data.status==='complete'){
     setJob(null);jobRef.current=null;
     if(data.kind==='simulate'){setRun(data.result);setCursor(0);timeRef.current=0;setPlaying(!matchMedia('(prefers-reduced-motion: reduce)').matches);}
     if(data.kind==='sweep')setSweep(data.result);
     if(data.kind==='optimize')setDesigns(data.result);
     if(data.kind==='compare')setComparison(data.result);
     if(data.kind==='balance')setFaults(data.result);
    }else if(['failed','cancelled'].includes(data.status)){setError(data.message);setJob(null);jobRef.current=null;}
    else setJob(j=>({...j,progress:data.progress,message:data.message}));
   }catch(e){if(active){setError(e.message);setJob(null);}}
  },500);return()=>{active=false;clearInterval(timer);};
 },[job?.id]);
 useEffect(()=>{
  if(!playing||!run)return;
  let last=performance.now(),id;
  const tick=now=>{const t=Math.max(0,Math.min(run.config.duration,timeRef.current+Math.max(0,now-last)/1000*speed));last=now;timeRef.current=t;setCursor(t);if(t>=run.config.duration){setPlaying(false);return;}id=requestAnimationFrame(tick);};
  id=requestAnimationFrame(tick);return()=>cancelAnimationFrame(id);
 },[playing,run,speed]);
 const rows=run?.rows||[],index=rows.length?Math.max(0,Math.min(rows.length-1,Math.round(cursor/(run.config.duration)*(rows.length-1)))):0,r=rows[index],s=run?.summary,c=run?.config;
 useEffect(()=>{
  if(!audio.current)return;
  const a=audio.current;
  a.osc.frequency.setTargetAtTime(Math.min(12000,Math.max(20,r?.frequency||440)),a.ctx.currentTime,.015);
  a.gain.gain.setTargetAtTime(audioOn&&playing?.025:0,a.ctx.currentTime,.025);
 },[r?.frequency,audioOn,playing]);
 async function toggleAudio(){
  if(!audio.current){
   const ctx=new AudioContext(),osc=ctx.createOscillator(),gain=ctx.createGain();
   osc.type='sine';gain.gain.value=0;osc.connect(gain).connect(ctx.destination);osc.start();audio.current={ctx,osc,gain};
  }
  await audio.current.ctx.resume();setAudioOn(x=>!x);
 }
 function seek(t){setCursor(t);timeRef.current=t;}
 const changed=run&&JSON.stringify(config)!==JSON.stringify(run.config);
 const dropdown=(key,label,options)=><TextField select size="small" fullWidth label={label} disabled={key==='spring'&&config.mode==='C'} value={key==='spring'&&config.mode==='C'?'bistable':config[key]} onChange={e=>set(key,e.target.value)}>{options.map(([v,l])=><MenuItem key={v} value={v}>{l}</MenuItem>)}</TextField>;
 if(!config)return <main><p>{error||'Loading the physics workbench…'}</p></main>;
 return <ThemeProvider theme={theme}><CssBaseline/><main>
 <header><div><div className="eyebrow">MECHANICS / AIRFLOW / ACOUSTICS</div><h1>Passive whistle lab</h1><p>Can a rotating piston whistle reset itself? Follow the forces, then listen to the predicted resonance.</p></div><Chip label="Local numerical model" variant="outlined"/></header>
 <div className="layout"><aside>
 <div className="control-top">{dropdown('mode','Mechanism',Object.entries(modes))}
 <TextField size="small" label="RPM / sweep maximum" type="number" value={config.rpm} onChange={e=>set('rpm',Number(e.target.value))} inputProps={{min:0,max:3000,step:.1}}/>
 {dropdown('shaft','Shaft orientation',[['vertical','Vertical · no radial gravity'],['horizontal','Horizontal · periodic gravity']])}
 {dropdown('spring','Restoring spring',[['linear','Linear'],['bistable','Bistable potential']])}
 {dropdown('acoustic','Resonance model',[['quarter','Quarter-wave pipe'],['helmholtz','Helmholtz cavity']])}
 {dropdown('modules','Evenly spaced modules',[1,2,4,6,8,12].map(n=>[n,String(n)]))}
 {dropdown('fault','Second piston fault',[['none','None'],['stuck','Stuck at initial position'],['late','Valve trips 5% of stroke later'],['friction','5% more friction'],['mass','5% more mass']])}
 <FormControlLabel control={<Switch checked={config.use_dump} onChange={e=>set('use_dump',e.target.checked)}/>} label="Couple C / D to pressure dump"/>
 <FormControlLabel control={<Switch checked={config.stator_cam} onChange={e=>set('stator_cam',e.target.checked)}/>} label="D: add stationary return cam"/>
 </div>
 {fields.map(([title,items])=><Accordion key={title} disableGutters><AccordionSummary expandIcon={<span>+</span>}>{title}</AccordionSummary><AccordionDetails><div className="field-grid">{items.map(([key,label,unit,min,max,step=1])=><TextField key={key} size="small" type="number" label={label} helperText={unit||'dimensionless'} value={config[key]} onChange={e=>set(key,Number(e.target.value))} inputProps={{min,max,step}}/>)}</div></AccordionDetails></Accordion>)}
 <div className="actions"><Button variant="contained" disabled={!!job} onClick={()=>start('simulate')}>Run physics</Button><Button disabled={!!job} onClick={async()=>{const c=await fetch('/api/example').then(r=>r.json());setConfig(c);start('simulate',c);}}>Load tuned example</Button><Button disabled={!!job} onClick={()=>start('compare')}>Compare A–D</Button><Button disabled={!!job} onClick={()=>start('sweep')}>Sweep RPM</Button><Button disabled={!!job} onClick={()=>start('balance')}>Test balance faults</Button><Button variant="outlined" disabled={!!job} onClick={()=>start('optimize')}>Find feasible design</Button></div>
 <p className="small">Inputs are draft settings until Run physics. All simulation steps run in Python. Playback shows the stored solution once; it does not invent a repeating cycle.</p>
 </aside><section className="workspace">
 {error&&<Alert severity="error" onClose={()=>setError('')}>{error}</Alert>}
 {job&&<div className="job"><div>{job.message} <Button onClick={()=>fetch('/api/jobs/'+job.id,{method:'DELETE'})}>Cancel</Button></div><LinearProgress variant={job.progress?'determinate':'indeterminate'} value={job.progress*100}/></div>}
 {changed&&<Alert severity="info">Draft settings differ from the displayed experiment. Run physics to apply them.</Alert>}
 {run&&<>
 <section className="feasibility"><div className="section-heading"><h2>Feasibility</h2><Chip color={s.self_cycles?'success':'default'} label={s.behavior}/></div><p className="reason">{s.reason}</p>
 <div className="metrics">
 {[['Piston moves',s.moved?'Yes':'No'],['Settles',s.settled?'Yes':'No'],['Completed returns',s.reset_count],['Primary self-cycles',s.self_cycles?'Yes · model only':s.forced&&s.maintained?'Rotation-forced':'Not established'],['Cycles by module',(s.module_cycle_counts||[s.reset_count]).join(' / ')],['Cycle rate',fmt(s.cycle_hz,3)+' Hz'],['Late-run pitch',fmt(s.pitch_min,0)+'–'+fmt(s.pitch_max,0)+' Hz'],['Equilibrium',fmt(s.equilibrium_mm,2)+' mm'],['Peak imbalance',fmt(s.peak_imbalance,3)+' N'],['Pitch now',fmt(r.frequency,0)+' Hz'],['Travel now',fmt(r.x*1000,2)+' mm'],['Pressure now',fmt(r.pressure,2)+' Pa']].map(([label,value])=><div key={label}><span>{label}</span><strong>{value}</strong></div>)}
 </div><p className="small">Classification uses the full {c.duration} s solution, including late-time return and amplitude checks. A finite run cannot establish indefinite operation.</p>
 {s.warnings.map(w=><Alert key={w} severity="warning">{w}</Alert>)}
 </section>
 <section className="visual"><Cutaway c={c} r={r}/>
 <div className="playback"><Button variant="outlined" onClick={()=>{if(cursor>=c.duration)seek(0);setPlaying(!playing);}}>{playing?'Pause':'Play solution'}</Button>
 <input aria-label="Playback time" type="range" min="0" max={c.duration} step=".01" value={cursor} onChange={e=>{setPlaying(false);seek(Number(e.target.value));}}/>
 <span>{fmt(cursor,2)} / {c.duration} s</span><TextField select size="small" label="Playback" value={speed} onChange={e=>setSpeed(Number(e.target.value))}>{[.25,.5,1,2].map(x=><MenuItem key={x} value={x}>{x}×</MenuItem>)}</TextField>
 <Button onClick={toggleAudio}>{audioOn?'Mute tone':'Hear resonance'}</Button></div>
 <p className="small">Tone = calculated resonance, even if airflow would not excite a whistle. No loudness, jet onset, or overblowing prediction. Rotation and forces use the computed state.</p></section>
 <div className="plots">
 <Plot rows={rows} series={[{key:'x',label:'Piston',scale:1000}]} title="Piston position" units="mm" cursor={cursor}/>
 <Plot rows={rows} series={[{key:'v',label:'Velocity'}]} title="Piston velocity" units="m/s" cursor={cursor}/>
 <Plot rows={rows} series={[{key:'fc',label:'Centrifugal'},{key:'spring',label:'Spring'},{key:'air',label:'Air'},{key:'friction',label:'Friction'}]} title="Radial forces · outward positive" units="N" cursor={cursor}/>
 <Plot rows={rows} series={[{key:'pressure',label:'Gauge pressure'}]} title="Chamber pressure" units="Pa" cursor={cursor}/>
 <Plot rows={rows} series={[{key:'frequency',label:'Resonance'}]} title="Predicted fundamental" units="Hz" cursor={cursor}/>
 <Plot rows={rows} series={[{key:'imbalance_n',label:'Rotating imbalance'},{key:'dynamic_reaction_n',label:'Including piston acceleration'}]} title="Shaft reaction estimates" units="N" cursor={cursor}/>
 </div>
 <details><summary>Force margins, power and numerical diagnostics</summary><div className="metrics">
 {[['Closed / open pressure',fmt(s.closed_pressure,3)+' / '+fmt(s.open_pressure,3)+' Pa'],['Minimum outward margin',fmt(s.outward_margin,5)+' N'],['Minimum return margin',fmt(s.return_margin,5)+' N'],['Peak acceleration',fmt(s.max_g,1)+' g'],['Peak centrifugal load',fmt(s.peak_fc,3)+' N'],['Peak spring load',fmt(s.peak_spring,3)+' N'],['Peak impact speed',fmt(s.peak_impact,3)+' m/s'],['Peak COM offset',fmt(s.peak_com_mm,3)+' mm'],['Pneumatic source power',fmt(s.source_power_w*1000,4)+' mW'],['Scoop drag power',fmt(s.scoop_drag_power_w*1000,4)+' mW'],['Pressure / cam work',fmt(s.pressure_work_j,5)+' / '+fmt(s.cam_work_j,5)+' J'],['Integration step',fmt(s.dt*1000,4)+' ms']].map(([k,v])=><div key={k}><span>{k}</span><strong>{v}</strong></div>)}</div><p className="small">Margins are quasi-static tests over the valve stroke, not a replacement for dynamics. End stops use dissipative contact impulses; peak contact force depends on timestep. No screening flag means only that the selected limits were not exceeded.</p></details>
 <div className="export"><Button onClick={()=>download('whistle-run.json',run)}>Export run JSON</Button><Button onClick={()=>{const keys=['t','x','v','fc','spring','air','friction','damping','gravity','stop','pressure','frequency','length','imbalance_n','com_mm'];download('whistle-run.csv',keys.join(',')+'\n'+rows.map(z=>keys.map(k=>z[k]).join(',')).join('\n'),'text/csv');}}>Export traces CSV</Button></div>
 </>}
 {comparison&&<section className="results"><h2>Same inputs · mechanisms A–D</h2><ResultsTable items={comparison.modes.map(z=>({label:modes[z.mode],...z.summary}))}/></section>}
 {faults&&<section className="results"><h2>Opposing-module fault tests</h2><ResultsTable items={faults.faults.map(z=>({label:z.fault,...z.summary}))}/></section>}
 {sweep&&<section className="results"><div className="section-heading"><h2>RPM operating map</h2><Button onClick={()=>download('whistle-rpm-sweep.json',sweep)}>Export</Button></div><p className="small">{sweep.method}</p><RpmMap sweep={sweep}/><ResultsTable rpm items={sweep.points.map(z=>({label:fmt(z.rpm,0)+' rpm',...z}))}/></section>}
 {designs&&<section className="results"><div className="section-heading"><h2>Design search</h2><Button onClick={()=>download('whistle-candidates.json',designs)}>Export</Button></div><p>{designs.candidates.length?designs.candidates.length+' model candidates passed the cycling, screening and half-step checks.':'No confirmed candidate in this search.'}</p><p className="small">{designs.note}</p>
 {designs.candidates.map((z,i)=><article className="candidate" key={i}><div><h3>Candidate {i+1} · {z.config.rpm} rpm</h3><p>{z.config.mass_g} g piston · Ø{z.config.piston_mm} mm · {z.config.travel_mm} mm available stroke · spring {fmt(z.config.spring_k,4)} N/m · preload {fmt(z.config.preload_n,5)} N</p><p>{fmt(z.summary.cycle_hz,3)} cycles/s · {fmt(z.summary.sweep_seconds,2)} s falling sweep · {fmt(z.summary.pitch_max,0)} → {fmt(z.summary.pitch_min,0)} Hz</p><p className="small">Peak speed {fmt(z.summary.peak_velocity,3)} m/s · load {fmt(z.summary.peak_fc,3)} N · nominal imbalance {fmt(z.summary.peak_imbalance,3)} N · with 5% friction mismatch: {fmt(z.friction_fault_imbalance,3)} N</p></div><Button disabled={!!job} onClick={()=>{setConfig(z.config);start('simulate',z.config);}}>Load & run</Button></article>)}</section>}
 <section className="notes"><h2>What this model can establish</h2><p>Constant RPM is maintained by an external drive. The rotor contains only springs, pistons, valves and optional passive latches. A stationary cam is an explicitly added mechanical connection to the frame, and its motion is classified as forced.</p><p>The pressure model uses a finite inlet, whistle leakage, a mechanically switched bypass and compressible chamber storage. Orifice flow is linearized; sealing friction and pressure recovery are assumptions. The valve is ideal and pressure-balanced: actuator travel, opening work and valve stiction are not modeled. A real labium may not whistle at the calculated resonance. The Helmholtz option describes a cavity with a narrow neck; the quarter-wave option describes a long closed-open tube.</p><p>For mode C, the snap threshold shapes a conservative double-well spring potential. It does not inject energy when the piston snaps. Mode D's latch releases or catches the piston without supplying reset energy. Enable the dump or stationary cam to test a specified energy pathway.</p><p>A matched pair is balanced only while its mass positions match. The balance calculations include moving piston masses and a centered rotor mass, not spring or air motion, bearing flexibility, axial couple imbalance or rotor strength.</p><p className="small">References: <a href="https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/dynamic-pressure/" target="_blank" rel="noreferrer">NASA dynamic pressure</a> · <a href="https://newt.phys.unsw.edu.au/jw/flutes.v.clarinets.html" target="_blank" rel="noreferrer">UNSW pipe resonance</a> · <a href="https://phys.unsw.edu.au/jw/Helmholtz.html" target="_blank" rel="noreferrer">UNSW Helmholtz resonance</a></p></section>
 </section></div></main></ThemeProvider>;
}
function ResultsTable({items}){
 return <div className="table-wrap"><table><thead><tr>{['Case','Measured behavior','Equilibrium mm','Cycle Hz','Returns by module','Pitch Hz (late)','Sweep s','Imbalance N','Screening'].map(x=><th key={x}>{x}</th>)}</tr></thead><tbody>{items.map((z,i)=><tr key={i}><td>{z.label}</td><td title={z.reason}>{z.behavior}</td><td>{fmt(z.equilibrium_mm)}</td><td>{fmt(z.cycle_hz,3)}</td><td>{(z.module_cycle_counts||[z.reset_count]).join(" / ")}</td><td>{fmt(z.pitch_min,0)}–{fmt(z.pitch_max,0)}</td><td>{fmt(z.sweep_seconds)}</td><td>{fmt(z.peak_imbalance,3)}</td><td>{z.warnings.length?'LIMIT EXCEEDED':'No flag'}</td></tr>)}</tbody></table></div>;
}
function RpmMap({sweep}){
 const color=z=>z.warnings.length?'#e58fa8':z.behavior==='RESET CYCLING'?'#70d6b7':z.behavior==='ROTATION-FORCED CYCLING'?'#9dabff':z.behavior==='SUSTAINED OSCILLATION'?'#7bcce3':z.behavior==='NO MOTION'?'#56676b':z.behavior.includes('DAMPED')?'#f3bb75':'#899b93';
 const cycling=sweep.points.filter(z=>z.maintained&&!z.warnings.length);
 return <><div className="rpm-map">{sweep.points.map((z,i)=><div key={i} style={{borderTopColor:color(z)}} title={z.behavior+'; '+z.reason}><span>{fmt(z.rpm,0)}</span><small>{z.warnings.length?'FLAG':z.self_cycles?'CYCLE':z.forced&&z.maintained?'FORCED':z.moved?'MOVED':'STILL'}</small></div>)}</div><p className="small">Tested cycling RPM samples: {cycling.length?cycling.map(z=>fmt(z.rpm,0)).join(', '):'none'}. Discrete samples do not establish a continuous operating range; narrow windows may fall between samples. Colors: gray no motion, amber damped, green reset cycling, blue oscillation, violet forced, pink screening flag.</p></>;
}
createRoot(document.getElementById('root')).render(<App/>);
