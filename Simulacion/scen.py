import subprocess, re, json, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import run
from run import RL
ALPHA=0.0005      # coef. de Isc, 0.05 %/degC (supuesto tipico silicio)
def iph(G,T): return 0.212*G/1000*(1+ALPHA*(T-25))
MODEL=".model DPV D(IS=3.32n N=19.5 EG=16.8 XTI=45 TNOM=25)"
def nl(mask,G,T,extra):
    s=run.netlist(mask,iph(G,T),False,extra).replace(".model DPV D(IS=3.74e-09 N=19.5)",MODEL)
    s=s.replace(".model DPV D(IS=3.74e-9 N=19.5)",MODEL)
    assert "EG=16.8" in s
    return f"* escenario\n.temp {T}\n"+s
def op(mask,G,T):
    t=nl(mask,G,T,".control\nop\nprint v(pv) v(ain0) v(sh)\n.endc\n.end\n")
    open('s.cir','w').write(t)
    o=subprocess.run(['ngspice','-b','s.cir'],capture_output=True,text=True).stdout
    g=lambda n: float(re.search(rf"v\({n}\)\s*=\s*([-\d.e+]+)",o,re.I).group(1))
    return g('pv'),g('ain0'),g('sh')
rows=json.load(open('rows.json')); masks=[r['mask'] for r in rows]
def exact(G,T):
    d=f"* c\nIPH 0 PV DC {iph(G,T)}\nDPV PV 0 DPV\n{MODEL}\nVS PV 0 0\n.temp {T}\n.control\ndc VS 0 9.6 0.005\nwrdata c.txt i(VS)\n.endc\n.end\n"
    open('c.cir','w').write(d); subprocess.run(['ngspice','-b','c.cir'],capture_output=True)
    x=np.loadtxt('c.txt'); V,I=x[:,0],x[:,1]; m=I>0; V,I=V[m],I[m]; P=V*I; k=P.argmax()
    return dict(Voc=V[-1],Isc=I[0],Vmp=V[k],Imp=I[k],Pmax=P[k])
out=[]
cases=[(G,25) for G in (200,400,600,800,1000,1100)]+[(1000,T) for T in (15,45,65)]+[(800,45),(600,15)]
for G,T in cases:
    e=exact(G,T); pts=[op(m,G,T) for m in masks]
    Pt=[v*s for v,a,s in pts]; i=int(np.argmax(Pt))
    cnt=lambda a:round(a/125e-6); 
    Pm=max(round(a/125e-6)*125e-6*4.3*round(s/15.625e-6)*15.625e-6 for v,a,s in pts)
    A0=max(a for v,a,s in pts); SH=max(s for v,a,s in pts)
    vref=iph(G,T)*1.0   # celda de referencia supuesta = Isc igual al modulo, shunt 1 ohm
    Gest=round(vref/15.625e-6)*15.625e-6/(0.212*(1+ALPHA*(T-25)))*1000
    out.append(dict(G=G,T=T,**e,Psweep=max(Pt),Pquant=Pm,A0max=A0,SHmax=SH,ref_mV=vref*1e3,Gest=Gest,
                    Vsc_cnt=round(SH/15.625e-6),Voc_cnt=round(pts[-1][1]/125e-6)))
    print(out[-1])
json.dump(out,open('scen.json','w'),indent=1)
# figura
fig,ax=plt.subplots(1,2,figsize=(6.4,2.9))
C=['#2E75C9','#B8560F','#2A8F5C']
Gs=[o for o in out if o['T']==25]; 
ax[0].plot([o['G'] for o in Gs],[o['Pmax'] for o in Gs],'-',color=C[1],label='Teórica (curva exacta)')
ax[0].plot([o['G'] for o in Gs],[o['Pquant'] for o in Gs],'o',color=C[0],mec='white',label='Barrido simulado (23 pts, con cuantización)')
ax[0].set_xlabel('Irradiancia (W/m²)'); ax[0].set_ylabel('$P_{max}$ (W)'); ax[0].grid(alpha=.25); ax[0].legend(frameon=False,fontsize=7)
Ts=[o for o in out if o['G']==1000]; Ts=sorted(Ts,key=lambda o:o['T'])
ax[1].plot([o['T'] for o in Ts],[o['Pmax'] for o in Ts],'-',color=C[1]); ax[1].plot([o['T'] for o in Ts],[o['Pquant'] for o in Ts],'o',color=C[0],mec='white')
ax[1].set_xlabel('Temperatura del módulo (°C)'); ax[1].set_ylabel('$P_{max}$ (W)'); ax[1].grid(alpha=.25)
for a in ax: a.spines[['top','right']].set_visible(False)
fig.tight_layout(); fig.savefig('fig_sim_esc.pdf'); fig.savefig('fig_sim_esc.png',dpi=160)
