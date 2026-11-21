#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gov_scanner.py — Módulo de Gobierno y Monitorización de ~/Proyectos
===================================================================
CODANOR — Jafa, S.L. | Barcelona, Catalunya

Escanea la carpeta ~/Proyectos (metadatos siempre; hash sha256 híbrido bajo
demanda y solo para ficheros < MAX_HASH_MB). Clasifica ficheros por categoría y
nivel de confidencialidad (ISO 27001 A.5.12 / ENS), genera una ficha técnica por
proyecto y detecta alertas de gobierno.

NO lee el contenido de proyectos marcados como "restringido" (p. ej. OSSINT):
solo registra metadatos de disco.

Usado por dashboard_server.py (:5003). BD propia: gov.db (independiente de
plataforma.db y tracker.db).
"""

import os
import re
import json
import time
import hashlib
import sqlite3
import datetime
import subprocess
import threading
from pathlib import Path

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────

MAX_HASH_MB = 20          # solo se calcula sha256 para ficheros < 20 MB
BIG_FILE_MB = 100         # alerta por ficheros > 100 MB

# Carpetas/nombres excluidos del escaneo (ruido, no proyectos)
EXCLUDE_DIRS = {
    'node_modules', '.git', '__pycache__', '.scannerwork',
    'snapshots', '.venv', 'venv', '.DS_Store', '.Trash',
    '.SynologyWorkingDirectory',
}
# Carpetas de nivel 1 que NO son proyectos (se inventarían pero se marcan aparte)
NON_PROJECT_DIRS = {
    'OBSOLETO', '_REVISION_BORRADOS_2026-06-07', 'Cambio Plantillas.app',
}
# Proyectos RESTRINGIDOS: solo metadatos, nunca open()/hash/git/LOC
RESTRICTED_PROJECTS = {'OSSINT'}

# Extensiones de código para el conteo de LOC
CODE_EXTS = {'.py', '.js', '.html', '.css', '.md', '.sh', '.sql'}

# Patrones de ficheros potencialmente sensibles (credenciales)
CRED_PATTERNS = re.compile(r'(\.env$|auth\.json$|.*token.*|.*secret.*|.*credential.*|'
                           r'clientes_codanor\.json$|.*\.pem$|.*\.key$)', re.IGNORECASE)

# Mapa proyecto → puerto del servidor Flask asociado (si aplica)
PROJECT_PORTS = {
    'Seguimiento de Actas de reunión': 5000,
    'Plataforma_Seguimiento_Proyectos': 5001,
    'Planificacion_Diaria_Proyectos': 5002,
    'PLATAFORMA_OpenCode-NEW': 5003,
    'Seguimiento_licitaciones': 5050,
    'legislacion_monitor-NEW': 8080,
    'Wiki_CODANOR': 3000,
}

# Servidores Flask del ecosistema para el health-check (:5003)
ECOSYSTEM_SERVERS = [
    {'puerto': 5000, 'nombre': 'Actas',         'bind': 'local'},
    {'puerto': 5001, 'nombre': 'Plataforma',    'bind': 'lan'},
    {'puerto': 5002, 'nombre': 'Tracker',       'bind': 'lan'},
    {'puerto': 5003, 'nombre': 'Gobierno',      'bind': 'lan'},
    {'puerto': 5050, 'nombre': 'Licitaciones',  'bind': 'local'},
    {'puerto': 8080, 'nombre': 'Legislación',   'bind': 'local'},
]

# Estado del job de escaneo en curso (patrón idéntico a _scanner_jobs de server.py)
_gov_job = {
    'running': False, 'fase': 'idle', 'n_ficheros': 0,
    'proyecto_actual': '', 'started': None, 'finished': None,
    'scan_id': None, 'error': None,
}
_gov_lock = threading.Lock()


# ─── BASE DE DATOS (gov.db) ────────────────────────────────────────────────────

def init_db(db_path):
    """Crea las tablas de gov.db si no existen. Seguro de ejecutar varias veces."""
    conn = sqlite3.connect(str(db_path))
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS gov_inventario (
            ruta                    TEXT PRIMARY KEY,
            nombre                  TEXT,
            ext                     TEXT,
            carpeta_raiz            TEXT,
            tamanyo                 INTEGER,
            mtime                   TEXT,
            sha256                  TEXT,
            categoria               TEXT,
            nivel_confidencialidad  TEXT,
            en_git                  INTEGER DEFAULT 0,
            scan_id                 INTEGER,
            updated_at              TEXT
        );
        CREATE TABLE IF NOT EXISTS gov_proyectos (
            nombre              TEXT PRIMARY KEY,
            ruta                TEXT,
            tamanyo             INTEGER,
            n_ficheros          INTEGER,
            tiene_git           INTEGER DEFAULT 0,
            tiene_agents        INTEGER DEFAULT 0,
            tiene_memory        INTEGER DEFAULT 0,
            tiene_opencode      INTEGER DEFAULT 0,
            loc_json            TEXT,
            ultimo_commit       TEXT,
            rama                TEXT,
            cambios_pendientes  INTEGER DEFAULT 0,
            puerto              INTEGER,
            nivel_dominante     TEXT,
            es_proyecto         INTEGER DEFAULT 1,
            scan_id             INTEGER,
            updated_at          TEXT
        );
        CREATE TABLE IF NOT EXISTS gov_scans (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha           TEXT,
            n_ficheros      INTEGER,
            tamanyo_total   INTEGER,
            n_nuevos        INTEGER DEFAULT 0,
            n_modificados   INTEGER DEFAULT 0,
            n_borrados      INTEGER DEFAULT 0,
            con_hash        INTEGER DEFAULT 0,
            duracion_s      REAL,
            estado          TEXT
        );
        CREATE TABLE IF NOT EXISTS gov_alertas (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo        TEXT,
            severidad   TEXT,
            ruta        TEXT,
            mensaje     TEXT,
            estado      TEXT DEFAULT 'abierta',
            creada_en   TEXT,
            resuelta_en TEXT
        );
        CREATE TABLE IF NOT EXISTS gov_auditoria (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            accion   TEXT,
            detalle  TEXT,
            usuario  TEXT,
            ip       TEXT,
            fecha    TEXT
        );
    ''')
    conn.commit()
    conn.close()


def _now_iso():
    return datetime.datetime.now().isoformat(timespec='seconds')


def auditar(db_path, accion, detalle='', usuario='sistema', ip=''):
    """Registra un evento en gov_auditoria (ISO 27001 A.8.15)."""
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        'INSERT INTO gov_auditoria (accion, detalle, usuario, ip, fecha) VALUES (?,?,?,?,?)',
        (accion, detalle, usuario, ip, _now_iso())
    )
    conn.commit()
    conn.close()


# ─── CLASIFICACIÓN (ISO 27001 A.5.12 / ENS) ────────────────────────────────────

def clasificar(ruta_rel, carpeta_raiz, ext):
    """Devuelve (categoria, nivel_confidencialidad) por reglas de patrón."""
    low = ruta_rel.lower()

    # Nivel por defecto según el proyecto raíz
    if carpeta_raiz in RESTRICTED_PROJECTS:
        return ('osint', 'restringido')

    # Datos personales / clientes → confidencial
    if ('clientes_codanor' in low or 'rgpd' in low or 'lopd' in low
            or 'eipd' in low or 'tracker.db' in low or 'plataforma.db' in low):
        return ('datos', 'confidencial')

    # Credenciales → restringido
    if CRED_PATTERNS.search(os.path.basename(low)):
        return ('secreto', 'restringido')

    # Riesgos
    if 'riesgo' in low or 'gestion_riesgos' in carpeta_raiz.lower():
        return ('riesgos', 'confidencial')

    # Legislación / normativa pública
    if 'legislacion' in low or 'boe' in low or 'ley' in low:
        return ('legislacion', 'publico')

    # Manuales / documentación
    if ext in ('.html', '.docx', '.pdf', '.md') and (
            'manual' in low or 'guia' in low or 'informe' in low
            or 'propuesta' in low or 'documento' in low):
        return ('manuales', 'interno')

    # Código / desarrollo
    if ext in CODE_EXTS:
        return ('desarrollo', 'interno')

    return ('otros', 'interno')


# ─── ESCANEO DE FICHEROS ───────────────────────────────────────────────────────

def _git_en(carpeta):
    return (Path(carpeta) / '.git').exists()


def _sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def escanear(root, db_path, con_hash=False):
    """Recorre root y vuelca metadatos a gov_inventario + fichas a gov_proyectos.

    Metadatos siempre; sha256 solo si con_hash y tamaño < MAX_HASH_MB.
    Proyectos RESTRICTED: solo metadatos, nunca hash/git/LOC/open().
    """
    root = Path(root).resolve()
    t0 = time.time()
    conn = sqlite3.connect(str(db_path))

    cur = conn.execute(
        'INSERT INTO gov_scans (fecha, estado, con_hash) VALUES (?,?,?)',
        (_now_iso(), 'en_curso', 1 if con_hash else 0)
    )
    scan_id = cur.lastrowid
    conn.commit()

    with _gov_lock:
        _gov_job.update({'running': True, 'fase': 'escaneando', 'n_ficheros': 0,
                         'scan_id': scan_id, 'started': _now_iso(),
                         'finished': None, 'error': None})

    n_ficheros = 0
    tamanyo_total = 0
    max_hash_bytes = MAX_HASH_MB * 1024 * 1024
    git_cache = {}

    try:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
            rel_dir = os.path.relpath(dirpath, root)
            carpeta_raiz = rel_dir.split(os.sep)[0] if rel_dir != '.' else ''

            with _gov_lock:
                _gov_job['proyecto_actual'] = carpeta_raiz

            if carpeta_raiz not in git_cache:
                git_cache[carpeta_raiz] = _git_en(root / carpeta_raiz) if carpeta_raiz else False
            en_git = 1 if git_cache[carpeta_raiz] else 0
            restringido = carpeta_raiz in RESTRICTED_PROJECTS

            for fn in filenames:
                if fn in EXCLUDE_DIRS or fn == 'Icon\r':
                    continue
                full = os.path.join(dirpath, fn)
                try:
                    st = os.lstat(full)
                except OSError:
                    continue
                if not os.path.isfile(full) or os.path.islink(full):
                    continue

                ext = os.path.splitext(fn)[1].lower()
                rel = os.path.relpath(full, root)
                size = st.st_size
                mtime = datetime.datetime.fromtimestamp(st.st_mtime).isoformat(timespec='seconds')
                categoria, nivel = clasificar(rel, carpeta_raiz, ext)

                sha = None
                if con_hash and not restringido and 0 < size < max_hash_bytes:
                    try:
                        sha = _sha256(full)
                    except OSError:
                        sha = None

                conn.execute('''
                    INSERT INTO gov_inventario
                      (ruta, nombre, ext, carpeta_raiz, tamanyo, mtime, sha256,
                       categoria, nivel_confidencialidad, en_git, scan_id, updated_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(ruta) DO UPDATE SET
                      tamanyo=excluded.tamanyo, mtime=excluded.mtime,
                      sha256=excluded.sha256, categoria=excluded.categoria,
                      nivel_confidencialidad=excluded.nivel_confidencialidad,
                      en_git=excluded.en_git, scan_id=excluded.scan_id,
                      updated_at=excluded.updated_at
                ''', (rel, fn, ext, carpeta_raiz, size, mtime, sha,
                      categoria, nivel, en_git, scan_id, _now_iso()))

                n_ficheros += 1
                tamanyo_total += size
                if n_ficheros % 500 == 0:
                    conn.commit()
                    with _gov_lock:
                        _gov_job['n_ficheros'] = n_ficheros

        # Borrar del inventario lo que ya no existe (de este scan)
        conn.execute('DELETE FROM gov_inventario WHERE scan_id != ?', (scan_id,))
        conn.commit()

        # Fichas por proyecto
        with _gov_lock:
            _gov_job['fase'] = 'fichando'
        fichar_proyectos(root, conn, scan_id)

        # Alertas
        with _gov_lock:
            _gov_job['fase'] = 'alertas'
        detectar_alertas(conn)

        dur = round(time.time() - t0, 2)
        conn.execute('''UPDATE gov_scans SET n_ficheros=?, tamanyo_total=?,
                        duracion_s=?, estado=? WHERE id=?''',
                     (n_ficheros, tamanyo_total, dur, 'ok', scan_id))
        conn.commit()

        with _gov_lock:
            _gov_job.update({'running': False, 'fase': 'completado',
                             'n_ficheros': n_ficheros, 'finished': _now_iso()})
    except Exception as exc:
        conn.execute('UPDATE gov_scans SET estado=? WHERE id=?', (f'error: {exc}', scan_id))
        conn.commit()
        with _gov_lock:
            _gov_job.update({'running': False, 'fase': 'error',
                             'error': str(exc), 'finished': _now_iso()})
    finally:
        conn.close()

    return scan_id, n_ficheros, tamanyo_total


# ─── FICHA TÉCNICA POR PROYECTO ────────────────────────────────────────────────

def _git_info(carpeta):
    """Devuelve (ultimo_commit, rama, cambios_pendientes) con timeout corto."""
    try:
        commit = subprocess.run(
            ['git', '-C', str(carpeta), 'log', '-1', '--format=%h %ci'],
            capture_output=True, text=True, timeout=5).stdout.strip()
        rama = subprocess.run(
            ['git', '-C', str(carpeta), 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True, text=True, timeout=5).stdout.strip()
        porcelain = subprocess.run(
            ['git', '-C', str(carpeta), 'status', '--porcelain'],
            capture_output=True, text=True, timeout=10).stdout
        cambios = len([l for l in porcelain.splitlines() if l.strip()])
        return (commit or '—', rama or '—', cambios)
    except Exception:
        return ('—', '—', 0)


def _loc_por_lenguaje(carpeta):
    """Cuenta líneas de código por extensión. Omitido en proyectos restringidos."""
    loc = {}
    for dirpath, dirnames, filenames in os.walk(carpeta):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext not in CODE_EXTS:
                continue
            full = os.path.join(dirpath, fn)
            try:
                if os.path.getsize(full) > 5 * 1024 * 1024:
                    continue
                with open(full, 'r', encoding='utf-8', errors='ignore') as f:
                    n = sum(1 for _ in f)
                loc[ext] = loc.get(ext, 0) + n
            except OSError:
                continue
    return loc


def fichar_proyectos(root, conn, scan_id):
    """Genera una ficha técnica por cada carpeta de nivel 1 en root."""
    root = Path(root)
    for entry in sorted(os.listdir(root)):
        full = root / entry
        if not full.is_dir() or entry in EXCLUDE_DIRS:
            continue

        restringido = entry in RESTRICTED_PROJECTS
        es_proyecto = 0 if entry in NON_PROJECT_DIRS else 1

        agg = conn.execute(
            'SELECT COUNT(*), COALESCE(SUM(tamanyo),0) FROM gov_inventario WHERE carpeta_raiz=?',
            (entry,)).fetchone()
        n_fich, tam = (agg[0], agg[1]) if agg else (0, 0)

        nivel_row = conn.execute('''
            SELECT nivel_confidencialidad, COUNT(*) c FROM gov_inventario
            WHERE carpeta_raiz=? GROUP BY nivel_confidencialidad ORDER BY c DESC LIMIT 1
        ''', (entry,)).fetchone()
        nivel_dom = nivel_row[0] if nivel_row else 'interno'

        tiene_git = 1 if (full / '.git').exists() else 0
        tiene_agents = 1 if (full / 'AGENTS.md').exists() else 0
        tiene_memory = 1 if (full / 'Memory.md').exists() else 0
        tiene_opencode = 1 if (full / 'opencode.json').exists() else 0

        if restringido:
            commit, rama, cambios, loc = ('—', '—', 0, {})
        else:
            commit, rama, cambios = _git_info(full) if tiene_git else ('—', '—', 0)
            loc = _loc_por_lenguaje(full)

        conn.execute('''
            INSERT INTO gov_proyectos
              (nombre, ruta, tamanyo, n_ficheros, tiene_git, tiene_agents,
               tiene_memory, tiene_opencode, loc_json, ultimo_commit, rama,
               cambios_pendientes, puerto, nivel_dominante, es_proyecto,
               scan_id, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(nombre) DO UPDATE SET
              tamanyo=excluded.tamanyo, n_ficheros=excluded.n_ficheros,
              tiene_git=excluded.tiene_git, tiene_agents=excluded.tiene_agents,
              tiene_memory=excluded.tiene_memory, tiene_opencode=excluded.tiene_opencode,
              loc_json=excluded.loc_json, ultimo_commit=excluded.ultimo_commit,
              rama=excluded.rama, cambios_pendientes=excluded.cambios_pendientes,
              puerto=excluded.puerto, nivel_dominante=excluded.nivel_dominante,
              es_proyecto=excluded.es_proyecto, scan_id=excluded.scan_id,
              updated_at=excluded.updated_at
        ''', (entry, str(full), tam, n_fich, tiene_git, tiene_agents,
              tiene_memory, tiene_opencode, json.dumps(loc, ensure_ascii=False),
              commit, rama, cambios, PROJECT_PORTS.get(entry), nivel_dom,
              es_proyecto, scan_id, _now_iso()))

    conn.execute('DELETE FROM gov_proyectos WHERE scan_id != ?', (scan_id,))
    conn.commit()


# ─── DETECCIÓN DE ALERTAS ──────────────────────────────────────────────────────

def detectar_alertas(conn):
    """Genera gov_alertas a partir del inventario actual. Reinicia las abiertas."""
    conn.execute("DELETE FROM gov_alertas WHERE estado='abierta'")
    ts = _now_iso()
    alertas = []

    # Ficheros > 100 MB
    for row in conn.execute(
            'SELECT ruta, tamanyo FROM gov_inventario WHERE tamanyo > ?',
            (BIG_FILE_MB * 1024 * 1024,)):
        mb = round(row[1] / 1024 / 1024, 1)
        alertas.append(('tamanyo', 'media', row[0], f'Fichero grande ({mb} MB)'))

    # Posibles credenciales fuera de git
    for row in conn.execute('SELECT ruta FROM gov_inventario WHERE categoria=? AND en_git=0',
                            ('secreto',)):
        alertas.append(('credencial', 'alta', row[0],
                        'Posible credencial/secreto fuera de control git'))

    # Datos confidenciales dentro de git (riesgo de fuga)
    for row in conn.execute(
            "SELECT ruta FROM gov_inventario WHERE nivel_confidencialidad='confidencial' "
            "AND en_git=1 AND ext IN ('.json','.db','.csv') AND nombre != 'opencode.json'"):
        alertas.append(('fuga_datos', 'alta', row[0],
                        'Dato confidencial potencialmente versionado en git'))

    # Duplicados por hash (si hay hashes)
    for row in conn.execute('''
            SELECT sha256, COUNT(*) c, GROUP_CONCAT(ruta, ' | ') rutas
            FROM gov_inventario WHERE sha256 IS NOT NULL
            GROUP BY sha256 HAVING c > 1 LIMIT 50'''):
        alertas.append(('duplicado', 'baja', (row[2] or '')[:500],
                        f'{row[1]} copias idénticas (sha256 {row[0][:12]}…)'))

    for tipo, sev, ruta, msg in alertas:
        conn.execute('''INSERT INTO gov_alertas
                        (tipo, severidad, ruta, mensaje, estado, creada_en)
                        VALUES (?,?,?,?,?,?)''', (tipo, sev, ruta, msg, 'abierta', ts))
    conn.commit()
    return len(alertas)


# ─── HEALTH-CHECK DE SERVIDORES ────────────────────────────────────────────────

def health_check():
    """Ping HTTP a los 6 servidores Flask del ecosistema (desde esta máquina)."""
    import urllib.request
    import concurrent.futures

    def ping(srv):
        url = f"http://127.0.0.1:{srv['puerto']}/"
        t0 = time.time()
        try:
            req = urllib.request.Request(url, method='GET')
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                code = resp.status
            estado = 'up' if code < 500 else 'down'
        except Exception:
            # Un 401/403/404 también significa que el servidor responde
            try:
                with urllib.request.urlopen(url, timeout=1.5):
                    estado = 'up'
            except Exception as e:
                estado = 'up' if any(c in str(e) for c in ('401', '403', '404')) else 'down'
        ms = round((time.time() - t0) * 1000)
        return {**srv, 'estado': estado, 'ms': ms}

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        return list(ex.map(ping, ECOSYSTEM_SERVERS))


# ─── RESUMEN / KPIs ────────────────────────────────────────────────────────────

def resumen(db_path):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    total = conn.execute('SELECT COUNT(*) n, COALESCE(SUM(tamanyo),0) t FROM gov_inventario').fetchone()
    por_cat = [dict(r) for r in conn.execute(
        'SELECT categoria, COUNT(*) n, COALESCE(SUM(tamanyo),0) t FROM gov_inventario '
        'GROUP BY categoria ORDER BY n DESC')]
    por_nivel = [dict(r) for r in conn.execute(
        'SELECT nivel_confidencialidad nivel, COUNT(*) n FROM gov_inventario '
        'GROUP BY nivel_confidencialidad ORDER BY n DESC')]
    ultimo = conn.execute('SELECT * FROM gov_scans ORDER BY id DESC LIMIT 1').fetchone()
    n_alertas = conn.execute("SELECT COUNT(*) FROM gov_alertas WHERE estado='abierta'").fetchone()[0]
    n_proy = conn.execute('SELECT COUNT(*) FROM gov_proyectos WHERE es_proyecto=1').fetchone()[0]
    conn.close()
    return {
        'n_ficheros': total['n'], 'tamanyo_total': total['t'],
        'por_categoria': por_cat, 'por_nivel': por_nivel,
        'n_proyectos': n_proy, 'n_alertas_abiertas': n_alertas,
        'ultimo_scan': dict(ultimo) if ultimo else None,
    }


# ─── VIGILANCIA DE TAMAÑO DE LOS AGENTS.md ──────────────────────────────────────

# Umbrales de líneas para clasificar el tamaño de un AGENTS.md
AGENTS_OK_MAX = 200       # < 200 líneas → OK (verde)
AGENTS_WARN_MAX = 500     # 200-500 → aviso (ámbar); > 500 → crítico (rojo)


def _estado_agents(lineas):
    """Clasifica un AGENTS.md por su nº de líneas."""
    if lineas < AGENTS_OK_MAX:
        return 'ok'
    if lineas <= AGENTS_WARN_MAX:
        return 'aviso'
    return 'critico'


def analizar_agents_md(root, max_depth=3):
    """Recorre ~/Proyectos buscando AGENTS.md y los clasifica por tamaño.

    Devuelve dict con la lista de ficheros (ruta relativa, proyecto, líneas,
    bytes, estado) y un resumen por estado. Respeta RESTRICTED_PROJECTS: para
    proyectos restringidos solo registra metadatos de disco (nunca open()).
    """
    root = Path(root).resolve()
    items = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        rel_dir = Path(dirpath).relative_to(root)
        if len(rel_dir.parts) > max_depth:
            dirnames[:] = []
            continue
        if 'AGENTS.md' not in filenames:
            continue
        ruta_abs = Path(dirpath) / 'AGENTS.md'
        rel = ruta_abs.relative_to(root)
        carpeta_raiz = rel.parts[0] if len(rel.parts) > 1 else '(raíz)'
        proyecto = carpeta_raiz if carpeta_raiz != '(raíz)' else 'Hub raíz'
        restringido = carpeta_raiz in RESTRICTED_PROJECTS
        bytes_ = ruta_abs.stat().st_size
        if restringido:
            lineas = None
            estado = 'restringido'
        else:
            try:
                with open(ruta_abs, 'r', encoding='utf-8', errors='replace') as fh:
                    lineas = sum(1 for _ in fh)
            except Exception:
                lineas = None
            estado = _estado_agents(lineas) if lineas is not None else 'desconocido'
        items.append({
            'proyecto': proyecto,
            'ruta': str(rel),
            'lineas': lineas,
            'bytes': bytes_,
            'estado': estado,
            'restringido': restringido,
        })

    items.sort(key=lambda x: (x['lineas'] is None, -(x['lineas'] or 0)))
    resumen_estados = {'ok': 0, 'aviso': 0, 'critico': 0, 'restringido': 0, 'desconocido': 0}
    for it in items:
        resumen_estados[it['estado']] = resumen_estados.get(it['estado'], 0) + 1
    return {
        'items': items,
        'total': len(items),
        'por_estado': resumen_estados,
        'umbrales': {'ok_max': AGENTS_OK_MAX, 'warn_max': AGENTS_WARN_MAX},
    }


def job_status():
    with _gov_lock:
        return dict(_gov_job)


def lanzar_escaneo_async(root, db_path, con_hash=False):
    """Arranca el escaneo en un hilo. Devuelve False si ya hay uno en curso."""
    with _gov_lock:
        if _gov_job['running']:
            return False
    th = threading.Thread(target=escanear, args=(root, db_path, con_hash), daemon=True)
    th.start()
    return True
