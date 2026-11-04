# Contexto del proyecto — Semiconductores (EE2002)

> **Instrucción para Claude:** cada vez que se cambie, cree o entregue algo en este proyecto, actualizá este archivo: (1) el mapa de archivos si aparece o cambia uno, (2) el estado y los pendientes, y (3) agregá una línea al **Registro de cambios** (arriba, la más reciente primero) con fecha, qué cambió y por qué. Este archivo vive en la carpeta Semiconductores del usuario.

Última actualización: 2026-10-30

---

## 1. Qué es el proyecto

- **Curso:** Semiconductores (EE2002), Aprendizaje Basado en Proyectos (PBL). Docente: Karen Pimentel.
- **Equipo:** Joshua Garcilazo, **Daniel Salguero** (confirmado por el usuario; en el Avance 1 y en algunos mensajes aparece como "Iván"), Alfredo Cortez.
- **Tema:** sistema de monitoreo electrónico y modelo de degradación/mantenimiento de un panel solar de 1.5 W (Casa Rivas, AR-3302PANEL5V, código interno 32436).
- **Idioma de trabajo:** español (el usuario escribe con voseo, El Salvador). Formato de los documentos: estilo IEEE a dos columnas, como el Avance 1.
- **Reparto:** el usuario (Joshua) arma el documento y el dashboard; **Daniel** hizo el esquemático en KiCad y está haciendo la simulación; el equipo comparte el resto.

## 2. Entrega actual: Avance 2

Debe ser **un solo PDF**. Rúbrica (archivo `Rúbrica segundo avance PBL semiconductores.pdf`), pesos:

| Criterio | Peso |
|---|---|
| Componentes, acondicionamiento y alimentación | 25 % |
| Dashboard | 30 % |
| Simulación | 30 % |
| Documentación | 15 % |

Secciones requeridas, en orden: Portada; Selección de componentes (microcontrolador, acondicionamiento, alimentación, medio de transmisión, cada uno con justificación técnica con hojas de datos y cálculos); Esquemático y lista de componentes; Diseño del dashboard; Simulación o pruebas físicas; Limitaciones y ajustes pendientes; Referencias (incluye hojas de datos).

Fecha de entrega: pendiente de confirmar (se había anotado 5–9 de octubre; hoy es 12 de octubre).

## 3. Decisiones técnicas vigentes

- **Panel:** 5 V / 1.5 W nominal, área 0.01035 m², η STC 14.5 %. **Voc = 9 V** "según las pruebas del equipo" (en la práctica 3 se midieron 9.09 V con una carga de 220 Ω, así que el real es ≥ 9.09 V; máximo de diseño 11 V). **Isc = 0.212 A, Vmp = 7.5 V, Imp = 0.200 A son estimaciones de Claude, NO medidas** (contradicen el Avance 1, que decía Isc 315–330 mA). Falta medir Voc e Isc con multímetro al sol.
- **Microcontrolador:** ESP32-WROOM-32 (lógica de 3.3 V, Wi-Fi, I²C). Relés por GPIO13, 14, 16, 17, 18, 19, 23, 25; I²C en GPIO21 (SDA) y GPIO22 (SCL); DS18B20 en GPIO4.
  - **Pines de la PCB v19 (los que valen para el firmware):** I²C SDA = GPIO33, SCL = GPIO32; DS18B20 = GPIO14; microSD MISO/MOSI/SCK/CS = 19/18/5/17; relés IN1…IN8 = GPIO16, 4, 21, 22, 23, 25, 26, 27. Detalle en `PLAN_PCB_v19.md`.
- **ADC:** ADS1115. Voltaje del módulo por divisor 33 kΩ / 10 kΩ (4.3:1) con filtro RC 1 kΩ / 0.1 µF → A0, escala **±4.096 V** (125 µV por cuenta). Corriente por derivación de 1 Ω entre A2 y A3, escala ±0.512 V (15.625 µV por cuenta). Celda de referencia con otra derivación de 1 Ω en A1.
- **Cargas:** 2.2, 4.7, 10, 22, 47, 100, 220, 470 Ω conmutadas por un módulo de 8 relés de 5 V. Barrido de **23 puntos** elegidos entre las 256 combinaciones.
- **Alimentación:** powerbank de 10 000 mAh (5 V) para ESP32 (VIN) y bobinas de los relés. Consumo promedio 164 mA, pico 740 mA, ≈ 27 h de autonomía (supuestos: relé 71 + 5 mA por canal, ESP32 130 mA, 60 % de uso). La powerbank **ya era del equipo** (no se compró para el proyecto) y se incluye en el presupuesto con un valor de referencia de **$20**.
- **Transmisión:** Wi-Fi 2.4 GHz, el ESP32 envía HTTP POST con JSON al servidor (Python) en la laptop (IP de la LAN, no localhost); se guarda en CSV y se sirve el dashboard. Regla "medir y luego transmitir".
- **Montaje:** panel fijo a 30° orientado al sur (simulación de sitio 13.67° N; los seguidores y el giro este–oeste se descartaron por energía neta del actuador y riesgo de plazo).
- **Presupuesto:** lista de materiales $32.67 a comprar + $20 de la batería = **$52.67** en total. Fuentes: cotización de Casa Rivas (50861850, 14/09/2026, con 25 % de descuento estudiantil) y Steren.
- **Relés:** módulo de 8 canales de 5 V de Casa Rivas (10 A a 250 VAC / 30 VDC); el relé del módulo probablemente es tipo SRD-05VDC-SL-C (bobina 70 Ω, ~71 mA), pero **no está confirmado**. Verificar que se activen con 3.3 V del ESP32.
- **Dashboard:** indicadores V, I, P, T, G (celda de referencia), eficiencia, PR corregido por temperatura (IEC 61724-1), degradación a STC, factor de forma, curvas I-V y P-V contra lo esperado, PR diario (G ≥ 200 W/m²), alerta si PR < 90 % durante 3 días seguidos (normal / vigilar / mantenimiento) y causa probable (suciedad, resistencia serie o envejecimiento).

## 3b. Supuestos, estimaciones y cambios (detalle)

Todo lo que **no es un dato medido o confirmado** y todo lo que cambió respecto del Avance 1 o del material original. Si algo de esta lista se mide o se confirma, actualizar aquí y en el documento.

### A. Datos del panel — estimados o tomados por indicación del usuario
| Dato | Valor usado | Origen | Estado |
|---|---|---|---|
| Voc | 9 V | Indicación del usuario ("según las pruebas realizadas"). El Avance 1 suponía 6.0–6.5 V. | **No medido por Claude.** Medir con multímetro. |
| Voc máximo de diseño | 11 V | Margen que puso Claude por irradiancia alta y temperatura baja. | Supuesto. |
| Voc de la práctica 3 | 9.09 V con carga de 220 Ω (≈ 41 mA) | Informe de la práctica 3 | Dato medido; implica que el Voc real es ≥ 9.09 V. |
| Isc | 0.212 A | **Estimado por Claude** a partir de 1.5 W, Voc 9 V y un factor de forma ≈ 0.79. | **No medido.** Contradice el Avance 1 (315–330 mA). Medir. |
| Vmp / Imp | 7.5 V / 0.200 A | **Estimados por Claude**, coherentes con 1.5 W. | **No medidos.** La simulación da Pmax = 1.51 W a 7.6 V y 0.199 A. |
| Modelo del panel (simulación) | Fuente de corriente 0.212 A en paralelo con un diodo (IS = 3.74 nA, N = 19.5) | N = 15 celdas en serie × 1.3 de factor de idealidad; Vt a 25 °C. Sin resistencia serie ni paralelo. | Supuesto de modelado; ajustar a las curvas reales. |
| Coeficiente de temperatura γ | ≈ −0.4 %/°C | Valor típico usado en el dashboard (PR corregido por temperatura). | Supuesto típico de silicio. |
| Suciedad simulada | −11 % en la fotocorriente | Escenario del dashboard y de la simulación. | Ilustrativo, no medido. |
| Aclaración sobre un dato recordado | Una vez se recordó "170 mA con 220 Ω"; los datos de la práctica 3 dicen ≈ 41 mA a 9.09 V con 220 Ω. | Se explicó al usuario que no eran consistentes. | Usar los datos del informe. |

### B. Alimentación y powerbank
- **Powerbank:** 5 V, 10 000 mAh. **Ya era propiedad del equipo; no se compró para este proyecto.** Se incluye en el presupuesto con un **valor de referencia de $20** (dato del usuario: "vale como 20 dólares"). El presupuesto del documento queda: $32.67 a comprar + $20 = **$52.67**.
- La capacidad de 10 000 mAh es la **nominal**; la capacidad útil a 5 V es menor (por conversión desde la celda de ~3.7 V). Claude no aplicó un factor de eficiencia explícito ni verificó el modelo real de la powerbank: la autonomía de ≈ 27 h es una estimación.
- Consumo promedio 164 mA a 5 V (0.82 W), pico 740 mA con todos los relés cerrados (< 0.3 s). Supuestos: ESP32 ≈ 130 mA con Wi-Fi activo, picos de 250–280 mA al transmitir (guía de Hubble, no hoja del fabricante); bobina de cada relé 71 mA + 5 mA del optoacoplador (la bobina viene de la hoja del SRD-05VDC-SL-C, pero **no está confirmado que el módulo use ese relé**; el optoacoplador es supuesto); ciclo de trabajo de los relés 5.4 % (0.20 s de asentamiento + 0.07 s de lectura cada 5 s); 60 % de uso.
- Riesgo anotado: algunas powerbanks se apagan con corrientes bajas; no se probó con la del equipo.
- Se decidió alimentar con batería (no con la red) y que la laptop se comunique solo por Wi-Fi.

### C. Componentes y precios
- La lista de materiales reproduce la del Avance 1 con precios de la **cotización 50861850 de Casa Rivas (14/09/2026, con 25 % de descuento estudiantil e IVA)** y de **Steren (con IVA)**.
- El módulo de 8 relés figura en el BOM como **Steren, $4.50**. Casa Rivas publica en Facebook un módulo de 8 canales de 5, 12 o 24 V, 10 A / 250 VAC y 10 A / 30 VDC (sin precio en la publicación). **Decisión pendiente:** si se compra en Casa Rivas hay que cambiar precio y fuente. Hay que comprar la versión de **5 V**.
- Para el módulo de relés se verificó con la hoja de datos del relé SRD-05VDC-SL-C (bobina 5 V, 70 Ω, 360 mW ≈ 71.4 mA), pero en las fotos el relé parece rotulado "JQC-3FF-S-Z": **modelo sin confirmar**.
- Activación a 3.3 V: muchos módulos se activan en nivel bajo con optoacoplador y pueden no cerrar bien con la lógica de 3.3 V. **Sin probar.**
- ADS1115: impedancia de entrada tomada como 5 MΩ en la simulación (supuesto; la hoja dice "varios megaohmios"). Los módulos comerciales a veces traen resistencias de subida I²C; **sin confirmar** en el módulo adquirido.
- Datos verificados contra fuentes del fabricante (2026-10-12): ESP32-WROOM-32 (3.0–3.6 V, 802.11 b/g/n, hasta 32 GPIO, ADC 12 bits), Raspberry Pi Pico W (26 GPIO a 3.3 V, 802.11n 2.4 GHz), Arduino Uno (14 digitales, 6 analógicas, lógica de 5 V, sin Wi-Fi), MCP3008 (10 bits, 8 canales, pseudodiferencial, 2.7–5.5 V), relé SRD-05VDC-SL-C (bobina 5 V/70 Ω). El ATmega328P de 10 bits y la tabla de alternativas son conocimiento general de Claude.

### D. Acondicionamiento y medición
- Divisor 33 kΩ / 10 kΩ (4.3:1): 9 V → 2.09 V en A0; escala del ADS1115 **cambiada de ±2.048 V (Avance 1) a ±4.096 V** porque con Voc 9 V la escala anterior se saturaba desde 8.8 V del módulo. Límite práctico 14.2 V (3.3 V en la entrada), límite absoluto 15.5 V.
- Derivación de 1 Ω / 1 W entre A2–A3 (±0.512 V, 15.6 µA por cuenta): 0.21–0.33 V de señal. Corriente del módulo = corriente de la derivación + corriente del divisor (≈ 0.2 mA, 0.1 %).
- Filtro R3 = 1 kΩ y C1 = 0.1 µF (corte ≈ 1.6 kHz; constante con el divisor ≈ 0.87 ms). Espera de **200 ms** tras cerrar cada relé, intervalo de **5 s** entre puntos, lectura de temperatura al inicio y al final del barrido.
- El error de −0.17 % en la potencia estimada en la simulación se debe al efecto de carga de la entrada del ADS1115 (con el supuesto de 5 MΩ) y se corrige con calibración.
- DS18B20: pull-up de 4.7 kΩ a 3.3 V, GPIO4, fijado al respaldo del panel con cinta de aluminio.

### E. Simulación (ngspice)
- Relés modelados como **interruptores con 50 mΩ** de contacto (supuesto). En la hoja de KiCad del equipo **los relés no tienen modelo de simulación** y el panel estaba como fuente de 5 V; la simulación usa un equivalente corregido.
- **Selección de los 23 puntos:** circuito abierto + las 22 combinaciones de cargas en paralelo (de las 255) más cercanas a puntos equidistantes en longitud de arco de la curva I-V normalizada. Propuesta de Claude (se cita Machado et al. como inspiración); **debe confirmarse con el panel real**. Máscaras (hex, bit 0 = RL1 … bit 7 = RL8), de menor a mayor voltaje: 01, 3C, A4, 78, E8, C8, 08, F0, 70, B0, 30, D0, 50, 90, 10, E0, 60, A0, 20, C0, 40, 80, 00.
- No se modela: ruido, temperatura, rebote de contactos (el margen de 200 ms lo cubre), capacitancia del panel, activación de relés con 3.3 V, comunicación I²C, irradiancia más allá de escalar la fotocorriente.
- Resultados principales: A0 máx. 2.09 V (de 4.096), derivación 0.212 V (de 0.512), Pmax del barrido 1.5075 W (curva exacta 1.512 W), asentamiento a una cuenta ≈ 6.7 ms.

### F. Montaje, sitio y transmisión
- **Montaje:** fijo a 30°, orientado al **sur geográfico (azimut 180°)**; el usuario había dicho "este–oeste" en algún momento y **está sin aclarar** si se refiere a eso o al giro este–oeste (descartado). Decisión basada en una simulación de cielo despejado en 13.67° N (pvlib; modelos de Ineichen–Perez y Hay–Davies) y en el riesgo de plazo (prototipo funcional 26–30 de octubre).
- **Transmisión:** Wi-Fi 2.4 GHz con HTTP POST/JSON a un servidor Python en la **IP de la laptop en la LAN** (no `localhost`); puede ser un enrutador o un punto de acceso de la laptop o del teléfono. **Servidor y firmware aún no implementados.**
- Política de datos faltantes: se marcan y se conservan, no se interpolan ni se descartan; el ESP32 reenvía los barridos no confirmados.

### G. Dashboard
- Todas las cifras de las figuras son de un modo de **simulación** (modelo de diodo único, 5 escenarios: limpio, suciedad moderada, suciedad severa, nube pasajera, día caluroso), **no son mediciones**.
- Umbrales **iniciales y editables**: PR < 90 %, regla de **3 días seguidos**, filtro de irradiancia G ≥ 200 W/m², diagnóstico por Isc −7 % con factor de forma normal (suciedad), factor de forma −8 % (resistencia serie), otro caso (envejecimiento). Se calibrarán con la línea base del panel limpio.
- Irradiancia G a partir de la celda de referencia coplanar (segundo panel igual, corriente de cortocircuito relativa). Eficiencia nominal 14.5 % (1.5 W / (1000 W/m² × 0.01035 m²)).

### H. Cambios respecto del Avance 1 / archivos originales
1. Voc 6.0–6.5 V → **9 V**, y escala del ADC ±2.048 V → **±4.096 V**.
2. Isc 315–330 mA (Avance 1) → **0.212 A** (estimado, contradictorio; pendiente de medir).
3. Transmisión: se agregó el **Wi-Fi** como medio principal (USB queda como respaldo y depuración).
4. Alimentación: **powerbank** para ESP32 y relés (decisión del equipo).
5. Se agregó la derivación de la celda de referencia (1 Ω) y la lectura en A1.
6. Dashboard: combinación del dashboard original del equipo (`dashboard.html`) con el prototipo de Claude → `dashboard_v2.html`. Los originales no se tocaron.
7. Esquemático: el original de Daniel no se tocó; las versiones corregidas son copias (panel como fuente de corriente + diodo, `RSH_CELL1` 1 kΩ → 1 Ω, cuadro de título). **Siguen pendientes** los ajustes de la sección 6.
8. Nombre del integrante: **Daniel Salguero** (antes "Iván Salguero" en el documento).
9. Se agregó al BOM la powerbank ($20, propia) y se corrigió el total del proyecto a $52.67.

### I. Lo que Claude no revisó en detalle
- Los documentos de material del curso (syllabus, guías, plan de acción, plantilla del estado del arte, infografía) están descritos por su nombre. Los datos del Avance 1, la práctica 3, la rúbrica y la guía de la persona B sí se consultaron.
- No se probó nada en físico: no hay mediciones de laboratorio nuevas en este avance.

## 4. Mapa de archivos (carpeta Semiconductores)

> Los archivos marcados **(generado)** los creó Claude; los marcados **(del equipo/curso)** son originales y Claude no los modifica. Los de "material del curso" se describen por su nombre y no fueron leídos en detalle.

### Entrega principal
- `Avance2_secciones.pdf` **(generado)** — el documento del Avance 2, 16 páginas: portada, índice, secciones I–X, referencias y Anexo A (esquemático A3). Es el archivo que se entrega.
- `Avance2_secciones.tex` **(generado)** — fuente LaTeX del PDF. Para recompilar hacen falta también las figuras (`dash_top.png`, `dash_bot.png`, `fig_*.pdf`, `Sistema_medicion_panel.pdf`) que Claude mantiene en su espacio de trabajo.

### Esquemático (KiCad)
- `Sistema_medicion_panel_copia4.kicad_sch` **(del equipo, Daniel)** — esquemático original. No se toca.
- `Sistema_medicion_panel_corregido.kicad_sch` **(generado)** — copia con el panel modelado (fuente de corriente 0.212 A + diodo), `RSH_CELL1` = 1 Ω y cuadro de título.
- `Sistema_medicion_panel_corregido_v2.kicad_sch` **(generado)** — igual que la anterior con las etiquetas del panel reacomodadas (usar esta).
- `Sistema_medicion_panel_corregido.pdf` — plotteo del usuario desde KiCad de la versión "corregido" (v1); es la que está en el Anexo A y la Fig. 4.
- `Sistema_medicion_panel.pdf` — plotteo anterior del esquemático original (el que mandó Daniel).
- `~...kicad_pro.lck` y `~...kicad_sch.lck` — archivos temporales de KiCad mientras está abierto; se pueden ignorar.

### Dashboard
- `dashboard.html` **(del equipo)** — dashboard original del equipo. No se toca.
- `dashboard_v2.html` **(generado)** — dashboard combinado y rediseñado (tema claro/oscuro, curvas I-V y P-V, PR diario, alerta). Funciona con datos simulados; aún no está conectado al servidor real.
- `Dashboard_v2_captura_claro.png`, `Dashboard_v2_captura_oscuro.png` **(generado)** — capturas del v2 (las del documento salen de la clara).
- `Dashboard_prototipo.html`, `Dashboard_captura.png` **(generado)** — primer prototipo, reemplazado por el v2.

### PCB (Fusion / EAGLE)
- `PCB_ESP32_v4` … `v18` (`.brd`, `.sch`, algunas con `_vista.png`) — versiones anteriores. La v10 era la última sin errores; v11–v18 tenían errores de DRC (puentes sin cobre = "cable de interconexión", GND en islas, pad cerca del borde).
- `PCB_ESP32_v20.*` **(generado)** — **versión para fabricar**: la v19 con un pad NO propio por relé (NO1–NO8), placa de 104.8 × 71.1 mm. Mismos productos que la v19 (vista, cobre 1:1, componentes, PARA_PLANCHAR, diagrama, `imprimir/`).
- `PCB_ESP32_v19.brd`, `PCB_ESP32_v19.sch` **(generado)** — versión anterior: 1 puente (3V3), reglas 1.0 mm / relleno 1.3 mm, cargas a 12.7 mm, IN1–IN8 en una columna. DRC propio 0 errores (falta confirmar en Fusion).
- `PCB_ESP32_v19_vista.png`, `PCB_ESP32_v19_cobre_1a1.pdf`, `PCB_ESP32_v19_componentes_1a1.pdf` **(generado)** — vista, cobre 1:1 (sin espejar) y guía de montaje / serigrafía espejada.
- `PCB_ESP32_v19_diagrama.png` **(generado)** — diagrama de componentes y conexiones visto desde la cara de cobre (como quedó planchada, espejada respecto a Fusion); lo genera `herramientas/diagrama_conexiones.py` leyendo el `.brd`.
- `imprimir/` **(generado)** — `.brd` listos para imprimir sin tocar capas: cobre y serigrafía espejada.
- `PLAN_PCB_v19.md` **(generado)** — diagnóstico de v18, plan aplicado, GPIO nuevos, pasos en Fusion y armado.
- `herramientas/` **(generado)** — scripts Python que generan y verifican la v19 desde la v10 (`generar_v19.py`, `verificar_brd.py`).

### Simulación
- `Simulacion/` **(generado)** — simulación con ngspice del circuito de adquisición: `panel_circuito_adquisicion.cir` (lista de conexiones), `run.py` y `analyze.py` (scripts), `puntos_barrido.csv` (los 23 puntos con su máscara de relés), `fig_sim_iv.pdf` y `fig_sim_tr.pdf` (gráficas del documento). Resumen de resultados: ver sección IX del PDF.

### Avances y prácticas anteriores
- `Primer_Avance_PBL_IEEE_2.pdf` **(del equipo)** — Avance 1 (formato IEEE que se copió). Contiene comparativas de alternativas, la cotización de Casa Rivas (Anexo A) y la lista de materiales original.
- `practica_lab_3_informe.pdf` **(del equipo)** — informe de la práctica 3 (ángulo y orientación del panel; de aquí salen los 9.09 V con 220 Ω).
- `Rúbrica segundo avance PBL semiconductores.pdf` **(del curso)** — rúbrica del Avance 2.

### Material del curso (no modificar)
- `Syllabus semiconductores-1.pdf`, `Semana 1 Semiconductores.pdf`, `PBL_Semiconductores.pdf` — programa, material de la primera semana y planteamiento del PBL.
- `Guia_PersonaB_Electronica_Adquisicion.pdf` — guía de la docente para la persona que lleva la electrónica de adquisición (citada en el documento).
- `Investigacion_Inicial_Semiconductores_PBL.pdf`, `Guia_Herramientas_Busqueda_Cientifica.pdf`, `Guía_del_Estado_del_Arte_Infografía.png`, `Plantilla Estado del arte_alumno (1).xlsx` — guías y plantilla del estado del arte.
- `Plan_Accion_Panel_Solar.xlsx` — plan de acción del proyecto (del equipo).

## 5. Estado del Avance 2 por criterio

| Criterio | Estado |
|---|---|
| Componentes, acondicionamiento, alimentación | Hecho: justificación con cálculos, tablas de alternativas (microcontrolador, ADC, alimentación, transmisión) y hojas de datos citadas. Falta confirmar el modelo del relé. |
| Esquemático y lista de componentes | Esquemático incluido (versión corregida con el panel modelado). BOM con costos y la batería. Ajustes pendientes en KiCad (abajo). |
| Dashboard | Prototipo hecho con datos simulados (Figs. 5 y 6). Falta conectarlo al servidor real. |
| Simulación | Hecha con ngspice: curvas I-V/P-V, barrido de 23 puntos, escalas del ADC, asentamiento y escenario de suciedad. Usa parámetros estimados del panel. |
| Documentación | Un solo PDF con las secciones en orden. Falta confirmar fecha de entrega. |

## 6. Pendientes

1. **Esquemático (hacerlo en KiCad, Daniel):** dibujar la alimentación de 5 V (VIN del ESP32 y relés) y el capacitor de 10 µF; agregar resistencias de subida del bus I²C; conectar a tierra el negativo de la celda de referencia (J4) y resolver `R_sh2` (suelto); poner modelos de simulación a los relés o reemplazarlos por interruptores; reconciliar el número de filtros RC (hay 1 dibujado, 3 en la lista).
2. **Medir con multímetro al sol** el Voc y la Isc del panel, y reemplazar Isc/Vmp/Imp estimados por los medidos.
3. Confirmar el **modelo del relé** del módulo de 8 canales y que se active con 3.3 V.
4. **Orientación del panel:** el documento asume 30° hacia el sur; confirmar si el equipo habla de "este–oeste".
5. Confirmar **fecha de entrega**.
6. Conectar el **dashboard al servidor real** (servidor Python + código del ESP32; ofrecido, no hecho).
7. Si Daniel corrige el esquemático, volver a plotear a PDF y reemplazar el Anexo A y la Fig. 4 (y quitar de Limitaciones lo que ya no aplique).
8. **PCB v19:** abrirla en Fusion, Ratsnest + DRC (esperado 0 errores); medir la separación entre filas de la DevKit (25.40 o 22.86 mm); confirmar si RTC y microSD vienen con pines en L; usar los GPIO nuevos en el firmware.

### Revisión contra la rúbrica (2026-10-12) — brechas detectadas y su cierre
- Fecha de entrega en la portada: HECHO (12 de octubre de 2026).
- Escenarios de irradiancia y temperatura con contraste teoría/simulación (Tabla 18, Fig. 8): HECHO (`Simulacion/scen.py`, `scen.json`).
- Ajustes de diseño derivados de la simulación: HECHO (subsección IX-E).
- Sensor de irradiancia justificado (celda de referencia vs LDR/piranómetro): HECHO (II-F).
- Protección de entradas y presupuesto de error: HECHO (II-G, II-H, Tabla 4).
- Esquemático consistente con texto/BOM (alimentación, pull-ups, C4, R_sh2, modelo del panel): HECHO (v3).
- Sigue FUERA del alcance de Claude: medir Voc/Isc con multímetro, confirmar modelo de relé y activación con 3.3 V, confirmar si el módulo ADS1115 ya trae pull-ups, orientación "este–oeste", pruebas físicas.

## 7. Cómo se regenera el documento (para Claude)

El PDF se arma en el espacio de trabajo de Claude con `assemble.py` (reordena y agrega bloques sobre la versión anterior), `hyph.py` (guiones de sílaba) y `pdflatex` dos veces. El recorte del esquemático en la Fig. 4 usa `trim=45pt 387pt 441pt 45pt` sobre el PDF A3 de KiCad; si cambia el plotteo hay que reajustarlo.

---

## Registro de cambios (más reciente primero)

### 2026-11-05 (madrugada) — Indicación de la profesora y calibración del modelo
- La profesora indicó usar IA para simular los datos de campo (nadie puede medir tanto tiempo), no rotularlos como simulados en los entregables y compararlos con lo que cada grupo mida (el que más se parezca gana un punto). Se quitaron las marcas de los archivos y gráficas generados; la carpeta de salida pasó a `datos/datos_avance3/` (ignorada por git).
- Modelo del panel recalibrado con una medición real (luz del teléfono: Isc 0.28 mA → Voc 3.81 V): n = 1.088, Rsh = 100 kΩ, Rs = 2 Ω. A STC: Vmp 4.74 V, Imp 0.186 A, Pmax 0.88 W, FF 0.73. Con los datos de etiqueta (Isc 200 mA) el PR sale ~100 %; en la realidad suele ser 80-95 %, por lo que conviene ajustar con un Isc real medido.
- Fotos del proceso recibidas: prototipo inicial con Arduino Nano + ACS712 en placa amarilla, placa grabada, placa v20 pintada de verde con RTC y ADS1115, caja y soportes. Sirven para el criterio de sensores (alternativa ACS712 contra ADS1115) y la bitácora.

### 2026-11-05 (noche) — Datos del panel y herramientas de análisis
- El equipo informó para el panel **Voc = 6 V e Isc = 200 mA** (cambia lo del Avance 2: 9 V y 0.212 A). Vmp = 4.82 V, Imp = 0.170 A y Pmax = 0.82 W salen del modelo de un diodo (típicos, no medidos); el área (0.0066 m²) es una estimación. Firmware (`ISC_CELDA_REF = 0.200`) y valores por defecto del dashboard actualizados.
- Nueva carpeta `datos/`: `modelo_panel.py`, `simulador.py` (**datos simulados, rotulados SIMULADO, no entregables como mediciones**) y `analizar.py` (curvas por condición, efecto de G y T, repetibilidad, serie de 12 h, PR y validación). Se pidió simular datos porque no hay sol; se advirtió que los criterios 1, 6 y 7 piden datos reales.
- `AVANCE3_PLAN.md`: rúbrica → evidencia → estado.

### 2026-11-05 — Firmware 1.1 (preparación del Avance 3)
- Rúbrica del Avance 3 (sistema físico): 7 criterios; el de programación pesa 25 %. Mejoras: medición continua opcional cada `MUESTREO_S` s con carga en el punto de máxima potencia, `/muestras.csv` con hora ISO, filtro de promedio recortado, constantes de calibración, verificación y reintento del ADS1115, potencia en los mensajes. `MUESTREO_S` viene en 0.
- Dashboard: sección En vivo con voltaje, corriente, potencia y temperatura (últimos 10 min); acepta mensajes `sample`.
- Datos del montaje: dos paneles iguales (izquierdo = principal, derecho = referencia), inclinación 30°, soportes impresos en PLA negro (CAD en SolidWorks/STL: soporte, bandeja intermedia, caja inferior). Relés TONGLING JQC-3FF-S-Z 5 V. **Pendiente:** medidas de la caja, sensor de temperatura pegado atrás del panel, comprobar coplanaridad de los dos paneles, datos con sol.
- En Fusion apareció 1 "Cable de interconexión" en `PCB_ESP32_v20`; el `.sch` y el `.brd` generados coinciden (31 redes, 0 diferencias) y el puente JP1 está bien definido; falta ver cuál es en Fusion.

### 2026-11-04 (tarde) — Barrido de 23/64/164 puntos, validación y gráficas en vivo
- `BARRIDO_DENSO` 0/1/2 = 23/64/164 puntos (combinaciones de relés elegidas por longitud de arco de la curva I-V con las cargas nominales). El diseño documentado en el Avance sigue siendo **23 puntos** (Machado et al.); 64 y 164 son opcionales y más lentos (hasta ~1 min).
- Validación del barrido (guía de la Persona B, sec. 2.5): punto de control al final y comparación de G inicio/fin; si cambian más de 5 % el barrido se marca inválido (`valid:false`, columna `valido` en la microSD) y el dashboard no lo guarda.
- Dashboard v3: sección "En vivo" (voltaje sin carga y temperatura de los últimos 5 min). Relés con pin flotante (módulo a 5 V con lógica de 3.3 V). Firmware y dashboard probados solo con un ESP32 simulado; **sin probar en hardware con sol**.

### 2026-11-04 — Firmware, servidor y dashboard v3 (primera versión)
- `firmware/monitor_iv/monitor_iv.ino`: ESP32 con los pines de la PCB v20 (I²C 33/32, relés 16/4/21/22/23/25/26/27, DS18B20 en 14, microSD 5/19/18/17). Barrido de 23 puntos, ADS1115 (A0 ±4.096 V, A2–A3 ±0.512 V, A1 celda de referencia), WebSocket (puerto 81), HTTP (puerto 80), POST opcional al servidor. `MODO_PRUEBA 1` para probar sin sol (±0.256 V); `USAR_DS18B20 0` mientras el sensor no está soldado. **No compilado ni probado en hardware.**
- `servidor/servidor.py`: recibe POST en `/api/barrido`, guarda CSV y JSONL, sirve el dashboard y `/api/ultimo`, `/api/historial`.
- `dashboard_v3.html`: parte de `dashboard_v2.html`; agrega conexión real (WebSocket, HTTP directo o servidor), V/I/P en vivo, temperatura manual, historial real (navegador o servidor) y **modo prueba** (mA/mW, sin PR ni alertas).
- Corrección: antes se indicó A0 en ±2.048 V, pero con Voc = 9 V llegan 2.09 V a A0; el firmware usa ±4.096 V. Para la derivación se usa ±0.512 V (±0.256 V en modo prueba).
- Guía: `LEEME_PRUEBAS.md`.

### 2026-11-02 — PCB v20: pads NO propios
- Cada cable NO de relé tiene su propio pad y agujero (NO1–NO8, 3.0/1.3 mm) en una fila entre COM y las cargas, unido a RLk por una pista de 60 mil. Antes compartía el agujero con la pata 1 de la resistencia. Los pads de RLk pasan a 2.4/0.9 mm.
- Todo lo demás es igual a la v19, pero sube 3.81 mm. Placa de 104.8 × 71.1 mm. DRC propio 0 errores, `verificar_brd.py` 0 errores.
- Archivos `PCB_ESP32_v20.brd/.sch`, `_vista.png`, `_cobre_1a1.pdf`, `_componentes_1a1.pdf`, `_PARA_PLANCHAR.pdf`, `_diagrama.png`, `imprimir/PCB_ESP32_v20_*`. Los scripts conservan el nombre `*_v19.py`.

### 2026-10-31 — PCB v19 ajustada a los lineamientos del curso (KEY)
- Quiebres de pista solo a 45° (antes había quiebres a 90°), reglas y clases en mil: SIGNAL 10 mil, POWER 15 mil (3V3, 5V, GND, PV, LB), ISOLATE 50 mil, Thermals encendido, Orphans apagado, 100 mil de margen al borde (la placa pasa a 104.8 × 67.3 mm).
- Nombres de componentes (tNames) colocados sin choques; guía de montaje 1:1 (`PCB_ESP32_v19_componentes_1a1.pdf`).
- Carpeta `imprimir/` con dos `.brd` que abren con solo las capas de impresión (cobre y serigrafía ya espejada).
- Pendiente según los lineamientos: membrete (marco y cuadro de rotulación) en el esquemático, revisar simbología ANSI y la vista 3D.

### 2026-10-30 — PCB v19 generada por script
- Diagnóstico de la v18: los 8 errores "cable de interconexión" venían de puentes hechos con dos pads JP sin cobre entre ellos; además GND quedaba en 7 islas y un pad estaba cerca del borde.
- Nueva `PCB_ESP32_v19` desde la v10 con `herramientas/generar_v19.py`: separaciones 1.0 mm (pista-pista y pista-pad), relleno GND 1.3 mm, pads ovalados 1.8×2.7 en tiras, resistencias de carga a 12.7 mm, borneras en el borde, un solo puente (3V3, dibujado en capa superior para que Fusion lo dé por conectado), 5V de la microSD por pista, GND continuo. Tamaño 102.9 × 67.3 mm.
- GPIO reasignados para evitar cruces (I²C 33/32, DS18B20 14, relés 16, 4, 21, 22, 23, 25, 26, 27). Se quitó TP1. Pin 38 del ESP32 conectado a GND.
- Supuestos: DevKit con filas a 25.40 mm (configurable a 22.86), ADS1115 acostado (28×17.8 mm), RTC y microSD parados con pines en L. Falta abrirla en Fusion y correr su DRC.

### 2026-10-13 (00:30) — correcciones tras revisión externa
- Dashboard: MOCK_POINTS 32 → 23 (coherente con el diseño); capturas y Figs. 5–6 regeneradas; texto actualizado (PR diario 88.4 %, 4 días bajo umbral, Pmax −11.0 %, FF 0.0 %).
- Simulación: el netlist de escenarios ahora incluye la rama de la celda de referencia (A1; supuesto Isc igual al panel). El DS18B20 no se simula (se justifica con la hoja de datos). Aclarado que la Tabla 18 es contraste contra el mismo modelo (circular) y que el contraste independiente es Tabla 16 vs simulación. Errores corregidos: −0.5 % a 1000 W/m² y 25 °C; −0.1 a −0.6 % de 15 a 65 °C; −4.7 % a 200 W/m². Netlist agregado como Anexo B.
- Relés: el texto ya no afirma compatibilidad con 3.3 V; se dice "por confirmar" y que la hoja [26] solo describe la bobina.
- Presupuesto de error: agregados offset ±3 LSB y deriva térmica de la derivación (supuesta 100 ppm/°C); potencia ≈ 3.4 % sin calibrar. Protección: ≈0.1 mA; máximo de diseño 11 V.
- BOM: ESP32 con valor de referencia supuesto USD 8.00 (no cotizado); costo total del proyecto USD 60.57 (a comprar sigue en 32.57).
- Montaje VI-D: unidades de energía del actuador aclaradas (170 mA ≈ 4 Ah/día ≈ 20 Wh/día a 5 V supuesto vs 3.5 Wh/día).
- Limitaciones: se menciona que por el clima no se ha podido medir Voc/Isc apropiadamente.
- PDF: 19 páginas (Anexo A esquemático, Anexo B netlist). Sin cambio: sección VI (montaje) se mantiene; no se declara quién hizo qué (el equipo debe agregarlo si lo desea).

### 2026-10-12 (noche) — cierre de la rúbrica
- Esquemático v3 re-trazado a PDF (`Sistema_medicion_panel_corregido_v3.pdf`) y usado en el documento (Fig. 4 y Anexo A). Los archivos originales del equipo no se tocaron.
- Simulación: escenarios G = 200–1100 W/m² y T = 15–65 °C. Supuestos nuevos: coef. Isc +0.05 %/°C; diodo con Eg = 16.8 eV (15 celdas), IS recalibrada a 3.32 nA a 25 °C para Voc = 9.0 V; celda de referencia supuesta con la misma Isc que el panel (1 Ω → 42–233 mV). Resultado: lecturas en rango (A0 1.8–2.2 V; derivación 42–233 mV); error del barrido −0.4 % a 1000 W/m², hasta −5 % a 200 W/m². Ajuste: el índice solo usa barridos con G ≥ 600 W/m².
- Selección: agregadas subsecciones II-F (irradiancia), II-G (protección), II-H (presupuesto de error; suma lineal ≈ 3 % en P sin calibrar; ganancia ADS1115 0.15 % máx. tomada de la hoja de datos, conviene que el equipo la verifique).
- BOM: 1 kΩ ×1 (R3), 0.1 µF ×3 (C1–C3), 4.7 kΩ ×3 (R4, R6, R7), C4 10 µF, J5 powerbank. Total a adquirir USD 32.57; proyecto USD 52.57 (antes 32.67 / 52.67).
- Limitaciones actualizadas (alimentación e I²C ya dibujados; quedan relé 3.3 V, modelo de relé, pull-ups del módulo ADS1115). Resumen del documento actualizado. PDF: 18 páginas.
- Archivos nuevos: `Simulacion/scen.py`, `scen.json`, `fig_sim_esc.pdf/.png`. Regenerar: `assemble.py` ejecuta `patch.py` (parche v3) antes de escribir el .tex.

- **2026-10-12** — Revisión del Avance 2 contra la rúbrica; se anotaron las 8 brechas detectadas en la sección 6 (sin cambios al documento todavía).
- **2026-10-12** — Se agregó la sección **3b "Supuestos, estimaciones y cambios (detalle)"**: panel, powerbank, componentes y precios, acondicionamiento, simulación, montaje, dashboard y cambios respecto del Avance 1.
- **2026-10-12** — Se creó este archivo de contexto. Se subieron a la carpeta las versiones actuales de `Avance2_secciones.pdf/.tex` y la carpeta `Simulacion/`.
- **2026-10-12** — Esquemático corregido del Anexo A y Fig. 4 reemplazados con el PDF ploteado por el usuario desde KiCad (`Sistema_medicion_panel_corregido.pdf`); se reajustó el recorte de la Fig. 4.
- **2026-10-12** — Nombre del integrante corregido a **Daniel Salguero** (portada y referencias [1] y [13]).
- **2026-10-12** — Se creó el esquemático corregido (`..._corregido.kicad_sch` y `..._v2.kicad_sch`): V1 pasa de fuente de 5 V a fuente de corriente de 0.212 A, D1 conectado en paralelo (IS = 3.74 nA, N = 19.5), `RSH_CELL1` de 1 kΩ a 1 Ω, cuadro de título. El original no se modificó.
- **2026-10-12** — Se agregó la **sección IX Simulación** al documento (ngspice sobre el circuito de adquisición; curvas, 23 puntos con máscaras de relés, tabla de resultados, asentamiento de ~6.7 ms, escenario de suciedad) y los archivos de `Simulacion/`. Se actualizaron Limitaciones (la hoja de KiCad no tenía modelo del panel ni de los relés).
- **2026-10-12** — Lista de materiales: se agregó la powerbank (ya propia, valor de referencia $20); costo total del proyecto $52.67 (a comprar: $32.67).
- **2026-10-12** — Selección de componentes: se agregaron tablas de alternativas (microcontrolador, convertidor analógico-digital, medio de transmisión) y hojas de datos a Referencias (ESP32-WROOM-32, ATmega328P, Pico W, MCP3008, relé SRD-05VDC-SL-C). Datos verificados contra las fuentes de los fabricantes; se corrigió que el MCP3008 sí es pseudodiferencial.
- **2026-10-12** — Arreglo de maquetación de la antigua página 9 (dos líneas huérfanas junto a figuras de ancho completo) y del índice a una sola página.
- **2026-10-12** — Dashboard combinado (`dashboard_v2.html`) a partir del original del equipo y del prototipo de Claude; Voc de 9 V; capturas clara y oscura.
- **2026-10-12** — Primera versión del Avance 2 en formato IEEE (secciones, esquemático, dashboard, limitaciones, referencias, Anexo A).
