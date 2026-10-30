"""Genera PCB_ESP32_v19.brd y PCB_ESP32_v19.sch a partir de la v10.

Uso (desde la carpeta del proyecto):
    pip install shapely matplotlib numpy
    python3 herramientas/generar_v19.py

Hace todo el proceso: coloca las piezas, enruta en la cara inferior, simula el
relleno de GND, revisa las reglas (DRC propio) y escribe los archivos para
Fusion/EAGLE, la vista PNG, el PDF 1:1 de cobre y un reporte.
"""
import copy
import json
import os
import sys
import xml.etree.ElementTree as ET

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)

import diseno_v19 as D                      # noqa: E402
import enrutar_v19 as E                     # noqa: E402
import pcb_drc as R                         # noqa: E402
import vista                                # noqa: E402
from pcb_geo import HUELLAS, REGLAS, ancho  # noqa: E402

BASE_BRD = os.path.join(RAIZ, 'PCB_ESP32_v10.brd')
BASE_SCH = os.path.join(RAIZ, 'PCB_ESP32_v10.sch')
SALIDA = os.path.join(RAIZ, 'PCB_ESP32_v19')
LIB = 'PCB_PBL_Semiconductores'
CABECERA = '<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE eagle SYSTEM "eagle.dtd">\n'


def f(v):
    """Numero corto para el XML."""
    s = ('%.4f' % v).rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def el(tag, **at):
    e = ET.Element(tag)
    for k, v in at.items():
        e.set(k.rstrip('_'), v if isinstance(v, str) else f(v))
    return e


# ------------------------------------------------------------------ paquetes
def paquete_xml(nombre):
    h = HUELLAS[nombre]
    p = el('package', name=nombre)
    d = ET.SubElement(p, 'description')
    d.text = h['desc']
    for (pn, x, y, dr, dia, forma) in h['pads']:
        p.append(el('pad', name=pn, x=x, y=y, drill=dr, diameter=dia, shape=forma))
    xs = [q[1] for q in h['pads']]
    ys = [q[2] for q in h['pads']]

    def rect(x0, y0, x1, y1, capa='21', w=0.2):
        for a, b in [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]:
            p.append(el('wire', x1=a[0], y1=a[1], x2=b[0], y2=b[1], width=w, layer=capa))

    if nombre.startswith(('SOCKET', 'MALE')):
        rect(-1.6, 1.27, 1.6, min(ys) - 1.27)
        p.append(el('text', x=-1.9, y=0, size=0.8, layer='21', align='center-right'))
        p[-1].text = '1'
    elif nombre == 'ESP32_DEVKIT38':
        sep = max(xs)
        rect(-1.6, 1.27, 1.6, min(ys) - 1.27)
        rect(sep - 1.6, 1.27, sep + 1.6, min(ys) - 1.27)
        x0, y0, x1, y1 = h['cuerpo']
        rect(x0, y0, x1, y1, '51', 0.15)
        for txt, x, y in [('ANTENA', sep / 2, 3.0), ('USB', sep / 2, min(ys) - 2.0)]:
            t = el('text', x=x, y=y, size=1, layer='21', align='center')
            t.text = txt
            p.append(t)
    elif nombre in ('TERM2_5MM', 'RES_H_T', 'CAP_5MM'):
        rect(*h['cuerpo'])
        if nombre == 'RES_H_T':
            t = el('text', x=-1.0, y=2.2, size=0.8, layer='21')
            t.text = 'NO'
            p.append(t)
    elif nombre == 'RES_V':
        p.append(el('circle', x=0, y=0, radius=1.9, width=0.2, layer='21'))
        p.append(el('wire', x1=1.9, y1=0, x2=3.88, y2=0, width=0.2, layer='21'))
    elif nombre == 'CAP_E_2_54':
        p.append(el('circle', x=1.27, y=0, radius=2.6, width=0.2, layer='21'))
        t = el('text', x=-1.4, y=1.4, size=1, layer='21')
        t.text = '+'
        p.append(t)
    elif nombre in ('WIREPAD', 'JPAD'):
        p.append(el('circle', x=0, y=0, radius=1.9 if nombre == 'WIREPAD' else 1.6, width=0.2, layer='21'))
    t = el('text', x=0, y=max(ys) + 2.2, size=1, layer='25')
    t.text = '>NAME'
    p.append(t)
    t = el('text', x=0, y=min(ys) - 2.6, size=0.8, layer='27')
    t.text = '>VALUE'
    p.append(t)
    return p


def reemplazar_paquetes(lib):
    viejo = lib.find('packages')
    nuevo = ET.Element('packages')
    usados = list(HUELLAS)
    for pk in viejo:  # conservar paquetes de la v10 que no se redefinen
        if pk.get('name') not in usados:
            nuevo.append(pk)
    for n in usados:
        nuevo.append(paquete_xml(n))
    idx = list(lib).index(viejo)
    lib.remove(viejo)
    lib.insert(idx, nuevo)


# ------------------------------------------------------------------ serigrafia
def textos_serigrafia(P, pads):
    """(x, y, texto, tamano, capa, align) para nombres de pines y avisos."""
    pp = {(p['parte'], p['pad']): p for p in pads}
    T = []

    def junto(parte, pad, txt, dx, align, size=0.8, capa='21'):
        p = pp[(parte, pad)]
        T.append((p['x'] + dx, p['y'], txt, size, capa, align))

    for k, n in enumerate(['VDD', 'GND', 'SCL', 'SDA', 'ADDR', 'ALRT', 'A0', 'A1', 'A2', 'A3']):
        junto('U2', str(k + 1), n, -1.9, 'center-right')
    for k, n in enumerate(['32K', 'SQW', 'SCL', 'SDA', 'VCC', 'GND']):
        junto('U5', str(k + 1), n, -1.9, 'center-right')
    for k, n in enumerate(['GND', 'VCC', 'MISO', 'MOSI', 'SCK', 'CS']):
        junto('U4', str(k + 1), n, 1.9, 'center-left')
    for parte, ins in [('J2', [1, 2, 3]), ('J6', [4, 5, 6]), ('J7', [7, 8])]:
        for k, i in enumerate(ins):
            junto(parte, str(k + 1), 'IN%d' % i, 1.9, 'center-left')
    junto('J5', '1', '5V', 0, 'bottom-center')
    T[-1] = (T[-1][0], T[-1][1] - 2.4, '5V', 0.8, '21', 'center')
    junto('J5', '2', 'GND', 0, 'center')
    T[-1] = (T[-1][0], T[-1][1] - 2.4, 'GND', 0.8, '21', 'center')
    for k, n in enumerate(['VDD', 'DQ', 'GND']):
        junto('J3', str(k + 1), n, -1.9, 'center-right')
    junto('J1', '1', 'PANEL+', 0, 'center')
    T[-1] = (T[-1][0], T[-1][1] + 4.3, 'PANEL +', 0.8, '21', 'center')
    junto('J1', '2', '-', 0, 'center')
    T[-1] = (T[-1][0], T[-1][1] + 4.3, '-', 1.0, '21', 'center')
    junto('J4', '1', 'REF+', 0, 'center')
    T[-1] = (T[-1][0] - 3.6, T[-1][1], 'REF+', 0.8, '21', 'center-right')
    junto('J4', '2', '-', 0, 'center')
    T[-1] = (T[-1][0] - 3.6, T[-1][1], '-', 1.0, '21', 'center-right')
    for k in range(1, 9):
        c = pp[('COM%d' % k, '1')]
        T.append((c['x'], c['y'] - 2.3, 'C%d' % k, 0.7, '21', 'center'))
    # nombres de GPIO junto a los pines usados del ESP32
    gpio_pad = {}
    for n, lst in D.REDES.items():
        for (e, pd) in lst:
            if e == 'U1':
                gpio_pad[pd] = n
    for pd, n in gpio_pad.items():
        p = pp[('U1', pd)]
        izq = p['x'] < D.XL + 1
        T.append((p['x'] + (1.9 if izq else -1.9), p['y'], n, 0.7, '21',
                  'center-left' if izq else 'center-right'))
    a = pp[('JP1A', '1')]
    b = pp[('JP1B', '1')]
    T.append((a['x'] + 1.9, (a['y'] + b['y']) / 2, 'PUENTE 3V3', 0.8, '21', 'center-left'))
    T.append((2.5, D.H - 2.6, 'PBL Semiconductores - Monitor I-V  v19', 1.2, '21', 'center-left'))
    return T


def contornos_docu(P):
    """Contornos (capa 51) de los modulos montados en tira hembra."""
    pos = {p.nombre: p for p in P}
    u2, u5, u4 = pos['U2'], pos['U5'], pos['U4']
    ads = (u2.x - 2.0, u2.y - 22.86 - 2.6, u2.x + 15.8, u2.y + 2.6, 'ADS1115 (modulo plano, 28x17.8)')
    rtc = (u5.x - 5.0, u5.y - 12.7 - 2.5, u5.x + 5.0, u5.y + 2.5, 'RTC parado (pines en L)')
    sd = (u4.x - 5.0, u4.y - 12.7 - 2.5, u4.x + 5.0, u4.y + 2.5, 'microSD parada')
    return [ads, rtc, sd]


# ------------------------------------------------------------------ .brd
def escribir_brd(st, tr, top, archivo):
    tree = ET.parse(BASE_BRD)
    root = tree.getroot()
    b = root.find('drawing/board')
    # plain
    plain = b.find('plain')
    for c in list(plain):
        plain.remove(c)
    W, H = D.W, D.H
    for a, c in [((0, 0), (W, 0)), ((W, 0), (W, H)), ((W, H), (0, H)), ((0, H), (0, 0))]:
        plain.append(el('wire', x1=a[0], y1=a[1], x2=c[0], y2=c[1], width=0, layer='20'))
    for (x, y, txt, size, capa, align) in textos_serigrafia(st.P, st.pads):
        t = el('text', x=x, y=y, size=size, layer=capa, align=align)
        t.text = txt
        plain.append(t)
    for (x0, y0, x1, y1, txt) in contornos_docu(st.P):
        for a, c in [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]:
            plain.append(el('wire', x1=a[0], y1=a[1], x2=c[0], y2=c[1], width=0.15, layer='51'))
        t = el('text', x=x0 + 0.5, y=y1 - 1.5, size=0.8, layer='51')
        t.text = txt
        plain.append(t)
    for (pts, w, net) in top:  # dibujo del puente en serigrafia
        plain.append(el('wire', x1=pts[0][0], y1=pts[0][1], x2=pts[1][0], y2=pts[1][1], width=0.3, layer='21'))
    # libreria
    reemplazar_paquetes(b.find('libraries/library'))
    # reglas
    dr = b.find('designrules')
    dr.set('name', 'PBL v19 (planchado / percloruro)')
    nuevos = {'mdWireWire': '1mm', 'mdWirePad': '1mm', 'mdWireVia': '1mm', 'mdPadPad': '0.5mm',
              'mdPadVia': '0.5mm', 'mdViaVia': '0.5mm', 'mdCopperDimension': '%gmm' % REGLAS['cobre_borde'],
              'msWidth': '0.8mm', 'psElongationLong': str(REGLAS['elong_long']),
              'psElongationOffset': str(REGLAS['elong_long']), 'layerSetup': '(1*16)'}
    for prm in dr.findall('param'):
        if prm.get('name') in nuevos:
            prm.set('value', nuevos[prm.get('name')])
    # clases: ancho minimo 0.8; separacion 0 = usar las reglas de diseno (pad-pad 0.5, pista 1.0)
    cl = b.find('classes')
    for c in cl:
        c.set('width', '0.8')
        for cc in c:
            cc.set('value', '0')
    clase = {'PV': '1', 'LB': '1', '5V': '2', '3V3': '2', 'GND': '2'}
    # elementos
    els = b.find('elements')
    for c in list(els):
        els.remove(c)
    for p in st.P:
        e = el('element', name=p.nombre, library=LIB, package=p.paquete, value=p.valor,
               x=p.x, y=p.y, rot='R%d' % (p.rot % 360))
        els.append(e)
    # senales
    sig = b.find('signals')
    for c in list(sig):
        sig.remove(c)
    for net, lst in D.REDES.items():
        s = el('signal', name=net, class_=clase.get(net, '0'))
        for (e, pd) in lst:
            s.append(el('contactref', element=e, pad=pd))
        for (pts, w) in tr.get(net, []):
            for a, c in zip(pts, pts[1:]):
                s.append(el('wire', x1=a[0], y1=a[1], x2=c[0], y2=c[1], width=w, layer='16'))
        for (pts, w, n2) in top:
            if n2 == net:
                s.append(el('wire', x1=pts[0][0], y1=pts[0][1], x2=pts[1][0], y2=pts[1][1], width=w, layer='1'))
        if net == 'GND':
            pg = el('polygon', width=REGLAS['ancho_relleno'], layer='16', isolate=REGLAS['aislamiento_gnd'],
                    pour='solid', orphans='no', thermals='no', rank='1')
            m = 0.5
            for (x, y) in [(m, m), (W - m, m), (W - m, H - m), (m, H - m)]:
                pg.append(el('vertex', x=x, y=y))
            s.append(pg)
        sig.append(s)
    ET.indent(root, space='')
    with open(archivo, 'w', encoding='utf-8') as fh:
        fh.write(CABECERA + ET.tostring(root, encoding='unicode'))


# ------------------------------------------------------------------ .sch
JPAD_SYM = '''<symbol name="SYM_JPAD">
<wire x1="0" y1="2.54" x2="12.7" y2="2.54" width="0.254" layer="94"/>
<wire x1="12.7" y1="2.54" x2="12.7" y2="-2.54" width="0.254" layer="94"/>
<wire x1="12.7" y1="-2.54" x2="0" y2="-2.54" width="0.254" layer="94"/>
<wire x1="0" y1="-2.54" x2="0" y2="2.54" width="0.254" layer="94"/>
<text x="0" y="3.556" size="1.778" layer="95">&gt;NAME</text>
<text x="0" y="-4.826" size="1.778" layer="96">&gt;VALUE</text>
<pin name="1" x="-2.54" y="0" length="short" direction="pas"/>
</symbol>'''
JPAD_DS = '''<deviceset name="JPAD" prefix="JP" uservalue="yes">
<gates><gate name="G$1" symbol="SYM_JPAD" x="0" y="0"/></gates>
<devices><device name="" package="JPAD"><connects>
<connect gate="G$1" pin="1" pad="1"/>
</connects><technologies><technology name=""/></technologies></device></devices>
</deviceset>'''


def escribir_sch(st, archivo):
    tree = ET.parse(BASE_SCH)
    root = tree.getroot()
    s = root.find('drawing/schematic')
    lib = s.find('libraries/library')
    reemplazar_paquetes(lib)
    if lib.find("symbols/symbol[@name='SYM_JPAD']") is None:
        lib.find('symbols').append(ET.fromstring(JPAD_SYM))
    if lib.find("devicesets/deviceset[@name='JPAD']") is None:
        lib.find('devicesets').append(ET.fromstring(JPAD_DS))
    # pad -> pin por deviceset
    pin_de = {}
    for ds in lib.find('devicesets'):
        m = {}
        for c in ds.iter('connect'):
            m[c.get('pad')] = c.get('pin')
        pin_de[ds.get('name')] = m
    sym_de = {ds.get('name'): ds.find('gates/gate').get('symbol') for ds in lib.find('devicesets')}
    pins_sym = {}
    for sy in lib.find('symbols'):
        pins_sym[sy.get('name')] = {p.get('name'): (float(p.get('x')), float(p.get('y'))) for p in sy.findall('pin')}
    partes = s.find('parts')
    for p in list(partes):
        if p.get('name') == 'TP1':
            partes.remove(p)
    valor = {p.nombre: p.valor for p in st.P}
    for n in ('JP1A', 'JP1B'):
        if partes.find("part[@name='%s']" % n) is None:
            partes.append(el('part', name=n, library=LIB, deviceset='JPAD', device='', value=valor[n]))
    ds_de = {p.get('name'): p.get('deviceset') for p in partes}
    sheet = s.find('sheets/sheet')
    inst = sheet.find('instances')
    for i in list(inst):
        if i.get('part') == 'TP1':
            inst.remove(i)
    pos_jp = {'JP1A': (280.0, 266.0), 'JP1B': (280.0, 253.3)}
    for n, (x, y) in pos_jp.items():
        if inst.find("instance[@part='%s']" % n) is None:
            inst.append(el('instance', part=n, gate='G$1', x=x, y=y))
    ipos = {i.get('part'): (float(i.get('x')), float(i.get('y'))) for i in inst}
    # segmentos existentes (pin con su cablecito y etiqueta), por (parte, pin)
    seg = {}
    nets = sheet.find('nets')
    for n in nets:
        for sg in n.findall('segment'):
            pr = sg.find('pinref')
            seg[(pr.get('part'), pr.get('pin'))] = sg
    for c in list(nets):
        nets.remove(c)

    def segmento(parte, pin):
        if (parte, pin) in seg:
            return copy.deepcopy(seg[(parte, pin)])
        px, py = pins_sym[sym_de[ds_de[parte]]][pin]
        ix, iy = ipos[parte]
        x, y = ix + px, iy + py
        dx = -5.08 if px <= 0 else 5.08
        sg = ET.Element('segment')
        sg.append(el('pinref', part=parte, gate='G$1', pin=pin))
        sg.append(el('wire', x1=x, y1=y, x2=x + dx, y2=y, width=0.1524, layer='91'))
        lb = el('label', x=x + dx, y=y, size=1.778, layer='95')
        if dx < 0:
            lb.set('rot', 'R180')
        sg.append(lb)
        return sg

    clase = {'PV': '1', 'LB': '1', '5V': '2', '3V3': '2', 'GND': '2'}
    for net, lst in D.REDES.items():
        nn = el('net', name=net, class_=clase.get(net, '0'))
        for (parte, pad) in lst:
            pin = pin_de[ds_de[parte]][pad]
            nn.append(segmento(parte, pin))
        nets.append(nn)
    # clases como en la placa
    for c in s.find('classes'):
        c.set('width', '0.8')
        for cc in c:
            cc.set('value', '0')
    for t in sheet.find('plain').iter('text'):
        if t.text and t.text.startswith('PBL Semiconductores'):
            t.text = 'PBL Semiconductores EE2002 - Monitor I-V de panel 1.5 W (ESP32 DevKitC) - v19'
    ET.indent(root, space='')
    with open(archivo, 'w', encoding='utf-8') as fh:
        fh.write(CABECERA + ET.tostring(root, encoding='unicode'))


# ------------------------------------------------------------------ revisiones de archivo
def revisar_archivos(brd, sch):
    """Compara partes, paquetes y redes entre .brd y .sch (anotacion directa/inversa)."""
    err = []
    rb = ET.parse(brd).getroot()
    rs = ET.parse(sch).getroot()
    eb = {e.get('name'): (e.get('package'), e.get('value')) for e in rb.iter('element')}
    s = rs.find('drawing/schematic')
    ds = {d.get('name'): d for d in s.iter('deviceset')}
    pk_de = {n: d.find('devices/device').get('package') for n, d in ds.items()}
    ps = {p.get('name'): (pk_de[p.get('deviceset')], p.get('value')) for p in s.find('parts')}
    if eb != ps:
        err.append('partes distintas entre brd y sch: %s' % set(eb.items()).symmetric_difference(ps.items()))
    pin_de = {n: {c.get('pin'): c.get('pad') for c in d.iter('connect')} for n, d in ds.items()}
    ds_de = {p.get('name'): p.get('deviceset') for p in s.find('parts')}
    nets_s = {}
    for n in s.iter('net'):
        nets_s[n.get('name')] = sorted((pr.get('part'), pin_de[ds_de[pr.get('part')]][pr.get('pin')])
                                       for pr in n.iter('pinref'))
    nets_b = {sg.get('name'): sorted((c.get('element'), c.get('pad')) for c in sg.findall('contactref'))
              for sg in rb.iter('signal')}
    if nets_s != nets_b:
        for k in set(nets_s) | set(nets_b):
            if nets_s.get(k) != nets_b.get(k):
                err.append('red %s distinta: sch=%s brd=%s' % (k, nets_s.get(k), nets_b.get(k)))
    # paquetes iguales en ambas librerias
    pb = {p.get('name'): ET.tostring(p) for p in rb.iter('package')}
    pss = {p.get('name'): ET.tostring(p) for p in rs.iter('package')}
    for k in pb:
        if k in pss and pb[k] != pss[k]:
            err.append('paquete %s distinto entre brd y sch' % k)
    return err


def extremos(st, tr):
    """En EAGLE una pista conecta por sus extremos: cada extremo debe caer en el centro
    de un pad de su red o sobre un vertice de otra pista de la misma red."""
    err = []
    for net, cams in tr.items():
        centros = {(round(p['x'], 3), round(p['y'], 3)) for p in st.pads if p['net'] == net}
        for k, (c, w) in enumerate(cams):
            for q in (c[0], c[-1]):
                q = (round(q[0], 3), round(q[1], 3))
                if q in centros:
                    continue
                otros = {(round(x, 3), round(y, 3)) for j, (c2, _) in enumerate(cams) if j != k for (x, y) in c2}
                if q not in otros:
                    err.append('extremo suelto en %s: %s' % (net, q))
    return err


def main():
    st, ok = E.enrutar_todo()
    if not ok:
        print('EL ENRUTADO FALLO: revisa la colocacion en diseno_v19.py')
        sys.exit(1)
    tr = {n: st.polilineas(n) for n in st.trazas}
    pp = {(p['parte'], p['pad']): p for p in st.pads}
    top = []
    for a, b, n in D.PUENTES:
        A, B = pp[(a, '1')], pp[(b, '1')]
        top.append(([(A['x'], A['y']), (B['x'], B['y'])], 0.8, n))
    rel, _ = R.relleno_gnd(D.W, D.H, st.pads, tr)
    errores = R.drc(D.W, D.H, st.pads, tr, rel, top) + R.conectividad(st.pads, tr, rel, top)
    errores += extremos(st, tr)
    escribir_brd(st, tr, top, SALIDA + '.brd')
    escribir_sch(st, SALIDA + '.sch')
    errores += revisar_archivos(SALIDA + '.brd', SALIDA + '.sch')
    vista.dibujar(D.W, D.H, st.P, st.pads, tr, ancho, SALIDA + '_vista.png', relleno=rel,
                  puentes=[t[0] for t in top], cuerpos=contornos_docu(st.P),
                  titulo='PCB v19 - cara inferior vista desde arriba - %d puente(s) - %.1f x %.1f mm'
                  % (len(top), D.W, D.H))
    vista.pdf_cobre(D.W, D.H, st.pads, tr, rel, SALIDA + '_cobre_1a1.pdf')
    rep = dict(errores=errores, ancho=D.W, alto=D.H, puentes=[(a, b, n) for a, b, n in D.PUENTES],
               gpio=D.GPIO, redes={n: [list(x) for x in v] for n, v in D.REDES.items()})
    json.dump(rep, open(os.path.join(AQUI, 'reporte_v19.json'), 'w'), indent=1, ensure_ascii=False)
    print('\nDRC propio: %d errores' % len(errores))
    for e in errores:
        print('  -', e)
    print('Archivos: %s.brd / .sch / _vista.png / _cobre_1a1.pdf' % SALIDA)


if __name__ == '__main__':
    main()
