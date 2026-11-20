#!/usr/bin/env python3
# ============================================================
# CODANOR — Panel de Control (Dashboard)
# dashboard_server.py  ·  Flask :5003  ·  Sin base de datos propia
# ============================================================
# Sirve plataforma-seguimiento.html y sus assets estáticos.
# Las APIs (tiquets, LLM, scanner, sonar_history) siguen en :5001.
#
# Rutas servidas:
#   /                        → plataforma-seguimiento.html
#   /analisis-codigo         → analisis-codigo.html (sidebar link)
#   /analisis-codigo.html    → analisis-codigo.html
#   /<cualquier fichero>     → asset estático de PLATAFORMA_OpenCode-NEW/
# ============================================================

import os
from pathlib import Path
from flask import Flask, send_from_directory, abort
from flask_cors import CORS

# ─── CONFIGURACIÓN ───────────────────────────────────────────────────────────

BASE_DIR   = Path(__file__).parent.resolve()  # .../PLATAFORMA_OpenCode-NEW/servidor/
STATIC_DIR = BASE_DIR.parent                  # .../PLATAFORMA_OpenCode-NEW/
PORT       = 5003
HOST       = '0.0.0.0'

# ─── APP FLASK ────────────────────────────────────────────────────────────────

app = Flask(__name__)
CORS(app)

# ─── RUTAS ────────────────────────────────────────────────────────────────────

@app.route('/')
@app.route('/dashboard')
def index():
    """Sirve plataforma-seguimiento.html — punto de entrada principal."""
    resp = send_from_directory(str(STATIC_DIR), 'plataforma-seguimiento.html')
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma']        = 'no-cache'
    resp.headers['Expires']       = '0'
    return resp


@app.route('/analisis-codigo')
@app.route('/analisis-codigo.html')
def analisis_codigo():
    """Sirve analisis-codigo.html — enlazado desde el sidebar de plataforma-seguimiento."""
    resp = send_from_directory(str(STATIC_DIR), 'analisis-codigo.html')
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma']        = 'no-cache'
    resp.headers['Expires']       = '0'
    return resp


@app.route('/<path:filename>')
def static_files(filename):
    """Sirve el resto de assets estáticos:
    homogeneizacion-proyectos.html, Manual_OpenCode_Codanor.html, etc."""
    try:
        return send_from_directory(str(STATIC_DIR), filename)
    except Exception:
        abort(404)


# ─── ARRANQUE ─────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print(f'''
╔══════════════════════════════════════════════════════════╗
║   CODANOR — Panel de Control  (Flask v1.0)              ║
╠══════════════════════════════════════════════════════════╣
║   http://localhost:{PORT}/                                  ║
║   APIs tiquets / LLM / scanner → :5001                  ║
╠══════════════════════════════════════════════════════════╣
║   http://localhost:{PORT}/              Dashboard          ║
║   http://localhost:{PORT}/analisis-codigo  Scanner IA      ║
║   Ctrl+C para detener                                   ║
╚══════════════════════════════════════════════════════════╝
''')
    app.run(host=HOST, port=PORT, debug=False)
