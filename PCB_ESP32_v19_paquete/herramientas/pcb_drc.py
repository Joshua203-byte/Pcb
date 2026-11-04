"""Relleno de GND simulado y revision de reglas (DRC) con geometria exacta."""
import itertools
from shapely.geometry import box, LineString, Point
from shapely.ops import unary_union

from pcb_geo import REGLAS, POWER, mil


def geom_traza(pts, w):
    if len(pts) == 1:
        return Point(pts[0]).buffer(w / 2, 32)
    return LineString(pts).buffer(w / 2, 32)


def relleno_gnd(W, H, pads, trazas):
    """Relleno GND con alivio termico (4 brazos por pad). Devuelve (cobre conectado, piezas descartadas)."""
    iso = REGLAS['aislamiento_gnd']
    wr = REGLAS['ancho_relleno']
    gap = REGLAS['alivio_termico']
    zona = box(0, 0, W, H).buffer(-REGLAS['cobre_borde'], join_style=2)
    ajeno = [p['geom'] for p in pads if p['net'] != 'GND']
    for n, cams in trazas.items():
        if n != 'GND':
            ajeno += [geom_traza(c, w) for c, w in cams]
    ajeno_u = unary_union(ajeno)
    libre = zona.difference(ajeno_u.buffer(iso, 32))
    gpads = [p for p in pads if p['net'] == 'GND']
    libre = libre.difference(unary_union([p['geom'] for p in gpads]).buffer(gap, 16))
    libre = libre.buffer(-wr / 2, 16).buffer(wr / 2, 16)
    # brazos del alivio termico: del centro del pad hacia +x, -x, +y, -y
    brazos = []
    for p in gpads:
        x0, y0, x1, y1 = p['geom'].bounds
        largo = max(x1 - x0, y1 - y0) / 2 + gap + wr
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            b = LineString([(p['x'], p['y']), (p['x'] + dx * largo, p['y'] + dy * largo)]).buffer(wr / 2, cap_style=2)
            if b.distance(ajeno_u) >= iso and zona.contains(b) and b.intersects(libre):
                brazos.append(b)
    gnd_cobre = [p['geom'] for p in gpads] + brazos
    gnd_cobre += [geom_traza(c, w) for c, w in trazas.get('GND', [])]
    gnd_u = unary_union(gnd_cobre)
    piezas = list(libre.geoms) if hasattr(libre, 'geoms') else [libre]
    vivas = [p for p in piezas if p.intersects(gnd_u)]
    muertas = [p for p in piezas if not p.intersects(gnd_u)]
    return unary_union(vivas + brazos), muertas


def grupos_gnd(pads, trazas, relleno):
    """Agrupa los pads GND por conexion real (pads + pistas GND + relleno)."""
    cobre = [p['geom'] for p in pads if p['net'] == 'GND']
    cobre += [geom_traza(c, w) for c, w in trazas.get('GND', [])]
    u = unary_union(cobre + [relleno])
    comps = list(u.geoms) if hasattr(u, 'geoms') else [u]
    grupos = []
    for c in comps:
        g = [p['parte'] + '.' + p['pad'] for p in pads if p['net'] == 'GND' and c.intersects(p['geom'])]
        if g:
            grupos.append(g)
    return grupos


def drc(W, H, pads, trazas, relleno, puentes_top=()):
    """Lista de violaciones (texto). trazas: red -> [(puntos, ancho)]."""
    err = []
    tol = 1e-3
    objs = []  # (red, tipo, geom, etiqueta)
    for p in pads:
        objs.append((p['net'], 'pad', p['geom'], '%s.%s' % (p['parte'], p['pad'])))
    for n, cams in trazas.items():
        for k, (c, w) in enumerate(cams):
            objs.append((n, 'pista', geom_traza(c, w), '%s#%d' % (n, k)))
            minimo = mil(15) if n in POWER else mil(10)
            if w < minimo - tol:
                err.append('ancho de pista %.3f mm < %.3f mm (clase) en %s' % (w, minimo, n))
    # separacion entre cobre de redes distintas
    for a, b in itertools.combinations(objs, 2):
        if a[0] is not None and a[0] == b[0]:
            continue
        if a[1] == 'pad' and b[1] == 'pad':
            lim = REGLAS['pad_pad']
        elif a[1] == 'pista' and b[1] == 'pista':
            lim = REGLAS['pista_pista']
        else:
            lim = REGLAS['pista_pad']
        d = a[2].distance(b[2])
        if d < lim - tol:
            err.append('separacion %.3f < %.2f entre %s y %s' % (d, lim, a[3], b[3]))
    # relleno contra cobre ajeno
    for o in objs:
        if o[0] != 'GND':
            d = relleno.distance(o[2])
            if d < REGLAS['aislamiento_gnd'] - 0.01:
                err.append('relleno GND a %.3f de %s' % (d, o[3]))
    # cobre al borde
    interior = box(0, 0, W, H).buffer(-REGLAS['cobre_borde'] + tol, join_style=2)
    for o in objs:
        if not interior.contains(o[2]):
            err.append('cobre a menos de %.1f mm del borde: %s' % (REGLAS['cobre_borde'], o[3]))
    # taladros a mas de 2 mm del borde
    for p in pads:
        dmin = min(p['x'], p['y'], W - p['x'], H - p['y']) - p['drill'] / 2
        if dmin < 2.0:
            err.append('taladro de %s.%s a %.2f mm del borde' % (p['parte'], p['pad'], dmin))
    # puentes (capa superior): no deben tocar pads de otras redes
    for (pts, w, net) in puentes_top:
        g = geom_traza(pts, w)
        for p in pads:
            if p['net'] != net and g.distance(p['geom']) < REGLAS['pista_pad'] - tol:
                err.append('puente %s a %.2f de %s.%s' % (net, g.distance(p['geom']), p['parte'], p['pad']))
    return err


def conectividad(pads, trazas, relleno, puentes_top=()):
    """Comprueba que cada red forme una sola pieza de cobre (sin cables sin rutear)."""
    err = []
    redes = {}
    for p in pads:
        if p['net']:
            redes.setdefault(p['net'], []).append(p)
    for n, ps in redes.items():
        cobre = [p['geom'] for p in ps] + [geom_traza(c, w) for c, w in trazas.get(n, [])]
        cobre += [geom_traza(pts, w) for (pts, w, net) in puentes_top if net == n]
        if n == 'GND':
            cobre.append(relleno)
        u = unary_union(cobre)
        comps = list(u.geoms) if hasattr(u, 'geoms') else [u]
        if len(ps) > 1 and len(comps) > 1:
            gr = []
            for c in comps:
                g = [p['parte'] + '.' + p['pad'] for p in ps if c.intersects(p['geom'])]
                if g:
                    gr.append(g)
            if len(gr) > 1:
                err.append('red %s partida en %d grupos: %s' % (n, len(gr), gr))
    return err


def angulos(trazas, tol=1.0):
    """Quiebres de mas de 45 grados en una misma pista (prohibidos: L-curso seccion 7)."""
    import math
    err = []
    for n, cams in trazas.items():
        for c, w in cams:
            for a, b, d in zip(c, c[1:], c[2:]):
                v1 = (b[0] - a[0], b[1] - a[1])
                v2 = (d[0] - b[0], d[1] - b[1])
                n1 = math.hypot(*v1)
                n2 = math.hypot(*v2)
                if n1 < 1e-6 or n2 < 1e-6:
                    continue
                cosang = max(-1, min(1, (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)))
                giro = math.degrees(math.acos(cosang))
                if giro > 45 + tol:
                    err.append('quiebre de %.0f grados en %s en (%.2f, %.2f)' % (giro, n, b[0], b[1]))
    return err
