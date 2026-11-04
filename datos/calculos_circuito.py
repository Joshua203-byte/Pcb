#!/usr/bin/env python3
"""Calculo de Vmp, Imp, Pmax, FF del panel (6 V / 200 mA, 12 celdas) y de las magnitudes del circuito de medida."""
import numpy as np
import modelo_panel as m

RL = [2.2, 4.7, 10, 22, 47, 100, 220, 470]
R1, R2, RSH1, PGA_V, PGA_I = 33e3, 10e3, 1.0, 4.096, 0.512
p = m.parametros(1000, 25)
print('STC: Voc=%.3f V Isc=%.4f A Vmp=%.3f V Imp=%.4f A Pmax=%.4f W FF=%.3f Rmpp=%.1f ohm' % (
    p['voc'], p['isc'], p['vmp'], p['imp'], p['pmax'], p['ff'], p['vmp'] / p['imp']))
k = (R1 + R2) / R2
print('Divisor %.1f:1  LSB V = %.1f uV -> %.3f mV en el panel ; LSB I = %.2f uA' % (k, PGA_V / 32768 * 1e6, PGA_V / 32768 * k * 1e3, PGA_I / 32768 / RSH1 * 1e6))
for n, V, I in (('Voc', p['voc'], 0), ('Vmp', p['vmp'], p['imp']), ('Isc', 0, p['isc'])):
    print('%s: A0=%.3f V (%d cuentas) ; shunt=%.1f mV (%d cuentas)' % (n, V / k, round(V / k / PGA_V * 32768), I * RSH1 * 1e3, round(I * RSH1 / PGA_I * 32768)))
mejores = []
for mask in range(1, 256):
    R = 1 / sum(1 / RL[i] for i in range(8) if mask >> i & 1)
    I, V = m.punto_operacion(R + RSH1, 1000, 25)
    mejores.append((float(V * I), mask, R))
mejores.sort(reverse=True)
for P, mask, R in mejores[:3]:
    print('Combinacion 0x%02X (%.2f ohm): P=%.4f W = %.1f %% de Pmax' % (mask, R, P, 100 * P / p['pmax']))
