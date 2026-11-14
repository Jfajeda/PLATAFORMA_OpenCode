#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera el documento Word "Guía Wiki_CODANOR con Open WebUI" para CODANOR.
Branding corporativo: #178DC2 (primary), #12A79D (accent), #1a1a2e (dark).
Fuente: Calibri (cuerpo) / Poppins (títulos simulado con Calibri bold).
Requiere: python-docx  →  pip install python-docx
Salida: /Users/jaimefajeda/Proyectos/PLATAFORMA_OpenCode-NEW/Guia_Wiki_CODANOR_OpenWebUI.docx
"""

import os
import copy
from datetime import date

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.opc.constants import RELATIONSHIP_TYPE as RT

# ─────────────────────────────────────────────────────────
# CONSTANTES DE BRANDING CODANOR
# ─────────────────────────────────────────────────────────
PRIMARY    = RGBColor(0x17, 0x8D, 0xC2)   # #178DC2
ACCENT     = RGBColor(0x12, 0xA7, 0x9D)   # #12A79D
DARK       = RGBColor(0x1A, 0x1A, 0x2E)   # #1a1a2e
GREY       = RGBColor(0x55, 0x5B, 0x66)   # texto secundario
LIGHT_GREY = RGBColor(0xCC, 0xCC, 0xCC)   # bordes suaves
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
TEXT_MAIN  = RGBColor(0x22, 0x22, 0x33)

# hex sin # para OxmlElement
HEX_PRIMARY  = "178DC2"
HEX_ACCENT   = "12A79D"
HEX_DARK     = "1A1A2E"
HEX_LIGHTBG  = "EAF6FB"   # fondo azul muy claro
HEX_LIGHTGRN = "E8F8F5"   # fondo verde muy claro
HEX_HDRBG    = "178DC2"   # cabecera de tabla
HEX_ROWODD   = "F0F9FF"
HEX_ROWEVEN  = "FFFFFF"
HEX_WARNING  = "FFF3CD"   # fondo aviso amarillo
HEX_DANGER   = "FDECEA"   # fondo aviso rojo
HEX_WHITE    = "FFFFFF"

LOGO_PATH = '/Users/jaimefajeda/Proyectos/Plataforma_Seguimiento_Proyectos/ENS-RD311-2022/img/logo-codanor.png'
OUT_PATH  = '/Users/jaimefajeda/Proyectos/PLATAFORMA_OpenCode-NEW/Guia_Wiki_CODANOR_OpenWebUI.docx'

# ─────────────────────────────────────────────────────────
# DOCUMENTO BASE
# ─────────────────────────────────────────────────────────
doc = Document()

# Estilo Normal base
normal_style = doc.styles['Normal']
normal_style.font.name = 'Calibri'
normal_style.font.size = Pt(11)
normal_style.font.color.rgb = TEXT_MAIN

# Márgenes A4: 2.5 arriba, 2.5 abajo, 2.0 izq, 2.0 der
for sec in doc.sections:
    sec.page_width  = Cm(21)
    sec.page_height = Cm(29.7)
    sec.top_margin    = Cm(2.5)
    sec.bottom_margin = Cm(2.5)
    sec.left_margin   = Cm(2.0)
    sec.right_margin  = Cm(2.0)


# ─────────────────────────────────────────────────────────
# HELPERS XML
# ─────────────────────────────────────────────────────────
def set_cell_shading(cell, hex_color):
    """Fondo de celda."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'),   'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'),  hex_color)
    tc_pr.append(shd)


def set_cell_borders(cell, top=None, bottom=None, left=None, right=None, color='178DC2', sz='4'):
    """Bordes de celda individuales."""
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_borders = OxmlElement('w:tcBorders')
    for side_name, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        if val:
            el = OxmlElement(f'w:{side_name}')
            el.set(qn('w:val'),   val)
            el.set(qn('w:sz'),    sz)
            el.set(qn('w:space'), '0')
            el.set(qn('w:color'), color)
            tc_borders.append(el)
    tc_pr.append(tc_borders)


def add_paragraph_bottom_border(p, color=HEX_ACCENT, sz='8'):
    """Línea inferior de párrafo."""
    pPr = p._p.get_or_add_pPr()
    pbdr = OxmlElement('w:pBdr')
    bot  = OxmlElement('w:bottom')
    bot.set(qn('w:val'),   'single')
    bot.set(qn('w:sz'),    sz)
    bot.set(qn('w:space'), '4')
    bot.set(qn('w:color'), color)
    pbdr.append(bot)
    pPr.append(pbdr)


def set_run_font(run, name='Calibri', size=None, bold=False, italic=False, color=None):
    run.font.name = name
    if size:
        run.font.size = Pt(size)
    run.bold   = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color


def set_table_no_spacing(tbl):
    """Elimina espaciado interno por defecto de tabla."""
    tbl_pr = tbl._tbl.get_or_add_tblPr()
    spacing = OxmlElement('w:tblCellSpacing')
    spacing.set(qn('w:w'),    '0')
    spacing.set(qn('w:type'), 'dxa')
    tbl_pr.append(spacing)


def set_col_width(cell, width_cm):
    """Fija el ancho de celda en cm."""
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tcW = OxmlElement('w:tcW')
    tcW.set(qn('w:w'),    str(int(Cm(width_cm).emu / 914.4)))
    tcW.set(qn('w:type'), 'dxa')
    tc_pr.append(tcW)


def add_page_number_field(run):
    """Inserta campo NUM/NUMPAGES en un run."""
    fld = OxmlElement('w:fldChar')
    fld.set(qn('w:fldCharType'), 'begin')
    run._r.append(fld)
    instr = OxmlElement('w:instrText')
    instr.set(qn('xml:space'), 'preserve')
    instr.text = ' PAGE '
    run._r.append(instr)
    fld2 = OxmlElement('w:fldChar')
    fld2.set(qn('w:fldCharType'), 'end')
    run._r.append(fld2)


def add_numpages_field(run):
    fld = OxmlElement('w:fldChar')
    fld.set(qn('w:fldCharType'), 'begin')
    run._r.append(fld)
    instr = OxmlElement('w:instrText')
    instr.set(qn('xml:space'), 'preserve')
    instr.text = ' NUMPAGES '
    run._r.append(instr)
    fld2 = OxmlElement('w:fldChar')
    fld2.set(qn('w:fldCharType'), 'end')
    run._r.append(fld2)


# ─────────────────────────────────────────────────────────
# PIE DE PÁGINA (todas las secciones)
# ─────────────────────────────────────────────────────────
def build_footer(section):
    footer = section.footer
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    p.clear()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Línea superior del pie
    pPr = p._p.get_or_add_pPr()
    pbdr = OxmlElement('w:pBdr')
    top  = OxmlElement('w:top')
    top.set(qn('w:val'),   'single')
    top.set(qn('w:sz'),    '6')
    top.set(qn('w:space'), '4')
    top.set(qn('w:color'), HEX_PRIMARY)
    pbdr.append(top)
    pPr.append(pbdr)

    # Texto izquierdo
    r1 = p.add_run('CODANOR — Jafa, S.L. | CONFIDENCIAL | Página ')
    r1.font.name = 'Calibri'
    r1.font.size = Pt(8)
    r1.font.color.rgb = GREY

    # Campo PAGE
    r2 = p.add_run()
    r2.font.name = 'Calibri'
    r2.font.size = Pt(8)
    r2.font.color.rgb = PRIMARY
    add_page_number_field(r2)

    r3 = p.add_run(' de ')
    r3.font.name = 'Calibri'
    r3.font.size = Pt(8)
    r3.font.color.rgb = GREY

    r4 = p.add_run()
    r4.font.name = 'Calibri'
    r4.font.size = Pt(8)
    r4.font.color.rgb = PRIMARY
    add_numpages_field(r4)


# ─────────────────────────────────────────────────────────
# CABECERA (secciones 2+)
# ─────────────────────────────────────────────────────────
def build_header(section, logo_path, title_text):
    header = section.header
    header.is_linked_to_previous = False
    p = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
    p.clear()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT

    # Logo pequeño si existe
    if os.path.exists(logo_path):
        r_logo = p.add_run()
        r_logo.add_picture(logo_path, height=Cm(0.7))
        r_logo.add_tab  = False
        p.add_run('   ')  # espacio

    r_title = p.add_run(title_text)
    r_title.font.name  = 'Calibri'
    r_title.font.size  = Pt(9)
    r_title.font.color.rgb = PRIMARY
    r_title.bold = True

    # Línea inferior azul
    add_paragraph_bottom_border(p, color=HEX_PRIMARY, sz='6')


# ─────────────────────────────────────────────────────────
# FUNCIONES DE CONTENIDO
# ─────────────────────────────────────────────────────────
def add_heading(text, level=1, page_break_before=False):
    p = doc.add_paragraph()
    if page_break_before:
        pPr = p._p.get_or_add_pPr()
        pbk = OxmlElement('w:pageBreakBefore')
        pbk.set(qn('w:val'), '1')
        pPr.append(pbk)
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.bold = True
    if level == 1:
        run.font.size = Pt(18)
        run.font.color.rgb = PRIMARY
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after  = Pt(8)
        add_paragraph_bottom_border(p, color=HEX_ACCENT, sz='8')
    elif level == 2:
        run.font.size = Pt(13.5)
        run.font.color.rgb = DARK
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after  = Pt(4)
    else:
        run.font.size = Pt(11.5)
        run.font.color.rgb = ACCENT
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after  = Pt(2)
    return p


def add_body(text, bold=False, italic=False, color=None, size=11, space_after=5):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name  = 'Calibri'
    run.font.size  = Pt(size)
    run.bold       = bold
    run.italic     = italic
    if color:
        run.font.color.rgb = color
    p.paragraph_format.space_after  = Pt(space_after)
    p.paragraph_format.space_before = Pt(0)
    return p


def add_bullet(text, bold_prefix=None, level=0, color=None):
    style_name = 'List Bullet' if level == 0 else 'List Bullet 2'
    try:
        p = doc.add_paragraph(style=style_name)
    except Exception:
        p = doc.add_paragraph()
        p.add_run('• ')
    if bold_prefix:
        r = p.add_run(bold_prefix)
        r.bold = True
        r.font.name = 'Calibri'
        r.font.color.rgb = DARK if not color else color
    r2 = p.add_run(text)
    r2.font.name = 'Calibri'
    r2.font.size = Pt(10.5)
    p.paragraph_format.space_after = Pt(2)
    return p


def add_numbered(items):
    """Lista numerada automática."""
    for text in items:
        try:
            p = doc.add_paragraph(style='List Number')
        except Exception:
            p = doc.add_paragraph()
        r = p.add_run(text)
        r.font.name = 'Calibri'
        r.font.size = Pt(10.5)
        p.paragraph_format.space_after = Pt(3)


def add_step_block(steps):
    """
    Tabla visual de pasos numerados con fondo alternado.
    steps: lista de (titulo_paso, descripcion)
    """
    tbl = doc.add_table(rows=0, cols=2)
    tbl.style = 'Table Grid'
    try:
        tbl_pr = tbl._tbl.get_or_add_tblPr()
        tbl_bdr = OxmlElement('w:tblBorders')
        for side in ['top','bottom','left','right','insideH','insideV']:
            el = OxmlElement(f'w:{side}')
            el.set(qn('w:val'),   'single')
            el.set(qn('w:sz'),    '4')
            el.set(qn('w:space'), '0')
            el.set(qn('w:color'), 'D0E8F5')
            tbl_bdr.append(el)
        tbl_pr.append(tbl_bdr)
    except Exception:
        pass

    for i, (titulo, desc) in enumerate(steps):
        row = tbl.add_row()
        c0, c1 = row.cells
        # Columna nº
        bg = HEX_PRIMARY if i % 2 == 0 else '0E6E9B'
        set_cell_shading(c0, bg)
        c0.width = Cm(1.2)
        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r0 = p0.add_run(str(i + 1))
        r0.bold = True
        r0.font.name  = 'Calibri'
        r0.font.size  = Pt(12)
        r0.font.color.rgb = WHITE

        # Columna descripción
        set_cell_shading(c1, HEX_ROWODD if i % 2 == 0 else HEX_ROWEVEN)
        p1 = c1.paragraphs[0]
        if titulo:
            rt = p1.add_run(titulo + ' ')
            rt.bold = True
            rt.font.name  = 'Calibri'
            rt.font.size  = Pt(10.5)
            rt.font.color.rgb = DARK
        rd = p1.add_run(desc)
        rd.font.name = 'Calibri'
        rd.font.size = Pt(10.5)
        p1.paragraph_format.space_after  = Pt(3)
        p1.paragraph_format.space_before = Pt(3)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return tbl


def add_callout(title, body_text, fill=HEX_LIGHTBG, title_color=PRIMARY, icon='ℹ️'):
    """Caja informativa con título y cuerpo."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.style = 'Table Grid'
    cell = tbl.cell(0, 0)
    set_cell_shading(cell, fill)

    p_t = cell.paragraphs[0]
    r_icon = p_t.add_run(icon + '  ')
    r_icon.font.size = Pt(11)
    r_title = p_t.add_run(title)
    r_title.bold = True
    r_title.font.name  = 'Calibri'
    r_title.font.size  = Pt(11)
    r_title.font.color.rgb = title_color
    p_t.paragraph_format.space_after = Pt(2)

    p_b = cell.add_paragraph()
    r_body = p_b.add_run(body_text)
    r_body.font.name = 'Calibri'
    r_body.font.size = Pt(10.5)
    p_b.paragraph_format.space_after  = Pt(4)
    p_b.paragraph_format.space_before = Pt(0)

    # Borde izquierdo de color
    try:
        tc_pr = cell._tc.get_or_add_tcPr()
        tc_bdr = OxmlElement('w:tcBorders')
        left_el = OxmlElement('w:left')
        left_el.set(qn('w:val'),   'single')
        left_el.set(qn('w:sz'),    '18')
        left_el.set(qn('w:space'), '0')
        left_el.set(qn('w:color'), HEX_PRIMARY)
        tc_bdr.append(left_el)
        tc_pr.append(tc_bdr)
    except Exception:
        pass

    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return tbl


def add_warning(title, body_text):
    return add_callout(title, body_text, fill=HEX_WARNING,
                       title_color=RGBColor(0x85, 0x5C, 0x00), icon='⚠️')


def add_danger(title, body_text):
    return add_callout(title, body_text, fill=HEX_DANGER,
                       title_color=RGBColor(0x8B, 0x00, 0x00), icon='🚫')


def add_generic_table(headers, rows, col_widths=None, zebra=True):
    """
    Tabla genérica con cabecera PRIMARY y filas cebra.
    headers: lista de str
    rows: lista de listas de str
    col_widths: lista de float (cm) o None
    """
    ncols = len(headers)
    tbl = doc.add_table(rows=1, cols=ncols)
    tbl.style = 'Table Grid'

    # Cabecera
    hdr_cells = tbl.rows[0].cells
    for j, h in enumerate(headers):
        set_cell_shading(hdr_cells[j], HEX_HDRBG)
        p = hdr_cells[j].paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.name  = 'Calibri'
        r.font.size  = Pt(10)
        r.font.color.rgb = WHITE
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if col_widths:
            set_col_width(hdr_cells[j], col_widths[j])

    # Filas
    for i, row_data in enumerate(rows):
        row_cells = tbl.add_row().cells
        bg = HEX_ROWODD if (zebra and i % 2 == 0) else HEX_WHITE
        for j, cell_text in enumerate(row_data):
            set_cell_shading(row_cells[j], bg)
            p = row_cells[j].paragraphs[0]
            r = p.add_run(str(cell_text))
            r.font.name = 'Calibri'
            r.font.size = Pt(10)
            if col_widths:
                set_col_width(row_cells[j], col_widths[j])

    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    return tbl


def add_code_block(code_text):
    """Bloque de código monoespacio con fondo gris oscuro."""
    tbl = doc.add_table(rows=1, cols=1)
    cell = tbl.cell(0, 0)
    set_cell_shading(cell, '1E1E2E')
    p = cell.paragraphs[0]
    r = p.add_run(code_text)
    r.font.name  = 'Courier New'
    r.font.size  = Pt(9.5)
    r.font.color.rgb = RGBColor(0xA8, 0xFF, 0x3E)  # verde terminal
    p.paragraph_format.space_after  = Pt(2)
    p.paragraph_format.space_before = Pt(2)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return tbl


def add_spacer(pts=8):
    p = doc.add_paragraph()
    p.paragraph_format.space_after  = Pt(pts)
    p.paragraph_format.space_before = Pt(0)


# ─────────────────────────────────────────────────────────
# ÍNDICE (TOC simple manual)
# ─────────────────────────────────────────────────────────
TOC_ENTRIES = [
    ('1.', 'Resumen Ejecutivo'),
    ('2.', 'Arquitectura del Sistema'),
    ('3.', 'Prerequisitos'),
    ('4.', 'Procedimiento de Arranque'),
    ('5.', 'Configuración Inicial'),
    ('6.', 'Las 10 Knowledge Bases'),
    ('7.', 'Configurar LLM en Open WebUI'),
    ('8.', 'Modelos Disponibles'),
    ('9.', 'Primera Consulta RAG'),
    ('10.', 'Ingestar Documentos en Knowledge Bases'),
    ('11.', 'Restricciones de Seguridad RGPD'),
    ('12.', 'Mantenimiento'),
    ('13.', 'Solución de Problemas'),
]


def build_toc():
    add_heading('Índice de Contenidos', 1)
    tbl = doc.add_table(rows=0, cols=2)
    for num, title in TOC_ENTRIES:
        row = tbl.add_row()
        c0, c1 = row.cells
        p0 = c0.paragraphs[0]
        r0 = p0.add_run(num)
        r0.bold = True
        r0.font.name  = 'Calibri'
        r0.font.size  = Pt(10.5)
        r0.font.color.rgb = PRIMARY
        set_col_width(c0, 1.0)

        p1 = c1.paragraphs[0]
        r1 = p1.add_run(title)
        r1.font.name = 'Calibri'
        r1.font.size = Pt(10.5)
        p0.paragraph_format.space_after = Pt(2)
        p1.paragraph_format.space_after = Pt(2)

    doc.add_page_break()


# ═══════════════════════════════════════════════════════════
# ██████████████████  PORTADA  ██████████████████████████████
# ═══════════════════════════════════════════════════════════
section_cover = doc.sections[0]
section_cover.different_first_page_header_footer = True
# Pie portada (vacío)
section_cover.first_page_footer.is_linked_to_previous = False

# Fondo: no disponible en python-docx directamente; usaremos espaciadores
add_spacer(40)

# Logo
if os.path.exists(LOGO_PATH):
    p_logo = doc.add_paragraph()
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_logo = p_logo.add_run()
    r_logo.add_picture(LOGO_PATH, width=Inches(3.0))
    add_spacer(20)
else:
    p_logo = doc.add_paragraph()
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_alt = p_logo.add_run('[ CODANOR ]')
    r_alt.bold = True
    r_alt.font.size = Pt(22)
    r_alt.font.color.rgb = PRIMARY
    add_spacer(20)

# Línea decorativa
tbl_dec = doc.add_table(rows=1, cols=1)
cell_dec = tbl_dec.cell(0, 0)
set_cell_shading(cell_dec, HEX_PRIMARY)
p_dec = cell_dec.paragraphs[0]
p_dec.paragraph_format.space_before = Pt(0)
p_dec.paragraph_format.space_after  = Pt(0)
r_dec = p_dec.add_run(' ')
r_dec.font.size = Pt(4)
add_spacer(10)

# Título principal
p_title = doc.add_paragraph()
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_t = p_title.add_run('Wiki_CODANOR')
r_t.bold = True
r_t.font.name  = 'Calibri'
r_t.font.size  = Pt(32)
r_t.font.color.rgb = PRIMARY
p_title.paragraph_format.space_after = Pt(4)

# Subtítulo
p_sub = doc.add_paragraph()
p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_s = p_sub.add_run('Guía de Configuración con Open WebUI')
r_s.bold = False
r_s.font.name  = 'Calibri'
r_s.font.size  = Pt(18)
r_s.font.color.rgb = DARK
p_sub.paragraph_format.space_after = Pt(6)

# Línea acento
p_acc = doc.add_paragraph()
p_acc.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_acc = p_acc.add_run('Sistema RAG local con Ollama · ChromaDB · nomic-embed-text')
r_acc.font.name  = 'Calibri'
r_acc.font.size  = Pt(12)
r_acc.font.color.rgb = ACCENT
p_acc.paragraph_format.space_after = Pt(30)

# Línea decorativa inferior
tbl_dec2 = doc.add_table(rows=1, cols=1)
cell_dec2 = tbl_dec2.cell(0, 0)
set_cell_shading(cell_dec2, HEX_ACCENT)
p_dec2 = cell_dec2.paragraphs[0]
p_dec2.paragraph_format.space_before = Pt(0)
p_dec2.paragraph_format.space_after  = Pt(0)
r_dec2 = p_dec2.add_run(' ')
r_dec2.font.size = Pt(4)
add_spacer(20)

# Tabla de metadatos
meta_data = [
    ('Versión',         'v1.0'),
    ('Fecha',           date.today().strftime('%d de %B de %Y').replace(
                        'January','enero').replace('February','febrero')
                        .replace('March','marzo').replace('April','abril')
                        .replace('May','mayo').replace('June','junio')
                        .replace('July','julio').replace('August','agosto')
                        .replace('September','septiembre').replace('October','octubre')
                        .replace('November','noviembre').replace('December','diciembre')),
    ('Responsable',     'Jafa, S.L. (CODANOR)'),
    ('Clasificación',   'CONFIDENCIAL — Uso interno'),
    ('Plataforma',      'Open WebUI + Ollama · Puerto 3000'),
]
tbl_meta = doc.add_table(rows=len(meta_data), cols=2)
tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
for i, (k, v) in enumerate(meta_data):
    c0, c1 = tbl_meta.rows[i].cells
    set_cell_shading(c0, HEX_LIGHTBG)
    p0 = c0.paragraphs[0]
    r0 = p0.add_run(k)
    r0.bold = True
    r0.font.name  = 'Calibri'
    r0.font.size  = Pt(10)
    r0.font.color.rgb = DARK
    set_col_width(c0, 3.5)

    p1 = c1.paragraphs[0]
    r1 = p1.add_run(v)
    r1.font.name = 'Calibri'
    r1.font.size = Pt(10)
    set_col_width(c1, 8.0)

doc.add_page_break()


# ═══════════════════════════════════════════════════════════
# NUEVA SECCIÓN — cabecera + pie permanentes
# ═══════════════════════════════════════════════════════════
from docx.oxml.ns import nsmap
from docx.oxml import OxmlElement as OE

# Añadir nueva sección continua para activar cabecera/pie
new_sec_prop = OxmlElement('w:sectPr')
doc.element.body.append(new_sec_prop)

# Forzar build de cabecera/pie en la sección principal existente
main_section = doc.sections[0]
build_header(main_section,
             LOGO_PATH,
             'Wiki_CODANOR · Guía de Configuración con Open WebUI')
build_footer(main_section)

# ─────────────────────────────────────────────────────────
# ÍNDICE
# ─────────────────────────────────────────────────────────
build_toc()


# ═══════════════════════════════════════════════════════════
# 1. RESUMEN EJECUTIVO
# ═══════════════════════════════════════════════════════════
add_heading('1. Resumen Ejecutivo', 1)

add_body(
    'Wiki_CODANOR es el sistema de gestión documental y base de conocimiento corporativo de '
    'CODANOR (Jafa, S.L.), desplegado en local mediante Open WebUI. Proporciona una interfaz '
    'web avanzada para interactuar con modelos de lenguaje (LLM) de manera privada, sin enviar '
    'ningún dato a terceros, y con capacidades de Recuperación Aumentada con Generación (RAG) '
    'sobre las 10 bases de conocimiento internas de la organización.'
)

add_heading('Arquitectura general', 2)
add_body(
    'El sistema se compone de cuatro componentes integrados que funcionan conjuntamente para '
    'ofrecer un entorno de IA completamente local y conforme al RGPD:'
)
add_bullet('Open WebUI — Interfaz web accesible en http://localhost:3000. Gestiona usuarios, '
           'Knowledge Bases, historial de chats y configuración de conexiones a LLMs.', 'Open WebUI: ')
add_bullet('Ollama (nativo macOS, puerto 11434) — Motor de inferencia local que ejecuta los modelos '
           'LLM descargados. Open WebUI se comunica con él via http://host.docker.internal:11434.', 'Ollama: ')
add_bullet('nomic-embed-text — Modelo de embeddings que convierte los documentos en vectores '
           'semánticos para la búsqueda RAG. Se descarga con: ollama pull nomic-embed-text.', 'nomic-embed-text: ')
add_bullet('ChromaDB / vectordb/ — Base de datos vectorial persistente que almacena los embeddings '
           'de todos los documentos ingestados en las Knowledge Bases. Se monta como volumen Docker.', 'ChromaDB: ')

add_spacer(6)
add_warning(
    'Restricción RGPD — Datos Privados',
    'Todo el sistema opera exclusivamente en la red local corporativa. Los documentos clasificados '
    'como PRIVADO (datos personales, expedientes de clientes, actas confidenciales) NUNCA '
    'abandonan la red interna. Open WebUI no tiene acceso a internet y Ollama funciona sin '
    'conexión exterior. Esta arquitectura garantiza el cumplimiento del RGPD y la ENS.'
)


# ═══════════════════════════════════════════════════════════
# 2. ARQUITECTURA DEL SISTEMA
# ═══════════════════════════════════════════════════════════
add_heading('2. Arquitectura del Sistema', 1, page_break_before=True)

add_body('La siguiente tabla describe cada componente del sistema, su función, puerto de red '
         'y ubicación en la infraestructura:')

add_generic_table(
    headers=['Componente', 'Tipo', 'Puerto / Ruta', 'Función'],
    rows=[
        ['wiki-codanor', 'Contenedor Docker', ':3000', 'Interfaz web Open WebUI — acceso usuario'],
        ['Open WebUI', 'Aplicación web', 'localhost:3000', 'UI de chat, Knowledge Bases, gestión de usuarios'],
        ['Ollama', 'Servicio nativo macOS', 'localhost:11434', 'Motor de inferencia LLM — ejecuta modelos .gguf'],
        ['nomic-embed-text', 'Modelo Ollama', 'Via Ollama :11434', 'Embeddings RAG — conversión texto → vector'],
        ['vectordb/', 'Volumen Docker', '~/Proyectos/Wiki_CODANOR/vectordb/', 'ChromaDB persistente — base de datos vectorial'],
        ['qwen2.5-coder:14b', 'Modelo Ollama', 'Via Ollama', 'Análisis técnico, código, normativa'],
        ['qwen3:8b', 'Modelo Ollama', 'Via Ollama', 'Uso general, redacción, consultas'],
        ['llama3.1:latest', 'Modelo Ollama', 'Via Ollama', 'Síntesis de actas, documentación'],
        ['gemma3:4b', 'Modelo Ollama', 'Via Ollama', 'Consultas rápidas, respuestas concisas'],
    ],
    col_widths=[3.5, 3.0, 3.5, 6.5],
    zebra=True
)

add_heading('Diagrama de flujo de datos', 2)
add_body('El flujo de una consulta RAG sigue la siguiente secuencia:')
add_numbered([
    'El usuario sube un documento PDF/DOCX a una Knowledge Base en Open WebUI.',
    'Open WebUI llama a Ollama con el modelo nomic-embed-text para vectorizar el documento.',
    'Los vectores se almacenan en ChromaDB (directorio vectordb/).',
    'En el chat, el usuario hace una pregunta seleccionando la Knowledge Base.',
    'Open WebUI recupera los fragmentos de texto más relevantes (RAG retrieval).',
    'La pregunta + fragmentos relevantes se envían al LLM seleccionado (Ollama local o externo).',
    'El LLM genera la respuesta contextualizada que se muestra al usuario.',
])

add_callout(
    'Persistencia de datos',
    'El directorio vectordb/ es un volumen Docker montado en ~/Proyectos/Wiki_CODANOR/vectordb/. '
    'Aunque se detenga o se elimine el contenedor Docker, los embeddings persisten en disco. '
    'Hacer backup de este directorio equivale a hacer backup de todas las Knowledge Bases.',
    fill=HEX_LIGHTGRN, title_color=ACCENT, icon='💾'
)


# ═══════════════════════════════════════════════════════════
# 3. PREREQUISITOS
# ═══════════════════════════════════════════════════════════
add_heading('3. Prerequisitos', 1, page_break_before=True)

add_body('Antes de iniciar el sistema, verifica que todos los componentes siguientes están '
         'instalados y operativos en el equipo:')

add_generic_table(
    headers=['Componente', 'Versión mínima', 'Estado requerido', 'Verificación'],
    rows=[
        ['Docker Desktop', '4.x', 'Instalado y en ejecución', 'Ballena en barra de menú macOS'],
        ['Ollama', 'v0.34.4+', 'Instalado (nativo macOS)', 'ollama --version en Terminal'],
        ['nomic-embed-text', 'latest', 'Descargado en Ollama', 'ollama list | grep nomic'],
        ['qwen2.5-coder:14b', '14B', 'Descargado en Ollama', 'ollama list | grep qwen2.5'],
        ['qwen3:8b', '8B', 'Descargado en Ollama', 'ollama list | grep qwen3'],
        ['llama3.1:latest', '8B', 'Descargado en Ollama', 'ollama list | grep llama3.1'],
        ['gemma3:4b', '4B', 'Descargado en Ollama', 'ollama list | grep gemma3'],
        ['Espacio libre en disco', '≥ 17 GB', 'Disponible', 'df -h ~ en Terminal'],
    ],
    col_widths=[3.5, 2.5, 3.5, 4.5],
    zebra=True
)

add_heading('Comandos de verificación rápida', 2)
add_code_block(
    '# Verificar Ollama instalado y versión\n'
    'ollama --version\n\n'
    '# Listar modelos descargados\n'
    'ollama list\n\n'
    '# Resultado esperado:\n'
    'NAME                   ID              SIZE    MODIFIED\n'
    'qwen2.5-coder:14b      ...             9.0 GB  ...\n'
    'qwen3:8b               ...             5.2 GB  ...\n'
    'llama3.1:latest        ...             4.7 GB  ...\n'
    'gemma3:4b              ...             3.3 GB  ...\n'
    'nomic-embed-text:latest ...            274 MB  ...'
)

add_warning(
    'Docker Desktop debe estar activo ANTES de lanzar el contenedor',
    'Si Docker Desktop no está en ejecución, el comando docker compose up -d fallará con '
    '"Cannot connect to the Docker daemon". Siempre abrir Docker Desktop primero y esperar '
    'a que aparezca la ballena en la barra de menú de macOS.'
)


# ═══════════════════════════════════════════════════════════
# 4. PROCEDIMIENTO DE ARRANQUE
# ═══════════════════════════════════════════════════════════
add_heading('4. Procedimiento de Arranque', 1, page_break_before=True)

add_body('El sistema se arranca en cuatro pasos. Sigue el procedimiento en el orden indicado '
         'para garantizar que todos los componentes están disponibles antes de acceder a la interfaz.')

add_step_block([
    ('Paso 1 — Abrir Docker Desktop:',
     'Abrir Spotlight (⌘ + Espacio) → escribir "Docker" → pulsar Enter. '
     'Esperar hasta que aparezca el icono de la ballena (🐳) en la barra de menú de macOS '
     'con estado "Running". Tiempo estimado: 15-30 segundos.'),
    ('Paso 2 — Abrir Terminal y navegar al directorio del proyecto:',
     'Abrir Terminal (⌘ + Espacio → "Terminal"). Ejecutar:\n'
     '  cd ~/Proyectos/Wiki_CODANOR\n'
     'Verificar que el archivo docker-compose.yml está presente con: ls -la'),
    ('Paso 3 — Lanzar el contenedor:',
     'Ejecutar el comando:\n'
     '  docker compose up -d\n'
     'El flag -d lanza el contenedor en segundo plano (detached). '
     'La primera vez puede tardar 1-2 minutos si descarga la imagen de Open WebUI.'),
    ('Paso 4 — Verificar que el contenedor está activo:',
     'Ejecutar:\n'
     '  docker ps | grep wiki-codanor\n'
     'El resultado debe mostrar "Up" en la columna STATUS. '
     'Si aparece "Restarting", revisar los logs: docker compose logs -f'),
    ('Paso 5 — Abrir la interfaz web:',
     'Abrir Safari (o cualquier navegador) y navegar a:\n'
     '  http://localhost:3000\n'
     'La página de inicio de Open WebUI debe cargarse en 2-5 segundos.'),
])

add_code_block(
    '# Secuencia completa de arranque\n'
    'cd ~/Proyectos/Wiki_CODANOR\n'
    'docker compose up -d\n'
    'docker ps | grep wiki-codanor\n'
    '# → debe mostrar: wiki-codanor ... Up X minutes   0.0.0.0:3000->8080/tcp'
)

add_heading('Parada del sistema', 2)
add_body('Para detener el sistema de forma limpia (sin perder datos):')
add_code_block(
    '# Detener el contenedor (los datos en vectordb/ se conservan)\n'
    'cd ~/Proyectos/Wiki_CODANOR\n'
    'docker compose stop\n\n'
    '# Para parar Y eliminar el contenedor (los datos siguen en disco):\n'
    'docker compose down'
)


# ═══════════════════════════════════════════════════════════
# 5. CONFIGURACIÓN INICIAL
# ═══════════════════════════════════════════════════════════
add_heading('5. Configuración Inicial', 1, page_break_before=True)

add_body('La primera vez que se accede a Open WebUI en http://localhost:3000 es necesario '
         'crear la cuenta de administrador. Este proceso solo se realiza una vez.')

add_step_block([
    ('Pantalla de bienvenida:',
     'Al acceder por primera vez, Open WebUI muestra la pantalla "Get Started". '
     'Pulsar el botón "Sign up" (crear cuenta).'),
    ('Rellenar el formulario de registro:',
     'Nombre completo: Jafa SL (o el nombre del administrador). '
     'Correo electrónico: el email corporativo. '
     'Contraseña: mínimo 8 caracteres, con mayúscula y número.'),
    ('Confirmar el registro:',
     'Pulsar "Create Account". Open WebUI creará la cuenta y asignará automáticamente '
     'el rol de Administrador al primer usuario registrado.'),
    ('Acceder al panel de administración:',
     'Ir a: Avatar (esquina superior derecha) → Admin Panel. '
     'Desde aquí se gestionan usuarios, modelos, conexiones y configuración avanzada.'),
])

add_warning(
    'El primer usuario registrado es Administrador automáticamente',
    'Open WebUI asigna el rol de Admin al primer usuario que se registra. '
    'Si se registra una cuenta de prueba antes que la cuenta real de administración, '
    'esa cuenta de prueba será la admin. En ese caso, eliminar la instalación y '
    'recrearla: docker compose down && docker volume rm wiki-openwebui-data && docker compose up -d'
)

add_heading('Verificar conexión con Ollama', 2)
add_body('Tras el primer login, verificar que Open WebUI detecta Ollama correctamente:')
add_step_block([
    ('Ir a Configuración de conexiones:',
     'Avatar → Paràmetres (Ajustes) → Connexions (Conexiones).'),
    ('Verificar Ollama:',
     'En la sección "Ollama API", debe aparecer la URL: http://host.docker.internal:11434. '
     'Pulsar el botón de verificación (⟳). Debe mostrar "Connected" en verde.'),
    ('Verificar modelos disponibles:',
     'En el selector de modelos del chat (barra superior), deben aparecer los modelos '
     'descargados: qwen2.5-coder:14b, qwen3:8b, llama3.1:latest, gemma3:4b.'),
])


# ═══════════════════════════════════════════════════════════
# 6. LAS 10 KNOWLEDGE BASES
# ═══════════════════════════════════════════════════════════
add_heading('6. Las 10 Knowledge Bases', 1, page_break_before=True)

add_body(
    'Wiki_CODANOR organiza el conocimiento corporativo en 10 Knowledge Bases temáticas. '
    'Cada KB es un espacio independiente con sus propios documentos ingestados y vectorizados. '
    'Al hacer una consulta RAG, se puede seleccionar una o varias KBs para contextualizar '
    'la respuesta del LLM.'
)

add_generic_table(
    headers=['ID', 'Nombre', 'Descripción', 'Tipo de documentos'],
    rows=[
        ['ENS', 'ENS — Esquema Nacional de Seguridad',
         'Normativa ENS (RD 311/2022), guías CCN-STIC, controles de seguridad, '
         'anexos técnicos y procedimientos de auditoría ENS.',
         'PDF, DOCX'],
        ['ISO27001', 'ISO 27001 — SGSI',
         'Norma ISO 27001:2022, controles Anexo A, políticas SGSI, '
         'procedimientos de gestión de riesgos y declaración de aplicabilidad.',
         'PDF, DOCX'],
        ['LOPD-RGPD', 'LOPD / RGPD — Protección de Datos',
         'Reglamento (UE) 2016/679, LOPDGDD, guías AEPD, registros de tratamiento, '
         'modelos de contratos de encargo y cláusulas informativas.',
         'PDF, DOCX, TXT'],
        ['NIS2', 'NIS2 — Seguridad Redes e Infraestructuras',
         'Directiva NIS2 (UE 2022/2555), transposición española, '
         'requisitos para entidades esenciales e importantes.',
         'PDF'],
        ['Legislacion', 'Legislación y Normativa General',
         'BOE, DOUE, leyes sectoriales, normas técnicas UNE/ISO relevantes '
         'para la consultoría de seguridad y privacidad.',
         'PDF, HTML'],
        ['Licitaciones', 'Licitaciones y Contratos Públicos',
         'Pliegos técnicos de licitaciones, PCAP, requisitos de solvencia, '
         'modelos de ofertas y experiencias previas.',
         'PDF, DOCX'],
        ['Logs-SIEM', 'Logs y SIEM — Ciberseguridad',
         'Guías de configuración de sistemas de logging, correlación de eventos, '
         'alertas SIEM, playbooks de respuesta a incidentes.',
         'PDF, TXT, MD'],
        ['Actas', 'Actas de Reuniones',
         'Actas de reuniones de consultoría con clientes, acuerdos, '
         'puntos de seguimiento y decisiones tomadas.',
         'DOCX, PDF'],
        ['Plantillas', 'Plantillas Corporativas CODANOR',
         'Plantillas Word/Excel de políticas, procedimientos, registros, '
         'informes de auditoría y entregables de proyectos.',
         'DOCX, XLSX'],
        ['OSINT', 'OSINT — Inteligencia de Fuentes Abiertas',
         'Técnicas OSINT, herramientas, casos de uso en auditorías de seguridad '
         'y evaluaciones de exposición en internet.',
         'PDF, MD'],
    ],
    col_widths=[1.5, 4.0, 7.0, 3.5],
    zebra=True
)

add_heading('Crear una nueva Knowledge Base', 2)
add_body('Para crear una KB adicional o verificar las existentes, seguir estos pasos:')
add_step_block([
    ('Navegar a Workspace:',
     'En la barra lateral izquierda → "Workspace" (icono de carpeta).'),
    ('Ir a Coneixement (Knowledge):',
     'Seleccionar la pestaña "Coneixement" (o "Knowledge" si la interfaz está en inglés).'),
    ('Crear nueva KB:',
     'Pulsar el botón "+" (azul, esquina superior derecha). '
     'Rellenar: Nombre (ej. ENS), Descripción, y opcionalmente una imagen de portada.'),
    ('Confirmar:',
     'Pulsar "Create Knowledge". La KB aparece en la lista y ya está lista para recibir documentos.'),
])


# ═══════════════════════════════════════════════════════════
# 7. CONFIGURAR LLM EN OPEN WEBUI
# ═══════════════════════════════════════════════════════════
add_heading('7. Configurar LLM en Open WebUI', 1, page_break_before=True)

add_body(
    'Open WebUI permite conectarse simultáneamente a múltiples proveedores LLM: '
    'Ollama local (ya configurado por defecto), OpenRouter, Groq, OpenAI, Anthropic '
    'y cualquier servicio compatible con la API de OpenAI. Esta sección describe '
    'cómo configurar los proveedores externos.'
)

add_heading('7.1. Acceder a la configuración de conexiones', 2)
add_step_block([
    ('Abrir Ajustes:',
     'Avatar (icono de usuario, esquina superior derecha) → "Paràmetres" (Ajustes).'),
    ('Ir a Conexiones:',
     'En el menú lateral de ajustes → "Connexions" (Conexiones).'),
    ('Vista general:',
     'Se muestran las conexiones activas: Ollama API (ya configurada) y '
     'OpenAI API (desactivada por defecto).'),
])

add_heading('7.2. Desactivar la conexión por defecto a OpenAI', 2)
add_body('Por defecto, Open WebUI incluye una entrada apuntando a https://api.openai.com/v1 '
         'sin API Key válida. Desactivarla evita errores en el selector de modelos:')
add_step_block([
    ('Localizar la entrada OpenAI:',
     'En "Connexions", buscar la fila con URL: https://api.openai.com/v1'),
    ('Desactivar el toggle:',
     'Pulsar el interruptor (toggle) de la fila para desactivarla. '
     'El toggle debe quedar en gris (desactivado).'),
])

add_heading('7.3. Añadir OpenRouter (recomendado — gratuito)', 2)
add_step_block([
    ('Añadir nueva conexión:',
     'En "Connexions" → sección "OpenAI API" → pulsar el botón "+" (añadir).'),
    ('Configurar URL:',
     'URL: https://openrouter.ai/api/v1'),
    ('Configurar API Key:',
     'API Key: sk-or-XXXXXXXXXXXX (obtener gratis en https://openrouter.ai → cuenta gratuita).'),
    ('Guardar:',
     'Pulsar "Guardar" o el icono ✓. Los modelos de OpenRouter aparecerán automáticamente '
     'en el selector del chat.'),
])

add_heading('7.4. Alternativa: Groq (alta velocidad, gratuito)', 2)
add_step_block([
    ('Añadir nueva conexión:',
     'En "Connexions" → sección "OpenAI API" → pulsar "+".'),
    ('Configurar:',
     'URL: https://api.groq.com/openai/v1\n'
     'API Key: gsk_XXXXXXXXXXXX (obtener gratis en https://console.groq.com)'),
    ('Guardar:',
     'Pulsar ✓. Los modelos Groq (llama-3.3-70b-versatile, etc.) aparecerán en el selector.'),
])

add_callout(
    'Ollama ya está conectado por defecto',
    'No es necesario configurar Ollama manualmente. Open WebUI se conecta automáticamente '
    'a http://host.docker.internal:11434 (la IP especial de Docker que apunta al host macOS). '
    'Todos los modelos descargados con "ollama pull" aparecen directamente en el selector de modelos.',
    fill=HEX_LIGHTGRN, title_color=ACCENT, icon='✅'
)

add_generic_table(
    headers=['Proveedor', 'URL base', 'Formato API Key', 'Coste', 'Velocidad'],
    rows=[
        ['Ollama (local)', 'http://host.docker.internal:11434', 'Sin key (local)', 'Gratis', 'Variable (CPU/GPU)'],
        ['OpenRouter', 'https://openrouter.ai/api/v1', 'sk-or-...', 'Gratis (límites)', 'Media'],
        ['Groq', 'https://api.groq.com/openai/v1', 'gsk_...', 'Gratis (límites)', 'Muy alta'],
        ['Google Gemini', 'https://generativelanguage.googleapis.com/v1beta/openai/', 'AIza...', 'Gratis (límites)', 'Alta'],
        ['OpenAI', 'https://api.openai.com/v1', 'sk-...', 'De pago', 'Muy alta'],
        ['Anthropic', 'https://api.anthropic.com/v1', 'sk-ant-...', 'De pago', 'Alta'],
    ],
    col_widths=[2.5, 5.0, 3.0, 2.0, 2.5],
    zebra=True
)


# ═══════════════════════════════════════════════════════════
# 8. MODELOS DISPONIBLES
# ═══════════════════════════════════════════════════════════
add_heading('8. Modelos Disponibles', 1, page_break_before=True)

add_body(
    'La instalación local de Wiki_CODANOR incluye los siguientes modelos Ollama, '
    'seleccionados por su equilibrio entre calidad, velocidad y tamaño en disco. '
    'Además, los modelos externos (OpenRouter/Groq) están disponibles si se configura '
    'la conexión correspondiente.'
)

add_heading('8.1. Modelos Ollama instalados localmente', 2)
add_generic_table(
    headers=['Modelo', 'Tamaño', 'Caso de uso principal', 'Velocidad', 'Contexto'],
    rows=[
        ['qwen2.5-coder:14b', '9.0 GB', 'Análisis técnico, código, normativa técnica ENS/ISO', 'Media', '32K tokens'],
        ['qwen3:8b', '5.2 GB', 'Uso general, redacción, consultas documentales', 'Alta', '32K tokens'],
        ['llama3.1:latest', '4.7 GB', 'Síntesis de actas, documentación narrativa', 'Alta', '128K tokens'],
        ['gemma3:4b', '3.3 GB', 'Consultas rápidas, respuestas cortas y concisas', 'Muy alta', '8K tokens'],
        ['nomic-embed-text', '274 MB', 'SOLO embeddings RAG — NO usar en chat', '—', '8K tokens'],
    ],
    col_widths=[3.5, 1.5, 5.5, 2.0, 2.5],
    zebra=True
)

add_warning(
    'nomic-embed-text no es un modelo de chat',
    'nomic-embed-text es un modelo especializado en la generación de embeddings vectoriales. '
    'Aparece en el selector de modelos de Open WebUI pero NO debe usarse en el chat: '
    'no genera texto coherente. Su función es exclusivamente interna para la indexación RAG '
    'de documentos en las Knowledge Bases.'
)

add_heading('8.2. Guía de selección de modelo', 2)
add_body('Usa esta guía para elegir el modelo más adecuado según la tarea:')
add_bullet('Consultar norma ENS o ISO 27001 (texto técnico, controles, referencias): '
           'qwen2.5-coder:14b', 'Normativa técnica → ')
add_bullet('Redactar políticas, procedimientos o responder preguntas generales: '
           'qwen3:8b', 'Redacción general → ')
add_bullet('Analizar un acta o documento largo de más de 50 páginas: '
           'llama3.1:latest (128K contexto)', 'Documentos largos → ')
add_bullet('Respuesta rápida a pregunta corta, sin contexto RAG: '
           'gemma3:4b', 'Respuesta rápida → ')
add_bullet('Consulta con contexto de múltiples documentos (RAG sobre KB): '
           'qwen3:8b o llama3.1:latest', 'RAG multi-documento → ')


# ═══════════════════════════════════════════════════════════
# 9. PRIMERA CONSULTA RAG
# ═══════════════════════════════════════════════════════════
add_heading('9. Primera Consulta RAG', 1, page_break_before=True)

add_body(
    'RAG (Retrieval-Augmented Generation) permite al LLM responder preguntas basándose '
    'en documentos específicos que tú le proporcionas, en lugar de solo su conocimiento '
    'de entrenamiento. Existen dos modos de RAG en Open WebUI:'
)
add_bullet('RAG de fichero ad-hoc — Subes un documento directamente en el chat para esa sesión.', 'Ad-hoc: ')
add_bullet('RAG sobre Knowledge Base — El LLM consulta automáticamente los documentos '
           'indexados en una KB seleccionada.', 'KB persistente: ')

add_heading('9.1. RAG con fichero ad-hoc (sesión única)', 2)
add_step_block([
    ('Abrir el chat:',
     'En la barra lateral → "New Chat" (o ⊕).'),
    ('Seleccionar modelo:',
     'En el selector de modelos (barra superior) → elegir "qwen3:8b" o "llama3.1:latest".'),
    ('Subir el documento:',
     'Pulsar el botón "+" (clip, junto al campo de texto) → "Fitxers" (Ficheros) → '
     'seleccionar el PDF o DOCX. El archivo aparece como chip adjunto.'),
    ('Hacer la pregunta:',
     'Escribir la pregunta en el campo de texto. Por ejemplo:\n'
     '  "¿Cuáles son los controles del Anexo A de ISO 27001 relacionados con cifrado?"\n'
     'Pulsar Enter o el botón de envío.'),
    ('Revisar la respuesta:',
     'El LLM responde citando el contenido del documento adjunto. '
     'Las citas aparecen con referencia al fragmento fuente.'),
])

add_heading('9.2. RAG sobre Knowledge Base', 2)
add_step_block([
    ('Abrir el chat:',
     'En la barra lateral → "New Chat" (o ⊕).'),
    ('Seleccionar modelo:',
     'Elegir el modelo deseado en el selector.'),
    ('Seleccionar la Knowledge Base:',
     'Pulsar el botón "+" → "Coneixement" (Knowledge). '
     'Se muestra la lista de KBs disponibles. Seleccionar una o varias (ej. "ENS", "ISO27001").'),
    ('Hacer la pregunta:',
     'La KB seleccionada aparece como chip. Hacer la pregunta normalmente. '
     'Open WebUI busca automáticamente los fragmentos más relevantes antes de llamar al LLM.'),
    ('Revisar fuentes:',
     'Bajo la respuesta aparece un desplegable "Fuentes" con los fragmentos de documento '
     'utilizados para generar la respuesta.'),
])

add_callout(
    'Tip — Preguntas efectivas para RAG',
    'Para obtener mejores resultados con RAG, formula preguntas específicas y citables. '
    'En lugar de "¿Qué dice la norma?", pregunta "¿Qué requisitos establece el control '
    'A.8.3 de ISO 27001:2022 sobre la gestión de activos?". Cuanto más precisa la pregunta, '
    'más relevante el fragmento recuperado.',
    fill=HEX_LIGHTBG, title_color=PRIMARY, icon='💡'
)


# ═══════════════════════════════════════════════════════════
# 10. INGESTAR DOCUMENTOS EN KNOWLEDGE BASES
# ═══════════════════════════════════════════════════════════
add_heading('10. Ingestar Documentos en Knowledge Bases', 1, page_break_before=True)

add_body(
    'La ingestión es el proceso de subir un documento a una Knowledge Base, vectorizarlo '
    'con nomic-embed-text y almacenar los embeddings en ChromaDB. Una vez ingestado, '
    'el documento es consultable mediante RAG en cualquier chat.'
)

add_step_block([
    ('Ir a Workspace → Coneixement:',
     'Barra lateral → "Workspace" → pestaña "Coneixement" (Knowledge).'),
    ('Seleccionar la Knowledge Base:',
     'Clic en el nombre de la KB donde subir el documento (ej. "ENS").'),
    ('Abrir el panel de la KB:',
     'Se muestra la lista de documentos ya ingestados. '
     'Pulsar el botón "+" (azul) para añadir nuevos documentos.'),
    ('Seleccionar o arrastrar el fichero:',
     'Arrastrar el fichero PDF/DOCX al área de drop, o pulsar "Browse files". '
     'Formatos soportados: PDF, DOCX, TXT, MD, HTML, CSV.'),
    ('Esperar el procesamiento:',
     'Open WebUI procesa el documento: lo divide en chunks, genera embeddings con '
     'nomic-embed-text y los almacena en ChromaDB. El progreso se muestra con una barra. '
     'Documentos de 100 páginas: ~30-60 segundos.'),
    ('Verificar la ingestión:',
     'El documento aparece en la lista de la KB con el número de chunks indexados. '
     'Si aparece en rojo, hubo un error de procesamiento (ver logs).'),
])

add_warning(
    'Documentos protegidos con contraseña',
    'Los PDFs protegidos con contraseña no pueden ser procesados por Open WebUI. '
    'Antes de subirlos, eliminar la protección con: Archivo → Imprimir → PDF (sin contraseña). '
    'Los DOCX con permisos de edición restringidos tampoco se procesan correctamente.'
)

add_heading('Formatos de fichero soportados', 2)
add_generic_table(
    headers=['Formato', 'Extensión', 'Notas'],
    rows=[
        ['PDF', '.pdf', 'Sin contraseña. OCR no incluido (texto debe ser seleccionable)'],
        ['Word', '.docx', 'Sin protección de edición'],
        ['Texto plano', '.txt', 'UTF-8 recomendado'],
        ['Markdown', '.md', 'Ideal para documentación técnica'],
        ['HTML', '.html', 'Se extrae el texto plano del HTML'],
        ['CSV', '.csv', 'Cada fila se trata como chunk independiente'],
    ],
    col_widths=[3.0, 2.5, 10.5],
    zebra=True
)


# ═══════════════════════════════════════════════════════════
# 11. RESTRICCIONES DE SEGURIDAD RGPD
# ═══════════════════════════════════════════════════════════
add_heading('11. Restricciones de Seguridad RGPD', 1, page_break_before=True)

add_body(
    'Wiki_CODANOR está diseñado para garantizar el cumplimiento del RGPD (Reglamento General '
    'de Protección de Datos) y la ENS (Esquema Nacional de Seguridad). La arquitectura asegura '
    'que los documentos privados nunca abandonen la red local corporativa.'
)

add_danger(
    'Documentos PRIVADO — Nunca salen de la red local',
    'Los documentos clasificados como PRIVADO (expedientes de clientes, datos personales, '
    'contratos confidenciales, actas con información sensible) DEBEN ingestarse ÚNICAMENTE '
    'usando modelos Ollama locales. NUNCA usar OpenRouter, Groq, OpenAI u otros proveedores '
    'externos cuando se trabaje con documentos privados. El texto del documento se envía '
    'al LLM para generar la respuesta RAG.'
)

add_heading('Medidas de seguridad implementadas', 2)
add_bullet('Open WebUI escucha solo en localhost:3000 — no expone el puerto en la red LAN '
           'a menos que se configure explícitamente en docker-compose.yml.', 'Acceso restringido: ')
add_bullet('Ollama (nativo macOS) escucha en localhost:11434 por defecto — '
           'sin acceso desde otros equipos de la red.', 'Ollama sin LAN: ')
add_bullet('Los embeddings se almacenan en vectordb/ (disco local) — '
           'no se sincronizan con ningún servicio en la nube.', 'Embeddings locales: ')
add_bullet('Sin telemetría — Open WebUI puede configurarse sin enviar datos de uso '
           'a los servidores del proveedor (WEBUI_SECRET_KEY y ENABLE_TELEMETRY=false).', 'Sin telemetría: ')
add_bullet('Autenticación obligatoria — todos los accesos a la interfaz requieren login '
           'con usuario y contraseña.', 'Autenticación: ')

add_heading('Clasificación de documentos', 2)
add_generic_table(
    headers=['Clasificación', 'Descripción', 'Modo RAG permitido', 'Ejemplo'],
    rows=[
        ['PÚBLICO', 'Normativa pública, guías CCN, estándares ISO',
         'Ollama local O proveedores externos', 'Guía CCN-STIC 804, ISO 27001:2022'],
        ['INTERNO', 'Documentación interna no sensible, plantillas',
         'Ollama local O proveedores externos', 'Plantillas de política, procedimientos genéricos'],
        ['CONFIDENCIAL', 'Documentos de proyecto, actas generales',
         'SOLO Ollama local', 'Actas de reunión, entregables de consultoría'],
        ['PRIVADO', 'Datos personales, expedientes de clientes',
         'SOLO Ollama local — NUNCA externo', 'Registros de tratamiento, contratos con DPIs'],
    ],
    col_widths=[2.5, 4.5, 4.0, 5.0],
    zebra=True
)

add_callout(
    'Configuración para uso exclusivamente local (máxima privacidad)',
    'Para garantizar que NINGUNA consulta sale al exterior, no configurar ningún proveedor '
    'externo (OpenRouter, Groq, OpenAI) en "Connexions". Con solo Ollama activo, '
    'el sistema opera en modo completamente offline — sin internet.',
    fill=HEX_LIGHTGRN, title_color=ACCENT, icon='🔒'
)


# ═══════════════════════════════════════════════════════════
# 12. MANTENIMIENTO
# ═══════════════════════════════════════════════════════════
add_heading('12. Mantenimiento', 1, page_break_before=True)

add_body('Esta sección describe las operaciones de mantenimiento habituales del sistema '
         'Wiki_CODANOR: parada y arranque, actualizaciones, backup y revisión de logs.')

add_heading('12.1. Operaciones de contenedor Docker', 2)
add_generic_table(
    headers=['Operación', 'Comando', 'Descripción'],
    rows=[
        ['Arrancar', 'docker compose up -d', 'Inicia el contenedor en segundo plano'],
        ['Parar', 'docker compose stop', 'Detiene el contenedor (datos conservados)'],
        ['Parar y eliminar', 'docker compose down', 'Elimina el contenedor (volúmenes conservados)'],
        ['Reiniciar', 'docker compose restart', 'Reinicia el contenedor sin perder datos'],
        ['Ver logs en tiempo real', 'docker compose logs -f', 'Muestra la salida del contenedor'],
        ['Ver logs (últimas 100 líneas)', 'docker compose logs --tail=100', 'Útil para diagnóstico'],
        ['Estado del contenedor', 'docker ps | grep wiki', 'Muestra estado y puertos activos'],
    ],
    col_widths=[3.5, 5.5, 7.0],
    zebra=True
)

add_heading('12.2. Actualizar la imagen de Open WebUI', 2)
add_body('Para actualizar Open WebUI a la última versión disponible:')
add_code_block(
    '# 1. Navegar al directorio del proyecto\n'
    'cd ~/Proyectos/Wiki_CODANOR\n\n'
    '# 2. Descargar la nueva imagen\n'
    'docker compose pull\n\n'
    '# 3. Recrear el contenedor con la nueva imagen\n'
    'docker compose up -d --force-recreate\n\n'
    '# Los datos en vectordb/ y el volumen de Open WebUI se conservan.'
)

add_heading('12.3. Backup de Knowledge Bases', 2)
add_body('El backup de las Knowledge Bases se reduce a copiar el directorio vectordb/:')
add_code_block(
    '# Backup del directorio vectordb/ (ChromaDB)\n'
    'cp -r ~/Proyectos/Wiki_CODANOR/vectordb/ ~/Backups/wiki_vectordb_$(date +%Y%m%d)/\n\n'
    '# Backup completo (vectordb + configuración docker-compose)\n'
    'tar -czf ~/Backups/wiki_codanor_$(date +%Y%m%d).tar.gz \\\n'
    '  ~/Proyectos/Wiki_CODANOR/vectordb/ \\\n'
    '  ~/Proyectos/Wiki_CODANOR/docker-compose.yml'
)

add_callout(
    'Frecuencia de backup recomendada',
    'Realizar backup del directorio vectordb/ cada vez que se ingestent documentos nuevos. '
    'La configuración de usuarios y chats de Open WebUI se almacena en el volumen Docker '
    '"wiki-openwebui-data" — hacer también backup con: '
    'docker run --rm -v wiki-openwebui-data:/data alpine tar czf - /data > openwebui_data.tar.gz',
    fill=HEX_LIGHTBG, title_color=PRIMARY, icon='💾'
)

add_heading('12.4. Actualizar modelos Ollama', 2)
add_code_block(
    '# Actualizar todos los modelos instalados\n'
    'ollama pull qwen2.5-coder:14b\n'
    'ollama pull qwen3:8b\n'
    'ollama pull llama3.1:latest\n'
    'ollama pull gemma3:4b\n'
    'ollama pull nomic-embed-text\n\n'
    '# Ver espacio usado por modelos\n'
    'ollama list\n\n'
    '# Eliminar un modelo que ya no se usa\n'
    'ollama rm nombre-del-modelo:tag'
)


# ═══════════════════════════════════════════════════════════
# 13. SOLUCIÓN DE PROBLEMAS
# ═══════════════════════════════════════════════════════════
add_heading('13. Solución de Problemas', 1, page_break_before=True)

add_body('Esta sección recoge los errores más frecuentes y sus soluciones. '
         'Si el problema persiste, revisar los logs completos con: '
         'docker compose logs -f (desde ~/Proyectos/Wiki_CODANOR/).')

add_generic_table(
    headers=['Error / Síntoma', 'Causa probable', 'Solución'],
    rows=[
        ['Cannot connect to the Docker daemon',
         'Docker Desktop no está en ejecución',
         'Abrir Docker Desktop y esperar a que aparezca la ballena en la barra de menú'],
        ['http://localhost:3000 no carga (ERR_CONNECTION_REFUSED)',
         'El contenedor no está activo',
         'Ejecutar: docker compose up -d y verificar con docker ps'],
        ['El contenedor aparece como "Restarting"',
         'Error de configuración o falta de recursos',
         'Revisar logs: docker compose logs -f. Comprueba que vectordb/ tiene permisos de escritura'],
        ['No aparecen modelos en el selector de chat',
         'Ollama no está ejecutándose o la URL es incorrecta',
         'Ejecutar: ollama serve (si no está como servicio). Verificar URL en Connexions: http://host.docker.internal:11434'],
        ['Error al ingestar documento: "Processing failed"',
         'nomic-embed-text no está descargado o PDF protegido',
         'Ejecutar: ollama pull nomic-embed-text. Verificar que el PDF no tiene contraseña'],
        ['RAG no encuentra información relevante',
         'El documento no está ingestado en la KB o pregunta muy genérica',
         'Verificar que el documento aparece en la KB con chunks > 0. Formular pregunta más específica'],
        ['Respuesta del LLM muy lenta (>2 minutos)',
         'Modelo demasiado grande para la RAM disponible, se usa swap',
         'Cambiar a gemma3:4b (más ligero) o cerrar otras aplicaciones pesadas'],
        ['Error 401 con OpenRouter / Groq',
         'API Key incorrecta o expirada',
         'Regenerar la API Key en el panel del proveedor y actualizar en Connexions'],
        ['Error 429 con OpenRouter / Groq',
         'Límite de cuota gratuita alcanzado',
         'Esperar al reset de cuota (suele ser cada hora/día) o cambiar de proveedor. Usar Ollama local'],
        ['Los documentos RAG no se actualizan tras re-ingestar',
         'Caché de embeddings del documento anterior',
         'En la KB → seleccionar el documento → botón de eliminar → re-ingestar el nuevo fichero'],
        ['Open WebUI pide login tras reiniciar',
         'La sesión expiró o el volumen de datos fue eliminado',
         'Login normal. Si la cuenta no existe, el volumen fue eliminado — recrear cuenta admin'],
        ['vectordb/ ocupa demasiado espacio',
         'Muchos documentos ingestados o documentos grandes',
         'Eliminar documentos de las KBs que ya no se usen. Cada eliminación limpia sus embeddings'],
    ],
    col_widths=[4.0, 4.5, 7.5],
    zebra=True
)

add_heading('Comandos de diagnóstico rápido', 2)
add_code_block(
    '# Estado completo del sistema\n'
    'docker ps -a | grep wiki\n\n'
    '# Logs recientes (últimas 50 líneas)\n'
    'cd ~/Proyectos/Wiki_CODANOR && docker compose logs --tail=50\n\n'
    '# Verificar Ollama responde\n'
    'curl -s http://localhost:11434/api/version\n\n'
    '# Listar modelos disponibles via API\n'
    'curl -s http://localhost:11434/api/tags | python3 -m json.tool\n\n'
    '# Verificar que Open WebUI ve a Ollama desde el contenedor\n'
    'docker exec wiki-codanor curl -s http://host.docker.internal:11434/api/version\n\n'
    '# Espacio en disco usado por vectordb\n'
    'du -sh ~/Proyectos/Wiki_CODANOR/vectordb/'
)

add_spacer(10)

# Nota final
add_callout(
    'Soporte y documentación adicional',
    'Para consultas técnicas sobre Open WebUI: https://docs.openwebui.com\n'
    'Para consultas sobre Ollama: https://ollama.com/library\n'
    'Para incidencias internas: crear un tiquet en la Plataforma CODANOR (módulo Tiquets).',
    fill=HEX_LIGHTBG, title_color=PRIMARY, icon='📚'
)


# ─────────────────────────────────────────────────────────
# GUARDAR EL DOCUMENTO
# ─────────────────────────────────────────────────────────
doc.save(OUT_PATH)
print(f'✓ Documento generado en:\n  {OUT_PATH}')
