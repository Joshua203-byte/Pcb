"""Junta en una sola hoja A4 el cobre 1:1 (arriba) y la serigrafia espejada (abajo).
Uso: python3 herramientas/una_hoja.py COBRE.pdf COMPONENTES.pdf SALIDA.pdf"""
import sys
from pypdf import PdfReader, PdfWriter, Transformation
mm = 72 / 25.4
r1 = PdfReader(sys.argv[1]); r2 = PdfReader(sys.argv[2])
base = r1.pages[0]
seri = r2.pages[1]
base.merge_transformed_page(seri, Transformation().translate(0, -140 * mm))
w = PdfWriter(); w.add_page(base)
w.write(sys.argv[3])
