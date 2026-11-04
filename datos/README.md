# Análisis de datos del monitor I-V

Tres scripts (Python 3 con numpy, scipy, pandas y matplotlib):

| Archivo | Qué hace |
|---|---|
| `modelo_panel.py` | Modelo de un diodo del panel (12 celdas, Voc 6 V, Isc 200 mA a STC). Da la curva "de referencia del fabricante" a cualquier G y T. |
| `simulador.py` | **Genera datos SIMULADOS** con el formato de la microSD, pasando por la cadena de medición real (relés, derivación, divisor, ADS1115, DS18B20, celda de referencia, validación por nubes). Solo sirve para probar el análisis. |
| `analizar.py` | Lee los CSV y genera tablas y gráficas: curvas I-V y P-V por condición contra el modelo del fabricante, efecto de G y T, repetibilidad, serie de 12 h, PR y validación contra instrumentos. |

## Con datos reales
```bash
python3 datos/analizar.py --barridos barridos.csv --muestras muestras.csv --validacion validacion.csv --pnom 0.82 --salida datos/salida_real
```
- `barridos.csv` y `muestras.csv` son los de la microSD (`/barridos.csv`, `/muestras.csv`). Para etiquetar condiciones, agregá una columna `condicion` (por ejemplo `manana`, `limpio_mediodia`, `sombra_parcial`) y usá `--rep limpio_mediodia` para la repetibilidad.
- `validacion.csv`: una fila por barrido que mediste con instrumentos: `barrido,voc_ref_V,isc_ref_A,t_ref_C`.
- `--dia` acepta un CSV de barridos de un día completo para ajustar el efecto de G y T y calcular el PR.
- Si los datos no traen `origen = SIMULADO`, las gráficas salen sin marca.

## Datos simulados
```bash
python3 datos/simulador.py
python3 datos/analizar.py --barridos datos/simulados/escenarios/barridos.csv --dia datos/simulados/dia_2026-11-06/barridos.csv \
  --muestras datos/simulados/dia_2026-11-06/muestras.csv --validacion datos/simulados/escenarios/validacion.csv --salida datos/simulados/salida
```
**Los datos simulados NO son mediciones y no se pueden entregar como resultados experimentales.** Todas sus filas y gráficas llevan la marca SIMULADO.
