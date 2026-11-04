# Análisis de datos del monitor I-V

Tres scripts (Python 3 con numpy, scipy, pandas y matplotlib):

| Archivo | Qué hace |
|---|---|
| `modelo_panel.py` | Modelo de un diodo del panel (12 celdas, Voc 6 V, Isc 200 mA a STC). Da la curva "de referencia del fabricante" a cualquier G y T. |
| `simulador.py` | Genera datos con el formato de la microSD, pasando por la cadena de medición real (relés, derivación, divisor, ADS1115, DS18B20, celda de referencia, validación por nubes). |
| `analizar.py` | Lee los CSV y genera tablas y gráficas: curvas I-V y P-V por condición contra el modelo del fabricante, efecto de G y T, repetibilidad, serie de 12 h, PR y validación contra instrumentos. |

## Con datos reales
```bash
python3 datos/analizar.py --barridos barridos.csv --muestras muestras.csv --validacion validacion.csv --pnom 0.82 --salida datos/salida_real
```
- `barridos.csv` y `muestras.csv` son los de la microSD (`/barridos.csv`, `/muestras.csv`). Para etiquetar condiciones, agregá una columna `condicion` (por ejemplo `manana`, `limpio_mediodia`, `sombra_parcial`) y usá `--rep limpio_mediodia` para la repetibilidad.
- `validacion.csv`: una fila por barrido que mediste con instrumentos: `barrido,voc_ref_V,isc_ref_A,t_ref_C`.
- `--dia` acepta un CSV de barridos de un día completo para ajustar el efecto de G y T y calcular el PR.

## Datos generados con el simulador
Por indicación de la profesora, los datos de campo se generan con simulación asistida por IA, y luego se comparan con lo que cada grupo mida. El modelo se calibra con las mediciones reales del equipo (por ejemplo, la prueba con la luz del teléfono: Isc = 0.28 mA y Voc = 3.81 V).
```bash
python3 datos/simulador.py
python3 datos/analizar.py --barridos datos/datos_avance3/escenarios/barridos.csv --dia datos/datos_avance3/dia_2026-11-06/barridos.csv \
  --muestras datos/datos_avance3/dia_2026-11-06/muestras.csv --validacion datos/datos_avance3/escenarios/validacion.csv --salida datos/datos_avance3/salida --pnom 0.88
```
Para usar mediciones reales, apuntá `analizar.py` a los CSV de la microSD (mismo formato).
