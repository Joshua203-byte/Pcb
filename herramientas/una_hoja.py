"""Junta en una sola hoja tamano CARTA (8.5 x 11 in) el cobre 1:1 (arriba) y la serigrafia espejada (abajo).
Uso: python3 herramientas/una_hoja.py COBRE.pdf COMPONENTES.pdf SALIDA.pdf"""
import sys
from pypdf import PdfReader, PdfWriter, Transformation, PageObject
mm = 72 / 25.4
r1 = PdfReader(sys.argv[1]); r2 = PdfReader(sys.argv[2])
a4 = r1.pages[0]
a4.merge_transformed_page(r2.pages[1], Transformation().translate(0, -140 * mm))
ALTO_A4 = float(a4.mediabox.height)
carta = PageObject.create_blank_page(width=612, height=792)
# misma distancia desde el borde de arriba que en A4; escala 1:1 sin cambios
carta.merge_transformed_page(a4, Transformation().translate(0, 792 - ALTO_A4))
w = PdfWriter(); w.add_page(carta)
w.write(sys.argv[3])
