"""Read actual CFD histories; no empirical airflow multipliers."""
from pathlib import Path
import math,json,re,csv,argparse,statistics
BASE=Path.home()/'.cache/angularmomflyer/cfd400'
AREA=math.pi*.072**2
OMEGA=400*2*math.pi/60

def summarize(case):
    out={'case':case.name}
    log=(case/'log.simpleFoam')
    if not log.exists():return out
    text=log.read_text(errors='replace')
    times=re.findall(r'^Time = (\S+)',text,re.M)
    out['iteration']=float(times[-1]) if times else 0
    out['ended']='\nEnd\n' in text
    out['residuals']={}
    for var in ['Ux','Uy','Uz','p']:
        a=re.findall(r'Solving for '+var+r', Initial residual = ([^,]+)',text)
        if a:out['residuals'][var]=float(a[-1])
    hist=[]
    for file in sorted((case/'postProcessing/loads').glob('*/moment.dat')):
        for line in file.read_text().splitlines():
            if line.startswith('#'):continue
            a=line.translate(str.maketrans({'(':' ',')':' '})).split()
            if len(a)>=10:hist.append((float(a[0]),float(a[3])))
    hist=sorted(dict(hist).items())
    if hist:
        last=hist[-100:];v=[b for a,b in last];avg=statistics.mean(v)
        out.update(torque_mNm=avg*1000,power_W=avg*OMEGA,torque_range_pct=100*(max(v)-min(v))/abs(avg),torque_window_iterations=[last[0][0],last[-1][0]])
    flow=[]
    for file in (case/'postProcessing/velocitySamples').glob('*/below_U.xy'):
        rows=[list(map(float,l.split())) for l in file.read_text().splitlines() if l.strip() and not l.startswith('#')]
        if len(rows)!=576:raise ValueError(f'{file}: {len(rows)} samples; expected 576')
        uz=[a[5] for a in rows]
        if not all(math.isfinite(v) and abs(v)<100 for v in uz):raise ValueError('Invalid velocities')
        flow.append((float(file.parent.name),-statistics.mean(uz)*AREA*1000))
    flow.sort()
    if flow:
        recent=flow[-3:];v=[b for a,b in recent];avg=statistics.mean(v)
        out.update(flow_L_s=flow[-1][1],flow_last3_range_pct=100*(max(v)-min(v))/abs(avg),flow_samples=recent,mean_disk_speed_m_s=flow[-1][1]/1000/AREA)
    check=case/'log.checkMesh'
    if check.exists():
        s=check.read_text();out['mesh_ok']='Mesh OK.' in s
        cells=re.search(r'cells:\s+(\d+)',s)
        if cells:out['cells']=int(cells[1])
    out['numerically_settled_screen']=bool(out.get('ended') and out.get('torque_range_pct',999)<2 and out.get('flow_last3_range_pct',999)<2 and max(out['residuals'].values(),default=1)<1e-3)
    return out,hist,flow

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--save',action='store_true');args=parser.parse_args()
    reports=[]
    dest=Path(__file__).resolve().parent/'results'
    if args.save:dest.mkdir(exist_ok=True)
    for case in sorted(BASE.glob('*_*')):
        result=summarize(case)
        if isinstance(result,dict):print(result);continue
        report,torque,flow=result;reports.append(report);print(json.dumps(report,indent=2))
        if args.save:
            for name,rows,headers in [('torque',torque,['iteration','torque_Nm']),('flow',flow,['iteration','flow_L_s'])]:
                with (dest/(case.name+'_'+name+'.csv')).open('w',newline='') as f:
                    w=csv.writer(f,lineterminator='\n');w.writerow(headers);w.writerows(rows)
    if args.save:(dest/'summary.json').write_text(json.dumps(reports,indent=2)+'\n')
