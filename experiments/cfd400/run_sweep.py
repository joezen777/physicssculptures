"""Bounded local transient sweep; restartable from written fields."""
from pathlib import Path
import argparse,subprocess,time,json,re,signal,fcntl
from foam_runtime import BIN,ENV
BASE=Path.home()/'.cache/angularmomflyer/cfd400'
p=argparse.ArgumentParser();p.add_argument('--hours',type=float,default=12);p.add_argument('--workers',type=int,default=4);args=p.parse_args()
assert args.hours>0 and 1<=args.workers<=4
cases=[BASE/f'{name}_transient_{rpm}' for rpm in [400,800,600] for name in ['original','scimitar','toroidal5','tubercled']]
cases.append(BASE/'original_fine_transient_400')
assert all((c/'experiment.json').exists() for c in cases)
lock=open(BASE/'sweep.lock','w')
fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
def interrupted(signum,frame):raise KeyboardInterrupt
signal.signal(signal.SIGTERM,interrupted)
started=time.time();deadline=started+args.hours*3600
running={};finished=[];pending=list(cases);last=0;stopping=False

def status():
 rows=[]
 for c in cases:
  log=c/'log.pimpleFoam';s=log.read_text(errors='replace') if log.exists() else ''
  times=re.findall(r'^Time = (\S+)',s,re.M)
  rows.append(dict(case=c.name,physical_seconds=float(times[-1]) if times else 0,ended=s.rstrip().endswith('End'),running=c in running))
 (BASE/'sweep_status.json').write_text(json.dumps(dict(started_unix=started,deadline_unix=deadline,budget_hours=args.hours,elapsed_hours=(time.time()-started)/3600,cases=rows,finished=finished),indent=2)+'\n')
 print(json.dumps(rows),flush=True)

try:
 while pending or running:
  now=time.time()
  if now>=deadline and not stopping:
   stopping=True;pending=[]
   for c in running:
    p=c/'system/controlDict';p.write_text(re.sub(r'stopAt \w+;', 'stopAt writeNow;',p.read_text()))
   print('Compute budget reached; asking solvers to write and stop.',flush=True)
  while pending and len(running)<args.workers and not stopping:
   c=pending.pop(0);p=c/'system/controlDict'
   existing=(c/'log.pimpleFoam').read_text() if (c/'log.pimpleFoam').exists() else ''
   times=re.findall(r'^Time = (\S+)',existing,re.M)
   if existing.rstrip().endswith('End') and times and float(times[-1])>=1.5-1e-8:
    finished.append(dict(case=c.name,status='already_complete'));continue
   s=p.read_text();s=re.sub(r'startFrom \w+;','startFrom latestTime;',s);s=re.sub(r'stopAt \w+;','stopAt endTime;',s);s=re.sub(r'endTime [^;]+;','endTime 1.5;',s);s=s.replace('writeInterval 0.003;','writeInterval 0.15;');p.write_text(s)
   f=open(c/'log.pimpleFoam','a');proc=subprocess.Popen([str(BIN/'pimpleFoam'),'-case',str(c)],env=ENV,stdout=f,stderr=f)
   running[c]=(proc,f);print('Started '+c.name,flush=True)
  for c,(proc,f) in list(running.items()):
   result=proc.poll()
   if result is not None:
    f.close();finished.append(dict(case=c.name,returncode=result));del running[c]
  if stopping and now>deadline+180:
   for c,(proc,f) in running.items():proc.terminate()
  if now-last>=30:status();last=now
  time.sleep(2)
finally:
 for c,(proc,f) in running.items():
  p=c/'system/controlDict';p.write_text(re.sub(r'stopAt \w+;','stopAt writeNow;',p.read_text()))
 status()
