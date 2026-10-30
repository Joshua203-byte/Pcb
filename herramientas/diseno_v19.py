"""Colocacion, lista de redes y orden de enrutado de la PCB v19."""
from pcb_geo import Parte, SEP_ESP32

Y1 = 62.23                    # fila del pin 1 del ESP32 (antena sobresale arriba)
XL = 55.88                    # columna izquierda del ESP32
XR = XL + SEP_ESP32           # columna derecha (depende de la DevKit: 25.40 o 22.86)
XH = XR + 15.24               # columna de microSD y tiras de reles
W, H = XH + 6.35, 67.31       # tamano de placa (mm)
XA = 22.86                    # ADS1115
XRTC = 48.26                  # RTC DS3231


def fila(k):
    return round(Y1 - 2.54 * k, 4)


def partes():
    P = []
    a = P.append
    a(Parte('U1', 'ESP32_DEVKIT38', 'ESP32 DevKitC 38 pines', XL, Y1, 0))
    a(Parte('U2', 'SOCKET_1X10', 'ADS1115 (modulo)', XA, fila(4), 0))
    a(Parte('U5', 'SOCKET_1X06', 'Modulo RTC DS3231', XRTC, fila(4), 0))
    a(Parte('U4', 'SOCKET_1X06', 'Modulo microSD SPI', XH, fila(5), 0))
    a(Parte('J2', 'MALE_1X03', 'Reles IN1-IN3', XH, fila(11), 0))
    a(Parte('J6', 'MALE_1X03', 'Reles IN4-IN6', XH, fila(14), 0))
    a(Parte('J7', 'MALE_1X02', 'Reles IN7-IN8', XH, fila(17), 0))
    # lado izquierdo, debajo del bus I2C (3V3 llega por el puente JP1)
    a(Parte('JP1A', 'JPAD', 'Puente 1 (3V3)', 52.07, fila(3), 0))
    a(Parte('JP1B', 'JPAD', 'Puente 1 (3V3)', 52.07, 40.64, 0))
    a(Parte('J3', 'MALE_1X03', 'DS18B20', 43.18, 35.56, 0))
    a(Parte('R4', 'RES_V', '4.7k', 46.99, 35.56, 270))
    a(Parte('J5', 'MALE_1X02', 'Rele 5V y GND', 50.8, fila(18), 270))
    a(Parte('C4', 'CAP_E_2_54', '10u 16V', 53.34, fila(18), 270))
    # entrada analogica, a la izquierda del ADS1115 (piezas bajas: el modulo ADS queda encima a la derecha)
    a(Parte('R1', 'RES_V', '33k 1%', 6.35, 57.15, 270))
    a(Parte('R2', 'RES_V', '10k 1%', 11.43, 57.15, 270))
    a(Parte('R3', 'RES_V', '1k', 6.35, 46.99, 270))
    a(Parte('C1', 'CAP_5MM', '0.1u', 11.43, 41.91, 0))
    a(Parte('R_SH2', 'RES_V', '1', 11.43, 34.29, 270))
    a(Parte('J4', 'TERM2_5MM', 'Celda referencia', 6.35, 35.56, 270))
    a(Parte('R_SH1', 'RES_V', '1', 17.78, 26.67, 90))
    a(Parte('J1', 'TERM2_5MM', 'Panel', 3.81, 12.7, 0))
    # banco de cargas abajo: COM (PV) abajo, NO en medio, LB arriba
    for k in range(8):
        x = 12.7 + 4.445 * k
        a(Parte('COM%d' % (k + 1), 'WIREPAD', 'COM K%d' % (k + 1), x, 4.445, 0))
        a(Parte('RL%d' % (k + 1), 'RES_H_T', ['2.2', '4.7', '10', '22', '47', '100', '220', '470'][k],
                x, 9.525, 90))
    return P


# ---------------------------------------------------------------- redes
# (pad de U1 por GPIO) columna izquierda: pin k = fila k-1; derecha: pin 38-k = fila k
REDES = {
    '3V3': [('U1', '1'), ('U2', '1'), ('U5', '5'), ('R4', '1'), ('J3', '1'), ('JP1A', '1'), ('JP1B', '1')],
    '5V': [('U1', '19'), ('J5', '1'), ('U4', '2'), ('C4', '1')],
    'GND': [('U1', '14'), ('U1', '32'), ('U1', '38'), ('U2', '2'), ('U2', '5'), ('U2', '10'), ('U4', '1'),
            ('U5', '6'), ('J5', '2'), ('J1', '2'), ('J4', '2'), ('J3', '3'), ('R2', '2'),
            ('R_SH1', '1'), ('R_SH2', '2'), ('C1', '2'), ('C4', '2')],
    'SCL': [('U1', '7'), ('U2', '3'), ('U5', '3')],       # IO32
    'SDA': [('U1', '8'), ('U2', '4'), ('U5', '4')],       # IO33
    'DQ': [('U1', '12'), ('J3', '2'), ('R4', '2')],       # IO14
    'MISO': [('U1', '31'), ('U4', '3')],
    'MOSI': [('U1', '30'), ('U4', '4')],
    'SCK': [('U1', '29'), ('U4', '5')],
    'CS': [('U1', '28'), ('U4', '6')],
    'IN1': [('U1', '27'), ('J2', '1')],   # IO16
    'IN2': [('U1', '26'), ('J2', '2')],   # IO4
    'IN3': [('U1', '33'), ('J2', '3')],   # IO21
    'IN4': [('U1', '36'), ('J6', '1')],   # IO22
    'IN5': [('U1', '37'), ('J6', '2')],   # IO23
    'IN6': [('U1', '9'), ('J6', '3')],    # IO25
    'IN7': [('U1', '10'), ('J7', '1')],   # IO26
    'IN8': [('U1', '11'), ('J7', '2')],   # IO27
    'PV': [('J1', '1'), ('R1', '1')] + [('COM%d' % k, '1') for k in range(1, 9)],
    'DIV': [('R1', '2'), ('R2', '1'), ('R3', '1')],
    'A0': [('R3', '2'), ('C1', '1'), ('U2', '7')],
    'REF': [('J4', '1'), ('R_SH2', '1'), ('U2', '8')],
    'LB': [('U2', '9'), ('R_SH1', '2')] + [('RL%d' % k, '2') for k in range(1, 9)],
}
for k in range(1, 9):
    REDES['NO%d' % k] = [('RL%d' % k, '1')]

# GPIO de cada red (para la tabla del firmware)
GPIO = {'SCL': 32, 'SDA': 33, 'DQ': 14, 'MISO': 19, 'MOSI': 18, 'SCK': 5, 'CS': 17,
        'IN1': 16, 'IN2': 4, 'IN3': 21, 'IN4': 22, 'IN5': 23, 'IN6': 25, 'IN7': 26, 'IN8': 27}

# orden de enrutado: (red, [puntos de paso opcionales por tramo])
ORDEN = ['MISO', 'MOSI', 'SCK', 'CS', 'IN1', 'IN2',
         'IN3', 'IN4', 'IN5', 'IN6', 'IN7', 'IN8',
         'SCL', 'SDA', '3V3', 'DQ', '5V',
         'LB', 'REF', 'A0', 'DIV', 'PV']

# puntos de paso: las senales de reles bajan por el canal bajo el ESP32 y suben a las tiras
g = 0.3175
def rj(v):
    return round(round(v / g) * g, 4)


PASO = 6 * g  # 1.905 mm entre pistas paralelas
CX = {n: rj(61.0 + i * 2.54) for i, n in enumerate(['IN8', 'IN7', 'IN6'])}
CX.update({n: rj(XR - 10.16 + i * 2.54) for i, n in enumerate(['IN5', 'IN4', 'IN3'])})
ORDEN_BAJO = ['IN3', 'IN4', 'IN5', 'IN6', 'IN7', 'IN8']
BY = {n: rj(13.97 - i * PASO) for i, n in enumerate(ORDEN_BAJO)}
SX = {n: rj(XR + 2.857 + i * PASO) for i, n in enumerate(ORDEN_BAJO)}
DEST = {'IN3': 'J2.3', 'IN4': 'J6.1', 'IN5': 'J6.2', 'IN6': 'J6.3', 'IN7': 'J7.1', 'IN8': 'J7.2'}
FILA_ESP = {'IN3': 5, 'IN4': 2, 'IN5': 1, 'IN6': 8, 'IN7': 9, 'IN8': 10}
FILA_J = {'IN3': 13, 'IN4': 14, 'IN5': 15, 'IN6': 16, 'IN7': 17, 'IN8': 18}
Y5V = rj(BY['IN8'] - PASO)

VIAS = {
    '3V3': {'grupos': [['U1.1', 'U2.1', 'JP1A.1'], ['JP1B.1', 'U5.5', 'R4.1', 'J3.1']]},
    '5V': {'desde': 'U1.19', 'orden': ['C4.1', 'J5.1', 'U4.2'],
           'puntos': {'U4.2': [(XL, Y5V), (XH + 3.175, Y5V), (XH + 3.175, fila(6))]}},
    # LB: del ADS a la derivacion solo sensa (fina); la corriente de carga va gruesa
    'LB': {'grupos': [{'pads': ['U2.9', 'R_SH1.2'], 'ancho': 0.8},
                      {'pads': ['R_SH1.2'] + ['RL%d.2' % k for k in range(1, 9)], 'ancho': 1.5}]},
    'PV': {'grupos': [{'pads': ['J1.1'] + ['COM%d.1' % k for k in range(1, 9)], 'ancho': 1.5},
                      {'pads': ['J1.1', 'R1.1'], 'ancho': 0.8}]},
}
for n in CX:
    VIAS[n] = {'puntos': {DEST[n]: [(CX[n], fila(FILA_ESP[n])), (CX[n], BY[n]), (SX[n], BY[n]),
                                    (SX[n], fila(FILA_J[n]))]}}
PUENTES = [('JP1A', 'JP1B', '3V3')]
