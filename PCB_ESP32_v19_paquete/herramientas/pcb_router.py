"""Enrutador de laberinto (A* en rejilla, 8 direcciones) para una sola capa.

Cada red se enruta respetando la separacion a todo el cobre ajeno. Las
conexiones de redes con varios pads se hacen como arbol: cada pad nuevo se
une al cobre ya enrutado de su red.
"""
import heapq
import math
import numpy as np
import shapely
from shapely.geometry import LineString, Point
from shapely.ops import unary_union

G = 0.3175  # paso de rejilla (2.54 / 8)
DIRS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]


class Router:
    def __init__(self, W, H, borde, margen=0.06):
        self.W, self.H, self.borde, self.margen = W, H, borde, margen
        self.nx = int(round(W / G)) + 1
        self.ny = int(round(H / G)) + 1
        xs = np.arange(self.nx) * G
        ys = np.arange(self.ny) * G
        self.X, self.Y = np.meshgrid(xs, ys, indexing='ij')

    def idx(self, x, y):
        return int(round(x / G)), int(round(y / G))

    def xy(self, i, j):
        return round(i * G, 4), round(j * G, 4)

    def bloqueo(self, ajeno, w, clr):
        """Mascara de celdas prohibidas para el centro de una pista de ancho w."""
        d = w / 2 + clr + self.margen
        zona = ajeno.buffer(d, 16) if ajeno is not None and not ajeno.is_empty else None
        m = np.zeros((self.nx, self.ny), bool)
        if zona is not None:
            m |= shapely.contains_xy(zona, self.X, self.Y)
        lim = self.borde + w / 2
        m |= (self.X < lim) | (self.Y < lim) | (self.X > self.W - lim) | (self.Y > self.H - lim)
        return m

    RUN_MIN = 4   # celdas rectas minimas despues de un quiebre (tramos a 45 grados visibles)

    def astar(self, bloq, fuentes, destinos, coste_extra=None, inicio=None):
        """A* con quiebres de 45 grados solamente (nunca 90) y tramos minimos entre quiebres.

        fuentes, destinos: conjuntos de celdas (i, j). inicio: (dir, recorrido) con el que
        se sigue un tramo anterior (para no quebrar a 90 grados en un punto de paso).
        Devuelve la lista de celdas; self.ultimo_estado guarda (dir, recorrido) al llegar.
        """
        if not destinos:
            return None
        dl = list(destinos)
        dx = np.array([d[0] for d in dl])
        dy = np.array([d[1] for d in dl])
        cache = {}

        def h(i, j):
            v = cache.get((i, j))
            if v is None:
                ddx = np.abs(dx - i)
                ddy = np.abs(dy - j)
                mn = np.minimum(ddx, ddy)
                mx = np.maximum(ddx, ddy)
                v = float(np.min(mx - mn + 1.4142 * mn))
                cache[(i, j)] = v
            return v

        K = self.RUN_MIN
        abiertos = []
        g = {}
        padre = {}
        d_ini, r_ini = inicio if inicio else (-1, K)
        for s in fuentes:
            st = (s[0], s[1], d_ini, r_ini)
            g[st] = 0.0
            heapq.heappush(abiertos, (h(*s), 0.0, st))
        destset = set(destinos)
        TURN = 0.4
        n = 0
        while abiertos:
            f, gc, st = heapq.heappop(abiertos)
            if gc > g.get(st, 1e18):
                continue
            i, j, d0, r0 = st
            if (i, j) in destset:
                self.ultimo_estado = (d0, r0)
                camino = [(i, j)]
                while st in padre:
                    st = padre[st]
                    camino.append((st[0], st[1]))
                return camino[::-1]
            n += 1
            if n > 4000000:
                return None
            for k, (di, dj) in enumerate(DIRS):
                if d0 >= 0 and k != d0:
                    dd = min((k - d0) % 8, (d0 - k) % 8)
                    if dd != 1 or r0 < K:
                        continue  # solo 45 grados, y solo tras un tramo recto minimo
                ni, nj = i + di, j + dj
                if ni < 0 or nj < 0 or ni >= self.nx or nj >= self.ny:
                    continue
                if bloq[ni, nj] and (ni, nj) not in destset:
                    continue
                if di and dj and bloq[i + di, j] and bloq[i, j + dj]:
                    continue
                c = 1.4142 if (di and dj) else 1.0
                if d0 >= 0 and k != d0:
                    c += TURN
                if coste_extra is not None:
                    c += coste_extra[ni, nj]
                r = min(r0 + 1, K) if k == d0 else 1
                ng = gc + c
                nst = (ni, nj, k, r)
                if ng < g.get(nst, 1e18):
                    g[nst] = ng
                    padre[nst] = st
                    heapq.heappush(abiertos, (ng + h(ni, nj), ng, nst))
        return None


def simplificar(celdas):
    """Quita puntos intermedios colineales."""
    if len(celdas) <= 2:
        return celdas
    out = [celdas[0]]
    for k in range(1, len(celdas) - 1):
        a, b, c = out[-1], celdas[k], celdas[k + 1]
        d1 = (np.sign(b[0] - a[0]), np.sign(b[1] - a[1]))
        d2 = (np.sign(c[0] - b[0]), np.sign(c[1] - b[1]))
        if d1 != d2:
            out.append(b)
    out.append(celdas[-1])
    return out
