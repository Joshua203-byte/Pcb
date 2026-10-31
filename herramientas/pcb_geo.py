"""Geometria de huellas, colocacion y reglas para la PCB v19.

Todas las medidas en mm. Origen de la placa abajo a la izquierda.
Cobre solo en la cara inferior (capa 16). Los puentes de cable se dibujan
como pistas en la capa superior (1): en Fusion cuentan como conexion
(no hay "cables de interconexion" sin rutear), pero esa capa NO se
fabrica; en la placa real son cables soldados entre pads JP.
"""
import math
from shapely.geometry import Point, LineString, box, Polygon
from shapely import affinity

# ---------------------------------------------------------------- reglas
def mil(v):
    """Milesimas de pulgada a mm (todo el diseno se define en mil, lineamiento L-07)."""
    return round(v * 0.0254, 4)


REGLAS = dict(
    pista_pista=mil(40),      # separacion entre pistas (mas que el minimo del curso: planchado)
    pista_pad=mil(40),        # separacion pista-pad
    pad_pad=mil(20),          # pads de una misma tira (100 mil) quedan a ~29 mil
    cobre_borde=mil(60),      # cobre al borde de la placa (curso: minimo 40 mil)
    aislamiento_gnd=mil(50),  # ISOLATE del poligono (curso: 40 mil o mas)
    ancho_relleno=mil(32),    # ancho de linea del relleno y de los brazos de alivio termico
    alivio_termico=mil(20),   # hueco entre pad GND y relleno en el alivio termico
    elong_long=50,            # pads ovalados de tiras: 1.8 x 2.7 mm
)

# clases de red del curso: SIGNAL 10 mil, POWER 15 mil (anchos minimos); los anchos usados son mayores
ANCHO = {  # ancho de pista por red
    'PV': mil(60), 'LB': mil(60), '5V': mil(40), 'GND': mil(40), '3V3': mil(40),
}
ANCHO_DEF = mil(32)
POWER = ('3V3', '5V', 'GND', 'PV', 'LB')


def ancho(net):
    return ANCHO.get(net, ANCHO_DEF)


# ---------------------------------------------------------------- huellas
# pad: (nombre, x, y, taladro, diametro, forma)  forma: round|square|long
def tira(n, taladro, dia, forma='long'):
    return [(str(i + 1), 0.0, -2.54 * i, taladro, dia,
             'square' if (i == 0 and forma != 'long') else forma)
            for i in range(n)]


def esp32(sep=25.4):
    pads = []
    for i in range(19):
        pads.append((str(i + 1), 0.0, -2.54 * i, 0.9, 1.8, 'long'))
    for i in range(19):
        pads.append((str(38 - i), sep, -2.54 * i, 0.9, 1.8, 'long'))
    return pads


SEP_ESP32 = 25.4  # MEDIR la DevKit real: algunas son 22.86

HUELLAS = {
    'ESP32_DEVKIT38': dict(
        pads=esp32(SEP_ESP32),
        desc='ESP32 DevKitC 38 pines en dos tiras hembra 1x19, filas a %.2f mm (MEDIR la tuya), pads ovalados 1.8x2.7, taladro 0.9' % SEP_ESP32,
        cuerpo=(-1.25, 6.5, SEP_ESP32 + 1.25, -48.2),
        textos=[('ANTENA', SEP_ESP32 / 2, 3.0, 1.0), ('USB', SEP_ESP32 / 2, -47.72, 1.0)]),
    'SOCKET_1X06': dict(pads=tira(6, 0.9, 1.8),
                        desc='Tira hembra 1x6, paso 2.54, taladro 0.9, pad ovalado 1.8x2.7'),
    'SOCKET_1X10': dict(pads=tira(10, 0.9, 1.8),
                        desc='Tira hembra 1x10, paso 2.54, taladro 0.9, pad ovalado 1.8x2.7'),
    'MALE_1X02': dict(pads=tira(2, 1.0, 1.8),
                      desc='Tira macho 1x2, paso 2.54, taladro 1.0, pad ovalado 1.8x2.7'),
    'MALE_1X03': dict(pads=tira(3, 1.0, 1.8),
                      desc='Tira macho 1x3, paso 2.54, taladro 1.0, pad ovalado 1.8x2.7'),
    'MALE_1X08': dict(pads=tira(8, 1.0, 1.8),
                      desc='Tira macho 1x8, paso 2.54, taladro 1.0, pad ovalado 1.8x2.7'),
    'MALE_1X10': dict(pads=tira(10, 1.0, 1.8),
                      desc='Tira macho 1x10, paso 2.54, taladro 1.0, pad ovalado 1.8x2.7'),
    'TERM2_5MM': dict(pads=[('1', 0, 0, 1.3, 3.2, 'square'), ('2', 5.08, 0, 1.3, 3.2, 'round')],
                      desc='Bornera de tornillo 2 pines, paso 5.08, taladro 1.3, pad 3.2',
                      cuerpo=(-2.6, 3.6, 7.7, -3.6)),
    'RES_V': dict(pads=[('1', 0, 0, 0.9, 2.4, 'square'), ('2', 5.08, 0, 0.9, 2.4, 'round')],
                  desc='Resistencia 1/2 W o 1 W montada vertical, separacion 5.08, taladro 0.9, pad 2.4'),
    'RES_H_T': dict(pads=[('1', 0, 0, 1.3, 3.0, 'square'), ('2', 12.7, 0, 0.9, 2.4, 'round')],
                    desc='Resistencia de carga 1/2 W acostada, separacion 12.7; pad 1 grande: aqui tambien se suelda el cable NO del rele',
                    cuerpo=(1.9, 1.8, 10.8, -1.8), textos=[('NO', -0.2, 2.6, 0.8)]),
    'CAP_5MM': dict(pads=[('1', 0, 0, 0.9, 2.4, 'square'), ('2', 5.08, 0, 0.9, 2.4, 'round')],
                    desc='Capacitor poliester, paso 5.08, taladro 0.9, pad 2.4',
                    cuerpo=(-1.6, 1.8, 6.7, -1.8)),
    'CAP_E_2_54': dict(pads=[('1', 0, 0, 0.8, 1.8, 'square'), ('2', 2.54, 0, 0.8, 1.8, 'round')],
                       desc='Capacitor electrolitico radial 2.54, pin 1 = +, taladro 0.8'),
    'WIREPAD': dict(pads=[('1', 0, 0, 1.3, 3.0, 'round')],
                    desc='Pad para cable al modulo de reles, taladro 1.3, pad 3.0'),
    'JPAD': dict(pads=[('1', 0, 0, 1.0, 2.5, 'round')],
                 desc='Pad exclusivo para cable puente (cara de componentes), taladro 1.0, pad 2.5'),
}


def rot_xy(x, y, rot):
    a = math.radians(rot)
    return (x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a))


def pad_shape(dia, forma, rot):
    """Forma del pad centrada en el origen (rot en grados)."""
    if forma == 'round':
        return Point(0, 0).buffer(dia / 2, 32)
    if forma == 'square':
        g = box(-dia / 2, -dia / 2, dia / 2, dia / 2)
    else:  # long: ovalo, largo = dia*(1+elong)
        L = dia * (1 + REGLAS['elong_long'] / 100.0)
        g = LineString([(-(L - dia) / 2, 0), ((L - dia) / 2, 0)]).buffer(dia / 2, 32)
    return affinity.rotate(g, rot, origin=(0, 0))


class Parte:
    def __init__(self, nombre, paquete, valor, x, y, rot=0):
        self.nombre, self.paquete, self.valor = nombre, paquete, valor
        self.x, self.y, self.rot = x, y, rot

    def pads(self):
        out = []
        for (pn, px, py, dr, dia, forma) in HUELLAS[self.paquete]['pads']:
            rx, ry = rot_xy(px, py, self.rot)
            cx, cy = self.x + rx, self.y + ry
            g = affinity.translate(pad_shape(dia, forma, self.rot), cx, cy)
            out.append(dict(parte=self.nombre, pad=pn, x=cx, y=cy, drill=dr,
                            dia=dia, forma=forma, geom=g))
        return out
