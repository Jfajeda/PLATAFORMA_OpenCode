#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_informe_incidente_propagacion.py
Genera INFORME-INCIDENTE-PROPAGACION-V01.docx usando python-docx.
Ejecutar: python3 generar_informe_incidente_propagacion.py
Requiere: pip install python-docx
"""

import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

# ── RUTAS ───────────────────────────────────────────────────────────────────
LOGO_PATH = (
    '/Users/jaimefajeda/Proyectos/'
    'Plataforma_Seguimiento_Proyectos/ENS-RD311-2022/img/logo-codanor.png'
)
OUTPUT_PATH = (
    '/Users/jaimefajeda/Proyectos/'
    'PLATAFORMA_OpenCode-NEW/INFORME-INCIDENTE-PROPAGACION-V01.docx'
)

# ── PALETA ───────────────────────────────────────────────────────────────────
PRIMARY_DK  = RGBColor(0x12, 0x75, 0xA3)
PRIMARY_LT  = RGBColor(0xE8, 0xF4, 0xFA)
ACCENT      = RGBColor(0x12, 0xA7, 0x9D)
DARK        = RGBColor(0x1A, 0x1A, 0x2E)
WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
GRAY_700    = RGBColor(0x4A, 0x4A, 0x5A)
GRAY_600    = RGBColor(0x6B, 0x6B, 0x7B)
GRAY_100    = RGBColor(0xF0, 0xF0, 0xF5)
SUCCESS     = RGBColor(0x1A, 0x7A, 0x4A)
SUCCESS_BG  = RGBColor(0xF0, 0xFA, 0xF4)
DANGER      = RGBColor(0xC0, 0x39, 0x2B)
DANGER_BG   = RGBColor(0xFD, 0xF2, 0xF2)
WARNING     = RGBColor(0xB7, 0x77, 0x0D)
WARNING_BG  = RGBColor(0xFE, 0xF9, 0xE7)
INFO_BG     = RGBColor(0xE8, 0xF4, 0xFA)


# ── HELPERS ──────────────────────────────────────────────────────────────────

def hex_to_rgb_str(rgb: RGBColor) -> str:
    """Devuelve string 'RRGGBB' para XML OxmlElement."""
    return f'{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}'


def set_cell_bg(cell, rgb: RGBColor):
    """Aplica color de fondo a una celda."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_to_rgb_str(rgb))
    tcPr.append(shd)


def set_cell_border_left(cell, color: RGBColor, size_pt: int = 12):
    """Aplica borde izquierdo de color a una celda (para cajas de aviso)."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    left = OxmlElement('w:left')
    left.set(qn('w:val'), 'single')
    left.set(qn('w:sz'), str(size_pt * 8))
    left.set(qn('w:color'), hex_to_rgb_str(color))
    tcBorders.append(left)
    # Remove other borders for cleaner look
    for side in ('top', 'right', 'bottom', 'insideH', 'insideV'):
        el = OxmlElement(f'w:{side}')
        el.set(qn('w:val'), 'none')
        tcBorders.append(el)
    tcPr.append(tcBorders)


def add_run(para, text: str, bold=False, italic=False,
            color: RGBColor = None, font_size_pt: int = None,
            font_name: str = None, mono: bool = False):
    """Añade un run al párrafo con el estilo indicado."""
    run = para.add_run(text)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color
    if font_size_pt:
        run.font.size = Pt(font_size_pt)
    if mono or font_name == 'mono':
        run.font.name = 'JetBrains Mono'
    elif font_name:
        run.font.name = font_name
    else:
        run.font.name = 'Nunito Sans'
    return run


def add_heading(doc, text: str, level: int = 1):
    """Añade un heading corporativo."""
    para = doc.add_paragraph()
    para.paragraph_format.space_before = Pt(16 if level == 1 else 10)
    para.paragraph_format.space_after = Pt(6)
    run = para.add_run(text)
    run.bold = True
    run.font.name = 'Poppins'
    if level == 1:
        run.font.size = Pt(16)
        run.font.color.rgb = DARK
    elif level == 2:
        run.font.size = Pt(13)
        run.font.color.rgb = PRIMARY_DK
    else:
        run.font.size = Pt(11)
        run.font.color.rgb = PRIMARY_DK
    # Borde inferior para h1
    if level == 1:
        pPr = para._p.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '8')
        bottom.set(qn('w:color'), hex_to_rgb_str(PRIMARY_DK))
        pBdr.append(bottom)
        pPr.append(pBdr)
    return para


def add_body(doc, text: str, space_before: int = 2, space_after: int = 6):
    """Añade un párrafo de cuerpo de texto."""
    para = doc.add_paragraph()
    para.paragraph_format.space_before = Pt(space_before)
    para.paragraph_format.space_after = Pt(space_after)
    run = para.add_run(text)
    run.font.name = 'Nunito Sans'
    run.font.size = Pt(10.5)
    run.font.color.rgb = GRAY_700
    return para


def add_bullet(doc, text: str, level: int = 0):
    """Añade un ítem de lista."""
    para = doc.add_paragraph(style='List Bullet')
    para.paragraph_format.left_indent = Cm(0.5 + level * 0.5)
    para.paragraph_format.space_after = Pt(3)
    run = para.add_run(text)
    run.font.name = 'Nunito Sans'
    run.font.size = Pt(10)
    run.font.color.rgb = GRAY_700
    return para


def add_code_block(doc, code: str):
    """Añade un bloque de código con fondo oscuro simulado."""
    # python-docx no soporta fondo de párrafo, usamos tabla de 1 celda
    table = doc.add_table(rows=1, cols=1)
    table.style = 'Table Grid'
    cell = table.cell(0, 0)
    set_cell_bg(cell, RGBColor(0x2B, 0x2B, 0x3B))
    cell.paragraphs[0].clear()
    para = cell.paragraphs[0]
    para.paragraph_format.space_before = Pt(4)
    para.paragraph_format.space_after = Pt(4)
    run = para.add_run(code)
    run.font.name = 'JetBrains Mono'
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(0xCD, 0xD6, 0xF4)
    # Quitar bordes externos de la tabla
    doc.add_paragraph()
    return table


def add_box(doc, label: str, text: str, box_type: str = 'info'):
    """Añade una caja de aviso (info/warning/danger/success)."""
    colors = {
        'info':    (PRIMARY_DK, INFO_BG),
        'warning': (WARNING,    WARNING_BG),
        'danger':  (DANGER,     DANGER_BG),
        'success': (SUCCESS,    SUCCESS_BG),
    }
    border_color, bg_color = colors.get(box_type, colors['info'])

    table = doc.add_table(rows=1, cols=1)
    table.style = 'Table Grid'
    cell = table.cell(0, 0)
    set_cell_bg(cell, bg_color)
    set_cell_border_left(cell, border_color, size_pt=6)

    cell.paragraphs[0].clear()
    p1 = cell.paragraphs[0]
    r1 = p1.add_run(label + ' ')
    r1.bold = True
    r1.font.name = 'Nunito Sans'
    r1.font.size = Pt(10)
    r1.font.color.rgb = border_color

    r2 = p1.add_run(text)
    r2.font.name = 'Nunito Sans'
    r2.font.size = Pt(10)
    r2.font.color.rgb = GRAY_700

    doc.add_paragraph()
    return table


def make_table_header(table, headers: list, col_widths_cm: list = None):
    """Aplica estilo corporativo a la primera fila (cabecera)."""
    row = table.rows[0]
    for i, cell in enumerate(row.cells):
        cell.text = ''
        set_cell_bg(cell, PRIMARY_DK)
        para = cell.paragraphs[0]
        run = para.add_run(headers[i])
        run.bold = True
        run.font.name = 'Poppins'
        run.font.size = Pt(9)
        run.font.color.rgb = WHITE
        if col_widths_cm and i < len(col_widths_cm):
            cell.width = Cm(col_widths_cm[i])


def add_table_row(table, values: list, even: bool = False,
                  mono_cols: list = None, bold_cols: list = None):
    """Añade una fila de datos a la tabla."""
    row = table.add_row()
    bg = GRAY_100 if even else WHITE
    for i, cell in enumerate(row.cells):
        set_cell_bg(cell, bg)
        cell.text = ''
        para = cell.paragraphs[0]
        is_mono = bool(mono_cols and i in mono_cols)
        is_bold = bool(bold_cols and i in bold_cols)
        run = para.add_run(str(values[i]))
        run.font.name = 'JetBrains Mono' if is_mono else 'Nunito Sans'
        run.font.size = Pt(9 if is_mono else 9.5)
        run.font.color.rgb = PRIMARY_DK if is_mono else GRAY_700
        run.bold = is_bold
    return row


def add_page_break(doc):
    doc.add_page_break()


def set_doc_margins(doc):
    """Márgenes A4 estándar."""
    for section in doc.sections:
        section.top_margin    = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin   = Cm(2.5)
        section.right_margin  = Cm(2.0)


def add_header(doc, title: str):
    """Cabecera en páginas 2+: título + línea azul."""
    section = doc.sections[0]
    header = section.header
    header.is_linked_to_previous = False
    para = header.paragraphs[0]
    para.clear()
    # Logo si existe
    if os.path.exists(LOGO_PATH):
        run_logo = para.add_run()
        run_logo.add_picture(LOGO_PATH, height=Cm(0.6))
        para.add_run('  ')
    run = para.add_run(title)
    run.font.name = 'Nunito Sans'
    run.font.size = Pt(9)
    run.font.color.rgb = GRAY_600
    run.bold = True
    # Línea inferior
    pPr = para._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:color'), hex_to_rgb_str(PRIMARY_DK))
    pBdr.append(bottom)
    pPr.append(pBdr)


def add_footer(doc):
    """Pie: empresa | clasificación | página."""
    section = doc.sections[0]
    footer = section.footer
    footer.is_linked_to_previous = False
    para = footer.paragraphs[0]
    para.clear()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = para.add_run('CODANOR — Jafa, S.L.  |  CONFIDENCIAL — Uso exclusivo CODANOR  |  Página ')
    run.font.name = 'Nunito Sans'
    run.font.size = Pt(8)
    run.font.color.rgb = GRAY_600
    # Campo número de página
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText')
    instrText.text = 'PAGE'
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')
    run2 = para.add_run()
    run2.font.name = 'Nunito Sans'
    run2.font.size = Pt(8)
    run2.font.color.rgb = GRAY_600
    run2._r.append(fldChar1)
    run2._r.append(instrText)
    run2._r.append(fldChar2)


def add_toc(doc):
    """Inserta campo TOC de Word."""
    para = doc.add_paragraph()
    run = para.add_run()
    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = 'TOC \\o "1-2" \\h \\z \\u'
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'end')
    run._r.append(fldChar)
    run._r.append(instrText)
    run._r.append(fldChar2)
    note = doc.add_paragraph()
    note_run = note.add_run('(Actualizar índice con Ctrl+A → F9 en Microsoft Word)')
    note_run.italic = True
    note_run.font.size = Pt(9)
    note_run.font.color.rgb = GRAY_600
    note_run.font.name = 'Nunito Sans'


# ── PORTADA ───────────────────────────────────────────────────────────────────

def build_cover(doc):
    # Fondo simulado con tabla de 1 celda full-width
    cover_table = doc.add_table(rows=1, cols=1)
    cover_table.style = 'Table Grid'
    cell = cover_table.cell(0, 0)
    set_cell_bg(cell, DARK)
    # Quitar todos los bordes de la tabla
    tbl = cover_table._tbl
    tblPr = tbl.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    for side in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        el = OxmlElement(f'w:{side}')
        el.set(qn('w:val'), 'none')
        tblBorders.append(el)
    tblPr.append(tblBorders)

    cell.paragraphs[0].clear()

    def cover_para(text, size_pt, bold=False, color=WHITE,
                   align=WD_ALIGN_PARAGRAPH.CENTER,
                   space_before=0, space_after=6, font='Nunito Sans'):
        p = cell.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after  = Pt(space_after)
        run = p.add_run(text)
        run.font.name = font
        run.font.size = Pt(size_pt)
        run.font.color.rgb = color
        run.bold = bold
        return p

    # Espaciado superior
    cover_para('', 10, space_before=20)

    # Logo si existe
    if os.path.exists(LOGO_PATH):
        p_logo = cell.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(0)
        p_logo.paragraph_format.space_after  = Pt(6)
        r = p_logo.add_run()
        r.add_picture(LOGO_PATH, height=Cm(1.8))

    # CODANOR
    cover_para('CODANOR', 32, bold=True, color=RGBColor(0x17, 0x8D, 0xC2),
               space_before=0, space_after=2, font='Poppins')
    cover_para('Jafa, S.L. — Barcelona, Catalunya', 9,
               color=RGBColor(0x88, 0x88, 0xAA), space_after=20)

    # Tipo
    cover_para('INFORME DE INCIDENTE', 10, bold=True,
               color=RGBColor(0x12, 0xA7, 0x9D), space_after=4, font='Poppins')

    # Título
    cover_para(
        'Sistema de Propagación entre Apps CODANOR',
        22, bold=True, color=WHITE, space_after=8, font='Poppins'
    )

    # Subtítulo
    cover_para(
        'Análisis, correcciones aplicadas y mejoras preventivas implementadas',
        12, color=RGBColor(0xCC, 0xCC, 0xDD), space_after=24
    )

    # Metadatos
    meta_items = [
        ('Versión',      'v1.0'),
        ('Fecha',        '01/10/2026'),
        ('Autor',        'Jaime Fajeda — CODANOR'),
        ('Referencia',   'INC-2026-001'),
    ]
    for label, value in meta_items:
        p = cell.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after  = Pt(3)
        r1 = p.add_run(f'{label}: ')
        r1.font.name = 'Nunito Sans'; r1.font.size = Pt(10)
        r1.font.color.rgb = RGBColor(0x88, 0x88, 0xAA)
        r2 = p.add_run(value)
        r2.bold = True; r2.font.name = 'Nunito Sans'; r2.font.size = Pt(10)
        r2.font.color.rgb = WHITE

    # Clasificación
    cover_para('', 8, space_before=16, space_after=2)
    cover_para('Documento interno — Uso exclusivo CODANOR',
               9, color=RGBColor(0x88, 0x88, 0xAA), space_after=20)

    doc.add_page_break()


# ── SECCIONES ─────────────────────────────────────────────────────────────────

def build_version_table(doc):
    add_heading(doc, '— Control de versiones', level=2)
    table = doc.add_table(rows=1, cols=4)
    table.style = 'Table Grid'
    make_table_header(table, ['Versión', 'Fecha', 'Autor', 'Descripción'],
                      [2.0, 2.5, 4.0, 8.5])
    add_table_row(table, ['v1.0', '01/10/2026', 'Jaime Fajeda',
                           'Versión inicial — documentación completa del incidente INC-2026-001'],
                  even=False, mono_cols=[0])
    doc.add_paragraph()


def build_sec1(doc):
    add_heading(doc, '1. Introducción y objeto')
    add_body(doc,
        'El ecosistema CODANOR consta de 9 aplicaciones ISO/ENS de gestión de sistemas '
        'de seguridad y calidad, todas servidas por un servidor Flask centralizado en '
        'localhost:5001 con base de datos SQLite (plataforma.db). '
        'Las 9 aplicaciones son: ISO27001-SGSI, ENS-RD311-2022, RGPD-LOPD-GDD, ISO27701-SGP, '
        'ISO42001-SGIA, ISO9001-SGQ_2015, ISO14001-SGMA_2015, ISO14001-SGMA_2026_NEW y TISAX.')
    add_body(doc,
        'El workspace principal de OpenCode es PLATAFORMA_OpenCode-NEW, desde donde se realizan '
        'todas las operaciones de mantenimiento sobre las 9 apps. Las operaciones de propagación '
        'de código — copiar fixes entre apps — son una tarea habitual del mantenimiento del '
        'ecosistema y se realizan mediante comandos sed, cp o scripts Python.')
    add_body(doc,
        'Este informe documenta el incidente INC-2026-001 ocurrido el 01/10/2026 durante la '
        'corrección de vulnerabilidades innerHTML inseguros (operación MP-1), en el que se produjo '
        'una pérdida accidental de más de 608 líneas de código exclusivo de la aplicación '
        'ENS-RD311-2022. El documento cubre las causas identificadas, las correcciones aplicadas '
        'y las mejoras preventivas implementadas para evitar que se repita.')
    add_box(doc,
        'Referencia: INC-2026-001  |  Clasificación: Pérdida de código en producción  |  '
        'Severidad: Alta — funcionalidad ENS completamente inoperativa  |  '
        'Estado final: Resuelto',
        '', box_type='info')


def build_sec2(doc):
    add_heading(doc, '2. Alcance')
    add_heading(doc, '2.1 Incluido en el alcance', level=2)
    for item in [
        'Propagación de archivos JavaScript entre las 9 apps ISO/ENS del ecosistema Plataforma_Seguimiento_Proyectos',
        'Arquitectura de instrucciones OpenCode (AGENTS.md principal + específicos de cada app)',
        'Workflow de correcciones masivas tipo MP (mantenimiento de plataforma)',
        'Gestión del archivo PROPAGATION_RULES.md como fuente de verdad operativa',
        'Archivos afectados: phase2-consulting.js, phase2-implementation.js, phase2-isms.js, tiquets.js, mapa-procesos.js, phase3-audit.js',
    ]:
        add_bullet(doc, item)
    add_heading(doc, '2.2 Excluido del alcance', level=2)
    for item in [
        'Proyectos independientes de CODANOR (OSSINT, legislacion_monitor-NEW, Planificacion_Diaria, etc.) — cada uno tiene su propio workspace y no comparte código con las 9 apps ISO/ENS',
        'Servidor Flask server.py y base de datos plataforma.db — no participan en el mecanismo de propagación',
        'Archivos de datos estáticos (ens-808-checklist.js, iso9001-clauses-detailed.js, etc.) — se editan directamente en cada app sin propagación',
        'Módulos completamente independientes: wiki.js, store.js, app.js — tienen su propio ciclo de mantenimiento',
    ]:
        add_bullet(doc, item)
    doc.add_paragraph()


def build_sec3(doc):
    add_heading(doc, '3. Descripción del incidente')
    add_heading(doc, '3.1 Incidente principal — pérdida de código ENS', level=2)

    table = doc.add_table(rows=1, cols=2)
    table.style = 'Table Grid'
    make_table_header(table, ['Campo', 'Valor'], [4.5, 12.5])
    rows_data = [
        ('Fecha y hora',        '01/10/2026, ~10:30h'),
        ('Operación en curso',  'Fix MP-1 — corrección de 5 vulnerabilidades innerHTML inseguros en los módulos JS de las 9 apps'),
        ('Commit causante',     '22379b8 — "fix: corregir innerHTML inseguros — escapar d.version, nombres modelos Ollama, result.message × 9 apps (MP-1)"'),
        ('Archivo destruido',   'ENS-RD311-2022/js/modules/phase2-consulting.js'),
        ('Código perdido',      '+608 líneas exclusivas de ENS'),
        ('Descubrimiento',      'Verificación manual en browser por el usuario'),
    ]
    for i, (k, v) in enumerate(rows_data):
        add_table_row(table, [k, v], even=(i % 2 == 1), bold_cols=[0], mono_cols=[])

    doc.add_paragraph()

    add_box(doc,
        '🚫 Funciones desaparecidas tras el commit 22379b8:\n'
        '  • _seg808Data(kind, itemId) — datos de Seguimiento CCN-STIC 808\n'
        '  • _evid808Data(kind, itemId) — datos de Evidencias CCN-STIC 808\n'
        '  • renderEvolucion() — pestaña Evolució con gráfico Chart.js\n'
        '  • takeSnapshot() — snapshot periódico de progreso ENS\n'
        '  • desglosarLineaCSV(kind, itemId, index) — gestión documental F2\n'
        '  • _visibleDocs(arr) — índices documentos propuestos',
        '', box_type='danger')

    add_heading(doc, '3.2 Incidentes relacionados activados por el mismo commit', level=2)
    add_box(doc,
        '⚠️ Incidente A — ISO9001/ISO14001: renderNormaTab() usaba ISO27001_CLAUSES_DETAIL '
        'en lugar de las variables propias de cada app. Resultado: pestaña "Punts de Norma" '
        'con 0 controles.',
        '', box_type='warning')
    add_box(doc,
        '⚠️ Incidente B — ISO9001/ISO14001: documentosPropuestos vacíos tras la corrección '
        'de renderNormaTab(). Las plantillas de documentos propuestas no aparecían en el selector.',
        '', box_type='warning')


def build_sec4(doc):
    add_heading(doc, '4. Análisis de causa raíz')
    add_body(doc,
        'Se identificaron tres vectores causales independientes que actuaron conjuntamente '
        'para permitir el incidente:')

    vectors = [
        ('Vector 1 — Regla incompleta en AGENTS.md',
         'La regla 7 del AGENTS.md principal indicaba: "al propagar phase2-consulting.js '
         'entre las 5 apps consulting, usar Python (no cp) para preservar las diferencias de appId". '
         'Esta regla era correcta para RGPD/ISO27701/ISO42001 pero INCOMPLETA porque no advertía '
         'que ENS tiene +608 líneas exclusivas que se destruyen con cualquier propagación completa — '
         'independientemente del método utilizado.'),
        ('Vector 2 — Información crítica inaccesible',
         'El AGENTS.md de ENS-RD311-2022 (334 líneas) contiene toda la información sobre el '
         'código exclusivo CCN-808, Evolució y Snapshots. Sin embargo, el workspace activo de '
         'OpenCode es PLATAFORMA_OpenCode-NEW. OpenCode solo carga el AGENTS.md del workspace '
         'activo — el agente nunca veía las advertencias críticas del AGENTS.md específico de ENS.'),
        ('Vector 3 — Ausencia de verificación automática',
         'No existía ningún mecanismo que verificara automáticamente que ENS conservaba su código '
         'exclusivo antes de hacer commit. El agente aplicó la propagación de buena fe siguiendo '
         'la regla incompleta del AGENTS.md principal, sin que ninguna herramienta alertara '
         'de la pérdida de las 608 líneas exclusivas.'),
    ]

    for title, body in vectors:
        add_heading(doc, title, level=2)
        add_body(doc, body)

    add_box(doc,
        'Conclusión: El incidente no fue causado por un error de juicio puntual sino por una '
        'deficiencia estructural en el sistema de instrucciones de OpenCode. Los tres vectores '
        'son independientes — cualquiera de ellos corregido individualmente hubiera sido suficiente '
        'para prevenir el incidente.',
        '', box_type='info')


def build_sec5(doc):
    add_heading(doc, '5. Mapa de divergencias entre las 9 apps')
    add_body(doc,
        'La tabla siguiente clasifica todos los archivos JS de propagación entre las 9 apps '
        'según su tipo. Esta clasificación es la fuente de verdad que debe consultarse antes '
        'de cualquier operación de propagación.')

    headers = ['App', 'Archivo', 'Tipo', 'Líneas exclusivas', 'Variables clave', '¿Propagable?']
    table = doc.add_table(rows=1, cols=6)
    table.style = 'Table Grid'
    make_table_header(table, headers, [3.5, 4.5, 2.5, 2.5, 4.5, 3.0])

    rows_data = [
        ('ISO27001-SGSI',       'phase2-consulting.js',   'BASE',          '—',    'ISO27001_CLAUSES_DETAIL, CLAUSE_GROUPS',  'Es el BASE'),
        ('ENS-RD311-2022',      'phase2-consulting.js',   'DIVERGENTE ⚠️', '+608', 'ENS_808_CHECKLIST',                      'NUNCA — solo patch quirúrgico'),
        ('RGPD-LOPD-GDD',       'phase2-consulting.js',   'CLON SEGURO',   '0',    '—',                                      'SÍ con sed'),
        ('ISO27701-SGP',        'phase2-consulting.js',   'CLON SEGURO',   '0',    'organizationRole (datos)',               'SÍ con sed'),
        ('ISO42001-SGIA',       'phase2-consulting.js',   'CLON SEGURO',   '0',    'AIIA module (archivo separado)',         'SÍ con sed'),
        ('ISO9001-SGQ_2015',    'phase2-implementation.js','PROPIO',       '—',    'ACTIVITY_GROUPS, ISO9001_CLAUSES_DETAIL','NUNCA — archivo propio'),
        ('ISO14001-SGMA_2015',  'phase2-implementation.js','PROPIO',       '—',    'CLAUSE_GROUPS, ISO14001_CLAUSES_DETAIL', 'NUNCA — archivo propio'),
        ('ISO14001-SGMA_2026',  'phase2-implementation.js','PROPIO',       '—',    'CLAUSE_GROUPS, ISO14001_CLAUSES_DETAIL', 'NUNCA — archivo propio'),
        ('TISAX',               'phase2-isms.js',          'PROPIO',       '—',    'ISA catalog, sin tabs, sin LLM',         'NUNCA — archivo único'),
    ]

    for i, row_vals in enumerate(rows_data):
        add_table_row(table, list(row_vals), even=(i % 2 == 1),
                      mono_cols=[1], bold_cols=[0])

    doc.add_paragraph()

    add_heading(doc, '5.1 Archivos con propagación segura en todas las apps', level=2)
    table2 = doc.add_table(rows=1, cols=3)
    table2.style = 'Table Grid'
    make_table_header(table2, ['Archivo', 'Tipo', 'Método de propagación'], [5.0, 4.0, 8.0])
    rows2 = [
        ('tiquets.js',       'CLON SEGURO × 8', 'sed — solo cambia this.appId'),
        ('mapa-procesos.js', 'CLON SEGURO × 8', 'sed — solo cambia appId:'),
        ('phase3-audit.js',  'CLON SEGURO × 8', 'cp directo — idéntico en todas las apps'),
    ]
    for i, r in enumerate(rows2):
        add_table_row(table2, list(r), even=(i % 2 == 1), mono_cols=[0])
    doc.add_paragraph()


def build_sec6(doc):
    add_heading(doc, '6. Correcciones aplicadas')
    add_heading(doc, '6.1 Commits correctores', level=2)

    headers = ['Commit', 'Descripción', 'Archivos afectados', 'Impacto']
    table = doc.add_table(rows=1, cols=4)
    table.style = 'Table Grid'
    make_table_header(table, headers, [2.0, 7.5, 4.5, 3.0])
    rows_data = [
        ('9fea92b',
         'fix(ENS): restaurar mejoras defc5ef (CCN-808 + Evolució + Snapshots) perdidas + reaplicar fixes innerHTML MP-1',
         'ENS-RD311-2022/js/modules/phase2-consulting.js',
         '+610 líneas restauradas'),
        ('85ba45a',
         'fix: restaurar variables correctas en renderNormaTab — ISO9001→ACTIVITY_GROUPS, ISO14001→CLAUSE_GROUPS',
         '6 archivos (ISO9001, ISO14001-2015, ISO14001-2026)',
         '"Punts de Norma" operativo'),
        ('fe6e71b',
         'fix: migración suave documentosPropuestos vacíos en ISO9001/ISO14001 — recupera plantillas propuestas',
         '6 archivos (ISO9001, ISO14001-2015, ISO14001-2026)',
         'Plantillas propuestas restauradas'),
    ]
    for i, r in enumerate(rows_data):
        add_table_row(table, list(r), even=(i % 2 == 1), mono_cols=[0])
    doc.add_paragraph()

    add_heading(doc, '6.2 Procedimiento de restauración ENS', level=2)

    steps = [
        ('PASO 1', 'Recuperar el archivo previo al incidente desde el commit defc5ef:',
         'git checkout defc5ef -- ENS-RD311-2022/js/modules/phase2-consulting.js'),
        ('PASO 2', 'Aplicar patch quirúrgico Python para los 4 fixes del commit 22379b8 válidos:',
         'src = src.replace(OLD_VERSION_SNIPPET, NEW_VERSION_SNIPPET)\n'
         'src = src.replace(OLD_OLLAMA_SNIPPET, NEW_OLLAMA_SNIPPET)\n'
         'src = src.replace(OLD_RESULT_SNIPPET, NEW_RESULT_SNIPPET)\n'
         'src = src.replace(OLD_ERROR_SNIPPET, NEW_ERROR_SNIPPET)'),
        ('PASO 3', 'Bump de versión en ENS-RD311-2022/index.html: 20260928c → 20260930b', None),
        ('PASO 4', 'Verificación de integridad ENS:',
         'grep -c "_seg808Data\\|renderEvolucion\\|takeSnapshot\\|desglosarLineaCSV" \\\n'
         '  ENS-RD311-2022/js/modules/phase2-consulting.js\n'
         '# Resultado esperado: 4'),
    ]

    for label, text, code in steps:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after  = Pt(2)
        r1 = p.add_run(label + ': ')
        r1.bold = True; r1.font.name = 'Poppins'; r1.font.size = Pt(10)
        r1.font.color.rgb = PRIMARY_DK
        r2 = p.add_run(text)
        r2.font.name = 'Nunito Sans'; r2.font.size = Pt(10)
        r2.font.color.rgb = GRAY_700
        if code:
            add_code_block(doc, code)

    add_box(doc,
        '✅ Estado final: Las 3 apps afectadas (ENS, ISO9001, ISO14001) han recuperado '
        'toda su funcionalidad. El ecosistema está operativo al 100%.',
        '', box_type='success')


def build_sec7(doc):
    add_heading(doc, '7. Mejoras preventivas implementadas')
    add_body(doc,
        'Se implementaron 4 mejoras estructurales para eliminar los tres vectores causales identificados:')

    mejoras = [
        ('Mejora 1 — PROPAGATION_RULES.md (nuevo archivo, 233 líneas)',
         'Se creó un archivo dedicado PROPAGATION_RULES.md en el workspace PLATAFORMA_OpenCode-NEW '
         'con la clasificación completa BASE/CLON SEGURO/DIVERGENTE/PROPIO de todos los archivos JS '
         'entre las 9 apps. Incluye tablas de clasificación, workflow paso a paso para 5 casos, '
         'script de verificación ENS (umbral ≥580 líneas exclusivas) y lista de funciones exclusivas '
         'que nunca deben perderse. Cargado automáticamente por OpenCode como segunda instrucción.'),
        ('Mejora 2 — opencode.json actualizado',
         'Se actualizó el campo "instructions" para cargar ambos archivos al inicio de cada sesión: '
         '["AGENTS.md", "PROPAGATION_RULES.md"]. De este modo OpenCode tiene acceso a la clasificación '
         'completa antes de ejecutar cualquier operación de propagación.'),
        ('Mejora 3 — AGENTS.md principal limpiado',
         'Se detectó y eliminó el contenido duplicado del AGENTS.md principal (el archivo contenía '
         'dos copias íntegras del mismo texto). Reducido de 1129 a 641 líneas. Las reglas de '
         'propagación incompletas fueron reemplazadas por referencias explícitas a PROPAGATION_RULES.md.'),
        ('Mejora 4 — Hub raíz ~/Proyectos/AGENTS.md actualizado',
         'Rutas corregidas (PLATAFORMA_OpenCode → PLATAFORMA_OpenCode-NEW, etc.), nueva sección '
         '"Arquitectura de instrucciones OpenCode" con jerarquía completa de AGENTS.md por workspace, '
         'tabla de servidores Flask activos y estado real de AGENTS.md por proyecto.'),
    ]

    for title, body in mejoras:
        add_heading(doc, title, level=2)
        add_body(doc, body)

    add_box(doc,
        '✅ Vectores corregidos: Los tres vectores causales han sido eliminados mediante estas '
        '4 mejoras. OpenCode ahora carga PROPAGATION_RULES.md en cada sesión y tiene acceso '
        'a la clasificación completa de tipos desde el workspace activo.',
        '', box_type='success')


def build_sec8(doc):
    add_heading(doc, '8. Workflow de propagación seguro (definitivo)')

    add_box(doc,
        '⚠️ Regla fundamental: Antes de propagar cualquier archivo JS entre apps, identificar '
        'su TIPO en PROPAGATION_RULES.md. Nunca asumir que todas las apps son iguales.',
        '', box_type='warning')

    casos = [
        ('Caso 1 — Fix en phase2-consulting.js', [
            'PASO 1: Editar ISO27001-SGSI/js/modules/phase2-consulting.js (archivo BASE)',
            'PASO 2: Propagar a RGPD/ISO27701/ISO42001 con sed — son CLONES SEGUROS (solo appId)',
            'PASO 3: ENS → patch quirúrgico Python SOLAMENTE — nunca cp, nunca sed completo',
            'PASO 4: Ejecutar script de verificación de integridad ENS (≥580 líneas)',
            'PASO 5: Bump versión en los 5 index.html de apps consulting',
        ]),
        ('Caso 2 — Fix en tiquets.js o mapa-procesos.js', [
            'PASO 1: Editar ISO27001-SGSI (BASE)',
            'PASO 2: Propagar a las 8 apps con sed — todas son CLONES SEGUROS',
            'PASO 3: Bump versión en los 9 index.html',
        ]),
        ('Caso 3 — Fix en phase2-implementation.js', [
            'PASO 1: Identificar qué apps específicas requieren el fix',
            'PASO 2: Editar cada app por separado (ISO9001, ISO14001-2015, ISO14001-2026) — TIPO D PROPIO',
            'PASO 3: Bump versión en los index.html de las apps afectadas',
        ]),
        ('Caso 4 — Fix en phase3-audit.js', [
            'PASO 1: Editar ISO27001-SGSI/js/modules/phase3-audit.js (BASE)',
            'PASO 2: Copiar con cp a las 8 apps restantes — idéntico en todas',
            'PASO 3: Bump versión en los 9 index.html',
        ]),
        ('Caso 5 — Fix en phase2-isms.js', [
            'PASO 1: Editar TISAX/js/modules/phase2-isms.js directamente — TIPO D PROPIO',
            'PASO 2: Bump versión en TISAX/index.html',
        ]),
    ]

    for title, steps in casos:
        add_heading(doc, title, level=2)
        for step in steps:
            add_bullet(doc, step)

    add_heading(doc, 'Script de verificación ENS (obligatorio antes de cualquier commit)', level=2)
    add_code_block(doc,
        '# Verificación de integridad ENS\n'
        'python3 -c "\n'
        'import subprocess, sys\n'
        'BASE = \'Plataforma_Seguimiento_Proyectos\'\n'
        'r = subprocess.run([\n'
        '    \'diff\',\n'
        '    f\'{BASE}/ISO27001-SGSI/js/modules/phase2-consulting.js\',\n'
        '    f\'{BASE}/ENS-RD311-2022/js/modules/phase2-consulting.js\'\n'
        '], capture_output=True, text=True)\n'
        'lines = r.stdout.count(\'\\n>\')\n'
        'if lines < 580:\n'
        '    print(f\'ERROR: ENS ha perdido codigo exclusivo ({lines} lineas, minimo 580)\')\n'
        '    sys.exit(1)\n'
        'print(f\'OK — ENS tiene {lines} lineas exclusivas (minimo 580)\')\n'
        '"')
    doc.add_paragraph()


def build_sec9(doc):
    add_heading(doc, '9. Lecciones aprendidas y recomendaciones')
    add_heading(doc, '9.1 Lecciones aprendidas', level=2)

    lecciones = [
        ('Lección 1 — Jerarquía de instrucciones',
         'La arquitectura de múltiples AGENTS.md (común + específicos) es correcta '
         'conceptualmente, pero requiere un mecanismo explícito para que las reglas operativas '
         'críticas sean accesibles desde el workspace principal. No es suficiente con documentar '
         'las reglas en el AGENTS.md específico de la app afectada — deben estar en el contexto activo del agente.'),
        ('Lección 2 — Alto riesgo de propagaciones masivas',
         'Las operaciones de propagación masiva (sed/cp sobre múltiples archivos) son de alto '
         'riesgo. Requieren verificación post-operación, no solo pre-operación. Una regla correcta '
         'pero incompleta puede ser más peligrosa que no tener regla, porque genera falsa seguridad.'),
        ('Lección 3 — Clasificación de tipos como mecanismo robusto',
         'Un archivo de clasificación explícita de tipos (BASE/CLON/DIVERGENTE/PROPIO) es '
         'significativamente más robusto que reglas textuales dispersas. La clasificación obliga '
         'a razonar sobre el tipo antes de actuar, mientras que las reglas textuales son '
         'susceptibles de interpretaciones parciales.'),
    ]

    for title, body in lecciones:
        add_heading(doc, title, level=3)
        add_body(doc, body)

    add_heading(doc, '9.2 Recomendaciones para el futuro', level=2)
    recs = [
        'Actualizar PROPAGATION_RULES.md cada vez que se añade código exclusivo a ENS u otra app — el umbral de 580 líneas puede crecer.',
        'Ejecutar el script de verificación ENS antes de cualquier commit que toque phase2-consulting.js en cualquiera de las 5 apps consulting.',
        'Considerar la extracción del código exclusivo de ENS a phase2-ens-extensions.js si supera las 1000 líneas.',
        'Añadir referencias cruzadas a PROPAGATION_RULES.md en los AGENTS.md específicos de cada app.',
        'Documentar las funciones exclusivas de ENS en los comentarios del propio archivo JS con un bloque de encabezado que las liste y advierta sobre la prohibición de sobreescritura.',
    ]
    for rec in recs:
        add_bullet(doc, rec)
    doc.add_paragraph()


def build_sec10(doc):
    add_heading(doc, '10. Glosario')

    terms = [
        ('BASE',
         'Archivo master que se edita directamente y se propaga a los CLONES mediante sed o cp. '
         'Ejemplo: ISO27001-SGSI/js/modules/phase2-consulting.js'),
        ('CLON SEGURO',
         'Idéntico al BASE excepto el appId. La propagación con sed es segura. '
         'Ejemplo: RGPD, ISO27701, ISO42001 para phase2-consulting.js'),
        ('DIVERGENTE',
         'Comparte la base pero tiene código exclusivo añadido. Nunca propagar completo desde BASE — '
         'usar exclusivamente patch quirúrgico Python. Ejemplo: ENS-RD311-2022'),
        ('PROPIO',
         'Archivo sin equivalente funcional en otra app. Se edita directamente, nunca se copia entre apps. '
         'Ejemplo: phase2-implementation.js en ISO9001/ISO14001'),
        ('Patch quirúrgico',
         'Modificación puntual de líneas específicas mediante Python str.replace() '
         'sobre el archivo completo, sin sobreescribir el archivo entero ni usar sed de sustitución completa.'),
        ('PROPAGATION_RULES.md',
         'Archivo de instrucciones operativas para propagación entre apps, cargado automáticamente '
         'por OpenCode como segunda instrucción junto con AGENTS.md.'),
        ('appId',
         'Identificador único de aplicación (iso27001, ens, rgpd, iso27701, iso42001, iso9001, '
         'iso14001, iso14001-2026, tisax) que diferencia los CLONES del BASE.'),
        ('CCN-STIC 808',
         'Guía del Centro Criptológico Nacional para la verificación del cumplimiento del Esquema '
         'Nacional de Seguridad (ENS). Implementada exclusivamente en ENS-RD311-2022.'),
        ('Evolució',
         'Pestaña exclusiva de ENS-RD311-2022 con gráfico Chart.js de tendencia de progreso '
         'a lo largo de snapshots periódicos.'),
        ('Snapshot',
         'Captura periódica del estado de cumplimiento ENS almacenada para alimentar '
         'el gráfico de tendencia de la pestaña Evolució.'),
        ('MP-1',
         'Operación de mantenimiento de plataforma número 1: corrección de 5 vulnerabilidades '
         'innerHTML inseguros en los módulos JS de las 9 apps ISO/ENS. Commit 22379b8.'),
        ('INC-2026-001',
         'Referencia oficial de este incidente en el registro CODANOR. Primer incidente '
         'documentado de pérdida de código en el ecosistema de 9 apps ISO/ENS.'),
    ]

    table = doc.add_table(rows=1, cols=2)
    table.style = 'Table Grid'
    make_table_header(table, ['Término', 'Definición'], [4.0, 13.0])
    for i, (term, defn) in enumerate(terms):
        add_table_row(table, [term, defn], even=(i % 2 == 1),
                      mono_cols=[0], bold_cols=[])
    doc.add_paragraph()


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    doc = Document()
    set_doc_margins(doc)

    # Estilos base globales
    style = doc.styles['Normal']
    style.font.name = 'Nunito Sans'
    style.font.size = Pt(10.5)

    # Cabecera y pie
    add_header(doc, 'Informe de Incidente — Sistema de Propagación entre Apps CODANOR  |  v1.0')
    add_footer(doc)

    # Portada
    build_cover(doc)

    # Control de versiones
    build_version_table(doc)
    add_page_break(doc)

    # TOC
    add_heading(doc, 'Índice de contenidos', level=2)
    add_toc(doc)
    add_page_break(doc)

    # Secciones
    build_sec1(doc)
    add_page_break(doc)
    build_sec2(doc)
    build_sec3(doc)
    add_page_break(doc)
    build_sec4(doc)
    add_page_break(doc)
    build_sec5(doc)
    add_page_break(doc)
    build_sec6(doc)
    add_page_break(doc)
    build_sec7(doc)
    add_page_break(doc)
    build_sec8(doc)
    add_page_break(doc)
    build_sec9(doc)
    add_page_break(doc)
    build_sec10(doc)

    # Guardar
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    doc.save(OUTPUT_PATH)
    print(f'✅ Documento generado: {OUTPUT_PATH}')


if __name__ == '__main__':
    main()
