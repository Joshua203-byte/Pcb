import subprocess, itertools, re, json, numpy as np, os
RL=[2.2,4.7,10,22,47,100,220,470]
IS=3.74e-9; N=19.5
def netlist(mask, iph=0.212, tran=False, extra=''):
    L=["* Sistema de medicion - panel 1.5 W (equivalente de la hoja KiCad)",
       f"IPH 0 PV DC {iph}",
       "DPV PV 0 DPV", f".model DPV D(IS={IS} N={N})",
       "R1 PV AD 33k","R2 AD 0 10k","R3 AD AIN0 1k","C1 AIN0 0 0.1u","RIN AIN0 0 5Meg",
       "RSH1 SH 0 1","RINSH SH 0 5Meg",
       ".model SWR SW(Ron=0.05 Roff=1e9 Vt=0.5 Vh=0.1)"]
    for k in range(8):
        on = (mask>>k)&1
        if tran and k==3: ctl="PULSE(0 5 1m 10u 10u 1 2)"; 
        else: ctl=f"DC {5*on}"
        L+= [f"VC{k+1} C{k+1} 0 {ctl}", f"S{k+1} PV N{k+1} C{k+1} 0 SWR", f"RL{k+1} N{k+1} SH {RL[k]}"]
    L+=[extra]
    return "\n".join(L)
def op(mask, iph=0.212):
    nl=netlist(mask,iph)+"\n.control\nop\nprint v(pv) v(ain0) v(sh)\n.endc\n.end\n"
    open('t.cir','w').write(nl)
    o=subprocess.run(['ngspice','-b','t.cir'],capture_output=True,text=True).stdout
    g=lambda n: float(re.search(rf"v\({n}\)\s*=\s*([-\d.e+]+)",o,re.I).group(1))
    return g('pv'),g('ain0'),g('sh')
if __name__=='__main__':
    res=[]
    for m in range(256):
        pv,a0,sh=op(m)
        res.append((m,pv,a0,sh))
    json.dump(res,open('combos.json','w'))
    print(len(res), res[0], res[8])
