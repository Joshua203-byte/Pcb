"""Verificacion independiente: lee un .brd ya escrito y revisa conexiones y separaciones.

No usa el estado interno del generador: reconstruye pads, pistas y relleno desde
el XML, como lo haria Fusion. Uso:  python3 herramientas/verificar_brd.py PCB_ESP32_v19.brd
"""
import math
import sys
import xml.etree.ElementTree as ET

from shapely.geometry import LineString, Point, box
from shapely import affinity

import pcb_drc
from pcb_geo import REGLAS


def leer(archivo):
    r = ET.parse(archivo).getroot()
    b = r.find('drawing/board')
    dr = {p.get('name'): p.get('value') for p in b.find('designrules').findall('param')}
    elong = float(dr.get('psElongationLong', '100'))
    paquetes = {p.get('name'): p for p in b.iter('package')}
    xs = [float(w.get(k)) for w in b.find('plain').findall('wire') if w.get('layer') == '20' for k in ('x1', 'x2')]
    ys = [float(w.get(k)) for w in b.find('plain').findall('wire') if w.get('layer') == '20' for k in ('y1', 'y2')]
    W, H = max(xs), max(ys)
    net_de = {}
    for s in b.find('signals'):
        for c in s.findall('contactref'):
            net_de[(c.get('element'), c.get('pad'))] = s.get('name')
    pads = []
    for e in b.find('elements'):
        rot = float(e.get('rot', 'R0').lstrip('MR'))
        ex, ey = float(e.get('x')), float(e.get('y'))
        for p in paquetes[e.get('package')].findall('pad'):
            px, py = float(p.get('x')), float(p.get('y'))
            a = math.radians(rot)
            cx = ex + px * math.cos(a) - py * math.sin(a)
            cy = ey + px * math.sin(a) + py * math.cos(a)
            d = float(p.get('diameter'))
            forma = p.get('shape', 'round')
            if forma == 'round':
                g = Point(0, 0).buffer(d / 2, 32)
            elif forma == 'square':
                g = box(-d / 2, -d / 2, d / 2, d / 2)
            elif forma == 'long':
                L = d * (1 + elong / 100)
                g = LineString([(-(L - d) / 2, 0), ((L - d) / 2, 0)]).buffer(d / 2, 32)
            else:
                raise ValueError(forma)
            g = affinity.translate(affinity.rotate(g, rot + float(p.get('rot', 'R0').lstrip('R')), origin=(0, 0)), cx, cy)
            pads.append(dict(parte=e.get('name'), pad=p.get('name'), x=cx, y=cy, drill=float(p.get('drill')),
                             geom=g, net=net_de.get((e.get('name'), p.get('name')))))
    trazas, top = {}, []
    for s in b.find('signals'):
        for w in s.findall('wire'):
            seg = ([(float(w.get('x1')), float(w.get('y1'))), (float(w.get('x2')), float(w.get('y2')))],
                   float(w.get('width')))
            if w.get('layer') == '16':
                trazas.setdefault(s.get('name'), []).append(seg)
            elif w.get('layer') == '1':
                top.append((seg[0], seg[1], s.get('name')))
    return W, H, pads, trazas, top


def airwires(pads, trazas, top):
    """Conexion estricta por extremos (como EAGLE): devuelve las redes partidas (sin GND)."""
    err = []
    redes = {}
    for p in pads:
        if p['net']:
            redes.setdefault(p['net'], []).append(p)
    for n, ps in redes.items():
        if n == 'GND' or len(ps) < 2:
            continue
        padre = {}

        def raiz(k):
            while padre.setdefault(k, k) != k:
                k = padre[k]
            return k

        def unir(a, b):
            padre[raiz(a)] = raiz(b)

        def clave(q):
            return (round(q[0], 3), round(q[1], 3))

        segs = [s for s, w in trazas.get(n, [])] + [pts for pts, w, nn in top if nn == n]
        for pts in segs:
            unir(clave(pts[0]), clave(pts[1]))
        for p in ps:
            unir(('pad', p['parte'], p['pad']), clave((p['x'], p['y'])))
        grupos = {raiz(('pad', p['parte'], p['pad'])) for p in ps}
        if len(grupos) > 1:
            err.append('red %s sin terminar (%d grupos)' % (n, len(grupos)))
    return err


if __name__ == '__main__':
    W, H, pads, tr, top = leer(sys.argv[1] if len(sys.argv) > 1 else 'PCB_ESP32_v19.brd')
    rel, _ = pcb_drc.relleno_gnd(W, H, pads, tr)
    e = pcb_drc.drc(W, H, pads, tr, rel, top) + pcb_drc.conectividad(pads, tr, rel, top) + airwires(pads, tr, top)
    print('placa %.2f x %.2f mm, %d pads, %d pistas, %d puente(s)' % (W, H, len(pads), sum(len(v) for v in tr.values()), len(top)))
    print('errores: %d' % len(e))
    for x in e:
        print(' -', x)
