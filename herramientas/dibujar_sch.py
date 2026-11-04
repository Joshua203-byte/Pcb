#!/usr/bin/env python3
"""Dibuja el esquematico (.sch de EAGLE / Fusion) en PNG y PDF, sin necesitar Fusion.

Lee los simbolos de la libreria, las instancias, los trazos de cada red y sus etiquetas, y los dibuja a escala.
Uso:  python3 herramientas/dibujar_sch.py PCB_ESP32_v20.sch [salida_sin_extension] [--compacto]
  --compacto: mismo circuito y mismas conexiones, con los componentes agrupados por funcion en una hoja apaisada.
"""
import os
import sys
import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

LARGOS = {'point': 0.0, 'short': 2.54, 'middle': 5.08, 'long': 7.62}
COL_SIM, COL_RED, COL_TXT, COL_PIN = '#7a1f1f', '#1f4e9c', '#111111', '#2e6b2e'


def dibujar(ruta_sch, salida, compacto=False):
    r = ET.parse(ruta_sch).getroot()
    sch = r.find('drawing/schematic')
    syms = {s.get('name'): s for s in sch.find('libraries/library/symbols')}
    gate_sym = {}
    for ds in sch.iter('deviceset'):
        for g in ds.iter('gate'):
            gate_sym[(ds.get('name'), g.get('name'))] = g.get('symbol')
    partes = {p.get('name'): p for p in sch.findall('parts/part')}
    hoja = sch.find('sheets/sheet')
    fig, ax = plt.subplots(figsize=(30, 21) if not compacto else (30, 15.5))
    xs, ys = [], []
    red_de = {}
    for net in hoja.findall('nets/net'):
        for seg in net.findall('segment'):
            for pr in seg.findall('pinref'):
                red_de[(pr.get('part'), pr.get('pin'))] = net.get('name')
    pos = {}
    if compacto:
        def caja(nombre):
            p = partes[nombre]; sim = syms[gate_sym[(p.get('deviceset'), 'G$1')]]
            X = [float(w.get(k)) for w in sim.findall('wire') for k in ('x1', 'x2')]; Y = [float(w.get(k)) for w in sim.findall('wire') for k in ('y1', 'y2')]
            return min(X), max(X), min(Y), max(Y)
        columnas = [['U1'], ['U2', 'U5', 'U4', 'J3', 'R4'], ['J1', 'J4', 'R1', 'R2', 'R3', 'C1', 'R_SH1', 'R_SH2', 'C4', 'JP1A', 'JP1B'],
                    ['J2', 'J6', 'J7', 'J5'], ['RL%d' % k for k in range(1, 9)], ['COM%d' % k for k in range(1, 9)], ['NO%d' % k for k in range(1, 9)]]
        x = 20.0
        for col in columnas:
            y = 230.0; ancho = 0
            for nombre in col:
                x0, x1, y0, y1 = caja(nombre)
                y -= (y1 + 8.0)
                pos[nombre] = (x - x0, y)
                y += y0 - 6.0
                ancho = max(ancho, x1 - x0)
            x += ancho + 38.0

    def linea(x1, y1, x2, y2, c, lw):
        ax.plot([x1, x2], [y1, y2], color=c, lw=lw, solid_capstyle='round')
        xs.extend([x1, x2]); ys.extend([y1, y2])

    for inst in hoja.findall('instances/instance'):
        p = partes[inst.get('part')]
        sim = syms[gate_sym[(p.get('deviceset'), inst.get('gate'))]]
        ox, oy = pos.get(inst.get('part'), (float(inst.get('x')), float(inst.get('y'))))
        for w in sim.findall('wire'):
            linea(ox + float(w.get('x1')), oy + float(w.get('y1')), ox + float(w.get('x2')), oy + float(w.get('y2')), COL_SIM, 1.4)
        for t in sim.findall('text'):
            txt = (t.text or '').strip()
            if txt == '>NAME':
                ax.text(ox + float(t.get('x')), oy + float(t.get('y')), inst.get('part'), color=COL_SIM, fontsize=9, weight='bold', va='bottom')
            elif txt == '>VALUE':
                ax.text(ox + float(t.get('x')), oy + float(t.get('y')), p.get('value') or '', color=COL_TXT, fontsize=7.5, va='top')
        for pin in sim.findall('pin'):
            px, py = ox + float(pin.get('x')), oy + float(pin.get('y'))
            L = LARGOS.get(pin.get('length', 'short'), 2.54)
            rot = pin.get('rot', 'R0')
            dx, dy = {'R0': (1, 0), 'R90': (0, 1), 'R180': (-1, 0), 'R270': (0, -1)}[rot]
            linea(px, py, px + dx * L, py + dy * L, COL_PIN, 1.0)
            if compacto and (inst.get('part'), pin.get('name')) in red_de:      # trazo corto con el nombre de la red
                nom = red_de[(inst.get('part'), pin.get('name'))]
                linea(px, py, px - dx * 5.08, py - dy * 5.08, COL_RED, 1.0)
                ax.text(px - dx * 5.6, py - dy * 5.6, nom, color=COL_RED, fontsize=6.8, va='center', ha='right' if dx > 0 else 'left')
            if pin.get('visible') != 'off':
                ha = 'left' if dx > 0 else 'right' if dx < 0 else 'center'
                ax.text(px + dx * (L + 0.5), py, pin.get('name'), color=COL_PIN, fontsize=6.2, va='center', ha=ha)
    for net in ([] if compacto else hoja.findall('nets/net')):
        for seg in net.findall('segment'):
            for w in seg.findall('wire'):
                linea(float(w.get('x1')), float(w.get('y1')), float(w.get('x2')), float(w.get('y2')), COL_RED, 1.0)
            for lb in seg.findall('label'):
                x, y = float(lb.get('x')), float(lb.get('y'))
                izq = lb.get('rot', 'R0') in ('R180', 'MR0', 'R270')
                ax.text(x + (-0.6 if izq else 0.6), y, net.get('name'), color=COL_RED, fontsize=6.8, va='center', ha='right' if izq else 'left')
    for t in hoja.findall('plain/text'):
        if compacto:
            ax.text(20, 244, 'Circuito de adquisición del monitor I-V (PCB v20): ESP32 + ADS1115 + banco de 8 cargas', fontsize=20, weight='bold', color=COL_TXT)
            ax.text(20, 236, 'Cada pin lleva el nombre de su red; los pines con el mismo nombre están conectados. PV = positivo del panel, LB = lado bajo de las cargas (hacia R_SH1), '
                    'NOk = contacto normalmente abierto del relé k.', fontsize=9, color=COL_TXT)
        else:
            ax.text(float(t.get('x')), float(t.get('y')), (t.text or '').strip(), fontsize=20, weight='bold', color=COL_TXT)
    ax.set_aspect('equal'); ax.axis('off')
    ax.set_xlim(min(xs) - 25, max(xs) + 45); ax.set_ylim(min(ys) - 10, max(ys) + 14)
    fig.tight_layout()
    fig.savefig(salida + '.png', dpi=110); fig.savefig(salida + '.pdf'); plt.close(fig)
    print('Esquematico dibujado:', salida + '.png', 'y', salida + '.pdf')


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    sch = args[0] if args else 'PCB_ESP32_v20.sch'
    comp = '--compacto' in sys.argv
    dibujar(sch, args[1] if len(args) > 1 else os.path.splitext(sch)[0] + ('_esquematico_compacto' if comp else '_esquematico'), comp)
