# Avance 3 (sistema físico): plan y estado

Rúbrica: 7 criterios. Cada uno se gana con **datos reales**; lo simulado solo prepara el camino.

| # | Criterio (peso) | Evidencia que se necesita | Estado |
|---|---|---|---|
| 1 | Curva I-V (10 %) | Curvas I-V y P-V en ≥ 2 condiciones, Isc, Voc, MPP, FF, comparación con el fabricante, efecto de T y G | Scripts listos (`datos/`); **faltan barridos reales con sol** |
| 2 | Sensores (10 %) | Justificación con rango, resolución y hoja de datos; comparación de alternativas | Base en el Avance 2; falta compilar hojas de datos y las etiquetas reales |
| 3 | Acondicionamiento (15 %) | Esquemático, cálculos de divisor, shunt, resolución, filtro y error; protecciones | PCB v20 hecha; **falta esquemático limpio, cálculos y protecciones** (la placa no las trae) |
| 4 | Programación (25 %) | Código modular y comentado, calibración, filtrado, errores, potencia, hora, datos listos para el modelo | Firmware 1.1 hecho (**sin probar con sol**) |
| 5 | Montaje (15 %) | Sistema instalado, sensor de T atrás del panel, cables firmes, protección ambiental | Caja y soportes impresos; **faltan: sensor pegado, cables fijos, sellado, coplanaridad** |
| 6 | Validación (15 %) | Mediciones contra multímetro y termómetro, error %, repetibilidad | Script listo; **faltan mediciones reales** |
| 7 | Documentación (10 %) | Esquemático, lista de materiales con costos, fotos del montaje, resultados, bitácora | En curso; faltan fotos del montaje final y la bitácora con fechas |

## Datos del montaje (dados por el equipo)
- Dos paneles iguales, de 6 V y 200 mA; izquierdo = principal, derecho = celda de referencia. Inclinación de 30°.
- Soportes y caja en PLA negro (CAD en SolidWorks/STL). Relés TONGLING JQC-3FF-S-Z de 5 V.

## Pendientes del equipo
- Barridos con sol en ≥ 2 condiciones; 10 barridos seguidos; Voc e Isc de cada panel con multímetro; R1, R2, R_SH1 y R_SH2 medidas.
- Sensor de temperatura pegado atrás del panel; comprobar que los dos paneles sean coplanares; medidas de la caja.
- Fotos del montaje final y capturas de Fusion.
