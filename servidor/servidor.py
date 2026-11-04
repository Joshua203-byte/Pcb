#!/usr/bin/env python3
"""Servidor del monitor I-V (solo biblioteca estandar de Python 3.8+).

  - Recibe cada barrido del ESP32 por HTTP POST (JSON) en /api/barrido.
  - Guarda todo en  servidor/datos/barridos.csv  (se abre en Excel)  y  barridos.jsonl  (para recargar).
  - Sirve el dashboard en  http://IP_DE_LA_LAPTOP:8000/  y su API:
        GET /api/ultimo           ultimo barrido
        GET /api/historial?dias=30  barridos de los ultimos N dias

Uso:   python3 servidor/servidor.py            (puerto 8000)
       python3 servidor/servidor.py --puerto 8080
En el firmware: SERVER_URL = "http://IP_DE_LA_LAPTOP:8000/api/barrido"  (IP de la LAN, no localhost).
"""
import argparse
import json
import os
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

AQUI = os.path.dirname(os.path.abspath(__file__))
DATOS = os.path.join(AQUI, 'datos')
CSV = os.path.join(DATOS, 'barridos.csv')
JSONL = os.path.join(DATOS, 'barridos.jsonl')
DASHBOARD = os.path.join(AQUI, '..', 'dashboard_v3.html')

BARRIDOS = []          # lista de dicts: n, ts, temperature, irradiance, points [[v,i],...]
CANDADO = threading.Lock()


def cargar():
    if os.path.exists(JSONL):
        with open(JSONL, encoding='utf-8') as f:
            for linea in f:
                linea = linea.strip()
                if linea:
                    try:
                        BARRIDOS.append(json.loads(linea))
                    except ValueError:
                        pass


def guardar(sw):
    os.makedirs(DATOS, exist_ok=True)
    nuevo = not os.path.exists(CSV)
    with open(CSV, 'a', encoding='utf-8') as f:
        if nuevo:
            f.write('epoch,barrido,paso,v_V,i_A,p_W,temperatura_C,irradiancia_Wm2\n')
        for k, (v, i) in enumerate(sw['points'], 1):
            t = '' if sw['temperature'] is None else sw['temperature']
            g = '' if sw['irradiance'] is None else sw['irradiance']
            f.write('%d,%d,%d,%.4f,%.5f,%.5f,%s,%s\n' % (sw['ts'], sw['n'], k, v, i, v * i, t, g))
    with open(JSONL, 'a', encoding='utf-8') as f:
        f.write(json.dumps(sw) + '\n')


def numero(x):
    return float(x) if isinstance(x, (int, float)) and not isinstance(x, bool) else None


class Manejador(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print('[%s] %s' % (time.strftime('%H:%M:%S'), fmt % args))

    def _enviar(self, codigo, cuerpo, tipo='application/json'):
        if isinstance(cuerpo, (dict, list)):
            cuerpo = json.dumps(cuerpo)
        datos = cuerpo.encode('utf-8') if isinstance(cuerpo, str) else cuerpo
        self.send_response(codigo)
        self.send_header('Content-Type', tipo + ('; charset=utf-8' if tipo.startswith('text') or tipo == 'application/json' else ''))
        self.send_header('Content-Length', str(len(datos)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(datos)

    def do_OPTIONS(self):
        self._enviar(204, b'')

    def do_GET(self):
        url = urlparse(self.path)
        if url.path in ('/', '/dashboard', '/index.html'):
            try:
                with open(DASHBOARD, 'rb') as f:
                    self._enviar(200, f.read(), 'text/html')
            except OSError:
                self._enviar(404, {'error': 'no encuentro dashboard_v3.html junto a la carpeta servidor'})
        elif url.path == '/api/ultimo':
            with CANDADO:
                self._enviar(200, BARRIDOS[-1] if BARRIDOS else {})
        elif url.path == '/api/historial':
            dias = float(parse_qs(url.query).get('dias', ['30'])[0])
            desde = time.time() - dias * 86400
            with CANDADO:
                self._enviar(200, {'barridos': [b for b in BARRIDOS if b['ts'] >= desde]})
        else:
            self._enviar(404, {'error': 'no existe'})

    def do_POST(self):
        if urlparse(self.path).path != '/api/barrido':
            return self._enviar(404, {'error': 'no existe'})
        try:
            largo = int(self.headers.get('Content-Length', 0))
            cuerpo = json.loads(self.rfile.read(largo))
            puntos = [[float(v), float(i)] for v, i in cuerpo['points']]
            if len(puntos) < 2:
                raise ValueError('muy pocos puntos')
        except (ValueError, KeyError, TypeError) as e:
            return self._enviar(400, {'error': 'JSON invalido: %s' % e})
        ts = cuerpo.get('ts')
        # si el ESP32 no tiene hora (ts = 0) se usa la de la laptop
        ts = int(ts) if isinstance(ts, (int, float)) and ts > 1.6e9 else int(time.time())
        with CANDADO:
            sw = {'n': (BARRIDOS[-1]['n'] + 1) if BARRIDOS else 1, 'ts': ts,
                  'temperature': numero(cuerpo.get('temperature')), 'irradiance': numero(cuerpo.get('irradiance')),
                  'points': puntos}
            BARRIDOS.append(sw)
            guardar(sw)
        self.log_message('barrido %d guardado (%d puntos)', sw['n'], len(puntos))
        self._enviar(200, {'ok': True, 'n': sw['n']})


def ip_lan():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return '127.0.0.1'


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--puerto', type=int, default=8000)
    a = ap.parse_args()
    cargar()
    print('Servidor del monitor I-V. %d barridos cargados.' % len(BARRIDOS))
    print('Dashboard:  http://%s:%d/' % (ip_lan(), a.puerto))
    print('En el firmware:  SERVER_URL = "http://%s:%d/api/barrido"' % (ip_lan(), a.puerto))
    ThreadingHTTPServer(('0.0.0.0', a.puerto), Manejador).serve_forever()
