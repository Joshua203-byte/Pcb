#!/usr/bin/env python3
"""Esquematico FUNCIONAL CABLEADO del monitor I-V (PCB v20): cada conexion esta dibujada como un cable.

Las conexiones se verifican contra las redes del archivo .sch (EAGLE/Fusion):
  - todo pin del .sch debe aparecer dibujado en su red,
  - los cables de una red deben formar un solo conjunto conectado (sin tramos sueltos),
  - ningun cable de una red debe tocar un pin ni un cable de otra red (sin cortos).
GND, 3V3 y 5V se dibujan con simbolos de alimentacion (misma red en todo el circuito) y ademas
con la hoja de distribucion de alimentacion (rieles dibujados con cable).
Uso: python3 herramientas/esquematico_cableado.py PCB_ESP32_v20.sch [salida_sin_extension]
"""
import os
import sys
import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

NEGRO = '#1b1b1b'
COLORES = {'PV': '#c0392b', 'DIV': '#e67e22', 'A0': '#8e44ad', 'REF': '#d35400', 'LB': '#16a085',
           'SCL': '#1f4e9c', 'SDA': '#2980b9', 'SCK': '#2e7d32', 'MISO': '#3d9a42', 'MOSI': '#58b05c', 'CS': '#82c785',
           'DQ': '#b8860b', 'GND': '#222222', '3V3': '#e67e22', '5V': '#c0392b'}


def color_red(n):
    if n in COLORES:
        return COLORES[n]
    if n.startswith('IN'):
        return '#795548'
    if n.startswith('NO'):
        return '#34495e'
    return NEGRO


def leer_redes(ruta):
    r = ET.parse(ruta).getroot()
    hoja = r.find('drawing/schematic/sheets/sheet')
    red = {}
    for n in hoja.findall('nets/net'):
        for pr in n.iter('pinref'):
            red[(pr.get('part'), pr.get('pin'))] = n.get('name')
    valores = {p.get('name'): (p.get('value') or '') for p in r.find('drawing/schematic').findall('parts/part')}
    return red, valores


def en_segmento(p, a, b, tol=1e-6):
    (px, py), (ax_, ay), (bx, by) = p, a, b
    if abs((bx - ax_) * (py - ay) - (by - ay) * (px - ax_)) > tol:
        return False
    return min(ax_, bx) - tol <= px <= max(ax_, bx) + tol and min(ay, by) - tol <= py <= max(ay, by) + tol


class Esq:
    def __init__(s, red, valores, tam=(26, 25)):
        s.red, s.val = red, valores
        s.cables, s.pines = [], {}
        s.fig, s.ax = plt.subplots(figsize=tam)
        s.ax.set_aspect('equal'); s.ax.axis('off')

    # ---------- primitivas ----------
    def txt(s, x, y, t, size=8, c=NEGRO, ha='left', va='center', w='normal', **k):
        s.ax.text(x, y, t, fontsize=size, color=c, ha=ha, va=va, weight=w, **k)

    def lin(s, pts, c=NEGRO, lw=1.3, ls='-'):
        s.ax.plot([p[0] for p in pts], [p[1] for p in pts], color=c, lw=lw, ls=ls, solid_capstyle='round', solid_joinstyle='round')

    def cable(s, red, pts, ls='-'):
        s.cables.append((red, list(pts)))
        s.lin(pts, color_red(red), 1.5, ls)

    def pin(s, comp, pn, pt, red):
        esperado = s.red.get((comp, pn))
        if esperado != red:
            raise SystemExit('ERROR: %s.%s esta en la red %s del .sch pero se dibujo en %s' % (comp, pn, esperado, red))
        s.pines[(comp, pn)] = (pt, red)
        s.ax.plot(*pt, 's', ms=3.2, color=color_red(red), zorder=5)

    def caja(s, x0, y0, x1, y1, titulo, sub='', tsize=11, dy=1.2, izq=True):
        s.ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=True, fc='#fbf7ea', ec='#7a1f1f', lw=1.6, zorder=1))
        s.txt(x0 if izq else (x0 + x1) / 2, y1 + dy, titulo, tsize, '#7a1f1f', 'left' if izq else 'center', 'bottom', 'bold')
        if sub:
            s.txt((x0 + x1) / 2, (y0 + y1) / 2, sub, 7.5, '#555555', 'center', 'center', style='italic')

    def bpin(s, comp, pn, x, y, lado, red, etiqueta=None):
        et = etiqueta or pn
        if lado == 'l':
            s.txt(x + 1, y, et, 7.5, '#2e6b2e', 'left')
        elif lado == 'r':
            s.txt(x - 1, y, et, 7.5, '#2e6b2e', 'right')
        elif lado == 't':
            s.txt(x, y - 1.2, et, 7.5, '#2e6b2e', 'center', 'top')
        else:
            s.txt(x, y + 1.2, et, 7.5, '#2e6b2e', 'center', 'bottom')
        s.pin(comp, pn, (x, y), red)
        return (x, y)

    def potencia(s, pt, red, abajo=True, extra=None):
        """Cable corto desde pt hasta un simbolo de alimentacion; devuelve el punto del simbolo."""
        x, y = pt
        if red == 'GND':
            y2 = y - 3 if abajo else y + 3
            s.cable(red, [pt, (x, y2)])
            for i, ancho in enumerate((3.2, 2.0, 0.8)):
                yy = y2 - i * 0.9 if abajo else y2 + i * 0.9
                s.lin([(x - ancho, yy), (x + ancho, yy)], color_red('GND'), 1.5)
        else:
            y2 = y + 3 if not abajo else y - 3
            s.cable(red, [pt, (x, y2)])
            s.lin([(x - 2.6, y2), (x + 2.6, y2)], color_red(red), 2.2)
            s.txt(x + 3.4, y2 + (0.6 if not abajo else -0.6), red, 7.5, color_red(red), 'left')
        return (x, y2)

    def res_v(s, comp, yt, yb, x, pt_pin, pb_pin, nt, nb, largo_nombre=True):
        s.lin([(x, yt), (x, yt - 4)], NEGRO, 1.4); s.lin([(x, yb), (x, yb + 4)], NEGRO, 1.4)
        s.ax.add_patch(Rectangle((x - 2, yb + 4), 4, yt - yb - 8, fill=True, fc='white', ec=NEGRO, lw=1.4, zorder=2))
        ym = (yt + yb) / 2
        s.txt(x + 3.5, ym + 1.4, comp, 9, '#7a1f1f', 'left', 'center', 'bold'); s.txt(x + 3.5, ym - 1.6, s.val.get(comp, ''), 8)
        s.pin(comp, pt_pin, (x, yt), nt); s.pin(comp, pb_pin, (x, yb), nb)

    def res_h(s, comp, xl, xr, y, pl, pr, nl, nr):
        s.lin([(xl, y), (xl + 4, y)], NEGRO, 1.4); s.lin([(xr, y), (xr - 4, y)], NEGRO, 1.4)
        s.ax.add_patch(Rectangle((xl + 4, y - 2), xr - xl - 8, 4, fill=True, fc='white', ec=NEGRO, lw=1.4, zorder=2))
        xm = (xl + xr) / 2
        s.txt(xm, y + 3.6, comp + '  ' + s.val.get(comp, ''), 8.2, '#7a1f1f', 'center', 'bottom', 'bold')
        s.pin(comp, pl, (xl, y), nl); s.pin(comp, pr, (xr, y), nr)

    def cap_v(s, comp, yt, yb, x, ptp, pbp, nt, nb, polar=False):
        ym = (yt + yb) / 2
        s.lin([(x, yt), (x, ym + 1)], NEGRO, 1.4); s.lin([(x, ym - 1), (x, yb)], NEGRO, 1.4)
        s.lin([(x - 3.5, ym + 1), (x + 3.5, ym + 1)], NEGRO, 2.2); s.lin([(x - 3.5, ym - 1), (x + 3.5, ym - 1)], NEGRO, 2.2)
        if polar:
            s.txt(x - 5.2, ym + 3, '+', 9, NEGRO, 'center')
        s.txt(x + 5, ym + 1.4, comp, 9, '#7a1f1f', 'left', 'center', 'bold'); s.txt(x + 5, ym - 1.6, s.val.get(comp, ''), 8)
        s.pin(comp, ptp, (x, yt), nt); s.pin(comp, pbp, (x, yb), nb)

    # ---------- verificacion ----------
    def verificar(s):
        fallos = []
        faltan = [k for k in s.red if k not in s.pines]
        if faltan:
            fallos.append('Pines del .sch sin dibujar: %s' % sorted(faltan))
        redes = {}
        for n, pts in s.cables:
            redes.setdefault(n, []).append(pts)
        segs = {n: [(l[i], l[i + 1]) for l in ls for i in range(len(l) - 1)] for n, ls in redes.items()}
        # cortos: pin de otra red sobre un cable, o cables de redes distintas con un extremo sobre el otro
        for (comp, pn), (pt, n) in s.pines.items():
            for m, sg in segs.items():
                if m != n and any(en_segmento(pt, a, b) for a, b in sg):
                    fallos.append('CORTO: pin %s.%s (%s) toca un cable de %s' % (comp, pn, n, m))
        for n, ls in redes.items():
            for m, ls2 in redes.items():
                if n >= m:
                    continue
                for l in ls:
                    for e in (l[0], l[-1]):
                        if any(en_segmento(e, a, b) for a, b in segs[m]):
                            fallos.append('CORTO: extremo de un cable %s sobre un cable %s en %s' % (n, m, e))
                for l in ls2:
                    for e in (l[0], l[-1]):
                        if any(en_segmento(e, a, b) for a, b in segs[n]):
                            fallos.append('CORTO: extremo de un cable %s sobre un cable %s en %s' % (m, n, e))
        # conectividad por red (redes de senal): un solo conjunto
        for n, ls in redes.items():
            if n in ('GND', '3V3', '5V'):
                continue
            padre = list(range(len(ls)))

            def raiz(i):
                while padre[i] != i:
                    padre[i] = padre[padre[i]]; i = padre[i]
                return i
            for i, a in enumerate(ls):
                for j, b in enumerate(ls):
                    if i >= j:
                        continue
                    if any(en_segmento(e, p, q) for e in (a[0], a[-1]) for p, q in zip(b, b[1:])) or \
                       any(en_segmento(e, p, q) for e in (b[0], b[-1]) for p, q in zip(a, a[1:])):
                        padre[raiz(i)] = raiz(j)
            for (comp, pn), (pt, nn) in s.pines.items():
                if nn != n:
                    continue
                if not any(en_segmento(pt, p, q) for l in ls for p, q in zip(l, l[1:])):
                    fallos.append('Pin %s.%s sin cable en la red %s' % (comp, pn, n))
            if len({raiz(i) for i in range(len(ls))}) > 1:
                fallos.append('La red %s esta dibujada en %d tramos separados' % (n, len({raiz(i) for i in range(len(ls))})))
        # pines de potencia: debe haber un cable de su red que llegue al pin
        for (comp, pn), (pt, n) in s.pines.items():
            if n in ('GND', '3V3', '5V') and not any(en_segmento(pt, p, q) for l in redes.get(n, []) for p, q in zip(l, l[1:])):
                fallos.append('Pin %s.%s sin cable de %s' % (comp, pn, n))
        return fallos

    def puntos(s):
        """Puntos de union: extremo de un cable apoyado en el interior de otro de la misma red, o 3+ cables concurrentes."""
        res = set()
        por_red = {}
        for n, pts in s.cables:
            por_red.setdefault(n, []).append(pts)
        for n, ls in por_red.items():
            if n in ('GND', '3V3', '5V'):
                continue
            cuenta = {}
            for l in ls:
                for e in (l[0], l[-1]):
                    cuenta[e] = cuenta.get(e, 0) + 1
                    for m in ls:
                        if m is l:
                            continue
                        for p, q in zip(m, m[1:]):
                            if en_segmento(e, p, q) and e not in (m[0], m[-1]):
                                res.add(e)
            for e, c in cuenta.items():
                if c >= 3:
                    res.add(e)
        for e in res:
            s.ax.plot(*e, 'o', ms=5.5, color=NEGRO, zorder=6)


def hoja_principal(red, valores):
    E = Esq(red, valores)
    t = E.txt
    # ------------------------------------------------ ESP32 (U1)
    E.caja(0, -50, 30, 166, 'U1  ESP32 DevKitC (38 pines)', dy=9)
    ys = {'DQ': 146, 'SDA': 140, 'SCL': 134, 'SCK': 120, 'MISO': 114, 'MOSI': 108, 'CS': 102}
    io = {'DQ': 'IO14', 'SDA': 'IO33', 'SCL': 'IO32', 'SCK': 'IO5', 'MISO': 'IO19', 'MOSI': 'IO18', 'CS': 'IO17'}
    for n, y in ys.items():
        E.bpin('U1', io[n], 30, y, 'r', n, io[n] + '  (' + n + ')')
    yin = {1: -6, 2: -10, 3: -14, 4: -22, 5: -26, 6: -30, 7: -38, 8: -42}
    ioin = {1: 'IO16', 2: 'IO4', 3: 'IO21', 4: 'IO22', 5: 'IO23', 6: 'IO25', 7: 'IO26', 8: 'IO27'}
    for k, y in yin.items():
        E.bpin('U1', ioin[k], 30, y, 'r', 'IN%d' % k, '%s  (IN%d)' % (ioin[k], k))
    p = E.bpin('U1', '3V3', 8, 166, 't', '3V3'); E.potencia(p, '3V3', abajo=False)
    p = E.bpin('U1', '5V', 22, 166, 't', '5V'); E.potencia(p, '5V', abajo=False)
    for k in (1, 2, 3):
        E.pin('U1', 'GND@%d' % k, (15, -50), 'GND')
    t(15, -48.2, 'GND (×3)', 7.5, '#2e6b2e', 'center', 'bottom'); E.potencia((15, -50), 'GND', abajo=True)

    # ------------------------------------------------ I2C: ADS1115 (U2) y RTC DS3231 (U5)
    E.caja(80, 84, 102, 152, 'U2  ADS1115', 'ADC 16 bit\nI²C 0x48\n(ADDR a GND)')
    E.bpin('U2', 'SDA', 80, 143, 'l', 'SDA'); E.bpin('U2', 'SCL', 80, 138, 'l', 'SCL')
    E.bpin('U2', 'ADDR', 80, 102, 'l', 'GND'); E.bpin('U2', 'AIN3', 80, 96, 'l', 'GND')
    E.bpin('U2', 'AIN2', 102, 144, 'r', 'LB', 'AIN2'); E.bpin('U2', 'AIN1', 102, 116, 'r', 'REF', 'AIN1')
    E.bpin('U2', 'AIN0', 102, 88, 'r', 'A0', 'AIN0')
    p = E.bpin('U2', 'VDD', 97, 152, 't', '3V3'); E.potencia(p, '3V3', abajo=False)
    p = E.bpin('U2', 'GND', 91, 84, 'b', 'GND'); E.potencia(p, 'GND', abajo=True)
    E.cable('GND', [(80, 102), (75, 102), (75, 96), (80, 96)]); E.potencia((75, 96), 'GND', abajo=True)
    t(73, 99, 'ADDR y AIN3\na GND', 7, '#555555', 'right')

    E.caja(80, 46, 102, 62, 'U5  RTC DS3231', '+ pila CR2032')
    E.bpin('U5', 'SDA', 80, 58, 'l', 'SDA'); E.bpin('U5', 'SCL', 80, 54, 'l', 'SCL')
    p = E.bpin('U5', 'VCC', 97, 62, 't', '3V3'); E.bpin('U5', 'GND', 91, 46, 'b', 'GND'); E.potencia((91, 46), 'GND', abajo=True)
    # puente JP1 (alambre) entre el pad del RTC y 3V3
    E.cable('3V3', [(97, 62), (97, 66), (106, 66)])
    E.pin('JP1B', '1', (106, 66), '3V3'); E.pin('JP1A', '1', (114, 66), '3V3')
    E.cable('3V3', [(106, 66), (114, 66)], ls=(0, (3, 2)))
    E.cable('3V3', [(114, 66), (114, 69)]); E.lin([(111.4, 69), (116.6, 69)], color_red('3V3'), 2.2); t(117.4, 69.6, '3V3', 7.5, color_red('3V3'))
    t(110, 63.4, 'JP1A–JP1B (puente de alambre)', 7, '#555555', 'center', 'top')
    # SPI: microSD (U4)
    E.caja(80, 16, 102, 32, 'U4  módulo microSD', 'SPI')
    for n, y in (('SCK', 30), ('MISO', 26), ('MOSI', 22), ('CS', 18)):
        E.bpin('U4', n, 80, y, 'l', n)
    p = E.bpin('U4', 'VCC', 97, 32, 't', '5V'); E.potencia(p, '5V', abajo=False)
    p = E.bpin('U4', 'GND', 91, 16, 'b', 'GND'); E.potencia(p, 'GND', abajo=True)

    # troncales I2C / SPI / DQ
    E.cable('SDA', [(30, 140), (68, 140), (68, 143), (80, 143)]); E.cable('SDA', [(68, 143), (68, 58), (80, 58)])
    E.cable('SCL', [(30, 134), (64, 134), (64, 138), (80, 138)]); E.cable('SCL', [(64, 138), (64, 54), (80, 54)])
    for n, xt, y0, y1 in (('SCK', 60, 120, 30), ('MISO', 56, 114, 26), ('MOSI', 52, 108, 22), ('CS', 48, 102, 18)):
        E.cable(n, [(30, y0), (xt, y0), (xt, y1), (80, y1)])
    # DQ sube al carril superior hasta el DS18B20
    E.cable('DQ', [(30, 146), (44, 146), (44, 164), (122, 164)])
    t(33, 147.3, 'DQ', 7.5, color_red('DQ'), 'left', 'bottom'); t(33, 141.3, 'SDA', 7.5, color_red('SDA'), 'left', 'bottom')
    t(33, 135.3, 'SCL', 7.5, color_red('SCL'), 'left', 'bottom')
    for n, y in (('SCK', 120), ('MISO', 114), ('MOSI', 108), ('CS', 102)):
        t(33, y + 1.3, n, 7.5, color_red(n), 'left', 'bottom')
    t(66, 148.5, 'I²C: SDA/SCL compartidos entre ADS1115 y RTC', 7.5, '#1f4e9c', 'center')

    # ------------------------------------------------ DS18B20 (J3) + R4
    E.caja(122, 158, 134, 170, 'J3', 'DS18B20', 9)
    E.bpin('J3', 'DQ', 122, 164, 'l', 'DQ'); p = E.bpin('J3', 'VDD', 130, 170, 't', '3V3'); E.potencia(p, '3V3', abajo=False)
    p = E.bpin('J3', 'GND', 128, 158, 'b', 'GND'); E.potencia(p, 'GND', abajo=True)
    E.res_v('R4', 180, 164, 112, '1', '2', '3V3', 'DQ')
    E.cable('DQ', [(112, 164), (112, 164)]) if False else None
    E.cable('3V3', [(112, 180), (112, 183)]); E.lin([(109.4, 183), (114.6, 183)], color_red('3V3'), 2.2); t(115.4, 183.6, '3V3', 7.5, color_red('3V3'))
    t(150, 166, 'sensor de temperatura\n(sonda sobre el panel)', 7.5, '#555555', 'left')

    # ------------------------------------------------ cadena de acondicionamiento
    # LB: AIN2 -> bus LB (derecha) ; R_SH1 al final del bus
    E.cable('LB', [(102, 144), (244, 144), (244, 16)])
    t(160, 145.4, 'LB  (lado bajo de las cargas) → AIN2: V sobre R_SH1', 7.5, color_red('LB'), 'center', 'bottom')
    # REF: AIN1 -> J4 y R_SH2
    E.cable('REF', [(102, 116), (150, 116)]); E.cable('REF', [(130, 116), (130, 112)])
    E.res_v('R_SH2', 112, 100, 130, '1', '2', 'REF', 'GND'); E.potencia((130, 100), 'GND', abajo=True)
    E.caja(150, 108, 162, 124, 'J4  celda ref.', '', 9)
    E.bpin('J4', '1', 150, 116, 'l', 'REF', '1  +'); p = E.bpin('J4', '2', 156, 108, 'b', 'GND', '2  –'); E.potencia(p, 'GND', abajo=True)
    t(116, 117.4, 'REF → AIN1 (V sobre R_SH2 = I celda)', 7.5, color_red('REF'), 'center', 'bottom')
    # A0: AIN0 -> C1 y R3
    E.cable('A0', [(102, 88), (150, 88)]); E.cable('A0', [(150, 88), (154, 88)]); E.cable('A0', [(150, 88), (150, 84)])
    E.cap_v('C1', 84, 74, 150, '1', '2', 'A0', 'GND'); E.potencia((150, 74), 'GND', abajo=True)
    E.res_h('R3', 154, 170, 88, '2', '1', 'A0', 'DIV')
    E.cable('DIV', [(170, 88), (174, 88)]); E.cable('DIV', [(174, 92), (174, 88), (174, 84)])
    E.res_v('R1', 108, 92, 174, '1', '2', 'PV', 'DIV'); E.res_v('R2', 84, 68, 174, '1', '2', 'DIV', 'GND')
    E.potencia((174, 68), 'GND', abajo=True)
    t(130, 89.4, 'A0 → AIN0', 7.5, color_red('A0'), 'center', 'bottom')
    t(177, 90.6, 'DIV', 7.5, color_red('DIV'), 'left', 'bottom')
    t(190, 82, 'Divisor R1/R2 (÷4.3)\n+ filtro RC (R3, C1)', 7.5, '#555555', 'left', va='top') if False else None
    # PV: panel (J1) y bus de comunes
    E.cable('PV', [(174, 108), (174, 112), (186, 112), (186, 23)]); E.cable('PV', [(186, 124), (186, 112)])
    E.caja(180, 124, 192, 136, 'J1  panel', '', 9)
    E.bpin('J1', '1', 186, 124, 'b', 'PV', '1  +'); E.pin('J1', '2', (180, 130), 'GND'); t(181, 130, '2  –', 7.5, '#2e6b2e', 'left')
    E.cable('GND', [(180, 130), (176, 130)]); E.potencia((176, 130), 'GND', abajo=True)
    t(184, 113.4, 'PV  (+ panel)', 7.5, color_red('PV'), 'right', 'bottom')

    # banco de cargas: filas
    t(215, 108, 'BANCO DE CARGAS', 10, '#7a1f1f', 'center', 'bottom', 'bold')
    t(215, 105.2, 'COMk → contacto del relé → NOk → RLk → LB', 7.5, '#555555', 'center', 'bottom')
    for k in range(1, 9):
        y = 100 - 11 * (k - 1)
        cp, np_ = 'COM%d' % k, 'NO%d' % k
        E.cable('PV', [(186, y), (192, y)])
        E.ax.add_patch(Rectangle((190.8, y - 1.4), 2.8, 2.8, fc='white', ec=color_red('PV'), lw=1.4, zorder=4))
        E.pin(cp, '1', (192, y), 'PV'); t(192.2, y + 2.2, cp, 6.8, '#7a1f1f', 'left', 'bottom')
        E.cable('PV', [(192, y), (198, y)]); E.ax.plot(198, y, 'o', ms=4, color=NEGRO, zorder=6)
        E.lin([(198, y), (211, y + 4)], NEGRO, 1.6); E.ax.plot(212, y, 'o', ms=4, color=NEGRO, zorder=6)
        E.cable(np_, [(212, y), (218, y)]); E.cable(np_, [(218, y), (222, y)])
        E.ax.add_patch(Rectangle((216.8, y - 1.4), 2.8, 2.8, fc='white', ec=color_red(np_), lw=1.4, zorder=4))
        E.pin(np_, '1', (218, y), np_); t(218.4, y + 2.2, np_, 6.8, '#7a1f1f', 'left', 'bottom')
        E.res_h('RL%d' % k, 222, 238, y, '1', '2', np_, 'LB')
        E.cable('LB', [(238, y), (244, y)])
        t(205, y - 4.6, 'K%d' % k, 7.2, '#555555', 'center', 'center')
    E.ax.add_patch(Rectangle((195, 17), 21, 90, fill=False, ec='#999999', lw=1.0, ls='--', zorder=0))
    t(205.5, 14.5, 'módulo de 8 relés', 7.5, '#777777', 'center', 'top')
    # R_SH1
    E.res_v('R_SH1', 16, 0, 244, '2', '1', 'LB', 'GND'); E.potencia((244, 0), 'GND', abajo=True)

    # ------------------------------------------------ cabeceras de relés y alimentación de relés
    for nombre, pines, y0, y1 in (('J2', (1, 2, 3), -3, -17), ('J6', (4, 5, 6), -19, -33), ('J7', (7, 8), -35, -45)):
        E.caja(44, y1, 58, y0, nombre, '', 9)
        for k in pines:
            E.cable('IN%d' % k, [(30, yin[k]), (44, yin[k])]); E.bpin(nombre, 'IN%d' % k, 44, yin[k], 'l', 'IN%d' % k, 'IN%d' % k)
        t(61, (y0 + y1) / 2, '→ módulo de relés', 7.5, '#555555', 'left')
    E.caja(44, -66, 56, -48, 'J5  entrada 5 V', '', 9)
    E.cable('5V', [(56, -52), (66, -52)]); E.cable('5V', [(66, -52), (66, -48)])
    E.pin('J5', '5V', (56, -52), '5V'); t(55, -52, '5V', 7.5, '#2e6b2e', 'right')
    E.lin([(63.4, -48), (68.6, -48)], color_red('5V'), 2.2); t(69.4, -47.4, '5V', 7.5, color_red('5V'))
    E.cable('GND', [(56, -62), (66, -62)]); E.pin('J5', 'GND', (56, -62), 'GND'); t(55, -62, 'GND', 7.5, '#2e6b2e', 'right')
    E.cap_v('C4', -52, -62, 66, '+', '-', '5V', 'GND', polar=True); E.potencia((66, -62), 'GND', abajo=True)

    # ------------------------------------------------ titulo y notas
    t(0, 200, 'Monitor I-V de panel solar — esquemático funcional cableado (PCB v20)', 20, NEGRO, 'left', 'bottom', 'bold')
    t(0, 197, 'Panel 6 V / 200 mA · ESP32 + ADS1115 (16 bit) + banco de 8 cargas por relés · RTC DS3231 + microSD + DS18B20 + celda de referencia', 9.5, '#444444', 'left', 'top')
    leyenda = ('Cada línea de color es un cable (misma red = mismo color); un punto negro es una unión; las líneas que se cruzan sin punto NO se tocan.\n'
               'Símbolos GND / 3V3 / 5V = la misma red en todo el circuito. Las conexiones están verificadas contra las redes de PCB_ESP32_v20.sch.')
    t(0, 192.5, leyenda, 8.5, '#444444', 'left', 'top')
    t(206, -20, 'Medición de V: PV → R1/R2 (÷4.3) → R3/C1 → AIN0\nMedición de I: carga activa → LB → R_SH1 (1 Ω) → GND; V(LB) se lee en AIN2 y AIN3 (GND)\n'
      'Irradiancia: celda de referencia en cortocircuito sobre R_SH2 (1 Ω) → AIN1\nTemperatura: DS18B20 (1-Wire) con pull-up R4 4.7 kΩ a 3V3', 8.2, '#333333', 'left', 'top')

    E.puntos()
    E.ax.set_xlim(-8, 262); E.ax.set_ylim(-72, 206)
    E.fig.tight_layout()
    return E


def hoja_alimentacion(red, valores):
    """Distribucion de GND / 3V3 / 5V con rieles dibujados con cable. Se genera desde las redes del .sch."""
    E = Esq(red, valores, (24, 11))
    redes = {'5V': 24, '3V3': 12, 'GND': 0}
    por_red = {n: sorted([k for k, v in red.items() if v == n]) for n in redes}
    ancho = max(len(v) for v in por_red.values()) * 9.5
    for n, y in redes.items():
        E.cable(n, [(0, y), (ancho, y)])
        E.txt(-1, y, n, 14, color_red(n), 'right', 'center', 'bold')
        for i, (comp, pn) in enumerate(por_red[n]):
            x = 4 + i * 9.5
            ycaja = y + 7 if n != 'GND' else y - 7
            E.cable(n, [(x, y), (x, ycaja)])
            E.ax.plot(x, y, 'o', ms=5, color=NEGRO, zorder=6)
            E.pin(comp, pn, (x, ycaja), n)
            E.txt(x, ycaja + (1.3 if n != 'GND' else -1.3), '%s\n%s' % (comp, pn), 7, '#222222', 'center', 'bottom' if n != 'GND' else 'top')
    # los rieles 5V y 3V3 salen de los puertos de U1 (3V3 regulado por la placa ESP32 desde 5V)
    E.txt(ancho / 2, 31.5, 'Distribución de alimentación — cada pin conectado al riel de su red (5 V desde USB o J5; 3V3 del regulador del ESP32)', 13, NEGRO, 'center', 'bottom', 'bold')
    E.ax.set_xlim(-12, ancho + 4); E.ax.set_ylim(-14, 34)
    E.fig.tight_layout()
    return E


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    ruta = args[0] if args else 'PCB_ESP32_v20.sch'
    base = args[1] if len(args) > 1 else os.path.splitext(ruta)[0] + '_esquematico_cableado'
    red, valores = leer_redes(ruta)
    malos = 0
    for nombre, f in (('', hoja_principal), ('_alimentacion', hoja_alimentacion)):
        E = f(red, valores)
        fallos = E.verificar()
        if nombre == '_alimentacion':
            fallos = [x for x in fallos if not x.startswith('Pines del .sch sin dibujar')]
        for x in fallos:
            print('  FALLO:', x)
        malos += len(fallos)
        E.fig.savefig(base + nombre + '.png', dpi=100); E.fig.savefig(base + nombre + '.pdf'); plt.close(E.fig)
        print('Dibujado:', base + nombre + '.png', '|', len(E.pines), 'pines,', len(E.cables), 'cables,', 'verificación:', 'OK' if not fallos else '%d fallos' % len(fallos))
    sys.exit(1 if malos else 0)


if __name__ == '__main__':
    main()
