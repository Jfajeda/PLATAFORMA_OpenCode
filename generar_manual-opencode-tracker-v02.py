#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Word — Manual de la Plataforma OpenCode Tracker (V02)
CODANOR — Jafa, S.L.
v2.0 · 16/11/2026 (documenta la app v1.1)
Ruta: /Users/jaimefajeda/Proyectos/PLATAFORMA_OpenCode-NEW/MANUAL-OPENCODE-TRACKER-V02.docx
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
SUBTITULO     = 'Guía de uso y estado actual (app v1.1) — Dashboard, Incidencias, Tiquets y Configuración IA'
TIPO          = 'Manual de usuario'
VERSION       = 'v2.0'
FECHA         = '16/11/2026'
AUTOR         = 'CODANOR — Jafa, S.L.'
CLASIFICACION = 'Documento interno — Uso exclusivo CODANOR'
RUTA_GUARDADO = '/Users/jaimefajeda/Proyectos/PLATAFORMA_OpenCode-NEW'
NOMBRE_ARCHIVO = 'MANUAL-OPENCODE-TRACKER-V02'


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
          [['v1.0', '15/11/2026', AUTOR,
            'Versión inicial. Documenta el estado de la app OpenCode Tracker v1.0 '
            '(plataforma-seguimiento.html) para su uso y actualización.'],
           [VERSION, FECHA, AUTOR,
            'Actualización al estado app v1.1: Dashboard híbrido (tiquets :5001 / Kanban local) con '
            'badge de fuente, progreso del Manual dinámico (array MANUAL), CVSS condicionado al tipo, '
            'proveedor Ollama en Config IA, tipografía JetBrains Mono y versionado explícito del HTML.']])

# ─── SECCIÓN 1 — INTRODUCCIÓN ───
add_section_heading(doc, 1, 'Introducción y objeto')
add_para(doc, 'OpenCode Tracker (título interno «Plataforma de Seguimiento OpenCode — CODANOR») es la '
              'aplicación web de panel de control corporativo de CODANOR para el seguimiento del trabajo con '
              'OpenCode. Es una SPA monolítica en un único archivo HTML (plataforma-seguimiento.html), con CSS '
              'embebido y JavaScript vanilla sin frameworks externos. Este documento (v2.0) describe la app en su '
              'versión v1.1.')
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
           ['Fuentes', 'Google Fonts', 'Poppins (titulares) + Nunito Sans (cuerpo) + JetBrains Mono (código/IDs/rutas) [v1.1].'],
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
add_sub(doc, 'Tarjetas de métricas [híbrido v1.1]')
add_para(doc, 'Desde la v1.1, renderDashboard() es asíncrono y usa una fuente de datos híbrida: con el backend :5001 '
              'accesible, agrega métricas de los tiquets reales del servidor (dashboardFromServer()); si no, cae al '
              'Kanban local (dashboardFromLocal()). Un badge #dashboardSource indica el origen de los datos. RESUELTO: '
              'las tarjetas ya reflejan los tiquets del servidor cuando hay conexión.')
add_table(doc,
          ['Tarjeta', 'ID', 'Online (tiquets :5001)', 'Offline (Kanban local)'],
          [['Total incidencias', '#metricTotal', 'tiquets.length', 'tickets.length'],
           ['Completadas', '#metricDone', 'estado in {resuelto, cerrado}', "status === 'done'"],
           ['En progreso', '#metricProgress', 'estado in {en_progreso, asignado}', "status === 'progress'"],
           ['Prioridad alta', '#metricHigh', 'prioridad in {critica, alta} y no cerrado', "priority === 'high' && status !== 'done'"]])
add_sub(doc, 'Progreso del Manual [dinámico v1.1]')
add_para(doc, 'El progreso ya NO está hardcodeado. Se calcula desde el array MANUAL (fuente única de verdad) con '
              'renderManualProgress(), que genera el porcentaje, el conteo «N de M» y la cuadrícula de capítulos. '
              'Para publicar una nueva versión basta con editar el array en el <script>. Estructura: '
              'MANUAL = { version, meta, capitulos:[{ n, titulo, estado }] }.')
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
add_para(doc, 'Barras por tipo (#typeSummary, vía _renderTypeSummary()). Online: 6 tipos de tiquet (Incidencias, '
              'Peticiones, Cambios, Problemas, Vulnerabilidades, Ciberincidentes). Offline: tipos del Kanban local '
              '(Bugs, Features, Documentación, Configuración, Rendimiento).')

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
add_para(doc, 'Aviso en la interfaz (v1.1): la página del Kanban muestra ahora un aviso que aclara que es un '
              'tablero local (guardado en el navegador), independiente del Gestor de Tiquets del servidor :5001.')

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
add_para(doc, 'CVSS condicionado al tipo (v1.1): tkToggleCvss() habilita/deshabilita y limpia el campo cvss_score '
              'según el tipo. Solo aplica a vulnerabilidad y ciberincidente; en el resto se envía null. Antes solo '
              'se atenuaba visualmente (opacidad).')
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
           ['Anthropic (Claude)', 'https://api.anthropic.com', 'claude-3-5-haiku-20241022'],
           ['Ollama (Local) [v1.1]', 'http://{hostname}:11434/v1', 'qwen2.5-coder:14b']])
add_para(doc, 'OpenRouter añade las cabeceras HTTP-Referer: https://codanor.com y X-Title: CODANOR Plataforma. '
              'Ollama añadido en v1.1: LAN-aware (http://{window.location.hostname}:11434/v1), sin cabecera '
              'Authorization y con el guard isOllamaKey (su «clave» es la cadena ollama, de 6 caracteres). Modelos: '
              'qwen2.5-coder:14b, qwen3:8b, llama3.1:latest, gemma3:4b.')
add_para(doc, 'Aviso claro si :5001 no está accesible (v1.1): corpLoadStatus() distingue el fallo de red y muestra '
              '«Servidor :5001 no accesible» con la instrucción para arrancar el backend, en lugar de un error genérico.')
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
    'Puerto 5001: endpoints de red → /api/tiquets/* (tiquets y, desde v1.1, métricas del Dashboard online) y '
    '/api/corp/llm-config, más pruebas directas a proveedores LLM.',
    'Puerto 5003: no aparece ninguna referencia interna; solo sirve el HTML.',
    'Dashboard (v1.1): híbrido — tiquets de :5001 si hay conexión; si no, Kanban local.',
    'Kanban, Documentación y Changelog: siguen siendo 100 % localStorage.',
])

# ─── SECCIÓN 11 — CORRECCIONES APLICADAS EN v1.1 ───
add_section_heading(doc, 11, 'Correcciones aplicadas en v1.1')
add_para(doc, 'Los puntos detectados en la revisión inicial (v1.0 del documento) se han abordado en la versión 1.1 '
              'de la app. Resumen del estado:')
add_bullets(doc, [
    'RESUELTO 1. Sistemas de incidencias conectados: el Dashboard es híbrido (tiquets :5001 online / Kanban local '
    'offline), con badge #dashboardSource y aviso en la UI del Kanban.',
    'RESUELTO 2. Progreso del Manual dinámico: calculado desde el array MANUAL con renderManualProgress().',
    'RESUELTO 3. CVSS realmente condicionado al tipo: tkToggleCvss() habilita/deshabilita y limpia; null salvo VUL/CIB.',
    'RESUELTO 5. Paridad y versionado: JetBrains Mono incorporada; proveedor Ollama (Local) añadido; app versionada '
    'como OpenCode Tracker v1.1 (pie del sidebar y <head>).',
    'MITIGADO 4. Dependencia del puerto 5001: es intrínseca al diseño LAN; en v1.1 se mitiga con degradación elegante '
    '(fallback a Kanban local y aviso claro «:5001 no accesible» en Configuración IA).',
])
add_sub(doc, 'Pendiente / posibles líneas futuras')
add_bullets(doc, [
    'Migrar completamente el Kanban al backend (hoy sigue siendo local) para una única fuente de datos.',
    'Endpoint de estadísticas agregadas en server.py para evitar el cálculo en cliente del Dashboard.',
    'Externalizar el array MANUAL a un JSON servido por :5003 (opcional).',
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
           ['Ollama', 'Motor LLM local (sin coste, sin clave real). En v1.1 seleccionable en Config IA; usa :11434/v1.'],
           ['Badge de fuente', 'Indicador #dashboardSource del Dashboard: muestra si las métricas vienen de :5001 o del Kanban local.'],
           ['JetBrains Mono', 'Fuente monoespaciada corporativa para código, IDs y rutas. Incorporada en v1.1.'],
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
