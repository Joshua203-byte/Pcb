# Probar el monitor I-V: firmware + dashboard

Archivos:
- `firmware/monitor_iv/monitor_iv.ino`: código del ESP32 (pines de la PCB v20).
- `dashboard_v3.html`: dashboard; se abre con doble clic (no necesita instalar nada).
- `servidor/servidor.py`: servidor opcional (guarda los barridos en CSV). Para la prueba de hoy no hace falta.

## 0. Antes de todo: prueba de la PCB (`firmware/prueba_pcb/prueba_pcb.ino`)
Programa con menú en el monitor serie (115200, "Nueva línea") que revisa por separado I²C (0x48 y 0x68), ADS1115 (voltaje, corriente, referencia), RTC, microSD, los 8 relés y el Wi-Fi. Úsalo primero; cuando todo dé OK, sube `monitor_iv.ino`.

## Relés que se quedan encendidos y se calientan
El módulo de relés va a 5 V y se activa con LOW; con los 3.3 V del ESP32 un HIGH no lo apaga. Por eso en los dos programas `RELE_ENTRADA_FLOTANTE` está en 1: apagado = pin flotante (INPUT), encendido = LOW. Si con esto ningún relé hace clic, pon `RELE_ENTRADA_FLOTANTE 0` y prueba `RELE_ACTIVO_BAJO` en `true` o `false`.

## 1. Subir el código al ESP32
1. Arduino IDE → Administrador de placas → instalar **esp32** (Espressif). Placa: **ESP32 Dev Module**.
2. Administrador de bibliotecas → instalar: **Adafruit ADS1X15**, **RTClib** (Adafruit), **WebSockets** (Markus Sattler). Si el IDE pregunta por dependencias, aceptá "instalar todo".
3. Abrí `monitor_iv.ino` (la carpeta debe llamarse `monitor_iv`). En la parte de arriba poné tu Wi-Fi en `WIFI_SSID` y `WIFI_PASS`. Si no tenés Wi-Fi a mano, no cambies nada: el ESP32 crea su propia red.
4. `MODO_PRUEBA 0` es para sol; ponelo en `1` para probar de noche con la linterna. `USAR_DS18B20 1` necesita las bibliotecas **OneWire** y **DallasTemperature**; si no tenés el sensor conectado, ponelo en `0`. Subilo y abrí el Monitor Serie a **115200**.
5. El monitor serie muestra `ADS1115: OK`, `RTC DS3231: OK`, `microSD: OK` y la IP. Si algo dice "NO RESPONDE", ese módulo no está bien conectado (el programa sigue funcionando sin RTC ni microSD).

## 2. Conectar el dashboard
- Con Wi-Fi: la computadora tiene que estar en la misma red; usá la IP que muestra el monitor serie.
- Sin Wi-Fi: conectá la compu o el teléfono a la red **MonitorIV** (clave `12345678`) y usá la IP **192.168.4.1**.
1. Abrí `dashboard_v3.html` en Chrome o Edge (desde el archivo, no desde una página https).
2. Apagá **Modo simulación**. Transporte: **WebSocket directo al ESP32**. Poné la IP y tocá **Conectar**.
3. Con `MODO_PRUEBA 1` el dashboard activa solo el **Modo prueba** (barra amarilla, escala en mA y mW).
4. Tocá **Iniciar barrido I-V**.

## 3. Prueba de noche con la linterna del teléfono
- Prendé la linterna y ponela a **2–5 cm del panel**, de frente y quieta. Una luz más fuerte o más cerca da más corriente.
- Mientras esperás, **V ahora** es el voltaje del panel sin carga (Voc): tiene que subir cuando acercás la luz y bajar cuando la tapás. Eso ya confirma divisor, ADS1115 y Wi-Fi.
- En el barrido vas a oír los relés cerrarse en secuencia (23 pasos, unos 8 s).
- **Forma esperada con poca luz:** la corriente queda casi **plana** (unos pocos mA) y el voltaje sube con cada carga mayor, hasta el último punto, el circuito abierto (Voc). Con la luz de un teléfono las cargas de la placa (hasta 470 Ω) no llegan a la "rodilla" de la curva: es normal. La curva completa solo sale con sol.
- Lo que se valida: relés, ADS1115, divisor, derivación de corriente, comunicación y dashboard.

| Si pasa esto | Revisá |
|---|---|
| `ADS1115: NO RESPONDE` | SDA = GPIO33, SCL = GPIO32, VCC 3.3 V, dirección 0x48 (ADDR a GND). |
| Los relés se activan al revés (todos cerrados en reposo) | Poné `RELE_ACTIVO_BAJO false`. |
| No suena ningún relé | Alimentación de 5 V del módulo, GND común con el ESP32, cables IN1–IN8. |
| Corriente siempre 0 | Cable COM/NO de los relés, orden de las patas del módulo de relés, R_SH1 soldada. |
| Voltaje 0 | J1 (panel), R1/R2 del divisor. |
| Voltaje muy distinto al del multímetro | Medí R1 y R2 y poné los valores reales en `DIV_R1`, `DIV_R2`. |

## 4. Cambio de escala (lo que hace el modo prueba)
- Firmware: la corriente se lee en ±0.256 V (7.8 µV por cuenta, para mA) y se promedian 16 muestras; no se mide irradiancia ni se envía nada al servidor.
- Dashboard: ejes en mA y mW sin curva esperada; eficiencia, PR, degradación y alertas se apagan y **no se guardan en el historial**.
- Para sol: `MODO_PRUEBA 0` (la corriente pasa a ±0.512 V, hasta 0.5 A) y desmarcá **Modo prueba**.
- Para el sensor de temperatura: `USAR_DS18B20 1` e instalar **OneWire** y **DallasTemperature**. Hasta entonces, la temperatura se escribe a mano en el dashboard.

## Puntos del barrido y gráficas en vivo
`BARRIDO_DENSO` (solo con `MODO_PRUEBA 0`): **0** = 23 puntos (~8 s), **1** = 64 puntos (~20 s), **2** = 164 puntos (~1 min, viene así). Son combinaciones de relés (hay 255 posibles) elegidas con las cargas nominales (2.2 a 470 Ω) y repartidas a lo largo de la curva. Con más puntos la curva sale más fina, pero el sol puede cambiar durante el barrido. En modo prueba siempre son 23.

El dashboard dibuja la curva I-V **punto por punto mientras dura el barrido**. Además, en la sección **En vivo** muestra el voltaje del panel (sin carga) y la temperatura de los últimos 5 minutos.

## 5. Con servidor (opcional, como pide el proyecto)
```bash
python3 servidor/servidor.py
```
Pone `SERVER_URL = "http://IP_DE_LA_LAPTOP:8000/api/barrido"` en el firmware (con `MODO_PRUEBA 0`); el servidor guarda `servidor/datos/barridos.csv` y el dashboard, en transporte **Servidor Python**, muestra el historial de 30 días y el PR diario. Poné `AUTO_BARRIDO_S = 600` para un barrido cada 10 minutos.

## Qué se probó aquí y qué no
- Probado: el dashboard (modo WebSocket con un ESP32 simulado, HTTP directo, servidor Python con barridos de 4 días, modo prueba) y el servidor.
- **No probado: el firmware nunca se compiló ni corrió en un ESP32** (aquí no hay hardware ni Arduino). Si el IDE da algún error al compilar, pegámelo y lo corrijo.
