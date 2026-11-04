"""Modelo de panel de un diodo (con Rs y Rsh) para 12 celdas en serie, ajustado a Voc = 6 V e Isc = 200 mA a STC.

Se usa SOLO para simular datos de prueba (datos/simulador.py) y para dibujar la curva "de referencia del fabricante"
(datos/analizar.py). V(I) se obtiene con la funcion W de Lambert, valida tambien para I mayor que la fotocorriente
(celdas sombreadas en polarizacion inversa).
"""
import numpy as np
from scipy.special import lambertw

KB, Q, EG = 1.380649e-23, 1.602176634e-19, 1.12      # J/K, C, eV (silicio)
NS, N_ID = 12, 1.3                                   # celdas en serie y factor de idealidad
ISC_STC, VOC_STC = 0.200, 6.0                        # datos del panel (los dio el equipo)
RS, RSH = 0.8, 300.0                                 # supuestos tipicos del modulo completo (ohm)
ALFA_ISC = 0.0005                                    # +0.05 %/C
T_REF = 298.15


def _a(Tc, celdas=NS):
    return celdas * N_ID * KB * (Tc + 273.15) / Q


def _i0_ref():
    a = _a(25.0)
    return (ISC_STC - VOC_STC / RSH) / (np.exp(VOC_STC / a) - 1.0)


I0_REF = _i0_ref()


def i0(Tc):
    T = Tc + 273.15
    return I0_REF * (T / T_REF) ** 3 * np.exp(EG * Q / (N_ID * KB) * (1.0 / T_REF - 1.0 / T))


def fotocorriente(G, Tc):
    return ISC_STC * (G / 1000.0) * (1.0 + ALFA_ISC * (Tc - 25.0)) + (VOC_STC / RSH) * 0.0


def v_grupo(I, iph, celdas, Tc):
    """Voltaje de un grupo de `celdas` en serie que lleva la corriente I (fotocorriente iph)."""
    a = _a(Tc, celdas)
    rs, rsh = RS * celdas / NS, RSH * celdas / NS
    io = i0(Tc)
    arg = np.log(io * rsh / a) + rsh * (iph + io - I) / a        # log del argumento de W
    arg = np.minimum(arg, 600.0)
    w = np.real(lambertw(np.exp(arg)))
    return rsh * (iph + io - I) - I * rs - a * w


def v_panel(I, G, Tc, sombra=None):
    """Voltaje del panel con corriente I. sombra = (celdas_sombreadas, fraccion_de_luz_que_llega) o None."""
    iph = fotocorriente(G, Tc)
    I = np.asarray(I, dtype=float)
    if not sombra:
        return v_grupo(I, iph, NS, Tc)
    n_s, frac = sombra
    return v_grupo(I, iph, NS - n_s, Tc) + v_grupo(I, iph * frac, n_s, Tc)


def punto_operacion(R, G, Tc, sombra=None):
    """Corriente y voltaje cuando el panel alimenta una resistencia R (ohm). R puede ser un arreglo; inf = circuito abierto."""
    R = np.asarray(R, dtype=float)
    iph = fotocorriente(G, Tc)
    lo = np.zeros_like(R); hi = np.full_like(R, iph * 1.02 + 1e-6)
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        f = v_panel(mid, G, Tc, sombra) - mid * R            # V(I) decrece con I; mid*R crece
        lo = np.where(f > 0, mid, lo); hi = np.where(f > 0, hi, mid)
    I = 0.5 * (lo + hi)
    I = np.where(np.isinf(R), 0.0, I)
    return I, v_panel(I, G, Tc, sombra)


def curva_iv(G, Tc, sombra=None, n=200):
    """Curva I-V completa (V creciente) por barrido de corriente."""
    iph = fotocorriente(G, Tc)
    I = np.linspace(iph * 1.0, 0.0, n)
    V = v_panel(I, G, Tc, sombra)
    ok = V >= 0
    return V[ok], I[ok]


def parametros(G=1000.0, Tc=25.0, sombra=None):
    V, I = curva_iv(G, Tc, sombra, 800)
    P = V * I; k = int(np.argmax(P))
    voc = float(V.max()); isc = float(I.max())
    return dict(voc=voc, isc=isc, vmp=float(V[k]), imp=float(I[k]), pmax=float(P[k]), ff=float(P[k] / (voc * isc)))


if __name__ == '__main__':
    for G, T in ((1000, 25), (1000, 50), (500, 30), (200, 25)):
        p = parametros(G, T)
        print('G=%4d T=%2d  Voc=%.3f V Isc=%.3f A Vmp=%.2f V Imp=%.3f A Pmax=%.3f W FF=%.3f' % ((G, T) + tuple(p[k] for k in ('voc', 'isc', 'vmp', 'imp', 'pmax', 'ff'))))
