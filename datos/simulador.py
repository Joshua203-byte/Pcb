#!/usr/bin/env python3
"""Simulador de datos del monitor I-V.

Genera archivos con el mismo formato que la microSD del firmware (barridos.csv y muestras.csv) para el script de
analisis y el documento. Reproduce la cadena de medicion real: banco de relés con las combinaciones
del firmware, derivacion R_SH1, divisor R1/R2, cuantizacion y ruido del ADS1115, autocero, DS18B20 y celda de referencia,
ademas del punto de control que valida el barrido (nubes).

Para usar datos medidos basta apuntar datos/analizar.py a la carpeta con los CSV reales.
Uso:  python3 datos/simulador.py
"""
import csv
import os
import re
import numpy as np
import modelo_panel as mp

AQUI = os.path.dirname(os.path.abspath(__file__))
FW = os.path.join(AQUI, '..', 'firmware', 'monitor_iv', 'monitor_iv.ino')
SALIDA = os.path.join(AQUI, 'datos_avance3')
DIA = '2026-11-03'
EPOCH_0 = int(np.datetime64(DIA + 'T00:00:00', 's').astype('int64')) + 6 * 3600     # 00:00 hora local (UTC-6) -> UTC
RL_NOM = np.array([2.2, 4.7, 10, 22, 47, 100, 220, 470])
SEMILLA = 20261103

# --------------------------------------------------------------------- cadena de medicion (valores "reales" distintos de los nominales)
rng = np.random.default_rng(SEMILLA)
RL_REAL = RL_NOM * (1 + rng.uniform(-0.05, 0.05, 8))        # resistencias de carga con tolerancia de 5 %
R_SH1, R_SH2 = 1.0 * 1.008, 1.0 * 0.996                     # derivaciones reales (el firmware supone 1.000)
R1, R2 = 33000 * 1.006, 10000 * 0.996                       # divisor real (el firmware supone 33k / 10k)
R_CONTACTO = 0.12                                           # relé + cableado
OFFSET_SHUNT = 250e-6                                       # offset observado en A2-A3 (el autocero lo corrige)
LSB_V, LSB_I = 0.125e-3, 15.625e-6                          # ADS1115: +-4.096 V y +-0.512 V
RUIDO_LSB, MUESTRAS = 0.8, 8
CAL_DIV, ISC_REF_FW = (33000 + 10000) / 10000, 0.200
REF_GANANCIA = 0.985                                        # la celda de referencia no es identica al panel principal

mascaras = [int(x, 16) for x in re.search(r'// 164 puntos\s*const uint8_t MASCARAS\[\] = \{(.*?)\};', open(FW).read(), re.S).group(1).replace('\n', '').split(',')]


def r_carga(mask):
    g = sum(1.0 / RL_REAL[k] for k in range(8) if (mask >> k) & 1)
    return np.inf if g == 0 else 1.0 / g


def adc(v, lsb, g=None):
    """Promedio recortado de 8 lecturas cuantizadas con ruido (como el firmware)."""
    v = np.atleast_1d(np.asarray(v, dtype=float))
    lec = np.round((v[..., None] + g.normal(0, RUIDO_LSB * lsb, v.shape + (MUESTRAS,))) / lsb) * lsb
    lec.sort(axis=-1)
    return lec[..., 1:-1].mean(axis=-1)


# --------------------------------------------------------------------- clima del dia (1 s de resolucion)
T_S = np.arange(6 * 3600, 18 * 3600 + 1)
H = T_S / 3600.0
G_CIELO = 1000.0 * np.clip(np.sin(np.pi * (H - 6) / 12), 0, None) ** 1.15
T_AMB = 24.0 + 9.0 * np.sin(np.pi * (H - 7) / 12)
NUBES = [(8 * 3600 + 40 * 60, 180, 0.45), (10 * 3600 + 15 * 60 + 20, 90, 0.50), (11 * 3600 + 50 * 60, 400, 0.30),
         (13 * 3600 + 45 * 60, 200, 0.60), (15 * 3600 + 27 * 60, 120, 0.55), (16 * 3600 + 20 * 60, 500, 0.25)]


def factor_nubes(t):
    f = np.ones_like(t, dtype=float)
    for (t0, dur, prof) in NUBES:
        x = np.clip((t - t0) / dur, 0, 1)
        f *= 1 - prof * np.sin(np.pi * x) ** 2
    return f


G_DIA = G_CIELO * factor_nubes(T_S)
T_CELDA = np.empty_like(G_DIA)                              # temperatura de celda con inercia termica (tau = 120 s)
T_CELDA[0] = T_AMB[0]
for k in range(1, len(T_S)):
    objetivo = T_AMB[k] + 0.0312 * G_DIA[k]
    T_CELDA[k] = T_CELDA[k - 1] + (objetivo - T_CELDA[k - 1]) / 120.0


def clima(t):
    return float(np.interp(t, T_S, G_DIA)), float(np.interp(t, T_S, T_CELDA))


# --------------------------------------------------------------------- una medicion de la cadena completa
def medir(mask, t, g, suciedad=1.0, sombra=None):
    """Devuelve (v_medido, i_medida) como las calcularia el firmware para la combinacion `mask` en el instante t."""
    G, Tc = clima(t)
    G_panel = G * suciedad
    rl = r_carga(mask)
    rama = rl + R_SH1 + R_CONTACTO
    r_ef = 1.0 / (1.0 / rama + 1.0 / (R1 + R2))
    I_pan, V = mp.punto_operacion(r_ef, G_panel, Tc, sombra)
    i_carga = V / rama if np.isfinite(rama) else 0.0
    v_a0 = float(V) / ((R1 + R2) / R2)
    v_med = float(adc(v_a0, LSB_V, g)[0]) * CAL_DIV
    return v_med, i_carga, Tc, G


def lectura_shunt(i_carga, g):
    return float(adc(i_carga * R_SH1 + OFFSET_SHUNT, LSB_I, g)[0])


def ds18b20(Tc, g):
    t = Tc - 1.5 + 0.2 + g.normal(0, 0.05)                  # sensor atras del panel + sesgo de +0.2 C
    return round(t / 0.25) * 0.25                           # resolucion de 10 bits


def celda_ref(G, Tc, T_med, g):
    i_ref = ISC_REF_FW * REF_GANANCIA * (G / 1000.0) * (1 + mp.ALFA_ISC * (Tc - 25.0))
    v = float(adc(i_ref * R_SH2, LSB_I, g)[0])
    if v < 0.010:
        return None
    return 1000.0 * (v / 1.0) / (ISC_REF_FW * (1 + mp.ALFA_ISC * (T_med - 25.0)))


# --------------------------------------------------------------------- barrido completo (como el firmware)
def barrido(t0, id_b, g, suciedad=1.0, sombra=None, espera=0.2, paso_t=0.33):
    off_est = lectura_shunt(0.0, g)                          # autocero con los reles abiertos
    _, _, Tc0, G0 = medir(0, t0, g)
    T_ini = ds18b20(Tc0, g)
    g_ini = celda_ref(G0, Tc0, T_ini, g)
    filas, t = [], t0 + 0.3
    for mask in mascaras:
        t += espera if mask is mascaras[0] else paso_t
        v, ic, Tc, G = medir(mask, t, g, suciedad, sombra)
        i = max((lectura_shunt(ic, g) - off_est) / 1.0, 0.0) + v / 43000.0
        filas.append((mask, v, i))
    t += paso_t
    vc, icg, Tc1, G1 = medir(mascaras[0], t, g, suciedad, sombra)
    ic = max((lectura_shunt(icg, g) - off_est) / 1.0, 0.0) + vc / 43000.0
    i0 = filas[0][2]
    variacion = abs(ic - i0) / i0 if i0 > 0.005 else 0.0
    T_fin = ds18b20(Tc1, g)
    g_fin = celda_ref(G1, Tc1, T_fin, g)
    valido = variacion <= 0.05
    if g_ini and g_fin and g_ini > 50 and abs(g_fin - g_ini) / g_ini > 0.05:
        valido = False
    T_b = 0.5 * (T_ini + T_fin)
    return dict(t0=t0, id=id_b, filas=filas, T=T_b, G=g_fin, valido=valido, variacion=variacion, t_fin=t)


def escribir_barridos(ruta, barridos, condiciones):
    nuevo = not os.path.exists(ruta)
    with open(ruta, 'a', newline='') as f:
        w = csv.writer(f)
        if nuevo:
            w.writerow(['epoch', 'barrido', 'paso', 'mascara', 'v_V', 'i_A', 'p_W', 'temperatura_C', 'irradiancia_Wm2', 'valido', 'condicion'])
        for b, cond in zip(barridos, condiciones):
            ep = EPOCH_0 + int(b['t0'])
            for k, (m, v, i) in enumerate(b['filas'], 1):
                w.writerow([ep, b['id'], k, '0x%02X' % m, '%.4f' % v, '%.5f' % i, '%.5f' % (v * i), '%.1f' % b['T'],
                            '' if b['G'] is None else '%.1f' % b['G'], int(b['valido']), cond])


def main():
    os.makedirs(os.path.join(SALIDA, 'dia_' + DIA), exist_ok=True)
    os.makedirs(os.path.join(SALIDA, 'escenarios'), exist_ok=True)
    g = np.random.default_rng(SEMILLA + 1)
    # ---------------- dia completo de 12 h: barridos cada 10 min + medicion continua cada 5 s
    ruta_b = os.path.join(SALIDA, 'dia_' + DIA, 'barridos.csv'); ruta_m = os.path.join(SALIDA, 'dia_' + DIA, 'muestras.csv')
    for r in (ruta_b, ruta_m):
        if os.path.exists(r):
            os.remove(r)
    inicios = [6 * 3600 + 5 * 60 + 600 * k for k in range(72)]
    barridos, mask_mon = [], 0x30
    muestras = []
    prox_b = iter(inicios); sig = next(prox_b); idb = 0
    t = 6 * 3600
    while t < 18 * 3600:
        if sig is not None and t >= sig:                      # los barridos tienen prioridad
            idb += 1
            b = barrido(sig, idb, g); barridos.append(b)
            if b['valido']:
                pm = max(((v * i, m) for m, v, i in b['filas'] if m != 0))[1]
                mask_mon = pm
            t = int(np.ceil(b['t_fin'])); sig = next(prox_b, None)
            continue
        v, ic, Tc, G = medir(mask_mon, t, g)
        off_est = lectura_shunt(0.0, g)
        i = max((lectura_shunt(ic, g) - off_est), 0.0) + v / 43000.0
        T_med = ds18b20(Tc, g)
        Gm = celda_ref(G, Tc, T_med, g)
        muestras.append((EPOCH_0 + t, v, i, T_med, Gm, mask_mon))
        t += 5
    escribir_barridos(ruta_b, barridos, ['dia'] * len(barridos))
    with open(ruta_m, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['epoch', 'iso', 'mascara', 'v_V', 'i_A', 'p_W', 'temperatura_C', 'irradiancia_Wm2', 'valido'])
        for ep, v, i, T_med, Gm, m in muestras:
            iso = np.datetime_as_string(np.datetime64(ep, 's'), unit='s') + 'Z'
            w.writerow([ep, iso, '0x%02X' % m, '%.4f' % v, '%.5f' % i, '%.5f' % (v * i), '%.1f' % T_med, '' if Gm is None else '%.1f' % Gm, 1])
    invalidos = [b['id'] for b in barridos if not b['valido']]
    print('dia: %d barridos (%d invalidos por nubes: %s), %d muestras' % (len(barridos), len(invalidos), invalidos, len(muestras)))

    # ---------------- escenarios para la caracterizacion: cielo estable al mediodia (sin nubes)
    global G_DIA
    G_DIA = G_CIELO.copy()
    ruta = os.path.join(SALIDA, 'escenarios', 'barridos.csv')
    if os.path.exists(ruta):
        os.remove(ruta)
    esc, cond, ref, idb = [], [], [], 1000
    def tiempo(h, m):
        return h * 3600 + m * 60
    for k in range(10):                                       # repetibilidad: 10 barridos seguidos, panel limpio
        idb += 1; esc.append(barrido(tiempo(12, 0) + 75 * k, idb, g)); cond.append('limpio_mediodia')
    for k in range(3):
        idb += 1; esc.append(barrido(tiempo(12, 30) + 75 * k, idb, g, suciedad=0.88)); cond.append('sucio_mediodia')
    for k in range(3):
        idb += 1; esc.append(barrido(tiempo(12, 45) + 75 * k, idb, g, sombra=(4, 0.30))); cond.append('sombra_parcial')
    for (h, m, etiqueta) in ((8, 30, 'manana'), (15, 30, 'tarde')):
        for k in range(3):
            idb += 1; esc.append(barrido(tiempo(h, m) + 75 * k, idb, g)); cond.append(etiqueta)
    escribir_barridos(ruta, esc, cond)
    # referencias "del multimetro y del termometro" (simuladas) para los 10 barridos de repeticion
    with open(os.path.join(SALIDA, 'escenarios', 'validacion.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['barrido', 'voc_ref_V', 'isc_ref_A', 't_ref_C'])
        for b, c in zip(esc, cond):
            if c != 'limpio_mediodia':
                continue
            G, Tc = clima(b['t0'] + 30)
            I, V = mp.punto_operacion(np.array([0.0001]), G, Tc)       # Isc con el amperimetro (burden ~0.1 ohm)
            voc = float(mp.v_panel(0.0, G, Tc))
            w.writerow([b['id'], '%.2f' % (voc * (1 + g.normal(0, 0.002))), '%.3f' % (float(I[0]) * (1 + g.normal(0, 0.004))),
                        '%.1f' % (Tc - 1.0 + g.normal(0, 0.3))])
    print('escenarios:', len(esc), 'barridos')


if __name__ == '__main__':
    main()
