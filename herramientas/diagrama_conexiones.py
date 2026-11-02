"""Diagrama de componentes y conexiones de la PCB v20 (estilo diagrama de referencia).

Por defecto se dibuja como se ve la placa ya planchada: cara de cobre, es decir,
ESPEJADA izquierda-derecha respecto a Fusion. Los componentes van del otro lado
(cara de la fibra) y se muestran "en transparencia".

Uso (desde la carpeta del proyecto):
    python3 herramientas/diagrama_conexiones.py [salida.png] [--sin-espejo]

--sin-espejo dibuja la vista de Fusion (lado de componentes).
Lee PCB_ESP32_v20.brd, asi que siempre coincide con la placa.
"""
import os
import sys
import functools
import xml.etree.ElementTree as ET

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt                                   # noqa: E402
from matplotlib.patches import PathPatch, Polygon as MPoly, FancyBboxPatch, Circle  # noqa: E402
from matplotlib.path import Path                                  # noqa: E402
from matplotlib.textpath import TextPath                          # noqa: E402
from matplotlib.font_manager import FontProperties                # noqa: E402
from matplotlib.transforms import Affine2D                        # noqa: E402
from shapely import affinity                                      # noqa: E402
from shapely.geometry import box, LineString, Polygon             # noqa: E402
from shapely.geometry.polygon import orient                       # noqa: E402
from shapely.ops import unary_union, nearest_points               # noqa: E402
from shapely.prepared import prep                                 # noqa: E402

import verificar_brd as V                                         # noqa: E402
import pcb_drc as R                                               # noqa: E402
import diseno_v19 as D                                            # noqa: E402
from pcb_geo import Parte, HUELLAS, rot_xy                        # noqa: E402
from generar_v19 import contornos_docu                            # noqa: E402

BRD = os.path.join(RAIZ, 'PCB_ESP32_v20.brd')

# ------------------------------------------------------------------ estilo
PX = 20                      # pixeles por mm
FONDO = '#0b1d1a'
PLACA = '#12322b'
AZUL = '#3f94e8'
ORO = '#e6d8a2'
BLANCO = '#eef4f1'
GRIS = '#a9bdb8'
COL = dict(R='#7be08a', C='#f4a640', J='#b79bf2', U='#7fd3f0', K='#f2d25a', JP='#ff9d3d')
FP = FontProperties(family='DejaVu Sans')
FPB = FontProperties(family='DejaVu Sans', weight='bold')
BIG = ('U1', 'U2', 'U4', 'U5')

# nombre -> (valor mostrado, funcion)
INFO = {
    'U1': ('ESP32 DevKit', 'microcontrolador · USB hacia abajo'),
    'U2': ('ADS1115', 'ADC 16 bits · módulo de 10 pines'),
    'U4': ('microSD', 'módulo SPI de 6 pines'),
    'U5': ('RTC DS3231', 'reloj · módulo de 6 pines'),
    'J1': ('Panel solar', 'bornera: + (cuadrado) y −'),
    'J4': ('Celda de referencia', 'bornera: + (cuadrado) y −'),
    'J2': ('Relés IN1–IN3', 'cables dupont al módulo de relés'),
    'J6': ('Relés IN4–IN6', 'cables dupont al módulo de relés'),
    'J7': ('Relés IN7–IN8', 'cables dupont al módulo de relés'),
    'J3': ('DS18B20', 'pines de arriba abajo: VDD · DQ · GND'),
    'J5': ('Relés 5V / GND', 'alimentación del módulo de relés'),
    'R1': ('33 kΩ', 'divisor del panel'),
    'R2': ('10 kΩ', 'divisor del panel'),
    'R3': ('1 kΩ', 'filtro RC'),
    'R4': ('4.7 kΩ', 'pull-up del DS18B20'),
    'R_SH1': ('1 Ω 1 W', 'shunt de corriente del panel'),
    'R_SH2': ('1 Ω', 'shunt de la celda de referencia'),
    'C1': ('0.1 µF', 'filtro RC'),
    'C4': ('10 µF 16 V', 'filtro 5V · el + va al pad cuadrado'),
}
VALOR_RL = ['2.2', '4.7', '10', '22', '47', '100', '220', '470']
ADS = ['VDD', 'GND', 'SCL', 'SDA', 'ADDR', 'ALRT', 'A0', 'A1', 'A2', 'A3']
RTC = ['32K', 'SQW', 'SCL', 'SDA', 'VCC', 'GND']
SDC = ['GND', 'VCC', 'MISO', 'MOSI', 'SCK', 'CS']
ADS_NOTA = {'VDD': 'VDD 3V3', 'ADDR': 'ADDR GND', 'A0': 'A0 divisor', 'A1': 'A1 REF', 'A2': 'A2 LB',
            'A3': 'A3 GND'}


# ------------------------------------------------------------------ texto vectorial (en mm)
@functools.lru_cache(maxsize=None)
def _tp(txt, size, bold):
    tp = TextPath((0, 0), txt, size=size, prop=FPB if bold else FP)
    return tp, tp.get_extents()


def medir(txt, size, bold=False):
    return _tp(txt, size, bold)[1].width


def texto(ax, txt, x, y, size, color=BLANCO, bold=False, ha='center', rot=0, z=20):
    tp, bb = _tp(txt, size, bold)
    off = {'left': bb.x0, 'center': bb.x0 + bb.width / 2, 'right': bb.x1}[ha]
    tf = Affine2D().translate(-off, -size * 0.36).rotate_deg(rot).translate(x, y)
    ax.add_patch(PathPatch(tf.transform_path(tp), fc=color, ec='none', zorder=z))
    w, h = bb.width, size
    if rot % 180:
        w, h = h, w
    cx = {'left': x + w / 2, 'center': x, 'right': x - w / 2}[ha] if not rot % 180 else x
    return box(cx - w / 2, y - h / 2, cx + w / 2, y + h / 2)


def parche(ax, g, **kw):
    """Dibuja un poligono shapely (con huecos) como un solo parche."""
    geoms = list(g.geoms) if hasattr(g, 'geoms') else [g]
    verts, codes = [], []
    for p in geoms:
        if p.is_empty or p.geom_type != 'Polygon':
            continue
        p = orient(p, 1.0)
        for ring in [p.exterior] + list(p.interiors):
            c = list(ring.coords)
            verts += c
            codes += [Path.MOVETO] + [Path.LINETO] * (len(c) - 2) + [Path.CLOSEPOLY]
    if verts:
        ax.add_patch(PathPatch(Path(verts, codes), **kw))


def mm_pt(mm):
    return mm * 72 / 25.4


# ------------------------------------------------------------------ datos de la placa
def leer_partes(brd):
    b = ET.parse(brd).getroot().find('drawing/board')
    out = []
    for e in b.find('elements'):
        rot = int(float(e.get('rot', 'R0').lstrip('MR')))
        out.append(Parte(e.get('name'), e.get('package'), e.get('value'), float(e.get('x')), float(e.get('y')), rot))
    return out


def color_de(nombre):
    if nombre.startswith(('COM', 'NO')):
        return COL['K']
    if nombre.startswith('JP'):
        return COL['JP']
    return COL[nombre[0]]


def construir(salida, espejo=True):
    W, H, pads, tr, top = V.leer(BRD)
    partes = leer_partes(BRD)
    pp = {p.nombre: p for p in partes}
    rel, _ = R.relleno_gnd(W, H, pads, tr)

    def mg(g):
        return affinity.scale(g, xfact=-1, yfact=1, origin=(W / 2, 0)) if espejo else g

    def mp(x, y):
        return ((W - x) if espejo else x, y)

    for p in pads:
        p['g'] = mg(p['geom'])
        p['c'] = mp(p['x'], p['y'])
    por_parte = {}
    for p in pads:
        por_parte.setdefault(p['parte'], []).append(p)
    trg = {}
    for n, cams in tr.items():
        trg[n] = unary_union([mg(LineString(c).buffer(w / 2, 16)) for c, w in cams])
    pour = mg(rel)

    # contornos de cada pieza
    cont = {c[4]: c[:4] for c in []}
    docu = {t[4].split()[0]: t[:4] for t in contornos_docu(partes)}
    ads, rtc, sd = docu['ADS1115'], docu['RTC'], docu['microSD']
    fijos = {'U2': ads, 'U5': rtc, 'U4': sd}
    contorno = {}
    for p in partes:
        h = HUELLAS[p.paquete]
        if p.nombre in fijos:
            g = box(*fijos[p.nombre])
        elif p.paquete in ('ESP32_DEVKIT38', 'TERM2_5MM', 'CAP_5MM') and 'cuerpo' in h:
            x0, y0, x1, y1 = h['cuerpo']
            pts = [rot_xy(a, b, p.rot) for a, b in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]]
            g = Polygon([(p.x + a, p.y + b) for a, b in pts])
        else:
            g = unary_union([q['geom'] for q in por_parte[p.nombre]]).convex_hull.buffer(0.7, 16)
        contorno[p.nombre] = mg(g)

    # ------------------------------------------------------------ lienzo
    MX, MB, MT, HH = 24.0, 24.0, 11.0, 13.0
    YCALL = -9.0   # los cuadros no bajan de aqui (debajo va la leyenda)
    xmin, xmax = -MX, W + MX
    ymin, ymax = -MB, H + MT + HH
    fig = plt.figure(figsize=((xmax - xmin) / 25.4, (ymax - ymin) / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.axis('off')
    ax.add_patch(plt.Rectangle((xmin, ymin), xmax - xmin, ymax - ymin, fc=FONDO, ec='none', zorder=0))
    ax.add_patch(plt.Rectangle((0, 0), W, H, fc=PLACA, ec='#2c5c52', lw=mm_pt(0.25), zorder=1))
    parche(ax, pour, fc=AZUL, ec='none', alpha=0.13, zorder=2)

    # contornos de piezas
    for p in partes:
        c = color_de(p.nombre)
        parche(ax, contorno[p.nombre], fc=c, ec=c, alpha=0.13, lw=0, zorder=3)
        g = contorno[p.nombre]
        ax.add_patch(MPoly(list(g.exterior.coords), closed=True, fc='none', ec=c, lw=mm_pt(0.2), zorder=4))

    # pistas
    for n, g in trg.items():
        parche(ax, g, fc=AZUL, ec='none', zorder=5)
    # cable puente (lado de componentes)
    for (pts, w, net) in top:
        a, b = mp(*pts[0]), mp(*pts[1])
        ax.plot([a[0], b[0]], [a[1], b[1]], color=COL['JP'], lw=mm_pt(0.55), ls=(0, (2, 1.4)), zorder=8,
                solid_capstyle='round')
    # pads
    for p in pads:
        parche(ax, p['g'], fc=ORO, ec='none', zorder=9)
        ax.add_patch(Circle(p['c'], p['drill'] / 2, fc=FONDO, ec='none', zorder=10))

    # ------------------------------------------------------------ ocupacion
    base = unary_union([p['g'].buffer(0.05) for p in pads] +
                       [g.buffer(0.12) for g in trg.values()])
    base_p = prep(base)
    borde = {n: g.exterior.buffer(0.12) for n, g in contorno.items()}
    interior = dict(contorno)
    puestos = []
    state = {'u': None, 'p': None}

    def poner(g):
        puestos.append(g)
        state['u'] = unary_union(puestos)
        state['p'] = prep(state['u'])

    def libre(rect, dueno=None, callout=False):
        if base_p.intersects(rect):
            return False
        if state['p'] is not None and state['p'].intersects(rect):
            return False
        for q, b in borde.items():
            if q != dueno and b.intersects(rect):
                return False
        if callout:
            for q, ar in interior.items():
                if (q != dueno or q not in BIG) and ar.intersects(rect):
                    return False
        return True

    # textos propios de las huellas (ANTENA / USB)
    u1 = contorno['U1']
    bx0, by0, bx1, by1 = u1.bounds
    poner(texto(ax, 'ANTENA', (bx0 + bx1) / 2, by1 - 1.6, 1.3, GRIS, True, z=12).buffer(0.2))
    poner(texto(ax, 'USB', (bx0 + bx1) / 2, by0 + 1.6, 1.3, GRIS, True, z=12).buffer(0.2))

    # marcas de polaridad: el pad cuadrado es el pin 1
    # etiquetas dentro del cuerpo de cada carga RL (giradas)
    for k in range(1, 9):
        n = 'RL%d' % k
        a, b = por_parte[n][0]['c'], por_parte[n][1]['c']
        cy = (a[1] + b[1]) / 2 + 1.5
        txt = '%s  %s Ω' % (n, VALOR_RL[k - 1])
        size = min(1.5, 8.0 / medir(txt, 1.0, True))
        poner(texto(ax, txt, a[0], cy, size, COL['R'], True, rot=90, z=15).buffer(0.1))

    # ------------------------------------------------------------ etiquetas de pad
    def etiqueta_texto(p):
        n, pad, net = p['parte'], p['pad'], p['net']
        i = int(pad) - 1
        if n == 'U1':
            if net is None:
                return None
            return net + (' IO%d' % D.GPIO[net] if net in D.GPIO else '')
        if n == 'U2':
            return ADS_NOTA.get(ADS[i], ADS[i]) if (net or ADS[i] == 'ALRT') else ADS[i]
        if n == 'U5':
            return RTC[i]
        if n == 'U4':
            return SDC[i]
        if n in ('J2', 'J6', 'J7', 'J3', 'J5'):
            return net if n != 'J3' else ['VDD', 'DQ', 'GND'][i]
        if n == 'J1':
            return ['+ PV', '− GND'][i]
        if n == 'J4':
            return ['+ REF', '− GND'][i]
        if n == 'C4':
            return ['+ 5V', '− GND'][i]
        if n.startswith(('COM', 'NO')):
            return n
        if n.startswith('JP'):
            return '3V3'
        return None

    def preferencia(p):
        n = p['parte']
        cx = p['c'][0]
        if n in ('U1', 'U2'):
            ccx = contorno[n].centroid.x
            return ['left', 'right'] if cx > ccx else ['right', 'left']
        if n == 'U5':
            return ['right', 'left'] if espejo else ['left', 'right']
        if n == 'U4':
            return ['left', 'right'] if espejo else ['right', 'left']
        if n.startswith(('COM', 'NO')):
            return ['down', 'up']
        if n.startswith('RL'):
            return ['down', 'up']
        return ['left', 'right'] if cx < W / 2 else ['right', 'left']

    sin_lugar = []
    pads_p = prep(unary_union([p['g'].buffer(0.05) for p in pads]))
    ajeno_cache = {}

    def cobre_ajeno(net):
        if net not in ajeno_cache:
            ajeno_cache[net] = prep(unary_union([g.buffer(0.12) for k, g in trg.items() if k != net]))
        return ajeno_cache[net]

    def libre_sobre_pista(rect, p, ignora_borde=False, cualquiera=False):
        """Permite tapar la pista de la propia red (la etiqueta lleva fondo), nada mas."""
        if pads_p.intersects(rect):
            return False
        if not cualquiera and cobre_ajeno(p['net'] or '').intersects(rect):
            return False
        if state['p'] is not None and state['p'].intersects(rect):
            return False
        if ignora_borde:
            return True
        return not any(q != p['parte'] and b.intersects(rect) for q, b in borde.items())

    for p in sorted(pads, key=lambda q: (q['parte'] not in BIG, q['parte'])):
        txt = etiqueta_texto(p)
        if not txt:
            continue
        hecho = False
        for modo in ('libre', 'sobre_pista', 'sobre_borde', 'cualquiera'):
            for size in (1.2, 1.0):
                w = medir(txt, size)
                h = size
                x0, y0, x1, y1 = p['g'].bounds
                cx, cy = p['c']
                pref = preferencia(p)
                orden = pref + [d for d in ('right', 'left', 'up', 'down') if d not in pref]
                for extra in ((0.0, 0.8, 1.6, 2.6) if modo == 'cualquiera' else (0.0, 0.8, 1.6)):
                    for d in orden:
                        g = 0.35 + extra
                        pos = {'right': (x1 + g + w / 2, cy), 'left': (x0 - g - w / 2, cy),
                               'up': (cx, y1 + g + h / 2), 'down': (cx, y0 - g - h / 2)}[d]
                        rect = box(pos[0] - w / 2 - 0.12, pos[1] - h / 2 - 0.1, pos[0] + w / 2 + 0.12,
                                   pos[1] + h / 2 + 0.1)
                        ok = (libre(rect, p['parte']) if modo == 'libre'
                              else libre_sobre_pista(rect, p, modo != 'sobre_pista', modo == 'cualquiera'))
                        if ok:
                            if modo != 'libre':
                                ax.add_patch(FancyBboxPatch((rect.bounds[0], rect.bounds[1]), rect.bounds[2] - rect.bounds[0],
                                                            rect.bounds[3] - rect.bounds[1],
                                                            boxstyle='round,pad=0,rounding_size=0.4', fc=FONDO, ec='none',
                                                            alpha=0.92, zorder=14))
                            texto(ax, txt, pos[0], pos[1], size, '#d7e8e2', False, z=15)
                            if extra >= 0.8 or modo == 'cualquiera':   # etiqueta lejos: linea guia al pad
                                a, b = nearest_points(rect, p['g'])
                                ax.plot([a.x, b.x], [a.y, b.y], color='#d7e8e2', lw=mm_pt(0.1), zorder=15)
                                ax.add_patch(Circle((b.x, b.y), 0.22, fc='#d7e8e2', ec='none', zorder=15))
                            poner(rect)
                            hecho = True
                            break
                    if hecho:
                        break
                if hecho:
                    break
            if hecho:
                break
        if not hecho:
            sin_lugar.append('%s.%s %s' % (p['parte'], p['pad'], txt))

    # ------------------------------------------------------------ etiquetas de red sobre pistas
    for net in ('PV', 'LB', '5V', '3V3', 'A0', 'DIV', 'REF', 'DQ'):
        segs = []
        for c, w in tr.get(net, []):
            for a, b in zip(c, c[1:]):
                L = ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
                segs.append((L, a, b))
        segs.sort(reverse=True)
        tw = medir(net, 1.1, True) + 1.0
        for L, a, b in segs:
            if L < tw + 1.0:
                break
            m = mp((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            rect = box(m[0] - tw / 2, m[1] - 0.95, m[0] + tw / 2, m[1] + 0.95)
            otros = unary_union([g for k, g in trg.items() if k != net] + [q['g'] for q in pads if q['net'] != net])
            if rect.distance(otros) < 0.25:
                continue
            if state['p'] is not None and state['p'].intersects(rect):
                continue
            ax.add_patch(FancyBboxPatch((rect.bounds[0], rect.bounds[1]), tw, 1.9,
                                        boxstyle='round,pad=0,rounding_size=0.5', fc=FONDO, ec=AZUL,
                                        lw=mm_pt(0.14), zorder=14))
            texto(ax, net, m[0], m[1], 1.1, '#bfe0ff', True, z=15)
            poner(rect)
            break

    # ------------------------------------------------------------ callouts
    S1, S2, PAD = 1.55, 1.15, 0.7

    def callout(clave, ref, valor, func, color, objetivo, dueno):
        w1 = medir(ref, S1, True) + 0.7 + medir(valor, S1, True)
        w2 = medir(func, S2)
        w = max(w1, w2) + 2 * PAD
        h = 2 * PAD + S1 + 0.55 + S2
        x0, y0, x1, y1 = objetivo.bounds
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        pw, ph = x1 - x0, y1 - y0
        cand = []
        if dueno in BIG:  # dentro del propio modulo, lo mas arriba posible
            ar = contorno[dueno]
            ax0, ay0, ax1, ay1 = ar.bounds
            yy = ay1 - h / 2 - 3.0
            while yy > ay0 + h / 2:
                xx = (ax0 + ax1) / 2
                for dx in (0, -2, 2, -4, 4, -6, 6):
                    cand.append((0.0, xx + dx, yy))
                yy -= 1.0
        for r in (0.8, 1.8, 3.0, 4.5, 6.5, 9.0, 12.0, 16.0, 21.0, 27.0, 34.0):
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)):
                bx = cx + dx * (pw / 2 + w / 2 + r)
                by = cy + dy * (ph / 2 + h / 2 + r)
                vars_ = [(bx, by)]
                if dx == 0:
                    vars_ += [(bx - (pw / 2 + w / 2 - 1.5), by), (bx + (pw / 2 + w / 2 - 1.5), by)]
                if dy == 0:
                    vars_ += [(bx, by - (ph / 2 + h / 2 - 1.5)), (bx, by + (ph / 2 + h / 2 - 1.5))]
                for (vx, vy) in vars_:
                    cand.append((r + abs(vx - bx) * 0.05 + abs(vy - by) * 0.05, vx, vy))
        cand.sort(key=lambda t: t[0])
        for (_, vx, vy) in cand:
            rect = box(vx - w / 2, vy - h / 2, vx + w / 2, vy + h / 2)
            if not (xmin + 0.6 < rect.bounds[0] and rect.bounds[2] < xmax - 0.6 and
                    YCALL < rect.bounds[1] and rect.bounds[3] < H + MT - 0.4):
                continue
            if dueno in BIG and contorno[dueno].contains(rect):
                ok = libre(rect, dueno, True)
            else:
                ok = libre(rect, dueno, True)
            if not ok:
                continue
            ax.add_patch(FancyBboxPatch((rect.bounds[0], rect.bounds[1]), w, h,
                                        boxstyle='round,pad=0,rounding_size=0.6', fc='#0a1a17', ec=color,
                                        lw=mm_pt(0.22), zorder=18))
            tx = rect.bounds[0] + PAD
            ty1 = rect.bounds[3] - PAD - S1 * 0.5
            ty2 = rect.bounds[1] + PAD + S2 * 0.5
            texto(ax, ref, tx, ty1, S1, color, True, 'left', z=20)
            texto(ax, valor, tx + medir(ref, S1, True) + 0.7, ty1, S1, BLANCO, True, 'left', z=20)
            texto(ax, func, tx, ty2, S2, GRIS, False, 'left', z=20)
            a, b = nearest_points(rect, objetivo)
            if a.distance(b) > 0.7:
                ax.plot([a.x, b.x], [a.y, b.y], color=color, lw=mm_pt(0.16), zorder=17, solid_capstyle='round')
                ax.add_patch(Circle((b.x, b.y), 0.32, fc=color, ec='none', zorder=17))
            poner(rect.buffer(0.15))
            return True
        sin_lugar.append('callout ' + clave)
        return False

    orden_callouts = ['U1', 'U2', 'U4', 'U5', 'J1', 'J4', 'J5', 'J3', 'J2', 'J6', 'J7',
                      'R1', 'R2', 'R3', 'R4', 'R_SH1', 'R_SH2', 'C1', 'C4']
    for n in orden_callouts:
        v, f = INFO[n]
        callout(n, n, v, f, color_de(n), contorno[n], n)
    # grupos
    rl = unary_union([contorno['RL%d' % k] for k in range(1, 9)])
    com = unary_union([unary_union([q['g'] for q in por_parte[c + '%d' % k]]).buffer(0.8)
                     for c in ('COM', 'NO') for k in range(1, 9)])
    callout('RL', 'RL1–RL8', 'cargas ½ W', '2.2 · 4.7 · 10 · 22 · 47 · 100 · 220 · 470 Ω', COL['R'], rl, 'RL')
    callout('COM', 'COM1–COM8', 'y NO1–NO8', 'COMk: cable COM del relé k · NOk: cable NO del relé k', COL['K'], com, 'COM')
    jp = unary_union([contorno['JP1A'], contorno['JP1B']])
    callout('JP', 'JP1A–JP1B', 'cable puente', 'une los dos pads de 3V3 (lado de componentes)', COL['JP'], jp, 'JP1A')

    # ------------------------------------------------------------ cabecera y leyenda
    ax.add_patch(plt.Rectangle((xmin, H + MT), xmax - xmin, HH, fc='#f2f4f3', ec='none', zorder=30))
    titulo = 'Sistema de medición de panel solar: componentes y conexiones de la PCB v20'
    tam = min(4.0, (xmax - xmin - 4.0) / medir(titulo, 1.0, True))
    texto(ax, titulo, xmin + 2.0, H + MT + HH - 4.0, tam, '#16302a', True, 'left', z=31)
    sub = ('Pistas azules = cobre (cara de abajo) · cuadros de colores = componentes (van del lado de la fibra) · '
           'círculos dorados = pads con su agujero · placa %.1f × %.1f mm' % (W, H))
    tam2 = min(1.9, (xmax - xmin - 4.0) / medir(sub, 1.0))
    texto(ax, sub, xmin + 2.0, H + MT + 3.0, tam2, '#4a5f59', False, 'left', z=31)
    nota = ('VISTA DESDE LA CARA DE COBRE, como quedó al planchar (izquierda y derecha invertidas respecto a Fusion).'
            if espejo else 'VISTA DESDE EL LADO DE LOS COMPONENTES (igual que Fusion).')
    texto(ax, nota, xmin + 2.0, -12.4, 1.7, '#f2d25a', True, 'left', z=31)
    x = xmin + 2.0
    y = -16.0
    for etiqueta, c in (('Resistencias', COL['R']), ('Capacitores', COL['C']), ('Conectores / borneras', COL['J']),
                        ('Módulos y ESP32', COL['U']), ('Pads COM / NO', COL['K']), ('Cable puente', COL['JP'])):
        ax.add_patch(FancyBboxPatch((x, y - 0.8), 2.6, 1.6, boxstyle='round,pad=0,rounding_size=0.4',
                                    fc=c, ec='none', alpha=0.9, zorder=31))
        t = texto(ax, etiqueta, x + 3.4, y, 1.5, BLANCO, False, 'left', z=31)
        x = t.bounds[2] + 3.2
    texto(ax, 'IOnn = número de GPIO del ESP32 · el pad cuadrado es el pin 1 / el + · todo el cobre azul tenue es GND', xmin + 2.0, -19.2,
          1.5, GRIS, False, 'left', z=31)
    texto(ax, 'Cables externos: panel → J1 · celda de referencia → J4 · módulo de relés: IN1–IN8 ← J2, J6, J7 y '
              '5V/GND ← J5; COMk y NOk de cada relé → pads COMk y NOk · DS18B20 → J3',
          xmin + 2.0, -22.0, 1.5, GRIS, False, 'left', z=31)

    fig.savefig(salida, dpi=PX * 25.4, facecolor=FONDO)
    plt.close(fig)
    print('Diagrama:', salida)
    if sin_lugar:
        print('Sin lugar libre para:', ', '.join(sin_lugar))
    else:
        print('Todas las etiquetas colocadas')


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    esp = '--sin-espejo' not in sys.argv
    sal = args[0] if args else os.path.join(RAIZ, 'PCB_ESP32_v20_diagrama.png' if esp else 'PCB_ESP32_v20_diagrama_lado_componentes.png')
    construir(sal, esp)
