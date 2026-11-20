#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Word — Manual de la Plataforma OpenCode Tracker
CODANOR — Jafa, S.L.
v1.0 · 15/11/2026
Ruta: /Users/jaimefajeda/Proyectos/PLATAFORMA_OpenCode-NEW/MANUAL-OPENCODE-TRACKER-V01.docx
"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ─── COLORES CORPORATIVOS ───
C_PRIMARY    = RGBColor(23, 141, 194)   # #178DC2
C_PRIMARY_DK = RGBColor(18, 117, 163)   # #1275A3
C_DARK       = RGBColor(26, 26, 46)     # #1a1a2e
C_GRAY_700   = RGBColor(74, 74, 90)     # #4a4a5a
C_GRAY_600   = RGBColor(107, 107, 123)  # #6b6b7b
C_WHITE      = RGBColor(255, 255, 255)  # #ffffff
C_ACCENT     = RGBColor(18, 167, 157)   # #12A79D

TITULO        = 'Manual de la Plataforma OpenCode Tracker'
SUBTITULO     = 'Guía de uso y estado actual — Dashboard, Incidencias, Tiquets y Configuración IA'
TIPO          = 'Manual de usuario'
VERSION       = 'v1.0'
FECHA         = '15/11/2026'
AUTOR         = 'CODANOR — Jafa, S.L.'
CLASIFICACION = 'Documento interno — Uso exclusivo CODANOR'
RUTA_GUARDADO = '/Users/jaimefajeda/Proyectos/PLATAFORMA_OpenCode-NEW'
NOMBRE_ARCHIVO = 'MANUAL-OPENCODE-TRACKER-V01'


# ─── HELPERS ───
def set_cell_bg(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)


def add_header_row(table, headers, bg='1275A3'):
    row = table.rows[0]
    for i, text in enumerate(headers):
        cell = row.cells[i]
        cell.text = text
        set_cell_bg(cell, bg)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.runs[0]
        run.font.name = 'Calibri'
        run.font.size = Pt(9)
        run.font.bold = True
        run.font.color.rgb = C_WHITE


def add_section_heading(doc, number, title, level=1):
    label = f'{number}. {title}' if number != '' else title
    h = doc.add_heading(label, level=level)
    h.runs[0].font.color.rgb = C_DARK if level == 1 else C_PRIMARY
    h.runs[0].font.name = 'Calibri'
    return h


def add_sub(doc, title):
    p = doc.add_paragraph()
    run = p.add_run(title)
    run.font.name = 'Calibri'
    run.font.size = Pt(12)
    run.font.bold = True
    run.font.color.rgb = C_PRIMARY
    return p


def add_para(doc, text):
    p = doc.add_paragraph(text)
    for run in p.runs:
        run.font.name = 'Calibri'
        run.font.size = Pt(10)
        run.font.color.rgb = C_GRAY_700
    return p


def add_bullets(doc, items):
    for it in items:
        p = doc.add_paragraph(it, style='List Bullet')
        for run in p.runs:
            run.font.name = 'Calibri'
            run.font.size = Pt(10)
            run.font.color.rgb = C_GRAY_700


def add_numbered(doc, items):
    for it in items:
        p = doc.add_paragraph(it, style='List Number')
        for run in p.runs:
            run.font.name = 'Calibri'
            run.font.size = Pt(10)
            run.font.color.rgb = C_GRAY_700


def add_table(doc, headers, rows, bg='1275A3'):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = 'Table Grid'
    add_header_row(t, headers, bg)
    for r in rows:
        cells = t.add_row().cells
        for i, val in enumerate(r):
            cells[i].text = val
            p = cells[i].paragraphs[0]
            run = p.runs[0] if p.runs else p.add_run('')
            run.font.name = 'Calibri'
            run.font.size = Pt(9)
            run.font.color.rgb = C_GRAY_700
    doc.add_paragraph()
    return t


# ─── DOCUMENTO ───
doc = Document()

for section in doc.sections:
    section.page_height = Cm(29.7)
    section.page_width = Cm(21.0)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.0)

# ─── PORTADA ───
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('(CODANOR 50)')
run.font.name = 'Calibri'
run.font.size = Pt(16)
run.font.bold = True
run.font.color.rgb = C_PRIMARY
doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run(TIPO.upper())
run.font.name = 'Calibri'
run.font.size = Pt(9)
run.font.color.rgb = C_ACCENT
doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run(TITULO)
run.font.name = 'Calibri'
run.font.size = Pt(24)
run.font.bold = True
run.font.color.rgb = C_DARK

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run(SUBTITULO)
run.font.name = 'Calibri'
run.font.size = Pt(12)
run.font.color.rgb = C_GRAY_700

doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run(f'{VERSION} · {FECHA} · {AUTOR}')
run.font.name = 'Calibri'
run.font.size = Pt(10)
run.font.color.rgb = C_GRAY_700

doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('CODANOR — Jafa, S.L. — Barcelona, Catalunya')
run.font.name = 'Calibri'
run.font.size = Pt(9)
run.font.bold = True
run.font.color.rgb = C_PRIMARY_DK

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run(CLASIFICACION)
run.font.name = 'Calibri'
run.font.size = Pt(8)
run.font.italic = True
run.font.color.rgb = C_GRAY_600

doc.add_page_break()

# ─── CONTROL DE VERSIONES ───
add_section_heading(doc, '', 'Control de versiones', level=1)
add_table(doc,
          ['Versión', 'Fecha', 'Autor', 'Descripción del cambio'],
          [[VERSION, FECHA, AUTOR,
            'Versión inicial. Documenta el estado actual de la app OpenCode Tracker '
            '(plataforma-seguimiento.html, 2822 líneas) para su uso y actualización.']])

# ─── SECCIÓN 1 — INTRODUCCIÓN ───
add_section_heading(doc, 1, 'Introducción y objeto')
add_para(doc, 'OpenCode Tracker (título interno «Plataforma de Seguimiento OpenCode — CODANOR») es la '
              'aplicación web de panel de control corporativo de CODANOR para el seguimiento del trabajo con '
              'OpenCode. Es una SPA monolítica en un único archivo HTML (plataforma-seguimiento.html, 2822 líneas), '
              'con CSS embebido y JavaScript vanilla sin frameworks externos.')
add_para(doc, 'Integra cuatro bloques funcionales: Dashboard de métricas, Kanban de incidencias local, Gestor de '
              'Tiquets conectado al backend Flask, y panel de Configuración IA corporativa. Además enlaza con '
              'herramientas externas de análisis de código y homogeneización de proyectos.')
add_sub(doc, 'Arquitectura de servicio en dos puertos')
add_table(doc,
          ['Puerto', 'Servidor', 'Rol'],
          [['5003', 'servidor/dashboard_server.py', 'Sirve el HTML y los assets estáticos. No tiene base de datos propia.'],
           ['5001', 'Plataforma_Seguimiento_Proyectos/servidor/server.py', 'Provee las APIs: tiquets (/api/tiquets/*) y configuración IA corporativa (/api/corp/llm-config).']])

# ─── SECCIÓN 2 — ALCANCE ───
add_section_heading(doc, 2, 'Alcance')
add_para(doc, 'Este manual describe el estado actual de la aplicación OpenCode Tracker tal y como está implementada '
              'en plataforma-seguimiento.html, como guía de uso y base para futuras actualizaciones.')
add_sub(doc, 'Dentro del alcance')
add_bullets(doc, [
    'Navegación general y estructura de la interfaz (sidebar, header, buscador, atajos).',
    'Funcionamiento del Dashboard y sus métricas.',
    'Gestión de incidencias en el Kanban local (localStorage).',
    'Uso del Gestor de Tiquets conectado al backend Flask :5001.',
    'Configuración de la clave LLM corporativa compartida en LAN.',
    'Persistencia de datos y endpoints consumidos.',
    'Observaciones del estado actual y puntos de mejora para la actualización.',
])
add_sub(doc, 'Fuera del alcance')
add_bullets(doc, [
    'Detalle interno del servidor server.py (:5001) y esquema completo de plataforma.db.',
    'El módulo IA/LLM de las 9 apps ISO/ENS.',
    'El contenido del Manual OpenCode v2.1 (los 16 capítulos del Dashboard).',
    'Las herramientas de análisis de código y homogeneización (se enlazan, no se documentan aquí).',
])

# ─── SECCIÓN 3 — ARQUITECTURA Y TECNOLOGÍAS ───
add_section_heading(doc, 3, 'Arquitectura y tecnologías')
add_sub(doc, 'Tipo de aplicación')
add_para(doc, 'SPA de un solo archivo. La navegación se gestiona con showPage(pageId), que alterna la clase active '
              'sobre los elementos .page. El Gestor de Tiquets y la Configuración IA viven fuera del contenedor '
              'principal como overlays position:fixed y ocultan el contenido con visibility:hidden.')
add_sub(doc, 'Tecnologías empleadas')
add_table(doc,
          ['Componente', 'Tecnología', 'Notas'],
          [['Lógica', 'JavaScript vanilla', 'Sin frameworks ni librerías.'],
           ['Estilos', 'CSS embebido', 'Variables :root de la paleta CODANOR.'],
           ['Fuentes', 'Google Fonts', 'Poppins (titulares) + Nunito Sans (cuerpo).'],
           ['Iconografía', 'SVG inline', 'Estilo Feather, sin icon-font.'],
           ['Logo', 'Recurso remoto', 'codanor.com/assets/img/logo_web-50.png'],
           ['Persistencia local', 'localStorage', '3 claves (ver Sección 10).'],
           ['Backend', 'Flask :5001', 'APIs de tiquets y config IA.']])
add_sub(doc, 'Paleta corporativa')
add_para(doc, 'Definida en :root: --primary #178DC2, --accent #12A79D, --dark #1a1a2e. Incluye @media print que '
              'oculta sidebar y header al imprimir.')

# ─── SECCIÓN 4 — INTERFAZ Y NAVEGACIÓN ───
add_section_heading(doc, 4, 'Interfaz y navegación')
add_sub(doc, 'Sidebar (barra lateral)')
add_para(doc, 'Encabezada por el logo CODANOR y la marca OpenCode Tracker, se organiza en cuatro grupos:')
add_table(doc,
          ['Grupo', 'Ítem', 'Destino', 'Indicador'],
          [['Principal', 'Dashboard', 'Página SPA dashboard', '—'],
           ['Principal', 'Incidencias', 'Página SPA kanban', 'Badge #kanbanBadge'],
           ['Recursos', 'Documentación', 'Página SPA docs', '—'],
           ['Recursos', 'Changelog', 'Página SPA changelog', '—'],
           ['Acciones', 'Gestor de Tiquets', 'Overlay tickets', 'Badge #ticketsBadge'],
           ['Acciones', 'Configuración IA', 'Overlay llm-admin', 'Badge «Corp»'],
           ['Herramientas', 'Análisis de Código', 'Enlace /analisis-codigo', 'Nueva pestaña'],
           ['Herramientas', 'Homogeneización', 'homogeneizacion-proyectos.html', 'Nueva pestaña']])
add_para(doc, 'El pie de la barra muestra «Jafa, S.L. — CODANOR» / «Barcelona, Catalunya».')
add_sub(doc, 'Cabecera (header)')
add_bullets(doc, [
    'Botón hamburguesa para alternar la barra lateral en móvil.',
    'Buscador global #globalSearch → handleSearch().',
    'Botón «+ Nueva incidencia» → openNewTicketModal().',
    'Título de página dinámico #pageTitle (inicia en «Dashboard»).',
])
add_sub(doc, 'Atajos de teclado')
add_table(doc, ['Atajo', 'Acción'],
          [['Esc', 'Cierra el modal abierto.'],
           ['Ctrl / Cmd + N', 'Abre el modal de nueva incidencia.']])

# ─── SECCIÓN 5 — DASHBOARD ───
add_section_heading(doc, 5, 'Dashboard')
add_para(doc, 'Página de inicio con un resumen visual del estado del trabajo. Se compone de cuatro bloques.')
add_sub(doc, 'Tarjetas de métricas')
add_para(doc, 'Se calculan en renderDashboard() a partir de las incidencias del Kanban local (localStorage), '
              'no de los tiquets del servidor.')
add_table(doc,
          ['Tarjeta', 'ID', 'Cálculo'],
          [['Total incidencias', '#metricTotal', 'tickets.length'],
           ['Completadas', '#metricDone', "status === 'done'"],
           ['En progreso', '#metricProgress', "status === 'progress'"],
           ['Prioridad alta', '#metricHigh', "priority === 'high' && status !== 'done'"]])
add_sub(doc, 'Progreso del Manual v2.1')
add_para(doc, 'Barra de progreso al 100 % (16 de 16 capítulos) con etiqueta «v2.1 Abril 2026». ATENCIÓN: el '
              'porcentaje y el número de capítulos están hardcodeados en el HTML; no se calculan dinámicamente.')
add_table(doc,
          ['Cap.', 'Título', 'Estado'],
          [['1', 'Introducción', 'actualizado'],
           ['2', 'Agentes', 'nuevo'],
           ['3', 'Permisos', 'nuevo'],
           ['4', 'Configuración', 'nuevo'],
           ['5', 'Servidores MCP', 'nuevo'],
           ['6', 'Comandos/Skills', 'nuevo'],
           ['7', 'OpenCode Zen', 'nuevo'],
           ['8', 'Error Imagen', '—'],
           ['9', 'Histórico', 'actualizado'],
           ['10', 'Procesos bloqueados', '—'],
           ['11', 'Rendimiento', 'actualizado'],
           ['12', 'Tool Aborted', 'nuevo'],
           ['13', 'Troubleshooting', 'nuevo'],
           ['14', 'Buenas Prácticas', 'actualizado'],
           ['15', 'Referencia Rápida', 'actualizado'],
           ['16', 'Copias de Seguridad', 'nuevo']])
add_para(doc, 'Resumen: 8 capítulos nuevos, 5 actualizados y 3 sin etiqueta.')
add_sub(doc, 'Actividad Reciente')
add_para(doc, 'Lista #activityList poblada desde localStorage[codanor_opencode_activity] (loadActivity()). '
              'Muestra las últimas 10 entradas con formato relativo (timeAgo()).')
add_sub(doc, 'Resumen por Tipo')
add_para(doc, 'Barras de progreso por tipo de incidencia local (#typeSummary): Bugs, Features, Documentación, '
              'Configuración y Rendimiento.')

# ─── SECCIÓN 6 — KANBAN ───
add_section_heading(doc, 6, 'Incidencias (Kanban local)')
add_para(doc, 'Tablero Kanban con arrastrar y soltar, totalmente local (localStorage). Es un sistema distinto e '
              'independiente del Gestor de Tiquets (Sección 7).')
add_sub(doc, 'Columnas / estados')
add_table(doc, ['Estado', 'Columna'],
          [['backlog', 'Backlog'], ['progress', 'En Progreso'],
           ['review', 'Revisión'], ['done', 'Completado']])
add_sub(doc, 'Campos de una incidencia')
add_para(doc, 'Modelo guardado por saveTicket(): id (T- + timestamp base36), title, desc, type, priority, '
              'status, createdAt, updatedAt.')
add_sub(doc, 'Tipos y prioridades')
add_table(doc, ['Tipos', 'Prioridades'],
          [['bug, feature, docs, config, perf',
            'high (Alta), medium (Media, por defecto), low (Baja)']])
add_sub(doc, 'Operaciones')
add_bullets(doc, [
    'Crear: «+ Nueva incidencia» → openNewTicketModal() (por defecto bug / medium / backlog).',
    'Editar: editTicket(id) rellena el modal.',
    'Guardar: saveTicket() exige título, registra actividad y re-renderiza.',
    'Eliminar: deleteTicket() con confirmación.',
    'Avanzar estado: moveTicketForward() o arrastre onDrop().',
])
add_para(doc, 'En la primera visita se siembran automáticamente 7 incidencias de ejemplo y 3 actividades '
              '(seedData()).')

# ─── SECCIÓN 7 — GESTOR DE TIQUETS ───
add_section_heading(doc, 7, 'Gestor de Tiquets')
add_para(doc, 'Módulo integrado con el backend Flask de la Plataforma (plataforma.db, SQLite), con fallback '
              'offline. Los datos se comparten en LAN.')
add_sub(doc, 'Endpoint base')
add_para(doc, 'TK_API = http://{hostname}:5001/api/tiquets — LAN-aware: usa window.location.hostname para '
              'funcionar desde cualquier PC de la red, nunca localhost hardcodeado.')
add_sub(doc, 'Endpoints consumidos')
add_table(doc, ['Método', 'Ruta', 'Función'],
          [['GET', '/clientes', 'Detección de modo + carga de clientes'],
           ['GET', '/proyectos?client_id=', 'Carga de proyectos'],
           ['GET', '?<filtros>', 'Lista de tiquets'],
           ['POST', '(base)', 'Crear / sincronizar'],
           ['PUT', '/<id>', 'Actualizar'],
           ['GET', '/<id>', 'Detalle'],
           ['POST', '/<id>/comentarios', 'Comentar'],
           ['POST', '/<id>/acciones', 'Crear acción'],
           ['PUT', '/<id>/acciones/<accionId>', 'Actualizar acción'],
           ['DELETE', '/<id>/acciones/<accionId>', 'Eliminar acción'],
           ['GET', '/exportar?<filtros>', 'Exportar CSV']])
add_sub(doc, 'Modo online / offline')
add_para(doc, 'tkDetectarModo() hace un GET /clientes con timeout de 2 s y muestra el indicador #tk-modo-ind '
              '(● Online / ● Offline). En offline usa la caché localStorage[codanor_tiquets_v2]. Reconecta '
              "automáticamente con el evento window 'online'.")
add_sub(doc, 'Tipos, estados y prioridades')
add_table(doc, ['Categoría', 'Valores'],
          [['Tipos', 'incidencia (INC), peticion (PET), cambio (CAM), problema (PRO), vulnerabilidad (VUL), ciberincidente (CIB)'],
           ['Estados', 'nuevo, asignado, en_progreso, pendiente, resuelto, cerrado'],
           ['Prioridades', 'critica, alta, media, baja']])
add_sub(doc, 'Campos del tiquet')
add_para(doc, 'titulo*, descripcion, tipo*, prioridad*, estado, asignado_a, solicitante, control_iso (ej. '
              'A.16.1.1), normas_afectadas (array, v1.2), cvss_score (0–10, solo VUL/CIB), client_id, app_id. '
              'Al crear exige cliente y norma.')
add_para(doc, 'Formato de ID (offline): TIK-{NNN}-{client_id}-{app_id}-{DD-MM-AAAA}.')
add_sub(doc, 'Panel de detalle')
add_para(doc, 'Muestra tipo, prioridad, estado, asignado, norma, control ISO, descripción y fecha. Incluye '
              'Acciones de Seguimiento (pendiente → en_curso → resuelta, con barra de progreso y auto-resolución '
              'del tiquet), Historial de cambios y Comentarios. El SLA se resalta en rojo cuando está vencido.')

# ─── SECCIÓN 8 — CONFIGURACIÓN IA ───
add_section_heading(doc, 8, 'Configuración IA corporativa')
add_para(doc, 'Panel para gestionar la clave LLM corporativa compartida en LAN. La clave se almacena ofuscada en '
              'la base de datos del servidor.')
add_sub(doc, 'Endpoint')
add_para(doc, 'CORP_API = http://{hostname}:5001/api/corp/llm-config')
add_table(doc, ['Método', 'Función', 'Acción'],
          [['GET', 'corpLoadStatus', 'Carga estado y badge «Corp».'],
           ['POST', 'corpSaveConfig', 'Guarda {provider, model, apiKey, setBy}.'],
           ['DELETE', 'corpDeleteConfig', 'Elimina la configuración corporativa.']])
add_para(doc, 'El botón «Probar» (corpTestConfig()) valida la conexión llamando directamente al endpoint '
              '/chat/completions del proveedor, no al servidor.')
add_sub(doc, 'Proveedores soportados')
add_table(doc, ['Proveedor', 'Base URL', 'Modelo por defecto'],
          [['OpenRouter (Gratis)', 'https://openrouter.ai/api/v1', 'openrouter/free'],
           ['Groq (Gratis)', 'https://api.groq.com/openai/v1', 'openai/gpt-oss-20b'],
           ['Google Gemini (Gratis)', '.../v1beta/openai', 'gemini-2.0-flash'],
           ['OpenAI (GPT)', 'https://api.openai.com/v1', 'gpt-4o-mini'],
           ['Anthropic (Claude)', 'https://api.anthropic.com', 'claude-3-5-haiku-20241022']])
add_para(doc, 'OpenRouter añade las cabeceras HTTP-Referer: https://codanor.com y X-Title: CODANOR Plataforma. '
              'A diferencia de las 9 apps ISO/ENS, este panel corporativo no incluye el proveedor ollama.')
add_sub(doc, 'Prioridad de claves')
add_numbered(doc, [
    'Clave personal (localStorage del navegador) — máxima prioridad.',
    'Clave corporativa (este panel) — compartida en LAN.',
    'Sin clave — se ofrece un prompt manual para copiar a ChatGPT/Claude.',
])

# ─── SECCIÓN 9 — HERRAMIENTAS ENLAZADAS ───
add_section_heading(doc, 9, 'Herramientas enlazadas')
add_para(doc, 'El grupo Herramientas del sidebar no abre páginas SPA, sino enlaces externos en una nueva pestaña.')
add_table(doc, ['Herramienta', 'Destino', 'Descripción'],
          [['Análisis de Código', '/analisis-codigo (ruta Flask :5003)', 'Panel SonarQube/SonarCloud (analisis-codigo.html).'],
           ['Homogeneización', 'homogeneizacion-proyectos.html', 'Dashboard de homogeneización (archivo local).']])
add_para(doc, 'Las tarjetas de Documentación enlazan a recursos externos de OpenCode: opencode.ai/docs, '
              '/troubleshooting, /providers, /discord y github.com/anomalyco/opencode.')

# ─── SECCIÓN 10 — PERSISTENCIA ───
add_section_heading(doc, 10, 'Persistencia de datos')
add_sub(doc, 'Claves de localStorage')
add_table(doc, ['Clave', 'Constante', 'Uso'],
          [['codanor_opencode_tracker', 'STORAGE_KEY', 'Incidencias del Kanban local.'],
           ['codanor_opencode_activity', 'ACTIVITY_KEY', 'Registro de actividad del dashboard.'],
           ['codanor_tiquets_v2', 'TK_STORE', 'Caché / fallback offline de tiquets.']])
add_sub(doc, 'Backend consumido')
add_bullets(doc, [
    'Puerto 5001: únicos endpoints de red → /api/tiquets/* y /api/corp/llm-config, más pruebas directas a proveedores LLM.',
    'Puerto 5003: no aparece ninguna referencia interna; solo sirve el HTML.',
    'Dashboard, Kanban, Documentación y Changelog no usan backend: son 100 % localStorage.',
])

# ─── SECCIÓN 11 — ESTADO ACTUAL Y OBSERVACIONES ───
add_section_heading(doc, 11, 'Estado actual y observaciones')
add_para(doc, 'Puntos relevantes detectados en la revisión del código, útiles como base para la actualización.')
add_bullets(doc, [
    '1. Dos sistemas de incidencias desconectados: el Kanban local (localStorage, alimenta las métricas del '
    'Dashboard) y el Gestor de Tiquets (SQLite :5001). Las métricas del Dashboard no reflejan los tiquets del servidor.',
    '2. Progreso del Manual hardcodeado: el 100 % / 16 de 16 está fijado en el HTML; debe editarse a mano.',
    '3. CVSS condicionado por tipo: solo se habilita para vulnerabilidad y ciberincidente.',
    '4. Dependencia de red del puerto 5001: el Gestor de Tiquets y la Configuración IA requieren server.py (:5001) '
    'operativo. Sin él, el Tracker funciona en modo degradado.',
])
add_sub(doc, 'Posibles líneas de actualización')
add_bullets(doc, [
    'Calcular el progreso del manual de forma dinámica (p. ej. desde un JSON de capítulos).',
    'Unificar o sincronizar el Kanban local con el Gestor de Tiquets, o aclarar en la UI que son distintos.',
    'Incorporar JetBrains Mono (hoy usa monospace del sistema) para alinear con la plantilla corporativa.',
    'Añadir el proveedor ollama al panel de Configuración IA para paridad con las apps ISO/ENS.',
    'Versionar explícitamente plataforma-seguimiento.html (hoy no tiene número de versión propio).',
])

# ─── GLOSARIO ───
add_section_heading(doc, 99, 'Glosario de términos')
add_table(doc, ['Término / Clave', 'Definición'],
          [['SPA', 'Single Page Application. Aplicación de una sola página que no recarga el navegador al navegar.'],
           ['localStorage', 'Almacenamiento persistente del navegador, local al equipo. No se comparte en red.'],
           ['Kanban', 'Tablero visual de tarjetas por columnas de estado (Backlog, En Progreso, Revisión, Completado).'],
           ['Tiquet', 'Registro gestionado en el backend SQLite y compartido en LAN. Distinto de la incidencia del Kanban.'],
           ['LAN-aware', 'Que detecta automáticamente el host de red (window.location.hostname) en vez de localhost fijo.'],
           ['SLA', 'Service Level Agreement. Plazo de resolución comprometido; se resalta si está vencido.'],
           ['CVSS', 'Common Vulnerability Scoring System. Puntuación 0–10 de severidad de una vulnerabilidad.'],
           ['LLM', 'Large Language Model. Modelo de lenguaje usado por los proveedores de IA configurables.'],
           ['Clave corporativa', 'Clave de API LLM compartida en LAN, almacenada ofuscada en el servidor.'],
           [':5001', 'Puerto del servidor Flask server.py que provee las APIs (tiquets, config IA).'],
           [':5003', 'Puerto de dashboard_server.py que sirve el HTML del Tracker; sin BD propia.']])

# ─── PIE DE PÁGINA ───
for section in doc.sections:
    footer = section.footer
    ft = footer.paragraphs[0]
    ft.clear()
    ft.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = ft.add_run(f'CODANOR — Jafa, S.L. — Barcelona, Catalunya  |  {CLASIFICACION}  |  {VERSION} · {FECHA}')
    run.font.name = 'Calibri'
    run.font.size = Pt(7)
    run.font.color.rgb = C_GRAY_600
    ft.add_run('\n')
    run2 = ft.add_run(f'{RUTA_GUARDADO}/{NOMBRE_ARCHIVO}.docx')
    run2.font.name = 'Courier New'
    run2.font.size = Pt(6)
    run2.font.color.rgb = C_GRAY_600

# ─── GUARDAR ───
output_path = f'{RUTA_GUARDADO}/{NOMBRE_ARCHIVO}.docx'
doc.save(output_path)
print(f'Generado: {output_path}')
