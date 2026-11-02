"""Nombres de componentes grabados en el cobre (capa Bottom), para que salgan al planchar.

Cada nombre va en un lugar donde solo hay relleno de GND: el relleno se aparta del
texto (ISOLATE) y las letras quedan como cobre aislado. Se escriben espejados (MR0)
para que se lean bien mirando la cara de cobre.
"""
from shapely.geometry import box
from shapely.ops import unary_union

from pcb_geo import REGLAS, HUELLAS
from pcb_drc import geom_traza

ANCHO_CAR = 0.95   # ancho de cada caracter (fuente vectorial), en alturas
RATIO = 18         # grosor del trazo en % de la altura (0.32 mm con letra de 1.8 mm)
TAMANOS = (1.6, 1.4, 1.3)


def caja(x, y, txt, size, rot=0):
    w = len(txt) * size * ANCHO_CAR
    if rot % 180:
        return box(x - size / 2, y - w / 2, x + size / 2, y + w / 2)
    return box(x - w / 2, y - size / 2, x + w / 2, y + size / 2)


def colocar(W, H, P, pads, trazas, puentes_top=()):
    """Devuelve [(nombre, x, y, size)] sin tocar cobre ajeno ni romper el relleno."""
    from pcb_drc import relleno_gnd, grupos_gnd
    sep = REGLAS['aislamiento_gnd'] + 0.05
    cobre = [p['geom'] for p in pads]
    for n, cams in trazas.items():
        cobre += [geom_traza(c, w) for c, w in cams]
    cobre_u = unary_union(cobre)
    zona = box(0, 0, W, H).buffer(-(REGLAS['cobre_borde'] + sep), join_style=2)
    puestos = []
    ocupado = []
    base_grupos = len(grupos_gnd(pads, trazas, relleno_gnd(W, H, pads, trazas)[0]))
    # filas repetidas (cargas): solo se rotulan la primera y la ultima, para no amontonar
    omitir = {'%s%d' % (n, k) for n in ('RL', 'COM', 'NO') for k in range(2, 8)}
    for p in sorted(P, key=lambda q: len(HUELLAS[q.paquete]['pads'])):
        if p.nombre in omitir:
            continue
        mis = unary_union([q['geom'] for q in pads if q['parte'] == p.nombre])
        x0, y0, x1, y1 = mis.bounds
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        vertical = (y1 - y0) > (x1 - x0) and p.paquete in ('RES_H_T', 'RES_V', 'CAP_5MM')
        hecho = False
        for size in TAMANOS:
            for rot in ((90, 0) if vertical else (0, 90)):
                largo = len(p.nombre) * size * ANCHO_CAR
                mw, mh = (size / 2, largo / 2) if rot else (largo / 2, size / 2)
                cands = [(cx, cy)]
                for k in range(0, 3):  # solo cerca de la pieza (a lo sumo ~2 mm extra)
                    d = mh + sep + 0.2 + 1.0 * k
                    dw = mw + sep + 0.2 + 1.0 * k
                    cands += [(cx, y1 + d), (cx, y0 - d), (x0 - dw, cy), (x1 + dw, cy)]
                for (x, y) in cands:
                    c = caja(x, y, p.nombre, size, rot)
                    if not zona.contains(c):
                        continue
                    if c.buffer(sep).intersects(cobre_u):
                        continue
                    if any(c.buffer(sep).intersects(o) for o in ocupado):
                        continue
                    obst = ocupado + [c]
                    rel, _ = relleno_gnd(W, H, pads, trazas, obstaculos=obst)
                    if len(grupos_gnd(pads, trazas, rel)) > base_grupos:
                        continue  # el texto no debe partir el GND en islas
                    puestos.append((p.nombre, round(x, 3), round(y, 3), size, rot))
                    ocupado.append(c)
                    hecho = True
                    break
                if hecho:
                    break
            if hecho:
                break
        if not hecho:
            print('  aviso: sin lugar en el cobre para el nombre', p.nombre)
    return puestos


def obstaculos(puestos):
    return [caja(x, y, n, s, r) for (n, x, y, s, r) in puestos]
