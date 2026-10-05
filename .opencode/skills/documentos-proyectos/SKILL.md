---
name: documentos-proyectos
description: >
  Usar cuando el usuario pide crear documentos corporativos CODANOR (HTML, .docx o .md)
  con plantilla estandarizada. Activa la plantilla con branding CODANOR, colores WCAG AA,
  portada fullscreen, TOC sticky, cabecera fija y pie de página. Usar SOLO para documentos
  corporativos CODANOR — no para código ni configuración de herramientas.
  Palabras clave: informe, manual, guía, propuesta, documento, corporativo, CODANOR, html, docx.
---


Crea un documento corporativo CODANOR siguiendo la plantilla estandarizada. Sigue estos pasos:

## PASO 1 — Recoger parámetros

Solicita al usuario (o extráelos del contexto si los ha proporcionado):

- **titulo**: Título principal del documento
- **subtitulo**: Descripción breve de una línea
- **tipo**: Manual | Informe | Propuesta | Guía | Documentación técnica | Changelog | README | Wiki
- **version**: Versión del documento (default: `v1.0`)
- **fecha**: Fecha en formato DD/MM/YYYY (default: fecha actual)
- **autor**: Nombre del autor
- **ruta_guardado**: Ruta absoluta donde se guardará el archivo
- **clasificacion**: Clasificación del documento (default: `Documento interno — Uso exclusivo CODANOR`)
- **secciones**: Lista de secciones de contenido específicas del documento
- **formato**: HTML | DOCX | MD | HTML+DOCX (ver tabla de selección automática abajo)

## PASO 2 — Seleccionar formato automáticamente

Si el usuario no especifica formato, aplica esta tabla:

| Tipo de documento | Formato |
|---|---|
| Manual, Informe, Propuesta, Guía | HTML + script Python .docx |
| Documentación técnica, README, Changelog, Wiki | .md |
| Indicado explícitamente por el usuario | El indicado |

## PASO 3 — Generar el documento

Según el formato seleccionado, aplica la plantilla correspondiente de las secciones siguientes.

---

# PLANTILLA A — HTML CORPORATIVO CODANOR

Genera un archivo `.html` completo y autónomo. Usa EXACTAMENTE esta estructura CSS y HTML como base, sustituyendo los marcadores `{{VARIABLE}}`.

**Reglas obligatorias:**
- La cabecera fija aparece en TODAS las páginas (posición sticky)
- El pie de página aparece al final del documento y en `@media print` en cada página
- El TOC es una lista numerada con enlaces internos ancla (`#seccion-N`)
- Cada sección tiene `id="seccion-N"` donde N es el número de sección
- Los colores cumplen WCAG AA (ratio mínimo 4.5:1 para texto normal)
- NO usar `color:#f39c12` sobre fondo blanco — usar `#b7770d` en su lugar
- NO usar texto `#aaaaaa` sobre blanco — usar `#6b6b7b` en su lugar
- NO usar texto blanco sobre `#f39c12` — usar texto `#1a1a2e` en su lugar
- NO usar texto blanco sobre `#12A79D` en badges pequeños — usar texto `#1a1a2e`

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{TITULO}} — CODANOR</title>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;600;700&family=Nunito+Sans:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    /* ─── TOKENS DE COLOR (WCAG AA garantizado) ─── */
    :root {
      --primary:        #178DC2;
      --primary-dark:   #1275A3;
      --primary-light:  #e8f4fa;
      --accent:         #12A79D;
      --accent-dark:    #0d7a71;
      --accent-light:   #e6f7f6;
      --dark:           #1a1a2e;
      --gray-900:       #2d2d44;
      --gray-700:       #4a4a5a;
      --gray-600:       #6b6b7b;  /* corregido: era #aaa, ratio 5.5 sobre blanco */
      --gray-500:       #7a7a8a;
      --gray-300:       #c4c4d0;
      --gray-100:       #f0f0f5;
      --white:          #ffffff;
      --warning-text:   #b7770d;  /* corregido: era #f39c12, ratio 4.5 sobre blanco */
      --warning-bg:     #fef9e7;
      --warning-dark:   #7d6608;  /* para texto sobre --warning-bg, ratio 5.3 */
      --danger-text:    #922b21;
      --danger-bg:      #fdedec;
      --success-text:   #0e7a72;
      --success-bg:     #e6f7f6;
      --info-text:      #1275A3;
      --info-bg:        #e8f4fa;
    }

    /* ─── RESET Y BASE ─── */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Nunito Sans', sans-serif;
      font-size: 16px;
      line-height: 1.7;
      color: var(--gray-700);
      background: var(--gray-100);
    }

    /* ─── CABECERA FIJA ─── */
    .page-header {
      position: sticky;
      top: 0;
      z-index: 100;
      background: var(--white);
      border-bottom: 3px solid var(--primary);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0.6rem 2rem;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .page-header-brand {
      display: flex;
      align-items: center;
      gap: 0.8rem;
    }
    .page-header-logo {
      font-family: 'Poppins', sans-serif;
      font-size: 1rem;
      font-weight: 700;
      color: var(--primary);
      letter-spacing: -0.5px;
    }
    .page-header-title {
      font-family: 'Poppins', sans-serif;
      font-size: 0.82rem;
      font-weight: 600;
      color: var(--primary-dark);
    }
    .page-header-meta {
      font-family: 'Poppins', sans-serif;
      font-size: 0.75rem;
      color: var(--gray-500);
    }

    /* ─── LAYOUT PRINCIPAL ─── */
    .layout {
      display: flex;
      min-height: calc(100vh - 56px);
    }

    /* ─── SIDEBAR TOC ─── */
    .sidebar {
      width: 260px;
      min-width: 260px;
      background: var(--white);
      border-right: 1px solid var(--gray-300);
      padding: 1.5rem 0;
      position: sticky;
      top: 56px;
      height: calc(100vh - 56px);
      overflow-y: auto;
    }
    .sidebar-label {
      font-family: 'Poppins', sans-serif;
      font-size: 0.65rem;
      font-weight: 600;
      color: var(--gray-500);
      text-transform: uppercase;
      letter-spacing: 0.8px;
      padding: 0 1.2rem;
      margin-bottom: 0.5rem;
    }
    .sidebar nav a {
      display: block;
      font-size: 0.88rem;
      color: var(--gray-700);
      text-decoration: none;
      padding: 0.35rem 1.2rem;
      border-left: 3px solid transparent;
      transition: all 0.15s;
    }
    .sidebar nav a:hover,
    .sidebar nav a.active {
      color: var(--primary);
      background: var(--primary-light);
      border-left-color: var(--primary);
    }
    .sidebar nav a.toc-sub {
      font-size: 0.82rem;
      padding-left: 2rem;
      color: var(--gray-700);
    }

    /* ─── CONTENIDO PRINCIPAL ─── */
    .main-content {
      flex: 1;
      padding: 0;
      min-width: 0;
    }

    /* ─── PORTADA ─── */
    .cover {
      background: var(--dark);
      color: var(--white);
      padding: 5rem 4rem 4rem;
      position: relative;
      overflow: hidden;
      page-break-after: always;
    }
    .cover::before {
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 5px;
      background: linear-gradient(90deg, var(--primary), var(--accent));
    }
    .cover-logo {
      font-family: 'Poppins', sans-serif;
      font-size: 1.4rem;
      font-weight: 700;
      color: var(--primary);
      margin-bottom: 4rem;
    }
    .cover-type {
      font-family: 'Poppins', sans-serif;
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--accent);
      text-transform: uppercase;
      letter-spacing: 2px;
      margin-bottom: 1rem;
    }
    .cover-title {
      font-family: 'Poppins', sans-serif;
      font-size: 2.8rem;
      font-weight: 700;
      color: var(--white);
      line-height: 1.15;
      margin-bottom: 1rem;
    }
    .cover-subtitle {
      font-family: 'Poppins', sans-serif;
      font-size: 1.2rem;
      font-weight: 300;
      color: rgba(255,255,255,0.75);
      margin-bottom: 3rem;
    }
    .cover-meta {
      display: flex;
      gap: 2.5rem;
      flex-wrap: wrap;
    }
    .cover-meta-item .label {
      font-size: 0.68rem;
      color: rgba(255,255,255,0.5);
      text-transform: uppercase;
      letter-spacing: 0.8px;
      margin-bottom: 0.2rem;
    }
    .cover-meta-item .value {
      font-family: 'Poppins', sans-serif;
      font-size: 0.92rem;
      font-weight: 600;
      color: var(--white);
    }
    .cover-footer {
      margin-top: 4rem;
      padding-top: 1.5rem;
      border-top: 1px solid rgba(255,255,255,0.15);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .cover-footer .company {
      font-size: 0.82rem;
      color: rgba(255,255,255,0.6);
    }
    .cover-footer .classification {
      font-size: 0.72rem;
      font-style: italic;
      color: rgba(255,255,255,0.45);
    }

    /* ─── SECCIONES DE CONTENIDO ─── */
    .content-section {
      background: var(--white);
      margin: 2rem;
      border-radius: 8px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.06);
      padding: 2.5rem 3rem;
      page-break-inside: avoid;
    }
    .content-section.full-width {
      margin: 0;
      border-radius: 0;
      box-shadow: none;
      border-bottom: 1px solid var(--gray-300);
    }

    /* ─── CONTROL DE VERSIONES ─── */
    .version-control {
      background: var(--white);
      margin: 2rem;
      border-radius: 8px;
      padding: 2rem 3rem;
      border-left: 4px solid var(--primary);
    }
    .version-control h2 {
      font-family: 'Poppins', sans-serif;
      font-size: 1rem;
      font-weight: 600;
      color: var(--primary-dark);
      margin-bottom: 1rem;
    }

    /* ─── TIPOGRAFÍA HEADINGS ─── */
    h1 {
      font-family: 'Poppins', sans-serif;
      font-size: 1.9rem;
      font-weight: 700;
      color: var(--dark);
      margin-bottom: 1rem;
      padding-bottom: 0.5rem;
      border-bottom: 2px solid var(--primary-light);
    }
    h2 {
      font-family: 'Poppins', sans-serif;
      font-size: 1.4rem;
      font-weight: 600;
      color: var(--primary);
      margin-top: 2rem;
      margin-bottom: 0.75rem;
    }
    h3 {
      font-family: 'Poppins', sans-serif;
      font-size: 1.1rem;
      font-weight: 600;
      color: var(--gray-900);
      margin-top: 1.5rem;
      margin-bottom: 0.5rem;
    }
    h4 {
      font-family: 'Poppins', sans-serif;
      font-size: 0.95rem;
      font-weight: 600;
      color: var(--gray-700);
      margin-top: 1rem;
      margin-bottom: 0.4rem;
    }
    .section-number {
      font-family: 'Poppins', sans-serif;
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--primary);
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 0.4rem;
    }

    /* ─── PÁRRAFOS Y LISTAS ─── */
    p { margin-bottom: 0.85rem; font-size: 0.95rem; }
    ul, ol { padding-left: 1.5rem; margin-bottom: 0.85rem; }
    li { font-size: 0.95rem; margin-bottom: 0.3rem; }

    /* ─── TABLAS ─── */
    .table-wrapper { overflow-x: auto; margin: 1.2rem 0; }
    table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
    thead th {
      font-family: 'Poppins', sans-serif;
      font-size: 0.82rem;
      font-weight: 600;
      color: var(--white);
      background: var(--primary-dark);  /* #1275A3 — ratio 4.6 sobre blanco */
      padding: 0.65rem 0.9rem;
      text-align: left;
      white-space: nowrap;
    }
    tbody td {
      padding: 0.6rem 0.9rem;
      border-bottom: 1px solid var(--gray-300);
      color: var(--gray-700);
      vertical-align: top;
    }
    tbody tr:hover td { background: var(--primary-light); }
    tbody tr:nth-child(even) td { background: #f8f8fb; }
    tbody tr:nth-child(even):hover td { background: var(--primary-light); }
    td code {
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.78rem;
      color: var(--primary-dark);
      background: var(--gray-100);
      padding: 0.1rem 0.3rem;
      border-radius: 3px;
    }

    /* ─── CÓDIGO ─── */
    code {
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.83rem;
      color: var(--primary-dark);
      background: var(--gray-100);
      padding: 0.15rem 0.4rem;
      border-radius: 4px;
    }
    pre {
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.82rem;
      background: var(--dark);
      color: #e0e0e0;
      padding: 1.2rem 1.5rem;
      border-radius: 6px;
      overflow-x: auto;
      line-height: 1.6;
      margin: 1rem 0;
    }
    pre code { color: inherit; background: none; padding: 0; font-size: inherit; }

    /* ─── ALERTAS / CALLOUTS ─── */
    .alert {
      padding: 0.9rem 1.1rem;
      border-radius: 6px;
      margin: 1rem 0;
      font-size: 0.9rem;
      border-left: 4px solid;
    }
    .alert-title {
      font-family: 'Poppins', sans-serif;
      font-weight: 600;
      margin-bottom: 0.3rem;
    }
    .alert-info    { background: var(--info-bg);    border-color: var(--primary);      color: var(--info-text); }
    .alert-warning { background: var(--warning-bg); border-color: var(--warning-text); color: var(--warning-dark); }
    .alert-danger  { background: var(--danger-bg);  border-color: var(--danger-text);  color: var(--danger-text); }
    .alert-success { background: var(--success-bg); border-color: var(--accent);       color: var(--success-text); }

    /* ─── BADGES ─── */
    .badge {
      display: inline-block;
      font-family: 'Poppins', sans-serif;
      font-size: 0.68rem;
      font-weight: 600;
      padding: 0.15rem 0.5rem;
      border-radius: 3px;
      letter-spacing: 0.3px;
    }
    .badge-primary { color: var(--primary-dark);  background: var(--primary-light); }
    .badge-accent  { color: var(--accent-dark);   background: var(--accent-light); }
    .badge-success { color: var(--success-text);  background: var(--success-bg); }
    .badge-warning { color: var(--warning-dark);  background: var(--warning-bg); }  /* corregido */
    .badge-danger  { color: var(--danger-text);   background: var(--danger-bg); }
    .badge-dark    { color: var(--white);         background: var(--gray-900); }
    .badge-new     { color: var(--dark);          background: var(--accent-light); }  /* corregido: texto oscuro */

    /* ─── STATUS CELLS ─── */
    .st-ok   { color: #0e7a72; background: #e6f7f6; padding: 0.15rem 0.5rem; border-radius: 3px; font-size: 0.8rem; font-weight: 600; }
    .st-warn { color: var(--warning-dark); background: var(--warning-bg); padding: 0.15rem 0.5rem; border-radius: 3px; font-size: 0.8rem; font-weight: 600; }
    .st-fail { color: var(--danger-text);  background: var(--danger-bg);  padding: 0.15rem 0.5rem; border-radius: 3px; font-size: 0.8rem; font-weight: 600; }
    .st-na   { color: var(--gray-700);    background: var(--gray-100);   padding: 0.15rem 0.5rem; border-radius: 3px; font-size: 0.8rem; font-weight: 600; }

    /* ─── PIE DE PÁGINA ─── */
    .doc-footer {
      background: var(--white);
      border-top: 3px solid var(--primary);
      padding: 1.2rem 2rem;
      display: grid;
      grid-template-columns: 1fr auto 1fr;
      align-items: center;
      gap: 1rem;
      margin-top: 2rem;
    }
    .doc-footer .footer-left   { font-size: 0.78rem; color: var(--gray-700); font-weight: 600; }
    .doc-footer .footer-center { font-size: 0.72rem; color: var(--gray-600); font-style: italic; text-align: center; }
    .doc-footer .footer-right  { font-size: 0.72rem; color: var(--gray-600); text-align: right; }
    .doc-footer .footer-path   { font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: var(--gray-600); margin-top: 0.2rem; }

    /* ─── BOTÓN IMPRIMIR ─── */
    .btn-print {
      position: fixed;
      bottom: 1.5rem;
      right: 1.5rem;
      background: var(--primary);
      color: var(--white);
      border: none;
      border-radius: 6px;
      padding: 0.6rem 1.1rem;
      font-family: 'Poppins', sans-serif;
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
      box-shadow: 0 2px 8px rgba(23,141,194,0.35);
      transition: background 0.15s;
      z-index: 200;
    }
    .btn-print:hover { background: var(--primary-dark); }

    /* ─── GLOSARIO ─── */
    .glossary-term { font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: var(--primary-dark); font-weight: 500; }

    /* ─── PRINT ─── */
    @media print {
      .sidebar, .page-header, .btn-print { display: none !important; }
      .main-content { padding: 0; }
      .content-section { margin: 0; box-shadow: none; border-radius: 0; page-break-inside: avoid; }
      body { font-size: 10pt; background: white; }
      pre { font-size: 8pt; }
      table { font-size: 8pt; }
      .cover { page-break-after: always; }
      .doc-footer {
        position: fixed;
        bottom: 0; left: 0; right: 0;
        border-top: 2px solid var(--primary);
        background: white;
        padding: 0.5rem 1.5rem;
        font-size: 8pt;
      }
    }

    /* ─── RESPONSIVE ─── */
    @media (max-width: 900px) {
      .sidebar { display: none; }
      .cover-title { font-size: 2rem; }
      .content-section { margin: 1rem; padding: 1.5rem; }
    }
  </style>
</head>
<body>

  <!-- CABECERA FIJA -->
  <header class="page-header">
    <div class="page-header-brand">
      <span class="page-header-logo">(CODANOR 50)</span>
      <span class="page-header-title">{{TITULO}}</span>
    </div>
    <span class="page-header-meta">{{VERSION}} · {{FECHA}}</span>
  </header>

  <div class="layout">

    <!-- SIDEBAR TOC -->
    <aside class="sidebar">
      <div class="sidebar-label">Índice de contenidos</div>
      <nav>
        <a href="#portada">Portada</a>
        <a href="#versiones">Control de versiones</a>
        <a href="#seccion-1">1. Introducción</a>
        <a href="#seccion-2">2. Alcance</a>
        <!-- AÑADIR AQUÍ EL RESTO DE SECCIONES SEGÚN EL DOCUMENTO -->
        <!-- <a href="#seccion-N" class="toc-sub">N.X Subsección</a> -->
        <a href="#glosario">Glosario</a>
      </nav>
    </aside>

    <!-- CONTENIDO -->
    <main class="main-content">

      <!-- PORTADA -->
      <div class="cover" id="portada">
        <div class="cover-logo">(CODANOR 50)</div>
        <div class="cover-type">{{TIPO}}</div>
        <h1 class="cover-title">{{TITULO}}</h1>
        <p class="cover-subtitle">{{SUBTITULO}}</p>
        <div class="cover-meta">
          <div class="cover-meta-item">
            <div class="label">Versión</div>
            <div class="value">{{VERSION}}</div>
          </div>
          <div class="cover-meta-item">
            <div class="label">Fecha</div>
            <div class="value">{{FECHA}}</div>
          </div>
          <div class="cover-meta-item">
            <div class="label">Autor</div>
            <div class="value">{{AUTOR}}</div>
          </div>
        </div>
        <div class="cover-footer">
          <span class="company">CODANOR — Jafa, S.L. — Barcelona, Catalunya</span>
          <span class="classification">{{CLASIFICACION}}</span>
        </div>
      </div>

      <!-- CONTROL DE VERSIONES -->
      <div class="version-control" id="versiones">
        <h2>Control de versiones</h2>
        <div class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Versión</th><th>Fecha</th><th>Autor</th><th>Descripción del cambio</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code>{{VERSION}}</code></td>
                <td>{{FECHA}}</td>
                <td>{{AUTOR}}</td>
                <td>Versión inicial</td>
              </tr>
              <!-- AÑADIR FILAS POR CADA REVISIÓN -->
            </tbody>
          </table>
        </div>
      </div>

      <!-- SECCIÓN 1 — INTRODUCCIÓN -->
      <div class="content-section" id="seccion-1">
        <div class="section-number">Sección 1</div>
        <h1>Introducción y objeto</h1>
        <p>{{DESCRIPCION_INTRODUCCION}}</p>
        <div class="alert alert-info">
          <div class="alert-title">Audiencia</div>
          {{AUDIENCIA}}. {{CLASIFICACION}}. {{VERSION}} — {{FECHA}}
        </div>
      </div>

      <!-- SECCIÓN 2 — ALCANCE -->
      <div class="content-section" id="seccion-2">
        <div class="section-number">Sección 2</div>
        <h1>Alcance</h1>
        <p>{{DESCRIPCION_ALCANCE}}</p>
        <h2>Dentro del alcance</h2>
        <ul>
          <!-- LISTAR AQUÍ LO QUE CUBRE EL DOCUMENTO -->
        </ul>
        <h2>Fuera del alcance</h2>
        <ul>
          <!-- LISTAR AQUÍ LO QUE NO CUBRE -->
        </ul>
      </div>

      <!-- SECCIONES DE CONTENIDO (N+1 secciones según el documento) -->
      <!-- REPETIR ESTE BLOQUE POR CADA SECCIÓN INDICADA EN LOS PARÁMETROS -->
      <div class="content-section" id="seccion-3">
        <div class="section-number">Sección 3</div>
        <h1>{{TITULO_SECCION_3}}</h1>
        <!-- CONTENIDO DE LA SECCIÓN -->
      </div>

      <!-- GLOSARIO (siempre última sección antes del pie) -->
      <div class="content-section" id="glosario">
        <div class="section-number">Glosario</div>
        <h1>Glosario de términos</h1>
        <div class="table-wrapper">
          <table>
            <thead>
              <tr><th>Término / Clave</th><th>Definición</th></tr>
            </thead>
            <tbody>
              <!-- AÑADIR FILAS: <tr><td class="glossary-term">término</td><td>definición</td></tr> -->
            </tbody>
          </table>
        </div>
      </div>

    </main>
  </div>

  <!-- PIE DE PÁGINA -->
  <footer class="doc-footer">
    <div class="footer-left">CODANOR — Jafa, S.L. — Barcelona, Catalunya</div>
    <div class="footer-center">{{CLASIFICACION}}</div>
    <div class="footer-right">
      {{VERSION}} · {{FECHA}}
      <div class="footer-path">{{RUTA_GUARDADO}}</div>
    </div>
  </footer>

  <!-- BOTÓN IMPRIMIR / PDF -->
  <button class="btn-print" onclick="window.print()">Imprimir / PDF</button>

  <!-- TOC HIGHLIGHT ACTIVO -->
  <script>
    const sections = document.querySelectorAll('[id^="seccion-"], #portada, #versiones, #glosario');
    const navLinks = document.querySelectorAll('.sidebar nav a');
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          navLinks.forEach(a => a.classList.remove('active'));
          const active = document.querySelector(`.sidebar nav a[href="#${entry.target.id}"]`);
          if (active) active.classList.add('active');
        }
      });
    }, { threshold: 0.3 });
    sections.forEach(s => observer.observe(s));
  </script>

</body>
</html>
```

---

# PLANTILLA B — SCRIPT PYTHON (.docx)

Genera un archivo `.py` con este nombre: `generar_{{NOMBRE_ARCHIVO}}.py`. El script usa `python-docx` para crear el equivalente Word del documento HTML.

**Reglas obligatorias del script:**
- Importar: `from docx import Document`, `from docx.shared import Pt, Cm, RGBColor`, `from docx.enum.text import WD_ALIGN_PARAGRAPH`, `from docx.oxml.ns import qn`
- Márgenes A4: top=2cm, bottom=2cm, left=2.5cm, right=2cm
- Colores corporativos como `RGBColor`: primary=`(23,141,194)`, dark=`(26,26,46)`, gray700=`(74,74,90)`
- Fuentes: títulos `Poppins` (si disponible, si no `Calibri`), cuerpo `Calibri`
- Cabecera: logo CODANOR + título del doc + versión (3 columnas)
- Pie: empresa (izq) + clasificación (centro) + versión/ruta (der)
- Control de versiones: tabla con 4 columnas (Versión | Fecha | Autor | Descripción)
- Secciones numeradas con Heading1/Heading2/Heading3
- Glosario: tabla 2 columnas al final
- Al final del script: `doc.save('{{NOMBRE_ARCHIVO}}.docx')` y `print('Generado: {{NOMBRE_ARCHIVO}}.docx')`

Estructura del script:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador Word — {{TITULO}}
CODANOR — Jafa, S.L.
{{VERSION}} · {{FECHA}}
Ruta: {{RUTA_GUARDADO}}
"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import datetime

# ─── COLORES CORPORATIVOS ───
C_PRIMARY    = RGBColor(23, 141, 194)   # #178DC2
C_PRIMARY_DK = RGBColor(18, 117, 163)   # #1275A3
C_DARK       = RGBColor(26, 26, 46)     # #1a1a2e
C_GRAY_700   = RGBColor(74, 74, 90)     # #4a4a5a
C_GRAY_600   = RGBColor(107, 107, 123)  # #6b6b7b
C_WHITE      = RGBColor(255, 255, 255)  # #ffffff
C_ACCENT     = RGBColor(18, 167, 157)   # #12A79D

# ─── HELPERS ───
def set_cell_bg(cell, hex_color):
    """Establece el color de fondo de una celda."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def add_header_row(table, headers, bg='1275A3'):
    """Añade fila de cabecera con fondo azul y texto blanco."""
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
    """Añade un heading numerado con estilo CODANOR."""
    h = doc.add_heading(f'{number}. {title}', level=level)
    h.runs[0].font.color.rgb = C_DARK if level == 1 else C_PRIMARY
    h.runs[0].font.name = 'Calibri'
    return h

# ─── DOCUMENTO ───
doc = Document()

# Márgenes A4
for section in doc.sections:
    section.page_height = Cm(29.7)
    section.page_width  = Cm(21.0)
    section.top_margin    = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin   = Cm(2.5)
    section.right_margin  = Cm(2.0)

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
run = p.add_run('{{TIPO}}'.upper())
run.font.name = 'Calibri'
run.font.size = Pt(9)
run.font.color.rgb = C_ACCENT
doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('{{TITULO}}')
run.font.name = 'Calibri'
run.font.size = Pt(24)
run.font.bold = True
run.font.color.rgb = C_DARK

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('{{SUBTITULO}}')
run.font.name = 'Calibri'
run.font.size = Pt(12)
run.font.color.rgb = C_GRAY_700

doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run(f'{{VERSION}} · {{FECHA}} · {{AUTOR}}')
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
run = p.add_run('{{CLASIFICACION}}')
run.font.name = 'Calibri'
run.font.size = Pt(8)
run.font.italic = True
run.font.color.rgb = C_GRAY_600

doc.add_page_break()

# ─── CONTROL DE VERSIONES ───
add_section_heading(doc, '', 'Control de versiones', level=1)
tver = doc.add_table(rows=2, cols=4)
tver.style = 'Table Grid'
add_header_row(tver, ['Versión', 'Fecha', 'Autor', 'Descripción del cambio'])
row = tver.rows[1].cells
row[0].text = '{{VERSION}}'
row[1].text = '{{FECHA}}'
row[2].text = '{{AUTOR}}'
row[3].text = 'Versión inicial'
doc.add_paragraph()

# ─── SECCIÓN 1 — INTRODUCCIÓN ───
add_section_heading(doc, 1, 'Introducción y objeto')
doc.add_paragraph('{{DESCRIPCION_INTRODUCCION}}')
doc.add_paragraph()

# ─── SECCIÓN 2 — ALCANCE ───
add_section_heading(doc, 2, 'Alcance')
doc.add_paragraph('{{DESCRIPCION_ALCANCE}}')
doc.add_paragraph()

# ─── SECCIONES DE CONTENIDO ───
# REPETIR add_section_heading() + contenido por cada sección del documento
# add_section_heading(doc, 3, '{{TITULO_SECCION_3}}')
# doc.add_paragraph('...')

# ─── GLOSARIO ───
add_section_heading(doc, 99, 'Glosario de términos')
tglos = doc.add_table(rows=2, cols=2)
tglos.style = 'Table Grid'
add_header_row(tglos, ['Término / Clave', 'Definición'])
# Añadir filas: cells = tglos.add_row().cells; cells[0].text='término'; cells[1].text='def'

# ─── PIE DE PÁGINA (todas las páginas) ───
from docx.oxml import OxmlElement
for section in doc.sections:
    footer = section.footer
    ft = footer.paragraphs[0]
    ft.clear()
    ft.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = ft.add_run('CODANOR — Jafa, S.L. — Barcelona, Catalunya  |  {{CLASIFICACION}}  |  {{VERSION}} · {{FECHA}}')
    run.font.name = 'Calibri'
    run.font.size = Pt(7)
    run.font.color.rgb = C_GRAY_600
    ft.add_run('\n')
    run2 = ft.add_run('{{RUTA_GUARDADO}}')
    run2.font.name = 'Courier New'
    run2.font.size = Pt(6)
    run2.font.color.rgb = C_GRAY_600

# ─── GUARDAR ───
output_path = '{{RUTA_GUARDADO}}/{{NOMBRE_ARCHIVO}}.docx'
doc.save(output_path)
print(f'Generado: {output_path}')
```

---

# PLANTILLA C — MARKDOWN (.md)

Genera un archivo `.md` con frontmatter YAML estandarizado y estructura de secciones numeradas. Úsala para documentación técnica, READMEs, changelogs, wikis y notas de versión.

**Reglas obligatorias:**
- El frontmatter YAML siempre encabeza el archivo (entre `---`)
- Todas las secciones van numeradas (1., 2., 3. ...)
- El glosario es siempre la última sección
- El pie de página es un bloque `---` con metadata al final del archivo
- Usar tablas Markdown para control de versiones y glosario
- Los bloques de código usan triple backtick con lenguaje especificado

```markdown
---
title: "{{TITULO}}"
subtitle: "{{SUBTITULO}}"
type: "{{TIPO}}"
version: "{{VERSION}}"
date: "{{FECHA}}"
author: "{{AUTOR}}"
project: "PLATAFORMA ISO/ENS — CODANOR"
classification: "{{CLASIFICACION}}"
path: "{{RUTA_GUARDADO}}"
---

# {{TITULO}}

> **CODANOR — Jafa, S.L. — Barcelona, Catalunya**
> {{VERSION}} · {{FECHA}} · {{CLASIFICACION}}

---

## Control de versiones

| Versión | Fecha | Autor | Descripción del cambio |
|---|---|---|---|
| {{VERSION}} | {{FECHA}} | {{AUTOR}} | Versión inicial |

---

## Índice

1. [Introducción y objeto](#1-introducción-y-objeto)
2. [Alcance](#2-alcance)
<!-- AÑADIR RESTO DE SECCIONES -->
N. [Glosario](#n-glosario)

---

## 1. Introducción y objeto

{{DESCRIPCION_INTRODUCCION}}

> **Audiencia:** {{AUDIENCIA}}
> **Clasificación:** {{CLASIFICACION}}

---

## 2. Alcance

{{DESCRIPCION_ALCANCE}}

**Dentro del alcance:**
- ...

**Fuera del alcance:**
- ...

---

<!-- REPETIR ESTE BLOQUE POR CADA SECCIÓN -->
## 3. {{TITULO_SECCION_3}}

...

---

## N. Glosario

| Término / Clave | Definición |
|---|---|
| `término` | Definición del término |

---

*CODANOR — Jafa, S.L. — Barcelona, Catalunya*
*{{CLASIFICACION}}*
*Ruta: `{{RUTA_GUARDADO}}`*
*Generado por OpenCode · {{FECHA}}*
```

---

# REGLAS DE NOMENCLATURA DE ARCHIVOS

Usa siempre el siguiente patrón para nombrar los archivos generados:

| Tipo | Patrón | Ejemplo |
|---|---|---|
| HTML | `NOMBRE-DOC-VXX.html` | `ARQUITECTURA-DB-V01.html` |
| Script Python | `generar_nombre-doc.py` | `generar_arquitectura-db.py` |
| Word generado | `NOMBRE-DOC-VXX.docx` | `ARQUITECTURA-DB-V01.docx` |
| Markdown | `nombre-doc.md` | `arquitectura-db.md` |

**Reglas:**
- HTML y DOCX: MAYÚSCULAS con guiones, sufijo `-VXX` (V01, V02...)
- Python: minúsculas con guiones bajos, prefijo `generar_`
- Markdown: minúsculas con guiones, sin versión en el nombre (el frontmatter YAML lleva la versión)
- Nunca usar espacios ni caracteres especiales en nombres de archivo

---

# CLASIFICACIÓN DE DOCUMENTOS POR FORMATO

Aplica esta tabla para decidir qué plantilla usar cuando el usuario no especifica formato:

| Tipo de documento | Plantilla A (HTML) | Plantilla B (.docx) | Plantilla C (.md) |
|---|---|---|---|
| Manual de usuario | SI | SI | NO |
| Informe técnico | SI | SI | NO |
| Propuesta formal | SI | SI | NO |
| Guía de configuración / migración | SI | SI | NO |
| Documentación técnica de código | NO | NO | SI |
| README de proyecto | NO | NO | SI |
| Changelog / notas de versión | NO | NO | SI |
| Wiki / base de conocimiento interna | NO | NO | SI |
| Instrucciones para agentes (AGENTS.md) | NO | NO | SI |
| Referencia de API / endpoints | NO | NO | SI |

---

# PALETA DE COLORES CORPORATIVA (WCAG AA)

Todos los colores de texto en documentos generados deben cumplir ratio mínimo 4.5:1 sobre su fondo. Usa siempre estos valores:

| Token | Hex | Uso | Ratio sobre blanco |
|---|---|---|---|
| `--primary` | `#178DC2` | Links, h2, bordes activos | 3.73 (solo texto grande ≥18px bold) |
| `--primary-dark` | `#1275A3` | Texto azul sobre blanco, th cabeceras | 4.57 PASS |
| `--dark` | `#1a1a2e` | H1, texto portada | 17.06 PASS |
| `--gray-900` | `#2d2d44` | H3, valores destacados | 13.37 PASS |
| `--gray-700` | `#4a4a5a` | Cuerpo de texto, td | 8.68 PASS |
| `--gray-600` | `#6b6b7b` | Pie de página, metadata | 5.54 PASS |
| `--warning-text` | `#b7770d` | Texto naranja sobre blanco | 4.52 PASS |
| `--warning-dark` | `#7d6608` | Texto sobre fondo amarillo claro | 5.27 PASS |
| `--danger-text` | `#922b21` | Texto rojo sobre fondo claro | 7.14 PASS |
| `--success-text` | `#0e7a72` | Texto verde sobre fondo claro | 4.70 PASS |
| `--info-text` | `#1275A3` | Texto azul sobre fondo info | 4.57 PASS |

**Combinaciones PROHIBIDAS (ratio < 3.0 — no usar en ningún documento):**
- `#f39c12` sobre blanco → usar `#b7770d`
- `#aaaaaa` sobre blanco → usar `#6b6b7b`
- Texto blanco sobre `#f39c12` → usar texto `#1a1a2e`
- Texto blanco sobre `#12A79D` en badges pequeños → usar texto `#1a1a2e`
- `#d68910` sobre `#fef9e7` → usar `#7d6608`
