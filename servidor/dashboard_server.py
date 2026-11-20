#!/usr/bin/env python3
# ============================================================
# CODANOR — Panel de Control (Dashboard) + Gobierno de Proyectos
# dashboard_server.py  ·  Flask :5003
# ============================================================
# Sirve plataforma-seguimiento.html y sus assets estáticos (como siempre) Y,
# desde v2.0, expone el módulo de Gobierno y Monitorización de ~/Proyectos:
#   - Escaneo/inventario/clasificación de ~/Proyectos (gov_scanner.py)
#   - Ficha técnica por proyecto
#   - Panel de salud de los 6 servidores Flask del ecosistema
#   - BD propia gov.db (independiente de plataforma.db y tracker.db)
#
# Rutas estáticas (SIN cambios respecto a v1.0):
#   /                        → plataforma-seguimiento.html
#   /dashboard               → plataforma-seguimiento.html
#   /analisis-codigo         → analisis-codigo.html
#   /analisis-codigo.html    → analisis-codigo.html
#   /<fichero>               → asset estático de PLATAFORMA_OpenCode-NEW/ (restringido)
#
# API de Gobierno (nuevo):
#   POST /api/gov/scan              GET  /api/gov/scan/status
#   GET  /api/gov/inventario        GET  /api/gov/resumen
#   GET  /api/gov/proyectos         PUT  /api/gov/inventario/clasificar
#   GET  /api/gov/scans             GET  /api/gov/export/word|excel
# API de Monitorización (nuevo):
#   GET  /api/mon/salud             GET  /api/mon/alertas
#   POST /api/mon/alertas/<id>/resolver
# ============================================================

import io
import os
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, send_file, abort
from flask_cors import CORS

import gov_scanner

# ─── CONFIGURACIÓN ───────────────────────────────────────────────────────────

BASE_DIR   = Path(__file__).parent.resolve()   # .../PLATAFORMA_OpenCode-NEW/servidor/
STATIC_DIR = BASE_DIR.parent.resolve()         # .../PLATAFORMA_OpenCode-NEW/  (assets web)
ROOT_DIR   = STATIC_DIR.parent.resolve()       # .../Proyectos/  (raíz para gobierno)
DB_PATH    = BASE_DIR / 'gov.db'               # BD PROPIA del :5003
PORT       = 5003
HOST       = '0.0.0.0'

# ─── APP FLASK ────────────────────────────────────────────────────────────────

app = Flask(__name__)
CORS(app)

gov_scanner.init_db(DB_PATH)


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def _no_cache(resp):
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp


def _safe_static(filename):
    """Devuelve la ruta absoluta de un asset SOLO si está dentro de STATIC_DIR.

    Refuerza contra path-traversal: ~/Proyectos NUNCA se sirve como archivos.
    """
    candidate = (STATIC_DIR / filename).resolve()
    if not candidate.is_relative_to(STATIC_DIR):
        abort(403)
    if not candidate.is_file():
        abort(404)
    return candidate


def _client_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr or '')


# ─── RUTAS ESTÁTICAS (comportamiento v1.0 preservado) ──────────────────────────

@app.route('/')
@app.route('/dashboard')
def index():
    return _no_cache(send_from_directory(str(STATIC_DIR), 'plataforma-seguimiento.html'))


@app.route('/analisis-codigo')
@app.route('/analisis-codigo.html')
def analisis_codigo():
    return _no_cache(send_from_directory(str(STATIC_DIR), 'analisis-codigo.html'))


@app.route('/<path:filename>')
def static_files(filename):
    """Sirve assets estáticos de PLATAFORMA_OpenCode-NEW/, restringido a STATIC_DIR."""
    ruta = _safe_static(filename)
    return send_from_directory(str(STATIC_DIR), str(ruta.relative_to(STATIC_DIR)))


# ─── API: GOBIERNO ─────────────────────────────────────────────────────────────

@app.route('/api/gov/scan', methods=['POST'])
def gov_scan():
    body = request.get_json(silent=True) or {}
    con_hash = bool(body.get('con_hash', False))
    lanzado = gov_scanner.lanzar_escaneo_async(ROOT_DIR, DB_PATH, con_hash=con_hash)
    if not lanzado:
        return jsonify({'ok': False, 'error': 'Ya hay un escaneo en curso'}), 409
    gov_scanner.auditar(DB_PATH, 'scan', f'con_hash={con_hash}', ip=_client_ip())
    return jsonify({'ok': True, 'status': gov_scanner.job_status()})


@app.route('/api/gov/scan/status', methods=['GET'])
def gov_scan_status():
    return jsonify(gov_scanner.job_status())


@app.route('/api/gov/resumen', methods=['GET'])
def gov_resumen():
    return jsonify(gov_scanner.resumen(DB_PATH))


@app.route('/api/gov/inventario', methods=['GET'])
def gov_inventario():
    import sqlite3
    cat = request.args.get('categoria')
    nivel = request.args.get('nivel')
    carpeta = request.args.get('carpeta')
    q = request.args.get('q')
    limit = min(int(request.args.get('limit', 500)), 5000)

    sql = 'SELECT ruta, nombre, ext, carpeta_raiz, tamanyo, mtime, categoria, nivel_confidencialidad, en_git FROM gov_inventario WHERE 1=1'
    params = []
    if cat:
        sql += ' AND categoria=?'; params.append(cat)
    if nivel:
        sql += ' AND nivel_confidencialidad=?'; params.append(nivel)
    if carpeta:
        sql += ' AND carpeta_raiz=?'; params.append(carpeta)
    if q:
        sql += ' AND ruta LIKE ?'; params.append(f'%{q}%')
    sql += ' ORDER BY tamanyo DESC LIMIT ?'; params.append(limit)

    conn = sqlite3.connect(str(DB_PATH)); conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute(sql, params)]
    conn.close()
    return jsonify({'items': rows, 'count': len(rows)})


@app.route('/api/gov/proyectos', methods=['GET'])
def gov_proyectos():
    import sqlite3, json as _json
    conn = sqlite3.connect(str(DB_PATH)); conn.row_factory = sqlite3.Row
    rows = []
    for r in conn.execute('SELECT * FROM gov_proyectos ORDER BY es_proyecto DESC, nombre'):
        d = dict(r)
        try:
            d['loc'] = _json.loads(d.pop('loc_json') or '{}')
        except Exception:
            d['loc'] = {}
        d['loc_total'] = sum(d['loc'].values())
        rows.append(d)
    conn.close()
    return jsonify({'items': rows, 'count': len(rows)})


@app.route('/api/gov/inventario/clasificar', methods=['PUT'])
def gov_clasificar():
    import sqlite3
    body = request.get_json(silent=True) or {}
    ruta = body.get('ruta'); nivel = body.get('nivel')
    if not ruta or nivel not in ('publico', 'interno', 'confidencial', 'restringido'):
        return jsonify({'ok': False, 'error': 'ruta y nivel válido requeridos'}), 400
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.execute('UPDATE gov_inventario SET nivel_confidencialidad=? WHERE ruta=?',
                       (nivel, ruta))
    conn.commit(); conn.close()
    if cur.rowcount == 0:
        return jsonify({'ok': False, 'error': 'ruta no encontrada'}), 404
    gov_scanner.auditar(DB_PATH, 'clasificar', f'{ruta} → {nivel}', ip=_client_ip())
    return jsonify({'ok': True})


@app.route('/api/gov/scans', methods=['GET'])
def gov_scans():
    import sqlite3
    conn = sqlite3.connect(str(DB_PATH)); conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute('SELECT * FROM gov_scans ORDER BY id DESC LIMIT 30')]
    conn.close()
    return jsonify({'items': rows})


# ─── API: MONITORIZACIÓN ───────────────────────────────────────────────────────

@app.route('/api/mon/salud', methods=['GET'])
def mon_salud():
    import sqlite3
    servidores = gov_scanner.health_check()
    conn = sqlite3.connect(str(DB_PATH)); conn.row_factory = sqlite3.Row
    try:
        integridad = conn.execute('PRAGMA integrity_check').fetchone()[0]
    except Exception as e:
        integridad = f'error: {e}'
    n_alertas = conn.execute("SELECT COUNT(*) FROM gov_alertas WHERE estado='abierta'").fetchone()[0]
    por_sev = {r['severidad']: r['n'] for r in conn.execute(
        "SELECT severidad, COUNT(*) n FROM gov_alertas WHERE estado='abierta' GROUP BY severidad")}
    ultimo = conn.execute('SELECT * FROM gov_scans ORDER BY id DESC LIMIT 1').fetchone()
    conn.close()
    return jsonify({
        'servidores': servidores,
        'gov_db_integridad': integridad,
        'n_alertas_abiertas': n_alertas,
        'alertas_por_severidad': por_sev,
        'ultimo_scan': dict(ultimo) if ultimo else None,
    })


@app.route('/api/mon/alertas', methods=['GET'])
def mon_alertas():
    import sqlite3
    estado = request.args.get('estado', 'abierta')
    conn = sqlite3.connect(str(DB_PATH)); conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute(
        'SELECT * FROM gov_alertas WHERE estado=? ORDER BY '
        "CASE severidad WHEN 'alta' THEN 0 WHEN 'media' THEN 1 ELSE 2 END, id DESC LIMIT 200",
        (estado,))]
    conn.close()
    return jsonify({'items': rows, 'count': len(rows)})


@app.route('/api/mon/alertas/<int:alerta_id>/resolver', methods=['POST'])
def mon_resolver(alerta_id):
    import sqlite3, datetime
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.execute("UPDATE gov_alertas SET estado='resuelta', resuelta_en=? WHERE id=?",
                       (datetime.datetime.now().isoformat(timespec='seconds'), alerta_id))
    conn.commit(); conn.close()
    if cur.rowcount == 0:
        return jsonify({'ok': False, 'error': 'alerta no encontrada'}), 404
    gov_scanner.auditar(DB_PATH, 'resolver_alerta', f'id={alerta_id}', ip=_client_ip())
    return jsonify({'ok': True})


# ─── API: EXPORTACIÓN ──────────────────────────────────────────────────────────

@app.route('/api/gov/export/excel', methods=['GET'])
def gov_export_excel():
    import sqlite3, openpyxl
    from openpyxl.styles import Font, PatternFill
    conn = sqlite3.connect(str(DB_PATH)); conn.row_factory = sqlite3.Row
    wb = openpyxl.Workbook()
    ws = wb.active; ws.title = 'Inventario'
    cols = ['ruta', 'nombre', 'ext', 'carpeta_raiz', 'tamanyo', 'mtime',
            'categoria', 'nivel_confidencialidad', 'en_git']
    ws.append([c.upper() for c in cols])
    for cell in ws[1]:
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill('solid', fgColor='1275A3')
    for r in conn.execute(f"SELECT {','.join(cols)} FROM gov_inventario ORDER BY tamanyo DESC"):
        ws.append([r[c] for c in cols])
    conn.close()
    buf = io.BytesIO(); wb.save(buf); buf.seek(0)
    return send_file(buf, as_attachment=True, download_name='gobierno-inventario.xlsx',
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@app.route('/api/gov/export/word', methods=['GET'])
def gov_export_word():
    import sqlite3
    from docx import Document
    from docx.shared import Pt, RGBColor
    conn = sqlite3.connect(str(DB_PATH)); conn.row_factory = sqlite3.Row
    r = gov_scanner.resumen(DB_PATH)
    doc = Document()
    t = doc.add_heading('Inventario de Gobierno — ~/Proyectos', level=0)
    t.runs[0].font.color.rgb = RGBColor(26, 26, 46)
    doc.add_paragraph('CODANOR — Jafa, S.L. — Barcelona, Catalunya')
    doc.add_paragraph(f"Ficheros: {r['n_ficheros']} · Tamaño: {round(r['tamanyo_total']/1024/1024)} MB "
                      f"· Proyectos: {r['n_proyectos']} · Alertas abiertas: {r['n_alertas_abiertas']}")
    doc.add_heading('Clasificación por nivel de confidencialidad', level=1)
    tbl = doc.add_table(rows=1, cols=2); tbl.style = 'Table Grid'
    tbl.rows[0].cells[0].text = 'Nivel'; tbl.rows[0].cells[1].text = 'Nº ficheros'
    for x in r['por_nivel']:
        c = tbl.add_row().cells; c[0].text = str(x['nivel']); c[1].text = str(x['n'])
    conn.close()
    buf = io.BytesIO(); doc.save(buf); buf.seek(0)
    return send_file(buf, as_attachment=True, download_name='gobierno-inventario.docx',
                     mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')


# ─── ARRANQUE ─────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print(f'''
╔══════════════════════════════════════════════════════════╗
║   CODANOR — Panel de Control + Gobierno  (Flask v2.0)   ║
╠══════════════════════════════════════════════════════════╣
║   http://localhost:{PORT}/                                  ║
║   Raíz de gobierno: {str(ROOT_DIR):<37}║
║   BD propia: {DB_PATH.name:<44}║
╠══════════════════════════════════════════════════════════╣
║   /                     Dashboard                        ║
║   /analisis-codigo      Scanner IA                       ║
║   /api/gov/*            Gobierno de ~/Proyectos          ║
║   /api/mon/*            Monitorización 6 servidores      ║
║   Ctrl+C para detener                                   ║
╚══════════════════════════════════════════════════════════╝
''')
    app.run(host=HOST, port=PORT, debug=False)
