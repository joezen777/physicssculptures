from pathlib import Path
import json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from summarize import BASE,summarize
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results';OUT.mkdir(exist_ok=True)
fig,axs=plt.subplots(1,2,figsize=(12,4.5))
for case in sorted(BASE.glob('*_*')):
    result=summarize(case)
    if isinstance(result,dict):continue
    report,torque,flow=result
    if torque:
        t,v=np.array(torque).T;axs[1].plot(t,v*1000,label=case.name)
    if flow:
        t,v=np.array(flow).T;axs[0].plot(t,v,'.-',label=case.name)
axs[0].set_ylabel('Downward disk flux (L/s)');axs[1].set_ylabel('Aerodynamic resisting torque (mN m)')
for ax in axs:ax.set_xlabel('SIMPLE iteration (not physical time)');ax.grid(alpha=.25);ax.legend(fontsize=8)
fig.suptitle('400 RPM CFD: convergence histories, not validated measurements')
fig.tight_layout();fig.savefig(OUT/'convergence.png',dpi=160)
fig,axs=plt.subplots(1,4,figsize=(13,3.8),sharex=True,sharey=True)
for ax,name in zip(axs,['original','scimitar','tubercled','toroidal5']):
    case=BASE/(name+'_coarse')
    files=list((case/'postProcessing/velocitySamples').glob('*/below_U.xy'))
    if not files:continue
    file=max(files,key=lambda p:float(p.parent.name));a=np.loadtxt(file)
    plot=ax.scatter(a[:,0]*1000,a[:,1]*1000,c=-a[:,5],s=12,cmap='coolwarm',vmin=-.5,vmax=1.5)
    ax.set_title(name+' / iteration '+file.parent.name,fontsize=9);ax.set_aspect('equal');ax.set_xlabel('x (mm)')
axs[0].set_ylabel('y (mm)');fig.subplots_adjust(right=.9,top=.78)
if 'plot' in locals():fig.colorbar(plot,cax=fig.add_axes([.92,.2,.015,.5]),label='Downward velocity (m/s)')
fig.suptitle('Computed flow through the downstream disk at z = -40 mm')
fig.savefig(OUT/'downstream_velocity.png',dpi=160)
