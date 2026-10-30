# PCB v19: plan y cómo usarla

La v19 se generó a partir de la v10 (la última sin errores) con un script (`herramientas/generar_v19.py`). Corrige los cinco puntos de la revisión y los errores que aparecieron entre la v11 y la v18.

| | v10 | v18 | **v19** |
|---|---|---|---|
| Errores de DRC en Fusion | 0 (con reglas de 0.5 mm) | 9 | **0 en el DRC propio** (falta confirmarlo en Fusion) |
| Puentes de cable | 3 | 5 | **1** (3V3) |
| Separación entre pistas / pista-pad | 0.5 mm | 0.5 mm | **1.0 mm** |
| Relleno GND a cualquier otra cosa | 0.8 mm | 0.8 mm | **1.3 mm** |
| Tamaño | 105.4 × 58.4 mm | 105.4 × 60.3 mm | **102.9 × 67.3 mm** |

## 1. Por qué fallaban las versiones v11–v18

* **8 errores de "cable de interconexión" (Unrouted):** en la v18 cada puente eran dos pads JP sueltos en la misma red, pero sin nada de cobre entre ellos. Para Fusion eso es una conexión sin rutear. Además, el relleno de GND quedaba partido en 7 islas.
* **1 error de "Separación del taladro":** un pad quedaba demasiado cerca del borde de la placa.
* Las reglas de la v10 (0.5 mm) no coincidían con lo que se quería en la placa (1.0 mm). Al subirlas a mano en Fusion aparecían errores en cadena, porque las pistas pasaban entre pines a 2.54 mm.

`herramientas/verificar_brd.py` lee el `.brd` igual que Fusion. Con la v18 encuentra esos mismos problemas: 3V3, SDA y 5V sin terminar, GND partido y pads a 0.3 mm.

## 2. Plan aplicado (punto por punto)

1. **Tiras hembra.** El ESP32 queda con dos filas de 19 pines y 25.40 mm entre filas, configurable en el script (ver sección 6). El ADS1115, el RTC y la microSD también van en tira hembra.
2. **Separaciones.** Las reglas quedan dentro del archivo: pista-pista 1.0 mm, pista-pad 1.0 mm, relleno 1.3 mm, cobre al borde 1.5 mm y ancho mínimo 0.8 mm. **Ninguna pista pasa entre dos pines de 2.54 mm.** El relleno no deja tiras de cobre de menos de 0.8 mm.
3. **Taladros y anillos.**
   * Tiras (ESP32, módulos, conectores): pad **ovalado 1.8 × 2.7 mm**, con más cobre para soldar sin achicar el hueco entre pines. Taladro de 0.9 mm (1.0 en las tiras macho).
   * Resistencias de señal: pad de 2.4 mm, taladro de 0.9 mm, separación de **5.08 mm**. Aquí caben las de 1 W de las derivaciones.
   * Resistencias de carga: separación de **12.7 mm**, como pedía la revisión. El pad del lado NO es de 3.0 mm con taladro de 1.3 mm, para soldar ahí el cable del relé.
   * Borneras: pad de 3.2 mm con taladro de 1.3 mm.
   * Ningún taladro queda a menos de 2 mm del borde.
4. **Puente con pads propios.** Queda **un solo puente**, el de 3V3, entre JP1A y JP1B. Son pads de 2.5 mm con taladro de 1.0 mm, y la línea está dibujada en la serigrafía. En el archivo, ese cable está dibujado como pista en la capa superior. Así Fusion lo ve conectado, pero esa capa **no se fabrica**: en la placa real es un cable soldado del lado de los componentes.
5. **Distribución.**
   * El 5V de la microSD llega con una pista, no con un puente: baja desde el pin 5V, pasa por debajo del ESP32 y sube por el borde derecho.
   * El GND es una sola pieza, sin puentes de GND, y el script comprueba que no queden islas.
   * Las borneras del panel (J1) y de la celda de referencia (J4) están en el borde izquierdo.
   * El banco de cargas está en el borde inferior: COM abajo, NO en medio y LB arriba.
   * Las 8 señales de los relés salen en **una sola columna ordenada IN1…IN8** en el borde derecho.
   * La entrada analógica (divisor, filtro y derivaciones) está junto al ADS1115, con pistas cortas.
   * **Contornos de los módulos** en la capa tDocu: el ADS1115 va acostado, con el cuerpo hacia la derecha y solo pistas debajo. El RTC y la microSD van parados (pines en L).

## 3. Cambios que afectan al firmware: GPIO nuevos

Para no cruzar pistas se reasignaron pines (el firmware todavía no estaba escrito):

| Función | GPIO v10 | **GPIO v19** |
|---|---|---|
| I²C SCL (ADS1115 + RTC) | 14 | **32** |
| I²C SDA | 27 | **33** |
| DS18B20 (DQ) | 32 | **14** |
| microSD MISO / MOSI / SCK / CS | 19 / 18 / 5 / 17 | 19 / 18 / 5 / 17 (sin cambio) |
| Relé IN1 … IN8 | 33, 25, 26, 23, 22, 21, 16, 4 | **16, 4, 21, 22, 23, 25, 26, 27** |

En el firmware: `Wire.begin(33, 32);` (SDA, SCL), `OneWire ds(14);` y `const int RELE[8] = {16, 4, 21, 22, 23, 25, 26, 27};`. El ADS1115 sigue en la dirección 0x48 (ADDR a GND).

Otros cambios respecto de la v10:

* Se quitó **TP1** (puntos de prueba), igual que en la v18: el 5V y el GND se pueden medir en J5, y el 3V3 en JP1.
* El pin 38 (GND) del ESP32 ahora también va a GND.

## 4. Cómo abrirla en Fusion

1. Abrí `PCB_ESP32_v19.sch` y `PCB_ESP32_v19.brd`, que deben estar en la misma carpeta.
2. En la placa, pulsá **Ratsnest**: así se calcula el relleno de GND, que en el archivo solo está el contorno.
3. Corré el **DRC**. Las reglas ya vienen en el archivo ("PBL v19"). Si Fusion te ofrece otras reglas, quedate con las del archivo. Debería dar 0 errores. Si aparece alguno, mandame la captura con la lista.
4. Si al abrir aparece el aviso de "preferencias de diseño" (como en tu captura), guardá una vez y desaparece.

## 5. Fabricación y armado

* **Para planchar:** usá `PCB_ESP32_v19_cobre_1a1.pdf`. Imprimí al 100 %, **sin espejar**, y comprobá que la regla mida 50 mm. Si imprimís desde Fusion, sacá solo las capas Bottom, Pads y Dimension. **No imprimas la capa Top**: es el puente.
* **Antes de imprimir, medí tu DevKit:** distancia de centro a centro entre las dos filas de pines. Si no es 25.40 mm, mirá la sección 6.
* **Puente JP1:** un cable aislado del lado de los componentes, de JP1A a JP1B, siguiendo la línea de la serigrafía. Se suelda por abajo como cualquier componente.
* **Cargas:** el cable NO del relé k va al pad grande "NO" de RLk, y el cable COM del relé k va al pad Ck (abajo).
* **Altura bajo los módulos:** bajo el ADS1115 (rectángulo punteado) no hay componentes, solo pistas. El RTC y la microSD se suponen parados, con los pines en L de fábrica. Si los tuyos vienen con pines rectos, avisame y reubico su cuerpo.

## 6. Cómo regenerarla (si cambia algo)

```bash
pip install shapely matplotlib numpy
python3 herramientas/generar_v19.py
python3 herramientas/verificar_brd.py PCB_ESP32_v19.brd
```

* Para una DevKit de **22.86 mm**, cambiá `SEP_ESP32 = 22.86` en `herramientas/pcb_geo.py` y volvé a correr el script. Ese caso ya se probó: enruta con 0 errores y la placa queda de 100.3 mm de ancho.
* La colocación está en `herramientas/diseno_v19.py`, y las reglas y huellas en `herramientas/pcb_geo.py`.
* Si movés piezas a mano en Fusion, ya no regeneres: el script parte siempre de la v10 y pisaría tus cambios.
