"""Coloca y enruta la PCB v19 con el enrutador de laberinto."""
import json
from shapely.geometry import LineString, Point
from shapely.ops import unary_union

import diseno_v19 as D
from pcb_geo import REGLAS, ancho
from pcb_router import Router, simplificar

CLR = max(REGLAS['pista_pista'], REGLAS['pista_pad'])


def preparar():
    P = D.partes()
    for p in P:  # la colocacion se escribe sin el corrimiento DX; aqui se aplica
        p.x = round(p.x + D.DX, 4)
        if not p.nombre.startswith(D.FIJAS):
            p.y = round(p.y + D.DY, 4)
    pads = []
    for p in P:
        pads += p.pads()
    red_de = {}
    for n, lst in D.REDES.items():
        for (e, pd) in lst:
            red_de[(e, pd)] = n
    for pd in pads:
        pd['net'] = red_de.get((pd['parte'], pd['pad']))
    return P, pads


def geom_traza(pts, w):
    if len(pts) == 1:
        return Point(pts[0]).buffer(w / 2, 16)
    return LineString(pts).buffer(w / 2, 16)


class Estado:
    def __init__(self):
        self.P, self.pads = preparar()
        self.R = Router(D.W, D.H, REGLAS['cobre_borde'])
        self.trazas = {}      # red -> lista de (celdas, ancho)
        self.juntas = {}      # red -> celdas donde arranca una rama (deben ser vertices)

    def cobre_ajeno(self, net):
        gs = [p['geom'] for p in self.pads if p['net'] != net]
        for n, caminos in self.trazas.items():
            if n != net:
                for c, w in caminos:
                    gs.append(geom_traza([self.R.xy(*q) for q in c], w))
        return unary_union(gs)

    def enrutar_red(self, net, via=None):
        via = via or {}
        if 'grupos' in via:
            ok = True
            for gr in via['grupos']:
                v2 = dict(gr) if isinstance(gr, dict) else {'pads': gr}
                ok &= self.enrutar_red(net, v2)
            return ok
        w = via.get('ancho', ancho(net))
        pads = [p for p in self.pads if p['net'] == net]
        if 'pads' in via:
            pads = [p for p in pads if p['parte'] + '.' + p['pad'] in via['pads']]
        if len(pads) < 2:
            return True
        bloq = self.R.bloqueo(self.cobre_ajeno(net), w, CLR)
        caminos = self.trazas.setdefault(net, [])
        juntas = self.juntas.setdefault(net, set())
        centros = {p['parte'] + '.' + p['pad']: self.R.idx(p['x'], p['y']) for p in pads}
        celdas_arbol = set()
        for c, _ in caminos:
            if any(q in c for q in centros.values()):
                celdas_arbol |= set(c)
        conectados = {k for k, v in centros.items() if v in celdas_arbol}
        if not conectados:
            primero = via.get('desde', pads[0]['parte'] + '.' + pads[0]['pad'])
            conectados.add(primero)
            celdas_arbol.add(centros[primero])
        orden = via.get('orden')
        while len(conectados) < len(centros):
            pend = [k for k in centros if k not in conectados]
            if orden:
                pend2 = [k for k in orden if k in pend]
                if pend2:
                    pend = pend2[:1]
            destinos = {centros[k] for k in pend}
            wp = via.get('puntos', {}).get(pend[0]) if len(pend) == 1 else None
            srcs = set(celdas_arbol)
            cam = []
            inicio = None
            for punto in (wp or []) + [None]:
                dst = destinos if punto is None else {self.R.idx(punto[0] + D.DX, punto[1] + D.DY)}
                if punto is not None and bloq[next(iter(dst))]:
                    print('  punto de paso bloqueado en %s: %s' % (net, punto))
                    return False
                tramo = self.R.astar(bloq, srcs, dst, inicio=inicio)
                if tramo is None:
                    print('  FALLA %s hacia %s (punto %s)' % (net, pend, punto))
                    return False
                cam = tramo if not cam else cam + tramo[1:]
                srcs = {tramo[-1]}
                inicio = self.R.ultimo_estado
            juntas.add(cam[0])
            caminos.append((cam, w))
            celdas_arbol |= set(cam)
            conectados |= {k for k, v in centros.items() if v in celdas_arbol}
        return True

    def polilineas(self, net):
        """Lista de (puntos, ancho); corta los caminos en las juntas de ramas."""
        juntas = set(self.juntas.get(net, set()))
        for c, _ in self.trazas.get(net, []):
            juntas.add(c[0]); juntas.add(c[-1])
        # todo pad de la red por el que pase una pista queda como vertice
        juntas |= {self.R.idx(p['x'], p['y']) for p in self.pads if p['net'] == net}
        out = []
        for c, w in self.trazas.get(net, []):
            s = set(simplificar(c))
            pts = [q for q in c if q in s or q in juntas]
            # quitar duplicados consecutivos
            limpio = [pts[0]] + [q for a, q in zip(pts, pts[1:]) if q != a]
            out.append(([self.R.xy(*q) for q in limpio], w))
        return out


def unir_gnd(E, max_iter=8):
    """Une las islas de GND con pistas hasta que todo el GND sea una sola pieza."""
    import numpy as np
    import shapely
    from pcb_drc import relleno_gnd, grupos_gnd
    for _ in range(max_iter):
        tr = {n: E.polilineas(n) for n in E.trazas}
        rel, _m = relleno_gnd(D.W, D.H, E.pads, tr)
        grupos = grupos_gnd(E.pads, tr, rel)
        if len(grupos) <= 1:
            return True
        grupos.sort(key=len, reverse=True)
        principal = set(grupos[0])
        cobre = [p['geom'] for p in E.pads if p['parte'] + '.' + p['pad'] in principal]
        u = unary_union(cobre + [rel])
        comps = list(u.geoms) if hasattr(u, 'geoms') else [u]
        zona = unary_union([c for c in comps if any(c.intersects(p['geom']) for p in E.pads
                                                     if p['parte'] + '.' + p['pad'] in principal)])
        w = ancho('GND')
        bloq = E.R.bloqueo(E.cobre_ajeno('GND'), w, CLR)
        # destino: centro de un pad GND (o vertice de pista GND) del grupo principal, asi la pista
        # termina en algo conectado (sin extremos sueltos dentro del relleno)
        destinos = {E.R.idx(p['x'], p['y']) for p in E.pads if p['parte'] + '.' + p['pad'] in principal}
        for c, _w in E.trazas.get('GND', []):
            destinos |= set(c)
        isla = grupos[1]
        fuentes = {E.R.idx(p['x'], p['y']) for p in E.pads if p['parte'] + '.' + p['pad'] in isla}
        cam = E.R.astar(bloq, fuentes, destinos)
        if cam is None:
            print('  no se pudo unir la isla GND', isla)
            return False
        cam = [(int(i), int(j)) for i, j in cam]
        print('  GND: isla %s unida con una pista de %d celdas' % (isla, len(cam)))
        E.trazas.setdefault('GND', []).append((cam, w))
        E.juntas.setdefault('GND', set()).add(cam[0])
    return False


def enrutar_todo():
    E = Estado()
    ok = True
    for net in D.ORDEN:
        r = E.enrutar_red(net, D.VIAS.get(net))
        print('%-5s %s' % (net, 'ok' if r else 'FALLA'))
        ok &= r
    ok &= unir_gnd(E)
    return E, ok


def guardar(E, archivo):
    res = {n: E.polilineas(n) for n in E.trazas}
    json.dump(res, open(archivo, 'w'), indent=0)


if __name__ == '__main__':
    E, ok = enrutar_todo()
    guardar(E, 'v20_ruteo.json')
