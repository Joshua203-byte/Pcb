"""Nombres de componentes (R1, C1, U1...) sin choques y guia de montaje 1:1.

Nada de esto es cobre: no cambia pistas, pads ni el DRC.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly
from shapely.geometry import box
from shapely.ops import unary_union

from pcb_geo import HUELLAS

TAM = 1.2          # alto del texto del nombre (mm)
ANCHO_CAR = 1.0    # ancho de cada caracter en alturas (fuente vectorial de Fusion, con espacio)


def caja_texto(x, y, txt, size, align='center', margen=0.25):
    w = len(txt) * size * ANCHO_CAR
    h = size
    if align.endswith('left'):
        x0 = x
    elif align.endswith('right'):
        x0 = x - w
    else:
        x0 = x - w / 2
    if align.startswith('bottom'):
        y0 = y
    elif align.startswith('top'):
        y0 = y - h
    else:
        y0 = y - h / 2
    return box(x0 - margen, y0 - margen, x0 + w + margen, y0 + h + margen)


def cuerpos(P):
    """Contorno del cuerpo de cada pieza (poligonos en coordenadas de placa)."""
    from pcb_geo import rot_xy
    from shapely.geometry import Polygon, Point
    out = []
    for p in P:
        h = HUELLAS[p.paquete]
        if 'cuerpo' in h:
            bx0, by0, bx1, by1 = h['cuerpo']
            esq = [rot_xy(a, b, p.rot) for a, b in [(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)]]
            out.append(Polygon([(p.x + a, p.y + b) for a, b in esq]))
        if p.paquete == 'RES_V':
            out.append(Point(p.x, p.y).buffer(1.9, 32))
    return out


def colocar_nombres(W, H, P, pads, textos, contornos=(), puentes=()):
    """Elige para cada parte un lugar libre cerca de ella. Devuelve {nombre: (x, y, size)}."""
    ocupado = [p['geom'].buffer(0.3) for p in pads]
    ocupado += [c.exterior.buffer(0.3) for c in cuerpos(P)]
    ocupado += [box(a, b, c, d).exterior.buffer(0.3) for (a, b, c, d, t) in contornos]
    from shapely.geometry import LineString
    ocupado += [LineString(pts).buffer(0.8) for pts in puentes]
    ocupado += [caja_texto(x, y, t, s, a) for (x, y, t, s, c, a) in textos]
    # textos de serigrafia propios de cada huella (ANTENA, USB, NO, +, 1)
    from pcb_geo import rot_xy
    for p in P:
        extra = [('1', -2.3, 0.0, 0.8)] if p.paquete.startswith(('SOCKET', 'MALE')) else []
        for (txt, tx, ty, ts) in HUELLAS[p.paquete].get('textos', []) + extra:
            dx, dy = rot_xy(tx, ty, p.rot)
            ocupado.append(caja_texto(p.x + dx, p.y + dy, txt, ts))
    borde = box(0.8, 0.8, W - 0.8, H - 0.8)
    zona_esp = cuerpos([q for q in P if q.paquete == 'ESP32_DEVKIT38'])
    out = {}
    # primero las piezas con menos lugar
    orden = sorted(P, key=lambda p: len(HUELLAS[p.paquete]['pads']))
    for p in orden:
        if p.paquete == 'RES_H_T':  # cargas: el nombre va dentro del cuerpo, girado
            from pcb_geo import rot_xy
            bx0, by0, bx1, by1 = HUELLAS[p.paquete]['cuerpo']
            dx, dy = rot_xy((bx0 + bx1) / 2, (by0 + by1) / 2, p.rot)
            out[p.nombre] = (p.x + dx, p.y + dy, 1.2, 90 if p.rot % 180 else 0)
            continue
        mis = [q for q in pads if q['parte'] == p.nombre]
        u = unary_union([q['geom'] for q in mis] + (cuerpos([p]) if p.paquete != 'ESP32_DEVKIT38' else []))
        x0, y0, x1, y1 = u.bounds
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        txt = p.nombre
        mejor = None
        intentos = []
        for k in range(0, 5):  # primero cerca (con cualquier tamano), despues mas lejos
            for size in (TAM, 1.0, 0.8):
                d = size / 2 + 0.6 + 1.5 * k
                mitad = len(txt) * size * ANCHO_CAR / 2
                for (x, y) in [(cx, y1 + d), (cx, y0 - d), (x0 - d - mitad, cy), (x1 + d + mitad, cy),
                               (x0 - d - mitad, y1), (x0 - d - mitad, y0), (x1 + d + mitad, y1),
                               (x1 + d + mitad, y0)]:
                    intentos.append((x, y, size))
        if p.paquete == 'WIREPAD':  # COMk: justo debajo de su pad
            intentos = [(cx, y0 - 1.05, 0.9), (cx, y0 - 0.95, 0.8)] + intentos
        for (x, y, size) in intentos:
            c = caja_texto(x, y, txt, size)
            if not borde.contains(c):
                continue
            if p.paquete != 'ESP32_DEVKIT38' and any(c.intersects(z) for z in zona_esp):
                continue  # debajo del ESP32 solo va su propio nombre
            if any(c.intersects(o) for o in ocupado):
                continue
            mejor = (x, y, size)
            break
        if mejor is None:  # sin lugar libre: encima de la pieza, chico
            mejor = (cx, cy, 0.8)
            print('  aviso: el nombre %s queda encima de la pieza' % txt)
        out[txt] = mejor + (0,)
        ocupado.append(caja_texto(mejor[0], mejor[1], txt, mejor[2]))
    return out


def _forma(ax, g, **kw):
    gs = g.geoms if hasattr(g, 'geoms') else [g]
    for q in gs:
        ax.add_patch(MPoly(list(q.exterior.coords), closed=True, **kw))


def _hoja(W, H, P, pads, textos, nombres, contornos, titulo, puentes=()):
    from pcb_geo import rot_xy
    mm = 1 / 25.4
    fig = plt.figure(figsize=(210 * mm, 297 * mm))
    x0, y0 = 20, 297 - 30 - H
    ax = fig.add_axes([x0 / 210, y0 / 297, W / 210, H / 297])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis('off')
    ax.add_patch(MPoly([(0, 0), (W, 0), (W, H), (0, H)], closed=True, fc='none', ec='black', lw=0.4))
    for p in pads:  # solo el contorno del pad, para ubicarse
        _forma(ax, p['geom'], fc='none', ec='#999', lw=0.3)
    for c in cuerpos(P):  # contorno del cuerpo de cada pieza
        ax.add_patch(MPoly(list(c.exterior.coords), closed=True, fc='none', ec='black', lw=0.5))
    for (bx0, by0, bx1, by1, t) in contornos:
        ax.add_patch(MPoly([(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)], closed=True,
                           fc='none', ec='black', lw=0.4, ls='--'))
    for (a, b) in puentes:  # cable puente: va por este lado de la placa
        ax.plot([a[0], b[0]], [a[1], b[1]], color='black', lw=2.2, solid_capstyle='round')
    ha = {'center-left': 'left', 'center-right': 'right'}
    pt_mm = 72 / 25.4  # puntos tipograficos por mm
    for (x, y, t, s, c, a) in textos:
        ax.text(x, y, t, fontsize=s * pt_mm, ha=ha.get(a, 'center'), va='center', color='#333')
    for t, (x, y, s, r) in nombres.items():
        ax.text(x, y, t, fontsize=s * pt_mm, ha='center', va='center', weight='bold', rotation=r)
    fig.text(x0 / 210, (y0 + H + 6) / 297, 'PCB_ESP32_v20 - ' + titulo, fontsize=8)
    fig.text(x0 / 210, (y0 - 8) / 297, 'Imprimir al 100 %%. El cuadro de la placa debe medir %.1f x %.1f mm.'
             % (W, H), fontsize=8)
    return fig


def pdf_serigrafia(W, H, P, pads, textos, nombres, contornos, archivo, puentes=()):
    """Dos hojas A4 1:1 de la cara de componentes: guia normal y la misma espejada para planchar."""
    import io
    import numpy as np
    from matplotlib.backends.backend_pdf import PdfPages
    with PdfPages(archivo) as pdf:
        fig = _hoja(W, H, P, pads, textos, nombres, contornos,
                    'Guia de montaje 1:1, cara de componentes vista desde arriba', puentes)
        pdf.savefig(fig)
        plt.close(fig)
        # hoja espejada: se rasteriza a 600 ppp y se voltea entera (letras incluidas)
        fig = _hoja(W, H, P, pads, textos, nombres, contornos,
                    'ESPEJADA: planchar sobre la fibra (lado de componentes)', puentes)
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=600)
        plt.close(fig)
        buf.seek(0)
        img = plt.imread(buf)[:, ::-1]
        mm = 1 / 25.4
        fig = plt.figure(figsize=(210 * mm, 297 * mm))
        ax = fig.add_axes([0, 0, 1, 1])
        ax.imshow(img, interpolation='nearest', aspect='auto')
        ax.axis('off')
        pdf.savefig(fig, dpi=600)
        plt.close(fig)
