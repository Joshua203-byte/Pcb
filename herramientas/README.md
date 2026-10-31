# Herramientas de la PCB v19

Generan `PCB_ESP32_v19.brd/.sch` a partir de `PCB_ESP32_v10.brd/.sch`. Ver `../PLAN_PCB_v19.md`.

| Archivo | Qué hace |
|---|---|
| `pcb_geo.py` | Reglas (separaciones, relleno), huellas nuevas y la medida entre filas del ESP32 (`SEP_ESP32`). |
| `diseno_v19.py` | Colocación de las piezas, lista de redes, GPIO y puntos de paso del enrutado. |
| `pcb_router.py` | Enrutador A* de una capa sobre una rejilla de 0.3175 mm. |
| `enrutar_v19.py` | Enruta red por red y une las islas de GND con pistas. |
| `pcb_drc.py` | Simula el relleno de GND y revisa separaciones, borde, taladros y conexiones. |
| `generar_v19.py` | Hace todo y escribe `.brd`, `.sch`, la vista PNG, el PDF 1:1 y `reporte_v19.json`. |
| `verificar_brd.py` | Revisa un `.brd` ya escrito, leyéndolo como Fusion. |
| `vista.py` | Dibujos (PNG y PDF de cobre 1:1). |
| `serigrafia.py` | Nombres de componentes sin choques y guía de montaje 1:1 (normal y espejada). |

```bash
pip install shapely matplotlib numpy
python3 herramientas/generar_v19.py
python3 herramientas/verificar_brd.py PCB_ESP32_v19.brd
```
