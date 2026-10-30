import json, subprocess, re, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run import RL, IS, N, op
res=json.load(open('combos.json'))
def req(m):
    g=sum(1/RL[k] for k in range(8) if (m>>k)&1)
    return 1/g if g else np.inf
# --- curve I-V of panel alone (ngspice .dc)
def curve(iph):
    nl=f"* curva del panel\nIPH 0 PV DC {iph}\nDPV PV 0 DPV\n.model DPV D(IS={IS} N={N})\nVS PV 0 0\n.control\ndc VS 0 9.3 0.02\nwrdata c.txt i(VS)\n.endc\n.end\n"
    open('c.cir','w').write(nl); subprocess.run(['ngspice','-b','c.cir'],capture_output=True)
    d=np.loadtxt('c.txt'); return d[:,0], d[:,1]
V0,I0=curve(0.212); V1,I1=curve(0.212*0.89)
m_=I0>0; V0,I0=V0[m_],I0[m_]; m_=I1>0; V1,I1=V1[m_],I1[m_]
P0=V0*I0; k=P0.argmax()
print("Panel limpio: Voc=%.3f Isc=%.4f Pmax=%.3f W @ %.2f V %.3f A FF=%.3f"%(V0[-1],I0[0],P0[k],V0[k],I0[k],P0[k]/(V0[-1]*I0[0])))
# --- seleccion de 23 puntos: circuito abierto + 22 combinaciones espaciadas por longitud de arco de la curva I-V normalizada
Voc_=V0[-1]; Isc_=I0[0]
xs=V0/Voc_; ys=I0/Isc_
arc=np.concatenate([[0],np.cumsum(np.hypot(np.diff(xs),np.diff(ys)))]); arc/=arc[-1]
pts=[(m,)+tuple(r[1:4:2]) for m,r in [(r[0],r) for r in res]]  # (m, V, Vsh)
sel=[]
tg=np.linspace(0,1,24)[1:-1]
for t in tg:
    i=np.argmin(abs(arc-t)); xt,yt=xs[i],ys[i]
    cand=[(np.hypot(p[1]/Voc_-xt,p[2]/Isc_-yt),p[0]) for p in pts if p[0]!=0 and p[0] not in sel]
    sel.append(min(cand)[1])
sel=[0]+sel
rows=[]
for m in sel:
    _,pv,a0,sh=[r for r in res if r[0]==m][0]
    cnt0=round(a0/125e-6); cnt1=round(sh/15.625e-6)
    Vm=cnt0*125e-6*4.3; Im=cnt1*15.625e-6
    Vtrue=pv; Itrue=sh
    rows.append(dict(mask=m,Req=req(m),V=pv,A0=a0,Vsh=sh,Vm=Vm,Im=Im,P=pv*sh,Pm=Vm*Im,cA0=cnt0,cSH=cnt1))
for r in rows: print("%3d Req=%7.2f V=%.3f A0=%.4f Vsh=%.4f cnt=%d/%d  P=%.4f Pm=%.4f"%(r['mask'],r['Req'],r['V'],r['A0'],r['Vsh'],r['cA0'],r['cSH'],r['P'],r['Pm']))
json.dump(rows,open('rows.json','w'))
Pm=max(r['Pm'] for r in rows); Pt=max(r['P'] for r in rows)
print("Pmax del barrido: simulado %.4f W, 'medido' tras cuantizar %.4f W, error %.3f %%"%(Pt,Pm,100*(Pm-Pt)/Pt))
print("A0 max=%.3f V (limite 4.096), Vsh max=%.3f V (limite 0.512)"%(max(r['A0'] for r in rows),max(r['Vsh'] for r in rows)))
# --- figura 1
C1,C2='#2E75C9','#B8560F'
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'font.family':'DejaVu Sans'})
fig,ax=plt.subplots(2,1,figsize=(6.4,5.6),sharex=True)
ax[0].plot(V0,I0*1e3,color=C2,lw=1.6,label='Panel limpio (modelo)')
ax[0].plot(V1,I1*1e3,color=C2,lw=1.2,ls='--',label='Panel con suciedad (−11 % en Iph)')
ax[0].plot([r['V'] for r in rows],[r['Vsh']*1e3 for r in rows],'o',color=C1,ms=5,mec='white',mew=0.8,label='Barrido de 23 puntos (circuito completo)')
ax[0].set_ylabel('Corriente (mA)'); ax[0].legend(frameon=False,fontsize=8,loc='lower left'); ax[0].grid(alpha=.25)
ax[1].plot(V0,P0,color=C2,lw=1.6); ax[1].plot(V1,V1*I1,color=C2,lw=1.2,ls='--')
ax[1].plot([r['V'] for r in rows],[r['P'] for r in rows],'o',color=C1,ms=5,mec='white',mew=0.8)
ax[1].set_ylabel('Potencia (W)'); ax[1].set_xlabel('Voltaje del módulo (V)'); ax[1].grid(alpha=.25)
fig.tight_layout(); fig.savefig('fig_sim_iv.pdf'); fig.savefig('fig_sim_iv.png',dpi=160)
# --- figura 2: transitorio al cerrar relé de 22 Ω
from run import netlist
nl=netlist(0,tran=True,extra=".control\ntran 20u 8m\nwrdata tr.txt v(pv) v(ain0) v(sh)\n.endc\n.end")
open('tr.cir','w').write(nl); subprocess.run(['ngspice','-b','tr.cir'],capture_output=True)
d=np.loadtxt('tr.txt'); t=d[:,0]*1e3; a0=d[:,3]
fin=a0[-1]; 
idx=np.where(abs(a0-fin)>125e-6)[0]; ts=t[idx[-1]]-1.0 if len(idx) else 0
print("A0 final=%.4f V; asentamiento a +-1 cuenta (125 uV) tras %.2f ms desde el cierre"%(fin,ts))
fig,ax=plt.subplots(figsize=(6.4,2.8))
ax.plot(t,a0,color=C1,lw=1.6); ax.axvline(1.0,color=C2,ls='--',lw=1); ax.text(1.1,a0.min()+0.02,'cierre del relé',color='#444',fontsize=8)
ax.set_xlabel('Tiempo (ms)'); ax.set_ylabel('Voltaje en A0 (V)'); ax.grid(alpha=.25)
fig.tight_layout(); fig.savefig('fig_sim_tr.pdf'); fig.savefig('fig_sim_tr.png',dpi=160)
json.dump(dict(ts=ts,fin=fin,Pt=Pt,Pm=Pm,Pmax=P0[k],Vmp=V0[k],Imp=I0[k],Isc=I0[0],Voc=float(V0[-1])),open('summary.json','w'))
