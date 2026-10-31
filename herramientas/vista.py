"""Dibuja la placa (pads, pistas, relleno GND y puentes) en un PNG."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly
from shapely.geometry import MultiPolygon

COL = {}
PALETA = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2',
          '#17becf', '#bcbd22', '#7f7f7f', '#393b79', '#637939', '#8c6d31', '#843c39']


def color(net):
    if net is None:
        return '#999999'
    if net == 'GND':
        return '#333333'
    if net not in COL:
        COL[net] = PALETA[len(COL) % len(PALETA)]
    return COL[net]


def poly(ax, g, **kw):
    if g.is_empty:
        return
    gs = g.geoms if hasattr(g, 'geoms') else [g]
    for p in gs:
        if p.geom_type != 'Polygon':
            continue
        ax.add_patch(MPoly(list(p.exterior.coords), closed=True, **kw))
        for h in p.interiors:
            ax.add_patch(MPoly(list(h.coords), closed=True, fc='white', ec='none', zorder=kw.get('zorder', 1) + 0.01))


def dibujar(W, H, partes, pads, trazas, anchos, archivo, relleno=None, puentes=(), titulo='', cuerpos=()):
    fig, ax = plt.subplots(figsize=(W / 7, H / 7))
    ax.add_patch(MPoly([(0, 0), (W, 0), (W, H), (0, H)], closed=True, fc='#f4efe2', ec='k', lw=1.5))
    if relleno is not None:
        poly(ax, relleno, fc='#c9b48a', ec='none', zorder=1)
    for (x0, y0, x1, y1, txt) in cuerpos:
        ax.add_patch(MPoly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], closed=True, fc='none',
                           ec='#888', lw=0.8, ls='--', zorder=6))
        ax.text(x0 + 0.5, y1 - 1.2, txt, fontsize=5, color='#777', zorder=6)
    for net, cams in trazas.items():
        for c, w in cams:
            xs = [p[0] for p in c]
            ys = [p[1] for p in c]
            lw = w * 72 / 7 / 25.4 * 7 * 0.98
            ax.plot(xs, ys, color=color(net), lw=lw, solid_capstyle='round', zorder=3)
    for p in pads:
        poly(ax, p['geom'], fc=color(p['net']), ec='k', lw=0.3, zorder=4)
        ax.add_patch(plt.Circle((p['x'], p['y']), p['drill'] / 2, fc='white', ec='none', zorder=5))
    for (a, b) in puentes:
        ax.plot([a[0], b[0]], [a[1], b[1]], color='red', lw=2, ls='--', zorder=7)
    for pt in partes:
        ax.text(pt.x, pt.y + 1.6, pt.nombre, fontsize=5, color='blue', zorder=8)
    for p in pads:
        if p['net'] and p['parte'] in ('U1',):
            ax.text(p['x'] + (1.5 if p['x'] > 60 else -1.5), p['y'], p['net'], fontsize=3.5,
                    ha='left' if p['x'] > 60 else 'right', va='center', zorder=8)
    ax.set_xlim(-2, W + 2)
    ax.set_ylim(-2, H + 2)
    ax.set_aspect('equal')
    ax.set_title(titulo)
    fig.tight_layout()
    fig.savefig(archivo, dpi=110)
    plt.close(fig)


def pdf_cobre(W, H, pads, trazas, relleno, archivo, nombres=()):
    """Cobre de la cara inferior a escala 1:1 en A4, visto desde arriba (sin espejar).

    Para planchado: se imprime asi, se apoya la cara impresa sobre el cobre y la
    imagen queda bien orientada vista desde los componentes.
    """
    from shapely.geometry import LineString, Point
    mm = 1 / 25.4
    fig = plt.figure(figsize=(210 * mm, 297 * mm))
    x0, y0 = 20, 297 - 30 - H
    ax = fig.add_axes([x0 / 210, y0 / 297, W / 210, H / 297])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis('off')
    k = dict(fc='black', ec='none')
    poly(ax, relleno, zorder=1, **k)
    for net, cams in trazas.items():
        for c, w in cams:
            g = LineString(c).buffer(w / 2, 24) if len(c) > 1 else Point(c[0]).buffer(w / 2)
            poly(ax, g, zorder=2, **k)
    for p in pads:
        poly(ax, p['geom'], zorder=3, **k)
        ax.add_patch(plt.Circle((p['x'], p['y']), min(0.4, p['drill'] / 2 * 0.6), fc='white', ec='none', zorder=4))
    # nombres en cobre: letras negras espejadas (en la placa se leen desde la cara de cobre)
    from matplotlib.textpath import TextPath
    from matplotlib.patches import PathPatch
    from matplotlib.font_manager import FontProperties
    from matplotlib.transforms import Affine2D
    fp = FontProperties(family='DejaVu Sans', weight='bold')
    for (n, x, y, s, r) in nombres:
        tp = TextPath((0, 0), n, size=1, prop=fp)
        bb = tp.get_extents()
        ancho = len(n) * s * 0.95
        sx = ancho / bb.width
        sy = s / bb.height
        tr_ = (Affine2D().translate(-bb.x0 - bb.width / 2, -bb.y0 - bb.height / 2)
               .scale(-sx, sy).rotate_deg(-r).translate(x, y))
        ax.add_patch(PathPatch(tr_.transform_path(tp), fc='black', ec='none', zorder=6))
    ax.add_patch(MPoly([(0, 0), (W, 0), (W, H), (0, H)], closed=True, fc='none', ec='black', lw=0.3, zorder=5))
    # regla de 50 mm para comprobar la escala de impresion
    ax2 = fig.add_axes([x0 / 210, (y0 - 18) / 297, 50 / 210, 6 / 297])
    ax2.set_xlim(0, 50)
    ax2.set_ylim(0, 6)
    ax2.axis('off')
    ax2.plot([0, 50], [2, 2], color='black', lw=1)
    for t in range(0, 51, 10):
        ax2.plot([t, t], [1, 3], color='black', lw=1)
    fig.text(x0 / 210, (y0 - 22) / 297, 'Esta regla debe medir 50 mm. Imprimir al 100 % (sin "ajustar a pagina").',
             fontsize=8)
    fig.text(x0 / 210, (y0 + H + 8) / 297, 'PCB_ESP32_v19 - cobre cara inferior con nombres, 1:1, listo para planchar '
             '(imprimir tal cual: los nombres salen al reves en el papel y derechos en la placa)', fontsize=7)
    fig.text(x0 / 210, (y0 + H + 4) / 297, 'La capa superior (puente JP1) NO se imprime: es un cable.', fontsize=8)
    fig.savefig(archivo)
    plt.close(fig)
