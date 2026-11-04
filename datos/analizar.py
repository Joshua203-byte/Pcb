#!/usr/bin/env python3
"""Analisis de barridos I-V del monitor .

Lee los CSV de la microSD (barridos.csv, muestras.csv) y, opcionalmente, validacion.csv con las mediciones de referencia
(multimetro y termometro). Genera tablas y graficas listas para el documento.

Uso:
  python3 datos/analizar.py --barridos escenarios/barridos.csv [--dia dia/barridos.csv] [--muestras dia/muestras.csv]
                            [--validacion escenarios/validacion.csv] [--salida salida] [--pnom 0.82] [--rep limpio_mediodia]
validacion.csv: columnas  barrido, voc_ref_V, isc_ref_A, t_ref_C   (una fila por barrido que mediste con instrumentos)
"""
import argparse
import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modelo_panel as mp

UTC_LOCAL = -6      # El Salvador


def md(df, dec=3):
    """Tabla en Markdown sin depender de la libreria tabulate."""
    d = df.copy()
    cab = '| ' + ' | '.join(str(c) for c in d.columns) + ' |'
    sep = '|' + '|'.join('---' for _ in d.columns) + '|'
    filas = ['| ' + ' | '.join(('%.*f' % (dec, x) if isinstance(x, (float, np.floating)) else str(x)) for x in r) + ' |' for r in d.itertuples(index=False)]
    return '\n'.join([cab, sep] + filas)


def leer(ruta):
    df = pd.read_csv(ruta)
    df['mascara_n'] = df['mascara'].map(lambda s: int(str(s), 16) if isinstance(s, str) else int(s))
    if 'origen' not in df.columns:
        df['origen'] = ''
    if 'condicion' not in df.columns:
        df['condicion'] = ''
    return df


def metricas(g):
    carga = g[g.mascara_n != 0]
    abierto = g[g.mascara_n == 0]
    v, i = carga.v_V.values, carga.i_A.values
    o = np.argsort(v); v, i = v[o], i[o]
    voc = float(abierto.v_V.iloc[0]) if len(abierto) else float(v.max())
    isc = float(np.polyfit(v[:4], i[:4], 1)[1])                 # Isc: recta I(V) con los 4 puntos de menor voltaje, valor en V = 0
    p = v * i
    k = int(np.argmax(p)); vmp, imp, pmax = float(v[k]), float(i[k]), float(p[k])
    if 2 <= k < len(v) - 2:                                      # refinamiento: parabola alrededor del maximo
        c = np.polyfit(v[k - 2:k + 3], p[k - 2:k + 3], 2)
        if c[0] < 0:
            vv = -c[1] / (2 * c[0])
            if v[k - 2] <= vv <= v[k + 2]:
                vmp, pmax = float(vv), float(np.polyval(c, vv)); imp = pmax / vmp
    gg = g.irradiancia_Wm2.dropna()
    return pd.Series(dict(epoch=int(g.epoch.iloc[0]), T=float(g.temperatura_C.iloc[0]), G=float(gg.iloc[0]) if len(gg) else np.nan,
                          valido=int(g.valido.iloc[0]), condicion=g.condicion.iloc[0], origen=g.origen.iloc[0],
                          Voc=voc, Isc=isc, Vmp=vmp, Imp=imp, Pmax=pmax, FF=pmax / (voc * isc), puntos=len(g)))


def tabla(df):
    t = df.groupby('barrido').apply(metricas, include_groups=False).reset_index()
    t['hora_local'] = pd.to_datetime(t.epoch, unit='s') + pd.Timedelta(hours=UTC_LOCAL)
    return t


def marca(fig, simulado):
    return None


def modelo_para(G, T, sombra=None):
    return mp.parametros(G, T, sombra)


def fig_condiciones(df, t, ruta, sim):
    conds = [('manana', 'Mañana'), ('limpio_mediodia', 'Mediodía, panel limpio'), ('tarde', 'Tarde'), ('sucio_mediodia', 'Mediodía, panel sucio (−12 % de luz)'),
             ('sombra_parcial', 'Mediodía, sombra parcial (4 de 12 celdas al 30 %)')]
    fig, ax = plt.subplots(1, 2, figsize=(13, 5.2))
    filas = []
    for (c, nombre), col in zip(conds, plt.cm.tab10.colors):
        ids = t[(t.condicion == c) & (t.valido == 1)].barrido.values
        if not len(ids):
            continue
        b = ids[0]; g = df[df.barrido == b]; m = t[t.barrido == b].iloc[0]
        v = g.v_V.values; i = g.i_A.values; o = np.argsort(v)
        sombra = (4, 0.30) if c == 'sombra_parcial' else None
        suc = 0.88 if c == 'sucio_mediodia' else 1.0
        mod = None
        if not np.isnan(m.G):
            V, I = mp.curva_iv(m.G * suc, m['T'] + 1.5, sombra, 300)
            ax[0].plot(V, I * 1000, '--', color=col, lw=1, alpha=.7); ax[1].plot(V, V * I, '--', color=col, lw=1, alpha=.7)
            mod = modelo_para(m.G * suc, m['T'] + 1.5, sombra)
        ax[0].plot(v[o], i[o] * 1000, 'o-', ms=2.2, lw=1.2, color=col, label='%s (G=%.0f W/m², T=%.1f °C)' % (nombre, m.G, m['T']))
        ax[1].plot(v[o], (v * i)[o], 'o-', ms=2.2, lw=1.2, color=col)
        ax[1].plot(m.Vmp, m.Pmax, 'D', color=col, mec='k')
        filas.append((nombre, m.G, m['T'], m.Isc, m.Voc, m.Vmp, m.Imp, m.Pmax, m.FF) +
                     ((mod['isc'], mod['voc'], mod['vmp'], mod['imp'], mod['pmax'], mod['ff']) if mod else (np.nan,) * 6))
    ax[0].set(xlabel='Voltaje (V)', ylabel='Corriente (mA)', title='Curva I-V'); ax[1].set(xlabel='Voltaje (V)', ylabel='Potencia (W)', title='Curva P-V (◆ = punto de máxima potencia)')
    for a in ax:
        a.grid(alpha=.3)
    ax[0].legend(fontsize=7.5, loc='lower left')
    fig.suptitle('Curvas I-V y P-V en distintas condiciones (puntos = medido, línea punteada = modelo del fabricante a esa G y T)', fontsize=10)
    marca(fig, sim); fig.tight_layout(); fig.savefig(ruta, dpi=160); plt.close(fig)
    cols = ['condicion', 'G', 'T', 'Isc_med', 'Voc_med', 'Vmp_med', 'Imp_med', 'Pmax_med', 'FF_med', 'Isc_mod', 'Voc_mod', 'Vmp_mod', 'Imp_mod', 'Pmax_mod', 'FF_mod']
    tb = pd.DataFrame(filas, columns=cols)
    for k in ('Isc', 'Voc', 'Vmp', 'Imp', 'Pmax'):
        tb['d_' + k + '_%'] = (tb[k + '_med'] - tb[k + '_mod']) / tb[k + '_mod'] * 100
    return tb


def ajustes(td):
    """Efecto de la irradiancia y la temperatura con los barridos validos del dia (G >= 300 W/m2)."""
    d = td[(td.valido == 1) & (td.G >= 300)].copy()
    k = float((d.G * d.Isc).sum() / (d.G ** 2).sum())
    r2 = 1 - ((d.Isc - k * d.G) ** 2).sum() / ((d.Isc - d.Isc.mean()) ** 2).sum()
    X = np.column_stack([np.ones(len(d)), d['T'], np.log(d.G / 1000)])
    a, b, c = np.linalg.lstsq(X, d.Voc.values, rcond=None)[0]
    y = (d.Pmax / (d.G / 1000)).values                           # potencia por cada 1000 W/m2: depende de T y (menos) de G
    a2, b2, c2 = np.linalg.lstsq(X, y, rcond=None)[0]            # se ajustan T y ln(G) a la vez porque G y T suben juntas en el dia
    return d, dict(isc_1000=1000 * k, r2_isc=r2, voc_a=a, dvoc_dT=b, dvoc_pct=b / (a + b * 25) * 100, dvoc_lnG=c,
                   pn_a=a2, pn_b=b2, pn_c=c2, pn_dT_pct=b2 / (a2 + b2 * 25) * 100, n=len(d))


def fig_efectos(d, aj, ruta, sim, pn):
    fig, ax = plt.subplots(2, 2, figsize=(12, 8.2))
    G = np.linspace(d.G.min() * .9, d.G.max() * 1.05, 50)
    ax[0, 0].scatter(d.G, d.Isc * 1000, s=14, c=d['T'], cmap='coolwarm'); ax[0, 0].plot(G, aj['isc_1000'] * G, 'k-', lw=1, label='ajuste: %.1f mA a 1000 W/m²' % (aj['isc_1000'] * 1000))
    ax[0, 0].plot(G, 200 * G / 1000, 'g--', lw=1, label='dato del fabricante: 200 mA a 1000 W/m²'); ax[0, 0].set(xlabel='Irradiancia G (W/m²)', ylabel='Isc (mA)', title='Isc contra irradiancia (R² = %.4f)' % aj['r2_isc']); ax[0, 0].legend(fontsize=8)
    sc = ax[0, 1].scatter(d['T'], d.Voc, s=14, c=d.G, cmap='viridis'); plt.colorbar(sc, ax=ax[0, 1], label='G (W/m²)')
    ax[0, 1].set(xlabel='Temperatura del panel (°C)', ylabel='Voc (V)', title='Voc contra temperatura: %.1f mV/°C (%.2f %%/°C)' % (aj['dvoc_dT'] * 1000, aj['dvoc_pct']))
    sc2 = ax[1, 0].scatter(d['T'], d.Pmax / (d.G / 1000), s=14, c=d.G, cmap='viridis'); Tt = np.linspace(d['T'].min(), d['T'].max(), 20)
    ax[1, 0].plot(Tt, aj['pn_a'] + aj['pn_b'] * Tt, 'k-', lw=1, label='ajuste a G = 1000 W/m²'); ax[1, 0].legend(fontsize=8)
    ax[1, 0].set(xlabel='Temperatura del panel (°C)', ylabel='Pmax por cada 1000 W/m² (W)', title='Potencia contra temperatura: %.2f %%/°C (ajuste con T y ln G)' % aj['pn_dT_pct'])
    ax[1, 1].scatter(d.G, d.FF, s=14, c=d['T'], cmap='coolwarm'); ax[1, 1].set(xlabel='Irradiancia G (W/m²)', ylabel='Factor de forma', title='Factor de forma contra irradiancia')
    for a in ax.ravel():
        a.grid(alpha=.3)
    fig.suptitle('Efecto de la irradiancia y la temperatura (barridos válidos del día, G ≥ 300 W/m², color = T o G)', fontsize=10)
    marca(fig, sim); fig.tight_layout(); fig.savefig(ruta, dpi=160); plt.close(fig)


def repetibilidad(df, t, cond, ruta, sim):
    ids = t[(t.condicion == cond) & (t.valido == 1)].barrido.values
    if len(ids) < 3:
        return None
    s = t[t.barrido.isin(ids)]
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.8))
    for b in ids:
        g = df[df.barrido == b]; o = np.argsort(g.v_V.values)
        ax[0].plot(g.v_V.values[o], g.i_A.values[o] * 1000, lw=.8, alpha=.7); ax[1].plot(g.v_V.values[o], (g.v_V * g.i_A).values[o], lw=.8, alpha=.7)
    ax[0].set(xlabel='Voltaje (V)', ylabel='Corriente (mA)', title='%d barridos seguidos (I-V)' % len(ids)); ax[1].set(xlabel='Voltaje (V)', ylabel='Potencia (W)', title='%d barridos seguidos (P-V)' % len(ids))
    for a in ax:
        a.grid(alpha=.3)
    marca(fig, sim); fig.tight_layout(); fig.savefig(ruta, dpi=160); plt.close(fig)
    filas = []
    for k, u in (('Isc', 'A'), ('Voc', 'V'), ('Vmp', 'V'), ('Imp', 'A'), ('Pmax', 'W'), ('FF', ''), ('G', 'W/m2'), ('T', 'C')):
        x = s[k].dropna()
        filas.append((k, u, x.mean(), x.std(ddof=1), x.std(ddof=1) / x.mean() * 100, x.min(), x.max(), len(x)))
    return pd.DataFrame(filas, columns=['magnitud', 'unidad', 'media', 'desv_est', 'CV_%', 'min', 'max', 'n'])


def validacion(t, ref, ruta, sim):
    m = t.merge(ref, on='barrido')
    if m.empty:
        return None
    filas = []
    fig, ax = plt.subplots(1, 3, figsize=(13, 4.3))
    for a, (k, kr, nombre) in zip(ax, (('Voc', 'voc_ref_V', 'Voc (V)'), ('Isc', 'isc_ref_A', 'Isc (A)'), ('T', 't_ref_C', 'Temperatura (°C)'))):
        grados = (k == 'T')
        e = (m[k] - m[kr]) if grados else (m[k] - m[kr]) / m[kr] * 100
        u = '°C' if grados else '%'
        a.plot(m[kr], m[k], 'o'); lo, hi = min(m[kr].min(), m[k].min()), max(m[kr].max(), m[k].max()); a.plot([lo, hi], [lo, hi], 'k--', lw=.8)
        a.set(xlabel='Referencia (instrumento)', ylabel='Sistema', title='%s  error medio %+.2f %s' % (nombre, e.mean(), u)); a.grid(alpha=.3)
        filas.append((k, u, e.mean(), e.std(ddof=1), e.abs().max(), len(e)))
    marca(fig, sim); fig.tight_layout(); fig.savefig(ruta, dpi=160); plt.close(fig)
    return pd.DataFrame(filas, columns=['magnitud', 'unidad_del_error', 'error_medio', 'desv_est', 'error_max_abs', 'n'])


def fig_serie(ms, tb, ruta, sim, pn):
    ms = ms.copy(); ms['h'] = pd.to_datetime(ms.epoch, unit='s') + pd.Timedelta(hours=UTC_LOCAL)
    fig, ax = plt.subplots(5, 1, figsize=(12, 11), sharex=True)
    for a, (k, f, nom) in zip(ax, (('v_V', 1, 'Voltaje (V)'), ('i_A', 1000, 'Corriente (mA)'), ('p_W', 1, 'Potencia (W)'), ('temperatura_C', 1, 'Temperatura (°C)'), ('irradiancia_Wm2', 1, 'Irradiancia (W/m²)'))):
        a.plot(ms.h, ms[k] * f, lw=.6); a.set_ylabel(nom); a.grid(alpha=.3)
    if tb is not None:
        for _, r in tb[tb.valido == 0].iterrows():
            for a in ax:
                a.axvline(r.hora_local, color='r', alpha=.25, lw=.8)
    ax[0].set_title('Registro continuo de ~12 h (una medición cada 5 s con la carga en el punto de máxima potencia). Líneas rojas = barridos I-V descartados', fontsize=9)
    marca(fig, sim); fig.tight_layout(); fig.savefig(ruta, dpi=150); plt.close(fig)


def fig_pr(td, aj, pn, ruta, sim):
    d = td[(td.valido == 1) & (td.G >= 200)].copy()
    gam = aj['pn_dT_pct'] / 100
    d['PR'] = d.Pmax / (pn * (d.G / 1000) * (1 + gam * (d['T'] - 25))) * 100
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.3))
    ax[0].plot(d.hora_local, d.Pmax, 'o-', ms=3); ax[0].set(ylabel='Pmax (W)', title='Potencia máxima por barrido válido'); ax[0].grid(alpha=.3)
    ax[1].plot(d.hora_local, d.PR, 'o-', ms=3); ax[1].axhline(90, color='orange', ls='--', label='umbral de alerta 90 %'); ax[1].set(ylabel='PR corregido por T (%)', title='Performance Ratio por barrido (Pnom = %.2f W)' % pn); ax[1].legend(); ax[1].grid(alpha=.3)
    for a in ax:
        a.tick_params(axis='x', rotation=30)
    marca(fig, sim); fig.tight_layout(); fig.savefig(ruta, dpi=150); plt.close(fig)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--barridos', required=True, help='CSV con los barridos de caracterizacion / escenarios')
    ap.add_argument('--dia', help='CSV de barridos de un dia completo (para irradiancia, temperatura y PR)')
    ap.add_argument('--muestras', help='CSV de la medicion continua')
    ap.add_argument('--validacion', help='CSV con las mediciones de referencia')
    ap.add_argument('--rep', default='limpio_mediodia', help='condicion de los barridos de repeticion')
    ap.add_argument('--pnom', type=float, default=None, help='potencia nominal (W) para el PR; por defecto la del modelo a STC')
    ap.add_argument('--salida', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'salida'))
    a = ap.parse_args()
    os.makedirs(a.salida, exist_ok=True)
    df = leer(a.barridos); t = tabla(df)
    sim = False
    pn = a.pnom or mp.parametros(1000, 25)['pmax']
    t.to_csv(os.path.join(a.salida, 'tabla_barridos.csv'), index=False)
    out = ['# Resumen del análisis', '']
    tb = fig_condiciones(df, t, os.path.join(a.salida, 'fig1_iv_pv_condiciones.png'), sim)
    tb.to_csv(os.path.join(a.salida, 'tabla_condiciones_vs_fabricante.csv'), index=False)
    out += ['## Condiciones vs modelo del fabricante', md(tb), '']
    rp = repetibilidad(df, t, a.rep, os.path.join(a.salida, 'fig3_repetibilidad.png'), sim)
    if rp is not None:
        rp.to_csv(os.path.join(a.salida, 'tabla_repetibilidad.csv'), index=False)
        out += ['## Repetibilidad (%s)' % a.rep, md(rp, 4), '']
    td = tabla(leer(a.dia)) if a.dia else None
    if td is not None:
        d, aj = ajustes(td)
        fig_efectos(d, aj, os.path.join(a.salida, 'fig2_efecto_irradiancia_temperatura.png'), sim, pn)
        pr = fig_pr(td, aj, pn, os.path.join(a.salida, 'fig6_potencia_y_pr.png'), sim)
        td.to_csv(os.path.join(a.salida, 'tabla_barridos_dia.csv'), index=False)
        out += ['## Efecto de G y T (%d barridos válidos con G ≥ 300)' % aj['n'],
                '- Isc a 1000 W/m² (ajuste lineal por el origen): %.1f mA (R² = %.4f)' % (aj['isc_1000'] * 1000, aj['r2_isc']),
                '- Coeficiente de Voc con la temperatura: %.1f mV/°C (%.2f %%/°C)' % (aj['dvoc_dT'] * 1000, aj['dvoc_pct']),
                '- Variación de Voc con la irradiancia: %.3f V por unidad de ln(G)' % aj['dvoc_lnG'],
                '- Coeficiente de la potencia normalizada con la temperatura: %.2f %%/°C' % aj['pn_dT_pct'],
                '- Barridos del día: %d, válidos: %d, descartados: %d' % (len(td), int(td.valido.sum()), int((td.valido == 0).sum())),
                '- PR medio (G ≥ 200): %.1f %%' % pr.PR.mean(), '']
    if a.muestras:
        ms = pd.read_csv(a.muestras)
        fig_serie(ms, td, os.path.join(a.salida, 'fig4_serie_12h.png'), sim, pn)
        out += ['## Registro continuo', '- %d mediciones; potencia media %.3f W; máxima %.3f W' % (len(ms), ms.p_W.mean(), ms.p_W.max()), '']
    if a.validacion:
        v = validacion(t, pd.read_csv(a.validacion), os.path.join(a.salida, 'fig5_validacion.png'), sim)
        if v is not None:
            v.to_csv(os.path.join(a.salida, 'tabla_validacion.csv'), index=False)
            out += ['## Validación contra instrumentos', md(v), '']
    open(os.path.join(a.salida, 'resumen.md'), 'w', encoding='utf-8').write('\n'.join(out))
    print('\n'.join(out)); print('\nArchivos en', a.salida)


if __name__ == '__main__':
    main()
