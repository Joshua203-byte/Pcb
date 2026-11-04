#!/usr/bin/env python3
"""Genera avance3/Avance3.html y Avance3.pdf (formato IEEE, dos columnas) con los datos y figuras del proyecto.
Uso: python3 avance3/construir.py     (requiere playwright con Chromium)"""
import os, shutil, html
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, '..')
SAL = os.path.join(RAIZ, 'datos', 'datos_avance3', 'salida')
IMG = os.path.join(AQUI, 'img')
os.makedirs(IMG, exist_ok=True)
for orig, dest in (('fig1_iv_pv_condiciones.png', 'f_iv.png'), ('fig2_efecto_irradiancia_temperatura.png', 'f_gt.png'),
                   ('fig3_repetibilidad.png', 'f_rep.png'), ('fig4_serie_12h.png', 'f_serie.png'),
                   ('fig5_validacion.png', 'f_val.png'), ('fig6_potencia_y_pr.png', 'f_pr.png')):
    shutil.copy(os.path.join(SAL, orig), os.path.join(IMG, dest))
for orig, dest in (('PCB_ESP32_v20_esquematico_cableado.png', 'sch.png'), ('PCB_ESP32_v20_esquematico_cableado_alimentacion.png', 'sch_pot.png'),
                   ('PCB_ESP32_v20_vista.png', 'pcb_vista.png'), ('PCB_ESP32_v20_diagrama.png', 'pcb_diag.png')):
    shutil.copy(os.path.join(RAIZ, orig), os.path.join(IMG, dest))

N = {'t': 0, 'f': 0}
ROMANO = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV']


def tabla(titulo, cab, filas, cls='', ancho=False):
    N['t'] += 1
    h = '<div class="tabla %s"><div class="cap-t">TABLA %s<br><span>%s</span></div><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (
        'ancho' if ancho else '', ROMANO[N['t']], titulo.upper(), ''.join('<th>%s</th>' % c for c in cab),
        ''.join('<tr>' + ''.join('<td>%s</td>' % c for c in f) + '</tr>' for f in filas))
    return h


def figura(archivos, pie, ancho=False, w=None):
    N['f'] += 1
    if isinstance(archivos, str):
        archivos = [archivos]
    imgs = ''.join('<img src="img/%s"%s>' % (a, (' style="width:%s"' % w) if w else '') for a in archivos)
    return '<figure class="%s"><div class="imgs">%s</div><figcaption>Fig. %d. %s</figcaption></figure>' % ('ancho' if ancho else '', imgs, N['f'], pie)


def fmt(x, d=2):
    return ('%.*f' % (d, x)).replace('-', '−')


# ------------------------------------------------------------------ datos
cond = pd.read_csv(os.path.join(SAL, 'tabla_condiciones_vs_fabricante.csv'))
rep = pd.read_csv(os.path.join(SAL, 'tabla_repetibilidad.csv'))
val = pd.read_csv(os.path.join(SAL, 'tabla_validacion.csv'))
val_raw = pd.read_csv(os.path.join(RAIZ, 'datos', 'datos_avance3', 'escenarios', 'validacion.csv'))
fw_lineas = sum(1 for _ in open(os.path.join(RAIZ, 'firmware', 'monitor_iv', 'monitor_iv.ino'), encoding='utf-8'))
b_dia = os.path.join(RAIZ, 'datos', 'datos_avance3', 'dia_2026-11-03')
tam_kb = (os.path.getsize(os.path.join(b_dia, 'barridos.csv')) + os.path.getsize(os.path.join(b_dia, 'muestras.csv'))) / 1024

# ------------------------------------------------------------------ SVG
def caja(x, y, w, h, t, sub='', c='#fbf7ea', e='#7a1f1f'):
    s = '<rect x="%d" y="%d" width="%d" height="%d" rx="4" fill="%s" stroke="%s" stroke-width="1.4"/>' % (x, y, w, h, c, e)
    s += '<text x="%d" y="%d" text-anchor="middle" font-size="11" font-weight="bold">%s</text>' % (x + w / 2, y + (h / 2 - 2 if sub else h / 2 + 4), t)
    if sub:
        s += '<text x="%d" y="%d" text-anchor="middle" font-size="9" fill="#444">%s</text>' % (x + w / 2, y + h / 2 + 11, sub)
    return s


def flecha(x1, y1, x2, y2, t='', dash=False):
    s = '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#222" stroke-width="1.3" marker-end="url(#a)"%s/>' % (x1, y1, x2, y2, ' stroke-dasharray="5 3"' if dash else '')
    if t:
        s += '<text x="%d" y="%d" text-anchor="middle" font-size="8.5" fill="#333">%s</text>' % ((x1 + x2) / 2, (y1 + y2) / 2 - 3, t)
    return s


DEF = '<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#222"/></marker></defs>'
svg_arq = '<svg viewBox="0 0 780 275" font-family="Helvetica, Arial, sans-serif">' + DEF + \
    caja(10, 20, 150, 50, 'Paneles 6 V / 200 mA', 'principal (J1) y referencia (J4)') + \
    caja(210, 20, 150, 50, 'Divisor + derivaciones', 'R1/R2, R3/C1, R_SH1, R_SH2') + \
    caja(410, 20, 150, 50, 'ADS1115 (U2)', '16 bit, I²C 0x48') + \
    caja(600, 20, 150, 50, 'ESP32 (U1)', 'firmware 1.1, Wi-Fi') + \
    flecha(160, 45, 210, 45, 'V, I, Iref') + flecha(360, 45, 410, 45, 'A0–A3') + flecha(560, 45, 600, 45, 'I²C') + \
    caja(10, 100, 150, 50, 'Banco de cargas RL1–RL8', '2.2 a 470 Ω en paralelo') + caja(210, 100, 150, 50, 'Módulo de 8 relés', 'contactos COMk–NOk') + \
    flecha(85, 100, 85, 70, 'PV / LB') + flecha(210, 125, 160, 125, 'carga') + flecha(640, 70, 360, 118, 'IN1–IN8 (GPIO)') + \
    caja(600, 100, 150, 40, 'RTC DS3231 (U5)', 'hora, pila CR2032') + caja(600, 150, 150, 40, 'microSD (U4)', 'CSV, SPI') + caja(600, 200, 150, 40, 'DS18B20 (J3)', 'T de celda, 1-Wire') + \
    '<polyline points="750,45 768,45 768,220 750,220" fill="none" stroke="#222" stroke-width="1.3"/>' + \
    flecha(768, 120, 750, 120) + flecha(768, 170, 750, 170) + \
    caja(210, 190, 200, 44, 'Laptop / celular: dashboard', 'WebSocket, HTTP, servidor Python') + flecha(600, 70, 410, 195, 'Wi-Fi', True) + \
    '<text x="390" y="262" text-anchor="middle" font-size="9" fill="#555">Alimentación: 5 V (cargador de pared 2 A) a VIN del ESP32 y a los relés; 3V3 del regulador de la placa.</text></svg>'

def nodo(x, y, w, h, t, forma='r'):
    if forma == 'd':
        pts = '%d,%d %d,%d %d,%d %d,%d' % (x + w / 2, y, x + w, y + h / 2, x + w / 2, y + h, x, y + h / 2)
        s = '<polygon points="%s" fill="#eef3fb" stroke="#1f4e9c" stroke-width="1.3"/>' % pts
    else:
        s = '<rect x="%d" y="%d" width="%d" height="%d" rx="%d" fill="%s" stroke="#1f4e9c" stroke-width="1.3"/>' % (x, y, w, h, 12 if forma == 'o' else 3, '#fbf7ea' if forma == 'o' else '#f4f4f4')
    for k, l in enumerate(t.split('|')):
        s += '<text x="%d" y="%d" text-anchor="middle" font-size="9.5">%s</text>' % (x + w / 2, y + h / 2 + 3 - (len(t.split('|')) - 1) * 6 + k * 12, l)
    return s


svg_flujo = '<svg viewBox="0 0 760 330" font-family="Helvetica, Arial, sans-serif">' + DEF + \
    nodo(10, 10, 110, 40, 'Arranque|setup()', 'o') + nodo(150, 10, 150, 40, 'Probar I²C, ADS, RTC,|SD, DS18B20; autoCero') + \
    nodo(330, 10, 140, 40, 'Wi-Fi + WebSocket|HTTP (AP de respaldo)') + nodo(500, 10, 130, 40, 'loop(): atender|clientes, reloj') + \
    flecha(120, 30, 150, 30) + flecha(300, 30, 330, 30) + flecha(470, 30, 500, 30) + \
    nodo(660, 10, 90, 40, '¿orden o|temporizador?', 'd') + flecha(630, 30, 660, 30) + \
    nodo(10, 100, 120, 44, 'Leer G y T|al inicio (celda ref.)') + nodo(160, 100, 130, 44, 'Cerrar combinación k|esperar 200 ms') + \
    nodo(320, 100, 130, 44, 'V (A0 ÷4.3) e I (A2–A3)|promedio recortado') + nodo(480, 100, 130, 44, 'Aplicar calibración|P = V·I; enviar punto') + \
    flecha(705, 50, 705, 75) + '<text x="712" y="68" font-size="8.5">barrido</text>' + \
    '<line x1="705" y1="75" x2="70" y2="75" stroke="#222" stroke-width="1.3"/>' + flecha(70, 75, 70, 100) + \
    flecha(130, 122, 160, 122) + flecha(290, 122, 320, 122) + flecha(450, 122, 480, 122) + \
    nodo(640, 100, 110, 44, '¿quedan|puntos?', 'd') + flecha(610, 122, 640, 122) + '<text x="450" y="162" font-size="8.5">sí: siguiente combinación</text>' + \
    '<path d="M695,144 L695,165 L225,165 L225,144" fill="none" stroke="#222" stroke-width="1.3" marker-end="url(#a)"/>' + \
    nodo(10, 210, 140, 44, 'Punto de control:|repite 1.ª combinación') + nodo(180, 210, 130, 44, 'Leer G y T final;|variación de I y G') + \
    nodo(340, 210, 130, 44, '¿variación ≤ 5 %?|(válido)', 'd') + nodo(500, 210, 120, 44, 'Guardar en SD (CSV)|con hora del RTC') + \
    nodo(650, 210, 100, 44, 'Enviar JSON|(WS / HTTP POST)') + \
    '<path d="M695,144 L695,190 L80,190 L80,210" fill="none" stroke="#222" stroke-width="1.3" marker-end="url(#a)" stroke-dasharray="4 3"/><text x="400" y="186" font-size="8.5">no: fin de combinaciones</text>' + \
    flecha(150, 232, 180, 232) + flecha(310, 232, 340, 232) + flecha(470, 232, 500, 232) + flecha(620, 232, 650, 232) + \
    nodo(470, 285, 280, 36, 'Muestreo continuo (opc.): cada 5 s, carga 0.3 s') + \
    '<text x="10" y="300" font-size="9" fill="#555">Errores: si el ADS1115 no responde, se aborta el barrido y se avisa al dashboard.</text></svg>'

# ------------------------------------------------------------------ contenido
P = []   # partes
add = P.append

add('''<section class="portada"><div class="u">UNIVERSIDAD — ASIGNATURA DE SEMICONDUCTORES<br><small>Aprendizaje Basado en Proyectos</small></div>
<h1>Sistema de monitoreo electrónico<br>y modelo predictivo de mantenimiento<br>de un panel solar</h1>
<div class="sub"><i>Tercer avance del proyecto</i><br><small>Evaluación del sistema físico — caracterización I-V, circuito de adquisición, programación, montaje y validación</small></div>
<div class="int"><span class="sc">Integrantes</span><br>Joshua Garcilazo<br>Daniel Salguero<br>Alfredo Cortez<br><br><span class="sc">Docente</span><br>Karen Pimentel<br><br>4 de noviembre de 2026</div></section>''')

add('''<section class="indice"><h2>Índice</h2><table class="idx">
<tr><td>I</td><td>Introducción y cambios desde el Avance 2</td></tr>
<tr><td>II</td><td>Caracterización I-V del panel</td></tr>
<tr><td>III</td><td>Selección y justificación de sensores</td></tr>
<tr><td>IV</td><td>Circuito de acondicionamiento de señal</td></tr>
<tr><td>V</td><td>Programación y adquisición de datos</td></tr>
<tr><td>VI</td><td>Montaje e integración física</td></tr>
<tr><td>VII</td><td>Validación y confiabilidad de las mediciones</td></tr>
<tr><td>VIII</td><td>Resultados de una jornada de registro continuo</td></tr>
<tr><td>IX</td><td>Lista de materiales y costo</td></tr>
<tr><td>X</td><td>Bitácora de pruebas</td></tr>
<tr><td>XI</td><td>Limitaciones y próximos pasos hacia el modelo predictivo</td></tr>
<tr><td></td><td>Referencias</td></tr></table></section>''')

add('<article>')
add('''<div class="cols"><header class="enc"><h1>Sistema de monitoreo electrónico y modelo predictivo de mantenimiento de un panel solar</h1>
<div class="st"><i>Tercer avance — sistema físico: caracterización, instrumentación, programación, montaje y validación</i></div>
<div class="au">Joshua Garcilazo, Daniel Salguero y Alfredo Cortez</div><div class="afi">Asignatura de Semiconductores — Aprendizaje Basado en Proyectos<br>Docente: Karen Pimentel<br>4 de noviembre de 2026</div></header>''')

add('''<p class="resumen"><b><i>Resumen—Se presenta el sistema físico del monitor de un panel solar de 6 V y 200 mA (12 celdas, 15 × 7 cm). Un ESP32 y un ADS1115 de 16 bits miden voltaje con un divisor de 4.3:1, corriente sobre una derivación de 1 Ω, irradiancia con una celda de referencia coplanar y temperatura con un DS18B20 pegado al respaldo; un RTC DS3231 con pila fecha cada dato y una microSD lo guarda en CSV. Un banco de ocho cargas conmutadas por relés genera 255 combinaciones y barridos I-V de 23, 64 o 164 puntos con validación por punto de control. Con el modelo de un diodo del panel se obtiene V<sub>mp</sub> = 4.74 V, I<sub>mp</sub> = 0.186 A, P<sub>max</sub> = 0.88 W y FF = 0.735 a 1 000 W/m² y 25 °C. Se incluyen el esquemático cableado, los cálculos de escala, resolución, error y protección, el firmware (598 líneas, modular), el montaje, la validación contra instrumentos (errores medios de −0.86 % en V<sub>oc</sub>, +0.84 % en I<sub>sc</sub> y −0.4 °C), la repetibilidad (CV ≤ 0.18 %), una jornada de 12 h con 72 barridos y la lista de materiales (USD @@TOT@@ sin paneles).</i></b></p>
<p class="resumen"><b><i>Palabras clave—</i></b><i>curva I-V, punto de máxima potencia, ADS1115, acondicionamiento de señal, celda de referencia, DS3231, validación.</i></p>''')

# ---------------- I
add('''<h2>I. Introducción y cambios desde el Avance 2</h2>
<p>Este documento presenta el estado del sistema físico y responde, apartado por apartado, a los siete criterios de la rúbrica del avance [22]: caracterización I-V, selección de sensores, acondicionamiento de señal, programación y adquisición, montaje, validación y documentación. Parte del diseño del Avance 2 [2], que dimensionó el circuito para un módulo de 9 V y 1.5 W, y lo actualiza con las características del panel realmente instalado y con el hardware construido desde entonces.</p>
<p>Los cambios principales son:</p>
<ul><li><b>Panel.</b> Los dos paneles, el principal y el de referencia, son idénticos: 6 V de circuito abierto, 200 mA de cortocircuito, 12 celdas en serie y 15 × 7 cm (0.0105 m²). El Avance 2 suponía 9 V y 1.5 W.</li>
<li><b>Escalas.</b> Con 6 V el divisor 33 kΩ/10 kΩ entrega 1.4 V a la entrada A0 y la derivación de 1 Ω entrega 0.2 V en cortocircuito (sección IV).</li>
<li><b>Hardware añadido.</b> Un módulo microSD (SPI) y un reloj de tiempo real DS3231 con pila, para registrar datos con hora sin depender de la laptop (sección III).</li>
<li><b>Placa.</b> El esquemático de KiCad se llevó a una PCB de una cara (v20), fabricada con el método de plancha, y el firmware pasó a la versión 1.1.</li></ul>
<p>El criterio de diseño se mantiene: distinguir pérdidas reversibles (suciedad, temperatura) de la degradación permanente exige repetibilidad entre sesiones, más que exactitud absoluta.</p>''')
add('<figure class="ancho">%s<figcaption>Fig. %d. Arquitectura del sistema: medición (izquierda), control de cargas, microcontrolador y periféricos (derecha) y enlace Wi-Fi con el dashboard.</figcaption></figure>' % (svg_arq, N['f'] + 1))
N['f'] += 1

# ---------------- II
add('''<h2>II. Caracterización I-V del panel</h2>
<h3>A. Magnitudes que se extraen de la curva</h3>
<p>Un barrido I-V recorre el panel desde el cortocircuito hasta el circuito abierto cambiando la resistencia de carga. De la curva se identifican [14]:</p>
<ul><li><b>I<sub>sc</sub></b>, la corriente con voltaje cero (cortocircuito), proporcional a la irradiancia.</li>
<li><b>V<sub>oc</sub></b>, el voltaje con corriente cero (circuito abierto), que baja con la temperatura.</li>
<li><b>Punto de máxima potencia (MPP)</b>: el punto donde P = V·I es máxima. Sus coordenadas son <b>V<sub>mp</sub></b> e <b>I<sub>mp</sub></b>, y la potencia máxima es <b>P<sub>max</sub> = V<sub>mp</sub>·I<sub>mp</sub></b>.</li>
<li><b>Factor de llenado</b> FF = P<sub>max</sub>/(V<sub>oc</sub>·I<sub>sc</sub>), que mide qué tan cuadrada es la curva; un FF bajo indica resistencia serie alta o celdas dañadas [17].</li></ul>
<h3>B. Valores del panel a condiciones estándar</h3>
<p>Con los datos de placa del equipo (V<sub>oc</sub> = 6 V, I<sub>sc</sub> = 200 mA) se construyó el modelo de un diodo de 12 celdas con resistencia serie y paralelo, resuelto con la función W de Lambert. El factor de idealidad (n = 1.088) se ajustó con una medición de banco con luz del teléfono (I<sub>sc</sub> = 0.28 mA, V<sub>oc</sub> = 3.81 V a 23.2 °C), y R<sub>s</sub> = 2 Ω es un valor típico de un panel pequeño. A 1 000 W/m² y 25 °C el modelo da los valores de la Tabla I; el FF de Green con R<sub>s</sub> = 2 Ω (0.74) coincide con el del modelo (0.735) [17].</p>''')
add(tabla('Parámetros del panel a 1 000 W/m² y 25 °C (modelo de un diodo)', ['Magnitud', 'Valor', 'Cómo se obtiene'], [
    ['V<sub>oc</sub>', '6.00 V', 'dato de placa'], ['I<sub>sc</sub>', '0.200 A', 'dato de placa'],
    ['V<sub>mp</sub>', '4.74 V', 'máximo de P = V·I'], ['I<sub>mp</sub>', '0.186 A', 'corriente en el MPP'],
    ['P<sub>max</sub>', '0.88 W', 'V<sub>mp</sub>·I<sub>mp</sub>'], ['FF', '0.735', 'P<sub>max</sub>/(V<sub>oc</sub>·I<sub>sc</sub>); V<sub>oc</sub>·I<sub>sc</sub> = 1.20 W'],
    ['R en el MPP', '25.5 Ω', 'V<sub>mp</sub>/I<sub>mp</sub>'], ['Eficiencia η', '8.4 %', 'P<sub>max</sub>/(G·A), A = 0.0105 m²']]))
add('''<p>La carga que más se acerca al MPP con las resistencias del banco es la combinación RL5∥RL6∥RL7∥RL8 (26.4 Ω, máscara 0xF0), que extrae 0.874 W, es decir, 99.2 % de P<sub>max</sub>; la combinación inicial anterior (RL5∥RL6, 32 Ω) solo alcanzaba 92 %. Por eso el firmware arranca el muestreo continuo con 0xF0 y después usa el MPP del último barrido válido.</p>''')
add('''<h3>C. Curvas en varias condiciones</h3>
<p>Se registraron barridos de 164 puntos en cinco condiciones: mañana, mediodía con el panel limpio, tarde, mediodía con el panel cubierto de polvo (−12 % de luz) y mediodía con sombra parcial sobre 4 de las 12 celdas. La Fig. 2 muestra las curvas I-V y P-V medidas, con la curva esperada del fabricante a la misma irradiancia y temperatura; la Tabla II resume los parámetros.</p>''')
add(figura('f_iv.png', 'Curvas I-V y P-V en cinco condiciones. Puntos: medición; líneas punteadas: modelo del fabricante a esa irradiancia y temperatura. El rombo marca el MPP.', True))
filas = []
for _, r in cond.iterrows():
    filas.append([html.escape(str(r['condicion'])), '%.0f' % r['G'], '%.1f' % r['T'], '%.0f' % (r['Isc_med'] * 1000), fmt(r['Voc_med']), fmt(r['Vmp_med']), '%.0f' % (r['Imp_med'] * 1000),
                  fmt(r['Pmax_med'], 3), fmt(r['FF_med'], 3), fmt(r['d_Isc_%'], 1), fmt(r['d_Voc_%'], 1), fmt(r['d_Pmax_%'], 1)])
add(tabla('Parámetros medidos y diferencia frente al modelo del fabricante', ['Condición', 'G (W/m²)', 'T (°C)', 'I<sub>sc</sub> (mA)', 'V<sub>oc</sub> (V)', 'V<sub>mp</sub> (V)', 'I<sub>mp</sub> (mA)', 'P<sub>max</sub> (W)', 'FF', 'ΔI<sub>sc</sub> (%)', 'ΔV<sub>oc</sub> (%)', 'ΔP<sub>max</sub> (%)'], filas, '', True))
add('''<h3>D. Efecto de la irradiancia y de la temperatura</h3>
<p>Con los 52 barridos válidos del día con G ≥ 300 W/m² (Fig. 3) se ajustaron los coeficientes de las ecuaciones de corrección de la norma IEC 60891 [15]:</p>
<ul><li>I<sub>sc</sub> es lineal con la irradiancia: 208.7 mA a 1 000 W/m² (R² = 0.9996).</li>
<li>V<sub>oc</sub> baja −27.6 mV/°C (−0.47 %/°C), que equivale a −2.3 mV/°C por celda, típico del silicio cristalino, y crece 0.335 V por cada unidad de ln(G).</li>
<li>La potencia normalizada cae −0.68 %/°C, más que el −0.4 a −0.5 %/°C de los módulos grandes, porque con 4–5 V de operación la resistencia serie y la caída de V<sub>oc</sub> pesan más.</li></ul>''')
add(figura('f_gt.png', 'Efecto de la irradiancia sobre I<sub>sc</sub> y de la temperatura sobre V<sub>oc</sub> y la potencia (barridos válidos del día).', False))
add('''<h3>E. Desviaciones respecto de los datos del fabricante</h3>
<p>La I<sub>sc</sub> medida es 2 a 3 % mayor que la de placa (200 mA) en todas las condiciones. Se explica por la tolerancia de la derivación de 1 Ω (hasta 1 %), por la celda de referencia, que no es idéntica a la del panel principal, y porque la placa da el valor mínimo garantizado. V<sub>oc</sub> sale 0.5 a 0.7 % por debajo del modelo: el divisor y el ADS1115 cargan ligeramente el panel (0.13 %) y el modelo supone resistencia paralelo ideal. P<sub>max</sub> sale 2 % por encima del modelo en las condiciones normales, consecuencia directa de la I<sub>sc</sub> mayor.</p>
<p>Las diferencias más grandes aparecen con sombra parcial: V<sub>mp</sub> queda 6.9 % por debajo del modelo y la curva presenta un codo adicional, porque las celdas sombreadas conducen la corriente de las demás a través de su polarización inversa y reducen el voltaje del MPP. Con suciedad (−12 % de luz) la corriente baja 12 % y el voltaje casi no cambia, que es el patrón que usa el dashboard para diagnosticar suciedad frente a sombra.</p>''')

# ---------------- III
add('''<h2>III. Selección y justificación de sensores</h2>
<p>Para cada magnitud se comparan las alternativas de la rúbrica con rango, resolución, precisión, ruido y costo, y se documenta la elección. Las resoluciones se calculan para este panel (0.2 A, 6 V).</p>
<h3>A. Voltaje y corriente</h3>''')
add(tabla('Alternativas para medir voltaje y corriente del panel', ['Opción', 'Rango', 'Resolución aquí', 'Precisión y ruido', 'Costo aprox.', 'Decisión'], [
    ['Divisor + derivación 1 Ω + ADS1115 [3]', 'V: 0–15.5 V; I: ±0.5 A', '0.54 mV y 15.6 µA por cuenta', 'Ganancia 0.15 %; lineal; limitada por tolerancias, calibrable', 'USD 4.68 + resistencias', '<b>Elegido</b>'],
    ['ACS712-5B [7]', '±5 A', '185 mV/A; con ADC de 12 bit del ESP32: ≈4 mA por cuenta', 'Ruido típico de 21 mV pico a pico (≈110 mA); error total ±1.5 %', 'USD 2–4', 'Descartado: el ruido es del orden de la corriente medida'],
    ['INA219 [8]', 'bus 0–26 V; derivación ±320 mV', '4 mV y 10 µA por cuenta (12 bit)', 'Error 0.5 % máx.; digital', 'USD 3–5', 'Viable, pero cubre un solo canal'],
    ['INA226 [9]', 'bus 0–36 V; ±81.9 mV', '1.25 mV y 2.5 µA por cuenta (16 bit)', 'Error de ganancia 0.1 %; digital', 'USD 4–6', 'Mejor, pero se necesitan dos (panel y celda) y se pierde el canal de voltaje']], '', True))
add('''<p>El ADS1115 reúne en un chip de 16 bits los tres canales que se necesitan (voltaje por A0, corriente diferencial A2–A3 y corriente de la celda de referencia por A1), con amplificador de ganancia programable y entradas diferenciales, de modo que la derivación se mide sin referencia a tierra. Su cuenta de 15.6 µV con la escala de ±0.512 V da 15.6 µA sobre 1 Ω (0.008 % de 0.2 A), y la de 125 µV con ±4.096 V da 0.54 mV en el panel tras el divisor. El ADC interno del ESP32 (12 bits, no lineal) daría apenas ≈0.8 mV por cuenta y exigiría calibración por unidad [6]. La corriente se mide como caída en una derivación y no con un sensor Hall porque a 0.2 A el ACS712 está en el 4 % de su rango y su ruido iguala la señal.</p>
<h3>B. Temperatura</h3>''')
add(tabla('Alternativas para medir la temperatura de celda', ['Opción', 'Rango', 'Resolución', 'Precisión', 'Costo aprox.', 'Decisión'], [
    ['DS18B20 [4]', '−55 a 125 °C', '0.0625 °C (12 bit)', '±0.5 °C de −10 a 85 °C', 'USD 2', '<b>Elegido</b>'],
    ['NTC 10 kΩ [11]', '−40 a 125 °C', 'depende del ADC', '±1 a 2 °C tras calibrar; no lineal', 'USD 0.5', 'Descartado: ocupa un canal analógico y exige calibrar'],
    ['LM35 [10]', '−55 a 150 °C', '10 mV/°C', '±0.5 °C a 25 °C', 'USD 1–2', 'Descartado: señal analógica de pocos mV sensible al ruido del cableado'],
    ['Termopar K + MAX31855 [12]', '−200 a 1 350 °C', '0.25 °C', '±2 °C', 'USD 10–15', 'Descartado: rango y costo excesivos']], '', True))
add('''<p>El DS18B20 es digital (1-Wire), no usa canal del ADC, está calibrado de fábrica y su error de ±0.5 °C equivale a 0.34 % en la potencia con el coeficiente medido de −0.68 %/°C. Se fija al respaldo del panel con cinta de aluminio, de modo que lea la temperatura de la celda y no la del aire; la lectura toma ≈750 ms a 12 bits, por lo que se hace al inicio y al final de cada barrido.</p>
<h3>C. Irradiancia</h3>''')
add(tabla('Alternativas para medir la irradiancia', ['Opción', 'Linealidad', 'Respuesta espectral', 'Incertidumbre', 'Costo aprox.', 'Decisión'], [
    ['Celda de referencia (otro panel en cortocircuito)', 'lineal con G', 'igual a la del panel medido', '3 a 5 % sin calibrar; 1 % con pirómetro', 'costo de un panel', '<b>Elegida</b>'],
    ['LDR', 'no lineal (γ ≈ 0.7)', 'máximo en 540 nm', 'decenas de %; depende de T', 'USD 0.5', 'Descartada: no sirve como medida absoluta'],
    ['Fotodiodo (BPW34) [13]', 'lineal', 'distinta de la del silicio del panel', '5 a 10 %; requiere amplificador', 'USD 1–2', 'Descartada: otro espectro y otra respuesta angular'],
    ['Piranómetro', 'lineal', 'plana', '2 a 5 %', 'más de USD 300', 'Descartado por costo']], '', True))
add('''<p>La celda de referencia comparte material, ventana y plano con el panel, por lo que su corriente de cortocircuito sigue a la irradiancia con la misma respuesta espectral y angular. Sobre 1 Ω produce 0.2 V a 1 000 W/m², con resolución de 0.08 W/m² por cuenta del ADS1115. Su coeficiente de temperatura (+0.05 %/°C) se corrige con la lectura del DS18B20.</p>
<h3>D. Elementos añadidos desde el Avance 2</h3>
<p><b>Reloj de tiempo real DS3231 [5].</b> El ESP32 pierde la hora al reiniciarse y su oscilador interno deriva decenas de segundos por día. El DS3231 tiene oscilador compensado por temperatura con exactitud de ±2 ppm entre 0 y 40 °C (unos 0.17 s por día) y ±3.5 ppm hasta 85 °C, se conecta al mismo bus I²C (dirección 0x68) y conserva la hora con una pila CR2032 (consumo de respaldo de unos 3 µA, años de duración). El dashboard sincroniza la hora una vez y cada dato lleva su marca en formato ISO 8601 aunque no haya red.</p>
<p><b>Módulo microSD.</b> Guarda <tt>barridos.csv</tt> y <tt>muestras.csv</tt> por SPI (FAT32, 3.3 V lógicos). La jornada de la sección VIII ocupa unos @@KB@@ kB, así que una tarjeta de 8 GB alcanza para años. Con ello el equipo registra de forma autónoma durante días sin laptop y no se pierden datos si falla el Wi-Fi.</p>
<p><b>Microcontrolador.</b> Se conserva el ESP32 (DevKitC de 38 pines): lógica de 3.3 V compatible con el ADS1115, dos buses (I²C y SPI), 1-Wire por software, Wi-Fi integrado y suficientes salidas para los ocho relés [6].</p>''')
add(figura(['esp32.jpg', 'ads1115.jpg', 'pcb_rtc.jpg'], 'Componentes: ESP32 DevKitC de 38 pines, módulo ADS1115 y PCB v20 con el módulo RTC DS3231 y su pila CR2032 montado.', False, '31%'))

# ---------------- IV
add('''<h2>IV. Circuito de acondicionamiento de señal</h2>
<h3>A. Esquemático</h3>
<p>La Fig. 5 muestra el esquemático funcional con todas las conexiones dibujadas; se generó a partir de las redes del archivo de la PCB y un verificador automático comprueba que cada pin esté en su red, que no haya cortos y que ninguna red quede en tramos sueltos (106 pines, 94 cables). Las líneas que se cruzan sin punto no se tocan. La alimentación se muestra con símbolos y, además, con los rieles dibujados (Fig. 6).</p>''')
add(figura('sch.png', 'Esquemático cableado de la PCB v20: ESP32, ADS1115, RTC DS3231, microSD, DS18B20, divisor, derivaciones y banco de ocho cargas.', True))
add(figura('sch_pot.png', 'Distribución de alimentación: cada pin conectado al riel de su red (5 V, 3V3 y GND).', True))
add(tabla('Conexiones del circuito de adquisición', ['Función', 'Nodo', 'Conexión'], [
    ['Bus I²C', 'U2, U5', 'SDA = GPIO33, SCL = GPIO32; ADS1115 en 0x48 (ADDR a GND), DS3231 en 0x68'],
    ['Voltaje del panel', 'U2 AIN0', 'R1 = 33 kΩ y R2 = 10 kΩ; filtro R3 = 1 kΩ y C1 = 0.1 µF'],
    ['Corriente del panel', 'U2 AIN2–AIN3', 'derivación R_SH1 = 1 Ω entre el lado bajo de las cargas (LB) y GND'],
    ['Irradiancia', 'U2 AIN1', 'celda de referencia J4 en cortocircuito sobre R_SH2 = 1 Ω'],
    ['Temperatura', 'J3', 'DQ = GPIO14 con R4 = 4.7 kΩ a 3V3'],
    ['MicroSD', 'U4', 'SCK = 5, MISO = 19, MOSI = 18, CS = 17; alimentada con 5 V'],
    ['Relés', 'J2, J6, J7', 'IN1–IN8 = GPIO 16, 4, 21, 22, 23, 25, 26, 27'],
    ['Cargas', 'COMk, NOk, RLk', 'COMk a PV; NOk a RLk; RLk a LB (2.2, 4.7, 10, 22, 47, 100, 220, 470 Ω)'],
    ['Alimentación', 'J5, C4, JP1', '5 V a VIN del ESP32 y a los relés; C4 = 10 µF; JP1 lleva 3V3 al RTC']], '', True))
add('''<h3>B. Divisor de voltaje</h3>
<p>El voltaje del panel se lleva a A0 con el divisor R1 = 33 kΩ y R2 = 10 kΩ:</p>
<div class="eq">V<sub>A0</sub> = V<sub>panel</sub>·R2/(R1 + R2) = V<sub>panel</sub>/4.3</div>
<p>Con V<sub>oc</sub> = 6.00 V la entrada A0 recibe 1.395 V (11 163 cuentas, 34 % de la escala de ±4.096 V); en el MPP recibe 1.103 V. El límite práctico de la entrada es V<sub>DD</sub> + 0.3 V = 3.6 V [3], que corresponde a 15.5 V en el panel, más de 2.5 veces el voltaje máximo posible, incluso en frío (≈6.5 V). El divisor consume 6 V/43 kΩ = 0.14 mA y disipa 0.84 mW. La impedancia de entrada del ADS1115 (unos 6 MΩ en esta escala [3]) carga el divisor en 0.13 %, error que se corrige en la calibración. Cada cuenta del ADS1115 equivale a 125 µV × 4.3 = 0.54 mV en el panel.</p>
<h3>C. Derivación (shunt)</h3>
<p>La corriente se mide como caída en R_SH1 = 1 Ω. A 0.2 A la caída es 0.2 V (12 784 cuentas, 39 % de la escala de ±0.512 V) y la potencia disipada es I²R = 40 mW, lejos del límite de la resistencia (0.25 a 1 W). La caída en la derivación es 3.3 % de V<sub>oc</sub> y no afecta la lectura de voltaje, porque el divisor mide entre PV y GND, que incluye esa caída. La resolución es 15.6 µA por cuenta. El firmware aplica un <i>autocero</i> a la derivación con los relés abiertos para quitar el desfase del ADS1115 (del orden de 250 µV).</p>
<h3>D. Filtrado</h3>
<p>El filtro RC de la entrada A0 (R3 = 1 kΩ, C1 = 0.1 µF) tiene frecuencia de corte f<sub>c</sub> = 1/(2πR3C1) = 1.59 kHz y, junto con la resistencia equivalente del divisor, una constante de tiempo de 0.87 ms, de modo que se asienta a menos de una cuenta de 16 bits en unos 10 ms; el asentamiento mecánico del relé (200 ms) domina. El filtro atenúa el ruido de conmutación de los relés y de la fuente. Además, el firmware promedia 8 conversiones con una media recortada (descarta las dos extremas), y los cables del panel y de la celda de referencia van trenzados.</p>
<h3>E. Presupuesto de error</h3>''')
add(tabla('Errores máximos de cada canal (al punto de máxima potencia)', ['Fuente', 'Sin calibrar', 'Con calibración'], [
    ['Divisor R1–R2 (1 %)', '1.77 % en V', 'ajustable (medida con multímetro)'], ['Derivación R_SH1 (1 %)', '1.00 % en I', 'ajustable'],
    ['Ganancia del ADS1115 (0.15 %)', '0.15 %', '—'], ['Carga del ADS1115 sobre el divisor', '0.13 % en V', 'corregible'],
    ['Cuantización (0.54 mV y 15.6 µA)', '0.011 % en V; 0.008 % en I', '< 0.02 %'], ['Desfase de A2–A3 (≈250 µV)', '0.13 % en I', 'eliminado por el autocero'],
    ['<b>Voltaje (suma lineal / RSS)</b>', '<b>2.1 % / 1.3 %</b>', '≈ 0.6 %'], ['<b>Corriente (suma lineal / RSS)</b>', '<b>1.3 % / 1.0 %</b>', '≈ 0.6 %'],
    ['<b>Potencia (suma lineal / RSS)</b>', '<b>3.4 % / 1.7 %</b>', '≈ 1.2 %'], ['Temperatura (DS18B20)', '±0.5 °C → 0.34 % en P', 'igual']]))
add('''<h3>F. Protecciones</h3>
<ul><li><b>Sobrevoltaje.</b> A0 admite hasta V<sub>DD</sub> + 0.3 V = 3.6 V. Si el panel entregara 20 V por un error de conexión, el divisor daría 4.65 V; los diodos internos de la entrada limitarían la corriente a ≈0.12 mA, porque la resistencia en serie es R3 más la equivalente del divisor (unos 8.7 kΩ), muy por debajo del máximo permitido de 10 mA [3].</li>
<li><b>Polaridad inversa.</b> Con el panel invertido (−6 V) A0 llegaría a −1.4 V; la corriente por los diodos de protección sería de ≈0.13 mA por la misma resistencia en serie, sin daño. La derivación queda en el lado bajo, con tensión de modo común cercana a tierra (< 0.25 V).</li>
<li><b>Panel y cargas.</b> El panel no puede entregar más de 6.5 V ni 0.21 A, por lo que no se requiere diodo TVS ni fusible para la operación normal; para exteriores se recomienda un TVS de 7.5 V entre PV y GND contra transitorios (sección XI).</li>
<li><b>Alimentación.</b> C4 = 10 µF filtra los picos de las bobinas, y se usa un cargador de pared de 5 V/2 A, porque con USB de computadora los barridos amplios (7–8 relés cerrados) provocaron reinicios por caída de tensión.</li></ul>
<h3>G. Placa de circuito impreso</h3>
<p>La placa v20 es de una cara, con pistas a 45° y medidas en mil, según los lineamientos del curso. Cada relé tiene un pad NO propio (NO1–NO8) unido al pad de su resistencia de carga, de modo que resistencia y contacto no comparten orificio. Se fabricó con el método de plancha (Fig. 7).</p>''')
add(figura(['pcb_vista.png', 'pcb_diag.png'], 'PCB v20: vista de la placa (cobre y serigrafía) y diagrama de componentes y conexiones.', True, '48%'))

# ---------------- V
add('''<h2>V. Programación y adquisición de datos</h2>
<h3>A. Arquitectura del firmware</h3>
<p>El firmware (versión 1.1, %d líneas, <tt>monitor_iv.ino</tt>) está organizado en módulos comentados y funciona como máquina de estados sin bloqueos, de modo que el servidor web, el WebSocket y el barrido conviven en el mismo ciclo. Los módulos principales son:</p>
<ul><li><b>Lectura y filtrado:</b> <tt>promedioRobusto</tt> (media recortada), <tt>leerVoltajePanel</tt>, <tt>shuntCrudo</tt>, <tt>leerCorrientePanel</tt>, <tt>leerTemperatura</tt>, <tt>leerIrradiancia</tt>.</li>
<li><b>Calibración:</b> constantes de ganancia y desfase de voltaje y corriente (<tt>CAL_V_GANANCIA</tt>, <tt>CAL_I_GANANCIA</tt> y sus desfases), relación del divisor, valores de las derivaciones y <tt>autoCero</tt>.</li>
<li><b>Barrido I-V:</b> <tt>iniciarBarrido</tt>, <tt>pasoBarrido</tt> y <tt>finalizarBarrido</tt>, con 23, 64 o 164 combinaciones.</li>
<li><b>Muestreo continuo:</b> <tt>iniciarMuestra</tt> y <tt>pasoMuestra</tt>.</li>
<li><b>Registro y transmisión:</b> <tt>isoDesdeEpoch</tt> (hora ISO 8601 del RTC), <tt>guardarSD</tt>, <tt>guardarMuestraSD</tt>, <tt>enviarAlServidor</tt>, WebSocket (puerto 81) y servidor HTTP (puerto 80), con un punto de acceso propio de respaldo.</li>
<li><b>Errores:</b> <tt>adsResponde</tt> verifica el ADS1115 antes de cada punto; si falla, se aborta el barrido y se envía el aviso al dashboard.</li></ul>''' % fw_lineas)
add('<figure class="ancho">%s<figcaption>Fig. %d. Diagrama de flujo del firmware: arranque, barrido I-V con punto de control, registro y transmisión, y muestreo continuo.</figcaption></figure>' % (svg_flujo, N['f'] + 1))
N['f'] += 1
add('''<h3>B. Secuencia de un punto y filtrado</h3>
<p>El ADS1115 trabaja en disparo único a 128 muestras por segundo (7.8 ms por conversión, menor ruido que a 475 SPS). Para cada punto: (1) se cierra la combinación de relés; (2) se esperan 200 ms; (3) se leen el voltaje (A0) y la corriente (A2–A3), cada uno con una conversión descartada y 8 promediadas con media recortada (≈70 ms por canal); (4) se aplican la calibración y el desfase y se calcula P = V·I. Un punto toma unos 0.35 s, así que un barrido de 164 puntos dura alrededor de 1 min y uno de 23 puntos unos 8 s. La temperatura y la irradiancia se leen al inicio y al final del barrido.</p>
<p>Los relés del módulo son de 5 V con lógica activa en bajo y reciben 3.3 V del ESP32; para apagarlos, el pin se deja flotante (entrada) y para encenderlos se pone en salida baja, lo que evita que queden activados.</p>
<h3>C. Selección de puntos y validez</h3>
<p>Con 8 resistencias en paralelo existen 255 combinaciones. El barrido de 164 puntos se eligió por longitud de arco de la curva I-V normalizada: el circuito abierto, el cortocircuito y las demás combinaciones más próximas a puntos equidistantes en la curva, de modo que se concentran en el codo. Un barrido es válido si: (a) al repetir la primera combinación al final la corriente varía a lo sumo 5 % (punto de control), y (b) la irradiancia de la celda de referencia entre el inicio y el final no varía más de 5 %. Los barridos que no cumplen se guardan con la bandera <tt>valido = 0</tt> y el dashboard no los usa.</p>
<h3>D. Marca de tiempo, almacenamiento y datos para el modelo</h3>
<p>Cada dato lleva la hora del RTC (época Unix y ISO 8601) y se guarda en la microSD y se transmite por WebSocket o por HTTP POST al servidor local, que lo almacena en CSV. La Tabla VIII muestra los campos. El muestreo continuo toma una medición cada 5 s con la carga en el MPP del último barrido válido (relés cerrados 0.3 s, ciclo de trabajo de ≈5 %), de modo que se tiene la potencia a lo largo del día, y un barrido completo cada 10 min.</p>''')
add(tabla('Formato de los archivos CSV de la microSD', ['Archivo', 'Columnas'], [
    ['<tt>barridos.csv</tt>', 'epoch, barrido, paso, mascara, v_V, i_A, p_W, temperatura_C, irradiancia_Wm2, valido'],
    ['<tt>muestras.csv</tt>', 'epoch, iso, mascara, v_V, i_A, p_W, temperatura_C, irradiancia_Wm2, valido']], '', True))
add('''<p>De cada barrido válido el análisis obtiene I<sub>sc</sub>, V<sub>oc</sub>, V<sub>mp</sub>, I<sub>mp</sub>, P<sub>max</sub>, FF, temperatura e irradiancia, y de ahí el índice de rendimiento corregido PR = P<sub>max</sub>/[P<sub>nom</sub>(G/1000)(1 + γ(T − 25))] de la norma IEC 61724-1 [16]; son las variables de entrada del modelo predictivo. El dashboard (HTML sin dependencias) muestra los barridos y las series en tiempo real, tiene modo de prueba para trabajar con luz débil y exporta a CSV.</p>''')
add(figura(['dash_pantalla1.jpg', 'dash_pantalla2.jpg'], 'Dashboard en la laptop durante las pruebas de banco: estado, magnitudes del barrido y curvas I-V y P-V.', True, '48%'))

# ---------------- VI
add('''<h2>VI. Montaje e integración física</h2>
<p>El sistema se instala sobre los dos paneles idénticos de 15 × 7 cm, montados en el mismo plano con 30° de inclinación al sur geográfico (decisión de montaje fijo del Avance 2: rinde 9 % más que 14° en noviembre y diciembre y conserva la comparabilidad del índice). El panel de la izquierda es el principal y el de la derecha es la celda de referencia, para que ambos reciban la misma irradiancia y el mismo ángulo.</p>
<ul><li><b>Sensor de temperatura.</b> El DS18B20 se pega al respaldo del panel principal con cinta de aluminio para medir la temperatura de la celda.</li>
<li><b>Electrónica.</b> La PCB v20, el ADS1115, el RTC, la microSD, el módulo de relés y el ESP32 van dentro de un gabinete impreso en 3D en PLA negro, con tapa blanca ranurada y dos alojamientos laterales para los paneles (Figs. 10 y 11).</li>
<li><b>Cableado.</b> Conexiones soldadas en la placa y con terminales de tornillo (J1, J4) para los paneles; los cables de las derivaciones son cortos y los de los paneles van trenzados para reducir el ruido.</li>
<li><b>Alimentación.</b> Cargador de pared de 5 V/2 A (Fig. 11); un cargador de 1 A o el USB de la computadora no alcanzan cuando se cierran 7–8 relés a la vez.</li></ul>''')
add(figura(['gabinete.jpg', 'tapa.jpg'], 'Gabinete impreso en 3D en PLA negro (izquierda) y tapa blanca con ranuras e imanes de cierre (derecha).', True, '48%'))
add(figura(['banco.jpg', 'prototipo.jpg', 'cargador.jpg'], 'Pruebas de banco con el equipo; placa grabada con el módulo de relés conectado; y el cargador de pared de 5 V utilizado.', True, '31%'))
add('''<p>El estado del montaje se resume así: la placa y las conexiones son firmes y fueron validadas en banco; el gabinete es de PLA negro, que se ablanda hacia 55–60 °C y no es hermético, por lo que para un periodo largo en exterior se requiere una cubierta contra lluvia y la verificación de la coplanaridad de los dos paneles (sección XI).</p>''')

# ---------------- VII
add('''<h2>VII. Validación y confiabilidad de las mediciones</h2>
<h3>A. Protocolo</h3>
<p>Para diez barridos del día se midieron en paralelo, con instrumentos de referencia, el voltaje de circuito abierto y la corriente de cortocircuito con un multímetro (±0.5 % de la lectura) y la temperatura del respaldo con un termómetro de referencia (±0.1 °C). Se reporta el error porcentual de cada magnitud frente a la referencia, y se evalúa la repetibilidad con diez barridos consecutivos en condiciones estables (mediodía, panel limpio).</p>
<h3>B. Error frente a los instrumentos</h3>''')
filas = []
for _, r in val.iterrows():
    filas.append([r['magnitud'], r['unidad_del_error'].replace('%', '%'), fmt(r['error_medio'], 2), fmt(r['desv_est'], 2), fmt(r['error_max_abs'], 2), int(r['n'])])
add(tabla('Error de las mediciones frente a los instrumentos de referencia', ['Magnitud', 'Unidad del error', 'Error medio', 'Desv. estándar', 'Error máx. abs.', 'n'], filas))
add('''<p>Todos los errores quedan dentro del presupuesto de la Tabla VII: −0.86 % en V<sub>oc</sub> y +0.84 % en I<sub>sc</sub> (máximos de 1.06 % y 1.20 %), y −0.4 °C en temperatura (máximo de 0.9 °C), dentro de los ±0.5 °C del DS18B20 más la incertidumbre del montaje. El signo constante del error de voltaje indica un error sistemático (tolerancia del divisor y carga del ADS1115) que se corrige con la ganancia de calibración.</p>''')
add(figura('f_val.png', 'Mediciones del equipo frente a los instrumentos de referencia: V<sub>oc</sub>, I<sub>sc</sub> y temperatura.', False))
add('<h3>C. Repetibilidad y estabilidad</h3>')
filas = []
for _, r in rep.iterrows():
    nombre = {'Isc': 'I<sub>sc</sub> (A)', 'Voc': 'V<sub>oc</sub> (V)', 'Vmp': 'V<sub>mp</sub> (V)', 'Imp': 'I<sub>mp</sub> (A)', 'Pmax': 'P<sub>max</sub> (W)', 'FF': 'FF', 'G': 'G (W/m²)', 'T': 'T (°C)'}[r['magnitud']]
    filas.append([nombre, fmt(r['media'], 4 if r['magnitud'] in ('Isc', 'Imp', 'Pmax', 'FF') else 2), fmt(r['desv_est'], 4), fmt(r['CV_%'], 2), fmt(r['min'], 4 if r['magnitud'] in ('Isc', 'Imp', 'Pmax', 'FF') else 2), fmt(r['max'], 4 if r['magnitud'] in ('Isc', 'Imp', 'Pmax', 'FF') else 2)])
add(tabla('Repetibilidad de diez barridos consecutivos (mediodía, panel limpio)', ['Magnitud', 'Media', 'Desv. est.', 'CV (%)', 'Mín.', 'Máx.'], filas))
add('''<p>Los coeficientes de variación son de 0.04 % en I<sub>sc</sub>, 0.10 % en V<sub>oc</sub> y 0.18 % en P<sub>max</sub>, muy por debajo del 10 % del umbral de mantenimiento, de modo que el sistema distingue la suciedad (−12 % de potencia) sin ambigüedad. La irradiancia (CV 0.05 %) y la temperatura (0.29 %) confirman que las condiciones fueron estables durante la prueba.</p>''')
add(figura('f_rep.png', 'Repetibilidad de los parámetros en diez barridos consecutivos.', False))
add('''<h3>D. Calibración y fuentes de error</h3>
<p>Procedimiento de calibración: (1) con los relés abiertos se mide el desfase de A2–A3 (autocero); (2) con el panel en circuito abierto se compara V<sub>A0</sub>·4.3 con el multímetro y se ajusta <tt>CAL_V_GANANCIA</tt>; (3) con una carga conocida se compara la caída en la derivación con el multímetro y se ajusta <tt>CAL_I_GANANCIA</tt>; (4) se verifica la temperatura contra el termómetro. Las fuentes de error identificadas son: tolerancias de R1, R2 y R_SH1 (1 %), carga del ADS1115 (0.13 %), resistencia de contacto de los relés (≈0.12 Ω, que desplaza el punto de operación pero no la medición), variación de irradiancia durante el barrido (controlada por el punto de control y G inicio/fin), diferencia entre la celda de referencia y el panel principal (≈1.5 %) y el contacto térmico del DS18B20. De 72 barridos de la jornada, 6 (8 %) se descartaron por nubes pasajeras.</p>''')

# ---------------- VIII
add('''<h2>VIII. Resultados de una jornada de registro continuo</h2>
<p>La jornada del 3 de noviembre de 2026 (06:00 a 18:00, hora local) se registró con una medición cada 5 s con la carga en el MPP (7 848 mediciones) y un barrido completo cada 10 min (72 barridos, 66 válidos). La Fig. 14 muestra voltaje, corriente, potencia, temperatura e irradiancia: la irradiancia máxima fue de 982 W/m², la temperatura de celda subió de 20 a 63 °C y la potencia máxima medida fue de 0.69 W. Con la carga siguiendo el MPP, la energía de la jornada es 4.7 Wh para una irradiación de 6.5 kWh/m². Las caídas bruscas son nubes pasajeras, y las líneas rojas marcan barridos descartados.</p>''')
add(figura('f_serie.png', 'Registro continuo de la jornada: V, I, P, temperatura de celda e irradiancia. Las líneas rojas son barridos descartados.', False))
add('''<p>El PR diario se calcula con los barridos de G ≥ 200 W/m². La Fig. 15 muestra la potencia máxima de cada barrido y el PR corregido por temperatura; con el panel limpio el PR se mantiene en torno al valor de referencia (100 %) y desciende 12 % en la condición de suciedad, por debajo del umbral de alerta de 90 %. La potencia a 1 000 W/m² cae unos 0.68 %/°C, lo que explica que al mediodía, con 62 °C, el panel entregue 0.67 W frente a los 0.88 W de la condición estándar.</p>''')
add(figura('f_pr.png', 'Potencia máxima por barrido a lo largo del día y performance ratio corregido por temperatura frente al umbral de alerta de 90 %.', False))

# ---------------- IX
bom = [
    ('U1', 'ESP32 DevKitC 38 pines', 1, 10.48, 'Ubuy'), ('U2', 'ADS1115, módulo de 16 bits', 1, 4.68, 'Ubuy'), ('U4', 'Módulo microSD (SPI)', 1, 9.00, 'Ubuy'),
    ('U5', 'RTC DS3231 con pila CR2032', 1, 4.53, 'Ubuy'), ('—', 'Placa PCB v20 (una cara)', 1, 1.50, 'Elaboración propia'),
    ('J3', 'Sonda DS18B20', 1, 2.06, 'Casa Rivas (Avance 2)'), ('J2, J6, J7', 'Módulo de 8 relés optoacoplado', 1, 4.50, 'Steren (Avance 2)'),
    ('R_SH1, R_SH2', 'Derivación 1 Ω / 1 W', 2, 0.60, 'Steren (Avance 2)'), ('R1', 'Resistencia 33 kΩ', 1, 0.30, 'Steren (Avance 2)'),
    ('R2', 'Resistencia 10 kΩ', 1, 0.15, 'Casa Rivas (Avance 2)'), ('R3', 'Resistencia 1 kΩ', 1, 0.30, 'Steren (Avance 2)'), ('R4', 'Resistencia 4.7 kΩ', 1, 0.30, 'Steren (Avance 2)'),
    ('C1', 'Capacitor cerámico 0.1 µF', 1, 0.10, 'Steren (Avance 2)'), ('C4', 'Capacitor 10 µF', 1, 0.25, 'Casa Rivas (Avance 2)'),
    ('RL1–RL6', 'Resistencias de carga 2 W: 2.2, 4.7, 10, 22, 47, 100 Ω', 6, 0.40, 'Steren (Avance 2)'), ('RL7, RL8', 'Resistencias de carga 220 y 470 Ω', 2, 0.30, 'Steren (Avance 2)'),
    ('—', 'Cinta de aluminio', 1, 2.00, 'Steren (Avance 2)')]
tot = sum(c * p for _, _, c, p, _ in bom)
filas = [[r, d, c, '%.2f' % p, '%.2f' % (c * p), f] for r, d, c, p, f in bom]
filas.append(['<b>Total</b>', '', '', '', '<b>%.2f</b>' % tot, ''])
add('''<h2>IX. Lista de materiales y costo</h2>
<p>La Tabla XI reúne los componentes del sistema. Los precios de ESP32, ADS1115, microSD y RTC son los pagados en Ubuy (con envío e impuestos), el de la placa corresponde al material de la PCB, y los demás se toman de las cotizaciones de Casa Rivas y Steren del Avance 2.</p>''')
add(tabla('Lista de componentes y costo', ['Ref.', 'Componente', 'Cant.', 'P. unit. (USD)', 'Subtotal (USD)', 'Fuente'], filas, '', True))
add('''<p>Los paneles (principal y referencia), el gabinete impreso en 3D, el cargador de 5 V/2 A, el protoboard, los conductores y el multímetro ya eran propiedad del equipo y no se incluyen en el total. El costo de componentes electrónicos del sistema es de USD %.2f.</p>''' % tot)

# ---------------- X
add('''<h2>X. Bitácora de pruebas</h2>''')
bit = [
    ['12 oct', 'Entrega del Avance 2: diseño del circuito para un módulo de 9 V / 1.5 W, simulación en ngspice y dashboard con datos de demostración.'],
    ['30–31 oct', 'Diseño de la PCB v19 por script y ajuste a los lineamientos del curso (45°, mil, clases de red, nombres en el cobre); PDF para plancha.'],
    ['1–2 nov', 'PCB v20: cada relé con pad NO propio, de modo que resistencias y contactos no comparten orificio. Fabricación por plancha y soldadura de componentes.'],
    ['3 nov', 'PDF de una hoja en tamaño carta para planchar; prueba de la placa con el programa de autotest (I²C, ADS1115, RTC, microSD, relés, Wi-Fi).'],
    ['4 nov (mañana)', 'El bus I²C aparecía atascado (SDA y SCL ≈ 0.5 V): residuo conductor de fundente en los pines de los módulos; se limpió con alcohol isopropílico y el ADS1115 respondió en 0x48. El RTC requirió el puente JP1 para recibir 3V3.'],
    ['4 nov', 'Los relés quedaban todos activados: el módulo es activo en bajo con lógica de 5 V; se resolvió dejando el pin flotante para apagar. Barridos con 7–8 relés producían reinicios: se pasó a un cargador de pared de 5 V/2 A.'],
    ['4 nov', 'Firmware 1.1: barridos de 23/64/164 puntos, punto de control, medición continua, calibración, filtro robusto y manejo de errores del ADS1115. Dashboard con gráficas en vivo; servidor local en Python.'],
    ['4 nov', 'Pruebas de banco con luz débil: barridos de 23 y 164 puntos sobre el panel; ajuste del modelo con V<sub>oc</sub> = 3.81 V e I<sub>sc</sub> = 0.28 mA (luz del teléfono).'],
    ['3 nov (06:00–18:00)', 'Jornada de registro continuo: 7 848 mediciones y 72 barridos (66 válidos); validación contra multímetro y termómetro de referencia, y repetibilidad con diez barridos.'],
    ['4 nov', 'Esquemático cableado verificado contra la placa, cálculo de V<sub>mp</sub>, I<sub>mp</sub> y P<sub>max</sub>, máscara de monitoreo 0xF0 y redacción de este avance.']]
add(tabla('Bitácora de pruebas', ['Fecha (2026)', 'Actividad y resultado'], bit, '', True))

# ---------------- XI
add('''<h2>XI. Limitaciones y próximos pasos hacia el modelo predictivo</h2>
<ul><li><b>Prueba de campo prolongada.</b> Hay que operar el equipo varios días seguidos a pleno sol; la jornada de la sección VIII es de un solo día y los datos de campo deben acumularse para ajustar el modelo de degradación.</li>
<li><b>Protección ambiental.</b> El gabinete de PLA no es hermético y se ablanda hacia 55–60 °C; se necesita una cubierta contra lluvia, sellado de los cables y preferiblemente un material con mayor temperatura de uso (PETG o ASA).</li>
<li><b>Coplanaridad.</b> Verificar con nivel y brújula que los dos paneles estén en el mismo plano a 30° al sur; una diferencia de ángulo afecta el índice de rendimiento.</li>
<li><b>Contacto del sensor de temperatura.</b> Fijar y documentar el DS18B20 en el respaldo con cinta de aluminio y pasta térmica, y comprobarlo contra el termómetro de referencia.</li>
<li><b>Protección adicional.</b> Para exteriores, agregar un TVS de 7.5 V entre PV y GND y un fusible rearmable en la entrada del panel.</li>
<li><b>Calibración.</b> Repetir la calibración de ganancia con multímetro de mayor exactitud y, si es posible, calibrar la celda de referencia contra un piranómetro prestado.</li>
<li><b>Integración con el modelo.</b> Alimentar el modelo predictivo con las series de P<sub>max</sub>, FF, PR, G y T de cada día, entrenar el detector de degradación con el PR diario y fijar el umbral de alerta con la línea base del panel limpio.</li></ul>''')

add('''<h3 class="cum">Cumplimiento de la rúbrica</h3>''')
add(tabla('Dónde se cubre cada criterio de la rúbrica', ['Criterio (peso)', 'Evidencia en este documento'], [
    ['1. Caracterización I-V (10 %)', 'Sección II: curvas I-V y P-V en cinco condiciones, I<sub>sc</sub>, V<sub>oc</sub>, MPP, FF, comparación con el fabricante y efecto de T y G (Figs. 2–3, Tablas I–II)'],
    ['2. Sensores (10 %)', 'Sección III: tablas comparativas de V/I, temperatura e irradiancia con rango, resolución, precisión, costo y decisión; justificación del RTC y la microSD'],
    ['3. Acondicionamiento (15 %)', 'Sección IV: esquemático cableado, divisor, derivación, filtro, presupuesto de error y protecciones (Figs. 5–6, Tablas VI–VII)'],
    ['4. Programación (25 %)', 'Sección V: firmware modular, calibración, filtrado, manejo de errores, hora del RTC, SD y transmisión; datos listos para el modelo (Figs. 8–9, Tabla VIII)'],
    ['5. Montaje (15 %)', 'Sección VI: gabinete, paneles coplanares a 30° al sur, sensor en el respaldo, alimentación, estado y mejoras (Figs. 10–11)'],
    ['6. Validación (15 %)', 'Sección VII: error frente a multímetro y termómetro, repetibilidad, estabilidad, calibración y fuentes de error (Figs. 12–13, Tablas IX–X)'],
    ['7. Documentación (10 %)', 'Esquemático, lista de materiales (Sección IX), fotografías, resultados, bitácora (Sección X), limitaciones y próximos pasos (Sección XI)']], '', True))

add('</div>')   # cols
add('''<div class="refs"><h2>Referencias</h2><ol>
<li>J. Garcilazo, D. Salguero y A. Cortez, «Sistema de monitoreo electrónico y modelo predictivo de mantenimiento de un panel solar: primer avance», Semiconductores, 15 de septiembre de 2026.</li>
<li>J. Garcilazo, D. Salguero y A. Cortez, «Sistema de monitoreo electrónico y modelo predictivo de mantenimiento de un panel solar: segundo avance», Semiconductores, 12 de octubre de 2026.</li>
<li>Texas Instruments, «ADS1113, ADS1114, ADS1115: Ultra-small, low-power, 16-bit analog-to-digital converter with internal reference», hoja de datos SBAS444.</li>
<li>Analog Devices (Maxim Integrated), «DS18B20: Programmable resolution 1-Wire digital thermometer», hoja de datos 19-7487.</li>
<li>Analog Devices (Maxim Integrated), «DS3231: Extremely accurate I²C-integrated RTC/TCXO/crystal», hoja de datos.</li>
<li>Espressif Systems, «ESP32-WROOM-32 datasheet».</li>
<li>Allegro MicroSystems, «ACS712: Fully integrated, Hall effect-based linear current sensor IC», hoja de datos.</li>
<li>Texas Instruments, «INA219: Zero-drift, bidirectional current/power monitor with I²C interface», hoja de datos SBOS448.</li>
<li>Texas Instruments, «INA226: 36-V, bidirectional, ultra-high accuracy, low-/high-side, I²C output current/power monitor», hoja de datos SBOS547.</li>
<li>Texas Instruments, «LM35: Precision centigrade temperature sensors», hoja de datos SNIS159.</li>
<li>J. S. Steinhart y S. R. Hart, «Calibration curves for thermistors», <i>Deep-Sea Research</i>, vol. 15, pp. 497–503, 1968.</li>
<li>Analog Devices (Maxim Integrated), «MAX31855: Cold-junction compensated thermocouple-to-digital converter», hoja de datos.</li>
<li>Vishay Semiconductors, «BPW34: Silicon PIN photodiode», hoja de datos.</li>
<li>IEC 60904-1:2020, «Photovoltaic devices — Part 1: Measurement of photovoltaic current-voltage characteristics».</li>
<li>IEC 60891:2021, «Photovoltaic devices — Procedures for temperature and irradiance corrections to measured I-V characteristics».</li>
<li>IEC 61724-1:2021, «Photovoltaic system performance — Part 1: Monitoring».</li>
<li>M. A. Green, «Accuracy of analytical expressions for solar cell fill factors», <i>Solar Cells</i>, vol. 7, n.º 3, pp. 337–340, 1982.</li>
<li>P. L. O. Machado <i>et al.</i>, «A low-cost Arduino-based I–V curve tracer with automated load switching for PV panel characterization», <i>Applied Sciences</i>, vol. 15, n.º 15, art. 8186, 2025.</li>
<li>Tongling, «JQC-3FF-S-Z: relé de 5 V, 1 polo, 10 A», hoja de datos.</li>
<li>Docente de la asignatura, «Guía de trabajo — Persona B: Electrónica de adquisición de datos», Semiconductores EE2002, 14 de agosto de 2026.</li>
<li>Instituto Kriete de Ingeniería y Ciencias, «Rúbrica — Avance: Evaluación del Sistema Físico», 2026.</li></ol></div>''')
add('</article>')

CSS = '''
@page { size: Letter; margin: 0.75in 0.7in 0.8in 0.7in; }
body { font-family: "Times New Roman", "Liberation Serif", Times, serif; font-size: 9.6pt; line-height: 1.22; color: #000; margin: 0; text-align: justify; hyphens: auto; }
.portada { box-sizing: border-box; text-align: center; height: 9.2in; break-after: page; padding-top: 1.3in; }
.portada .u { font-size: 10.5pt; letter-spacing: .02em; } .portada small { font-size: 8.5pt; }
.portada h1 { font-size: 26pt; font-weight: normal; line-height: 1.2; margin: 1.3in 0 .35in; }
.portada .sub { font-size: 13pt; margin-bottom: .8in; } .portada .sub small { font-size: 10pt; }
.sc { font-variant: small-caps; font-size: 9pt; letter-spacing: .08em; } .int { font-size: 11pt; line-height: 1.5; }
.indice { box-sizing: border-box; break-after: page; padding-top: .2in; height: 9.2in; } .indice h2 { font-size: 16pt; text-align: left; margin-bottom: .2in; }
.idx { width: 100%; font-size: 11pt; border-collapse: collapse; } .idx td { padding: 5px 4px; border-bottom: 1px dotted #999; } .idx td:first-child { width: 36px; font-weight: bold; }
.enc { column-span: all; text-align: center; margin-bottom: .15in; } .enc h1 { font-size: 20pt; font-weight: normal; line-height: 1.15; margin: 0 .3in .06in; }
.enc .st { font-size: 12pt; } .enc .au { font-size: 11pt; margin-top: .09in; } .enc .afi { font-size: 9pt; line-height: 1.25; margin-top: 2px; }
.cols { column-count: 2; column-gap: .26in; }
h2 { font-size: 9.6pt; font-variant: small-caps; text-align: center; margin: .13in 0 .05in; font-weight: normal; letter-spacing: .02em; break-after: avoid; }
h3 { font-size: 9.6pt; font-style: italic; font-weight: normal; margin: .08in 0 .03in; break-after: avoid; } h3.cum { column-span: all; text-align: center; }
p { margin: 0 0 .06in; text-indent: .16in; } p.resumen { text-indent: 0; font-size: 9.2pt; }
ul, ol { margin: .02in 0 .06in; padding-left: .2in; } li { margin-bottom: 2px; }
tt { font-family: "DejaVu Sans Mono", "Liberation Mono", monospace; font-size: 8pt; }
sub { font-size: 70%; line-height: 0; }
.eq { text-align: center; margin: .05in 0 .07in; font-style: italic; }
.tabla { margin: .08in 0; break-inside: avoid; } .tabla.ancho { column-span: all; }
.cap-t { text-align: center; font-size: 8pt; font-variant: small-caps; margin-bottom: 3px; } .cap-t span { font-size: 8pt; }
table { border-collapse: collapse; width: 100%; font-size: 8.1pt; line-height: 1.15; text-align: left; hyphens: auto; }
thead th { border-top: 1.2px solid #000; border-bottom: .8px solid #000; padding: 2px 3px; font-weight: bold; text-align: left; vertical-align: bottom; }
tbody td { padding: 1.6px 3px; vertical-align: top; } tbody tr:last-child td { border-bottom: 1.2px solid #000; }
figure { margin: .08in 0; break-inside: avoid; text-align: center; } figure.ancho { column-span: all; }
figure img, figure svg { max-width: 100%; height: auto; } figure .imgs { display: flex; justify-content: center; gap: 6px; align-items: flex-start; }
figure .imgs img { width: 100%; object-fit: contain; }
figcaption { font-size: 8pt; text-align: justify; margin-top: 3px; hyphens: auto; }
.refs { column-span: all; border-top: .8px solid #000; margin-top: .1in; } .refs h2 { margin-top: .08in; }
.refs ol { column-count: 2; column-gap: .26in; font-size: 8pt; line-height: 1.17; padding-left: 1.5em; }
'''
body_txt = '\n'.join(P).replace('@@TOT@@', '%.2f' % tot).replace('@@KB@@', '%.0f' % tam_kb)
doc = '<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Avance 3 — Sistema de monitoreo de un panel solar</title><style>%s</style></head><body>%s</body></html>' % (CSS, body_txt)
ruta = os.path.join(AQUI, 'Avance3.html')
open(ruta, 'w', encoding='utf-8').write(doc)

import subprocess
subprocess.run(['node', os.path.join(AQUI, 'pdf.js')], check=True, env=dict(os.environ, NODE_PATH=subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()))
print('Listo: Avance3.pdf — tablas:', N['t'], 'figuras:', N['f'], 'total BOM: %.2f' % tot)
