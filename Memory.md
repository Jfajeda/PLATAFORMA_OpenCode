# Memory.md — PLATAFORMA_OpenCode
> Ultima actualizacion: 2026-10-28

## Estado actual

- **Fase**: Produccion / mantenimiento activo
- **Version**: Manual v3.0 (20 capitulos) + Manual IA Actas v1.0
- **Ultimo cambio significativo**: Documento `PENDIENTES-PLATAFORMA-V01.html` generado (2026-10-28) — 15 pendientes con prioridad, estado, pasos de mejora y dependencias
- **Issues abiertos**: 72 bugs de reliability + 3 security hotspots detectados por SonarCloud

## Infraestructura

| Elemento | Estado | Detalle |
|----------|--------|---------|
| Git | Si | rama principal |
| GitHub | Si | github.com/Jfajeda/PLATAFORMA_OpenCode |
| SonarCloud | Si | Security A, Reliability B, Maintainability A, 3.5% duplications |
| .gitignore | Si | Excluye .DS_Store, backups, __pycache__ |
| AGENTS.md | Si | Actualizado 2026-10-28 — Módulo SIG v1.0 + Módulo Capas Ciberseguridad v1.1.0 |
| PENDIENTES-PLATAFORMA-V01.html | Si | Informe seguimiento 15 pendientes — prioridad, estado, pasos mejora — 79 KB — 2026-10-28 |
| PROPAGATION_RULES.md | Si | 2026-10-01 — clasificación BASE/CLON/DIVERGENTE/PROPIO + workflows + script verificación ENS |
| opencode.json | Si | MCP SonarQube + instructions: AGENTS.md + PROPAGATION_RULES.md |
| Memory.md | Si | Este archivo |
| `.opencode/commands/documentos-proyectos.md` | Si | Skill plantilla documentos corporativos (HTML + .docx + .md) — 33 KB — 2026-10-05 |
| plataforma.db | Activa | **23 tablas**, WAL mode, 298 clientes, 36 proyectos |
| server.py | Activo | Puerto 5001, HOST 0.0.0.0, **5377 lineas**, **111 endpoints**, APP_DIRS incluye `capas-seguridad` |
| Ollama | Activo | localhost:11434, v0.35.1. Modelos: qwen2.5-coder:14b, qwen3:8b, llama3.1:latest, gemma3:4b |
| Wiki_CODANOR | Activa | Open WebUI :3000 (Docker), ChromaDB vectordb/, 10 KBs, Ollama + OpenRouter conectados |

## Componentes del proyecto

### PLATAFORMA_OpenCode-NEW

| Archivo | Descripcion | Version |
|---------|-------------|---------|
| Manual_OpenCode_Codanor.html | Manual v3.0, 20 capitulos | ~137 KB |
| Manual_IA_Actas_Codanor.html | Manual IA módulo actas v1.0, 10 secciones | ~99 KB |
| Manual_Seguimiento_Acta_Sintesis_IA-V02.html | Manual Acta y Síntesis con IA v2.0 — Groq por defecto, TOC sticky | ~60 KB |
| plataforma-seguimiento.html | Dashboard + Kanban + Tiquets + Config IA Corp | ~98 KB |
| analisis-codigo.html | Panel SonarCloud exportable, 5 pestanas | ~46 KB |
| plan-homogeneizacion-modulos.html | Plan de homogeneizacion (14 caps) | ~72 KB |
| homogeneizacion-proyectos.html | Dashboard homogeneizacion (5 pestanas) | ~46 KB |
| propuesta-herramienta-tiquets.html | Propuesta tecnica tiquets v1.2 | ~98 KB |
| backup-opencode.sh | Script backup NAS CODANOR (8 modos) | ~14 KB |
| PROPAGATION_RULES.md | Reglas propagación entre 9 apps — BASE/CLON/DIVERGENTE/PROPIO | commit 2026-10-01 |
| `.opencode/commands/documentos-proyectos.md` | Skill plantilla documentos corporativos (HTML + .docx + .md) | 33 KB — 2026-10-05 |
| **CAPAS-CIBERSEGURIDAD-V01.html** | **Propuesta técnica módulo Capas de Ciberseguridad** — portada, 10 secciones, tablas ENS/ISO27001/ISO42001 | **Oct 2026** |
| **SIG-MODULO-V01.html** | **Propuesta técnica módulo SIG** — 10 secciones, arquitectura, endpoints, correspondencias | **71 KB — Oct 2026** |
| **PENDIENTES-PLATAFORMA-V01.html** | **Informe de seguimiento de 15 pendientes activos** — prioridad, estado, archivos afectados, pasos de mejora, dependencias. 8 secciones por área temática + glosario | **79 KB — 2026-10-28** |

### Plataforma_Seguimiento_Proyectos/servidor/

| Archivo | Descripcion | Estado |
|---------|-------------|--------|
| server.py | Flask app: **111 endpoints** — Core + Tiquets + Wiki + LLM + Riesgos + EIPD + Sonar + SIG + **Capas** + Estáticos | **5377 lineas** |
| plataforma.db | SQLite WAL: **23 tablas** | Activa |
| migration_tiquets.sql | DDL standalone v1.0→v1.4 | 147 lineas |
| uploads/tiquets/ | Archivos adjuntos de tiquets (max 10 MB) | Excluido Git |
| uploads/wiki/ | Documentos wiki (PDF/DOCX/TXT) | Excluido Git |
| ARQUITECTURA_DB_SQLITE-V01.html | Documentacion BD actualizada V01 — 19 tablas, 86 endpoints | 58 KB |

### Plataforma_Seguimiento_Proyectos/capas-seguridad/ ← NUEVO 2026-10-21

| Archivo | Descripcion | Estado |
|---------|-------------|--------|
| `index.html` | SPA app standalone: 3 vistas + 2 modales | 15 KB |
| `js/data.js` | 11 capas, 50 controles (ENS+ISO27001+ISO42001), 178 herramientas base | 3540 líneas |
| `js/app.js` | Store LAN+localStorage, CRUD herramientas, diagrama SVG anillos, leyenda, informe HTML | ~1360 líneas |
| `css/styles.css` | Paleta CODANOR, responsive, SVG, modales | 24 KB |

### Plataforma_Seguimiento_Proyectos — 9 apps ISO/ENS (versiones actuales 2026-10-28)

| App | app_id | app.js | tiquets.js | phase2-*.js | llm.js |
|-----|--------|--------|------------|-------------|--------|
| ISO27001-SGSI | iso27001 | **v=20261021a** | v=20260829f | v=20261007b | v=20261007a |
| ENS-RD311-2022 | ens | **v=20261021a** | v=20260829f | v=20261007b | v=20261007a |
| ISO42001-SGIA | iso42001 | **v=20261021a** | v=20260829f | v=20261007b | v=20261007a |
| RGPD-LOPD-GDD | rgpd | v=20260923a | v=20260829f | v=20261007b | v=20261007a |
| ISO27701-SGP | iso27701 | v=20260904c | v=20260829f | v=20261007b | v=20261007a |
| ISO9001-SGQ_2015 | iso9001 | v=20260917a | v=20260829f | v=20261007b | v=20261007a |
| ISO14001-SGMA_2015 | iso14001 | v=20260904c | v=20260829f | v=20261007b | v=20261007a |
| ISO14001-SGMA_2026_NEW | iso14001-2026 | v=20260904c | v=20260829f | v=20261007b | v=20261007a |
| TISAX | tisax | v=20260904c | v=20260829f | v=20261007b | v=20261007a |

## Módulo Capas de Ciberseguridad (v1.1.0 — 2026-10-21/27)

### Arquitectura

App HTML standalone en `Plataforma_Seguimiento_Proyectos/capas-seguridad/`. Servida por Flask en `/capas-seguridad/`. Accesible desde el sidebar de ISO27001, ENS e ISO42001 con el enlace "🔒 Capas Ciberseguridad".

### Datos (data.js)

- **11 capas** concéntricas (exterior→interior): Sistemas IA (orden=0, morado) · Ubicación · Proveedores · Comunicaciones · Auxiliares/Soportes · Hardware · Aplicaciones · Personas externas · Personas internas · Servicios · Información (orden=10, más interior)
- **50 controles** con referencias ENS (mp.*, op.*), ISO 27001 (A.x.y) e ISO 42001 (A.x.y)
- **178 herramientas base** — 18 corporativas + 160 recomendaciones genéricas (extraídas de 12 CSVs de referencia)
- Tipo nuevo `'recomendacion'` — badge naranja `#e65100`

### Diagrama SVG

- Técnica: `stroke` en lugar de `fill` — cada anillo es independiente, no se tapa
- Leyenda lateral izquierda con color + nombre + descripción de cada capa
- Etiquetas distribuidas en arco superior (-155° → -25°)
- Clic en anillo o en leyenda → muestra controles + herramientas en panel derecho
- Título dinámico con `CAPAS_DATA.length`
- Bug corregido: `centerFill.style.pointerEvents = 'none'` → clic en Información funciona

### Persistencia (Store)

- **Primario**: Flask SQLite (`capas_herramientas` table, endpoint `/api/capas/herramientas`)
- **Fallback offline**: `localStorage` clave `codanor_capas_v1`
- Indicador topbar: `● LAN — SQLite` (verde) / `● Offline — localStorage` (naranja)
- Sync automático de herramientas base al servidor en el primer `load()`

### Endpoints API (5 rutas nuevas en server.py)

| Método | URL | Descripción |
|---|---|---|
| GET | `/api/capas/herramientas` | Lista todas las herramientas |
| POST | `/api/capas/herramientas` | Crear / upsert por id |
| PUT | `/api/capas/herramientas/<id>` | Actualizar |
| DELETE | `/api/capas/herramientas/<id>` | Eliminar (protege base) |
| POST | `/api/capas/herramientas/bulk` | Importación masiva |

### Tabla nueva en plataforma.db

`capas_herramientas` — id, nombre, url, logo (dataURL), tipo, descripcion, capas (JSON), controles (JSON), notas, activa, es_base, changelog (JSON), fecha_alta, updated_at

### Informe HTML (botón "📄 Informe")

- Portada con 6 KPIs (capas, controles, herramientas, corporativas, recomendaciones, % cobertura)
- TOC con enlaces a cada sección
- Sección 1: mapa de capas ordenado exterior→interior, tabla 5 columnas (ENS / ISO 27001 / ISO 42001 / Herramientas)
- Sección 2: catálogo completo 178 herramientas por tipo
- Sección 3: estadísticas de cobertura por capa con barras de progreso
- Branding CODANOR: Poppins + Nunito Sans, paleta `#1275A3`, badges coloreados

### Reglas críticas

1. **`pointer-events: none`** en `centerFill` y `centerText` del SVG — obligatorio para que el clic en el anillo Información funcione.
2. **Orden de capas**: `orden=0` = Sistemas IA (exterior, radio máximo). `orden=10` = Información (interior, radio mínimo). El SVG itera `sort((a,b)=>a.orden-b.orden)` para geometría.
3. **Técnica SVG**: `stroke` en `<circle fill="none">` — NO `fill` en círculos sólidos (provoca efecto de tapado).
4. **`capas-seguridad` en APP_DIRS**: registrado en `server.py` → accesible en `http://IP:5001/capas-seguridad/`.
5. **Sidebar**: el enlace usa `window.location.origin+'/capas-seguridad/'` — funciona en localhost y LAN sin hardcodear IP.

## Módulo SIG — Sistema Integrado de Gestión (v1.0 — 2026-10-20)

### Arquitectura

App HTML standalone en `Plataforma_Seguimiento_Proyectos/SIG-INTEGRACION/`. Servida por Flask en `/sig/`. Principio arquitectónico: **"Lo que es del proyecto SIG vive en el SIG. Lo que es de la norma vive en la norma."**

### Archivos del módulo

| Archivo | Rol | Líneas |
|---|---|---|
| `SIG-INTEGRACION/index.html` | SPA: router + layout + sidebar | ~250 |
| `SIG-INTEGRACION/js/app.js` | Router SPA, CRUD proyectos SIG, `NORMAS_META` (9 normas) | ~377 |
| `SIG-INTEGRACION/js/store.js` | Cliente API LAN-aware (`window.location.hostname`) | ~136 |
| `SIG-INTEGRACION/css/styles.css` | Paleta CODANOR morada (#5C35A0) para SIG | ~464 |
| `SIG-INTEGRACION/js/modules/sig-overview.js` | Dashboard progreso por norma + acceso directo | 127 |
| `SIG-INTEGRACION/js/modules/sig-meetings.js` | Reuniones unificadas cross-norma | 208 |
| `SIG-INTEGRACION/js/modules/sig-tasks.js` | Tareas unificadas cross-norma | 221 |
| `SIG-INTEGRACION/js/modules/sig-formacion.js` | Formación unificada cross-norma | 188 |
| `SIG-INTEGRACION/js/modules/sig-documents.js` | Documentos unificados cross-norma | 188 |
| `SIG-INTEGRACION/js/modules/sig-normas.js` | Gestión de normas miembro del SIG | 197 |
| `SIG-INTEGRACION/js/modules/sig-tiquets.js` | Vista tiquets integrada del SIG | 181 |
| `SIG-INTEGRACION/js/modules/sig-correspondencias.js` | Tabla pivot HLS + búsqueda + reload | 160 |

**Versión:** `v20261020a` — todos los archivos congelados a 2026-10-20.

### Endpoints API (14 rutas en server.py)

| Método | URL | Descripción |
|---|---|---|
| GET | `/api/sig/projects` | Listar proyectos SIG |
| POST | `/api/sig/projects` | Crear proyecto SIG |
| GET | `/api/sig/projects/<sig_id>` | Proyecto SIG completo |
| PUT | `/api/sig/projects/<sig_id>` | Actualizar proyecto SIG |
| DELETE | `/api/sig/projects/<sig_id>` | Eliminar proyecto SIG |
| GET/POST | `/api/sig/<sig_id>/phase/<phase>` | Datos de fase por SIG |
| GET | `/api/sig/<sig_id>/norma/<app_id>/phase/<phase>` | Datos norma-fase cruzados |
| GET | `/api/sig/<sig_id>/progress` | Progreso consolidado |
| GET/POST | `/api/sig/<sig_id>/tiquets` | Tiquets del SIG |
| GET | `/api/sig/correspondencias` | Tabla de correspondencias |
| GET | `/api/sig/correspondencias/status` | Estado carga de CSVs |
| POST | `/api/sig/correspondencias/reload` | Recarga CSVs desde disco |

**Rutas estáticas:** `GET /sig/` y `GET /sig/<path:filename>` → `SIG-INTEGRACION/` (con `no-cache` para `.js`).
**Variable:** `SIG_DIR = ROOT_DIR / 'SIG-INTEGRACION'` (fuera de `APP_DIRS`).

### CSVs de correspondencias normativas

Ubicación: `servidor/data/` — cargados automáticamente al arrancar Flask.

| Archivo | Filas |
|---|---|
| `99_AGRUPACION_NORMATIVO.csv` | 1.972 (HLS cross-norma) |
| `ENS_hacia_ISO27001.csv` | 170 |
| `ISO27001_hacia_ENS.csv` | 173 |

**BD:** 678 filas en `sig_correspondencias`. Ningún proyecto SIG creado en producción aún.

### Integración en 9 apps ISO/ENS

Todos los 9 `app.js` tienen badge SIG y métodos de integración:

| Método | Línea (ISO27001) | Función |
|---|---|---|
| `_checkSigMembership()` | L439 | Consulta `/api/sig/projects` para mostrar badge si el proyecto pertenece a un SIG |
| `_toastSigWarning()` | L477 | Toast anti-duplicación — avisa al usuario que esa sección ya existe en el SIG |
| `_openSigFromSidebar()` | En sidebar | Abre `/sig/` con `window.open` |

**Nota:** `_toastSigWarning` está implementado en los 9 `app.js` pero **aún no se invoca** desde `phase2-*.js` (pendiente, ver lista de pendientes).

### Tarjeta en pantalla de inicio Flask

Color `#5C35A0` (morado), posición al final del grid, badge dinámico con contador de SIGs activos.

### Documento de propuesta

`PLATAFORMA_OpenCode-NEW/SIG-MODULO-V01.html` — 71 KB, 10 secciones, propuesta técnica completa.

## BD: plataforma.db — 23 tablas (total actual)

**Originales (4):** `clients` · `projects` · `phase_data` · `settings`

**Tiquets (6):** `contadores_tiquets` · `tiquets` · `tiquets_historial` · `tiquets_comentarios` · `tiquets_acciones` · `tiquets_adjuntos`

**Wiki (2):** `wiki_documents` · `wiki_articles`

**Sonar (1):** `sonar_history`

**Riesgos/EIPD (5):** `risk_projects` · `risk_assets` · `risk_seguimiento` · `eipd_projects` · `eipd_data`

**SIG (3):** `sig_projects` · `sig_phase_data` · `sig_correspondencias`

**Capas Ciberseguridad (1):** `capas_herramientas`

**+ 1:** `sqlite_sequence` (gestionada por SQLite)

## Fix LLM — Groq como proveedor corporativo (v20261007a)

- Key corporativa Groq en BD: `provider: groq`, `model: openai/gpt-oss-20b`
- Default `getConfig()` → Groq en `llm.js` × 9 apps
- `FREE_FALLBACK_CHAIN` actualizada con 7 modelos verificados oct-2026
- Versiones: `llm.js?v=20261007a`, `llm-models.js?v=20261007a`, `phase2-*.js?v=20261007b`

## Fix LLM LAN — Key Corporativa + Modal (v20261003a)

- `await LLMUtil.loadCorpConfig()` antes de cada `if (!hasApiKey())` × 9 apps
- XOR clave fija `b'codanor_llm_2026_xor_key_fixed!!'` en server.py + llm.js
- Guard `isOllamaKey` en ENS `_syncLLMConfigFromForm`

## Historial de decisiones (selección reciente)

| Fecha | Decision | Razon |
|-------|----------|-------|
| 2026-10-28 | Generado `PENDIENTES-PLATAFORMA-V01.html` (79 KB) | Documento de seguimiento de los 15 pendientes activos con prioridad, estado, pasos de mejora y dependencias |
| 2026-10-27 | `pointer-events:none` en centerFill/centerText SVG | Bug: clic en anillo Información no funcionaba — centerFill tapaba el hitArea |
| 2026-10-27 | Informe HTML refactorizado: portada + TOC + ISO42001 + catálogo + estadísticas | El informe anterior no tenía columna ISO42001, ni catálogo, ni estadísticas de cobertura |
| 2026-10-27 | Leyenda lateral izquierda en Vista Diagrama | Mejorar legibilidad — nombre + descripción de cada capa visible sin hacer clic |
| 2026-10-22 | Técnica SVG stroke en lugar de fill para anillos | fill+círculos sólidos tapaban capas → solo se veía el último círculo (morado IA gigante) |
| 2026-10-21 | Módulo Capas de Ciberseguridad v1.0 standalone | App standalone sin modificar apps existentes — CRUD herramientas, 11 capas, 178 herramientas |
| 2026-10-21 | `capas-seguridad` en APP_DIRS de server.py | Necesario para servir la app standalone vía Flask en la LAN |
| 2026-10-21 | Capa IA orden=0 (exterior) en lugar de orden=11 | ISO 42001 como marco transversal que envuelve las 10 capas de ciberseguridad |
| 2026-10-21 | 160 herramientas de recomendación + tipo 'recomendacion' | 12 CSVs de referencia con herramientas ENS/ISO27001 → biblioteca de 178 herramientas |
| 2026-10-21 | Sidebar ISO27001 + ENS + ISO42001: enlace Capas Ciberseguridad | Acceso rápido desde las apps relevantes sin modificar la arquitectura SPA existente |
| 2026-10-07 | Groq como proveedor corporativo por defecto | OpenRouter :free rotó modelos 3 veces en una semana sin aviso |
| 2026-10-03 | XOR clave fija server.py + llm.js | XOR dependiente de hostname fallaba desde 127.0.0.1 vs IP LAN |
| 2026-10-02 | Módulo Análisis de Riesgos v1.0 IndexedDB→Flask | IndexedDB es local al navegador — no compartido en LAN |
| 2026-09-06 | PHASE_KEYS constante en store.js × 9 apps | ISO9001/ISO14001 usan gap/implementation, no phase1-5 |
| 2026-08-29 | TK_API con window.location.hostname | localhost no funciona en equipos LAN remotos |

## Pendiente

### Prioridad Crítica
- [ ] **[P-09]** Regenerar token SonarCloud — desbloquea verificación de todos los hotspots
- [ ] **[P-01]** Corregir los 18 innerHTML restantes (XSS — security hotspots SonarCloud) — requiere P-09

### Prioridad Alta
- [ ] **[P-02]** **SIG: activar `_toastSigWarning` desde `phase2-*.js`** — implementado en 9 `app.js` pero aún no invocado desde `addMeeting()` / `addTask()` de los módulos phase2
- [ ] **[P-03]** **SIG: corregir duplicado `8.11` en `ISO27001_hacia_ENS.csv`** (líneas 76-77, el segundo debería ser `8.12`) y añadir `UNIQUE` constraint a `sig_correspondencias`
- [ ] **[P-07]** Dashboard de riesgos para ISO9001, ISO14001, ISO42001, ISO27701 (actualmente "Próximamente")
- [ ] **[P-08]** Conceder "Acceso total al disco" en Ajustes → Privacidad para backup NAS — acción manual macOS
- [ ] **[P-10]** Activar Ollama en LAN (`OLLAMA_HOST=0.0.0.0 ollama serve`) — bloqueado por firewall MDM

### Prioridad Media
- [ ] **[P-04]** **SIG: bump `app.js` de 6 apps** a versión unificada — RGPD en `v20260923a`, ISO9001 en `v20260917a`, ISO27701/ISO14001/ISO14001-2026/TISAX en `v20260904c` (tienen el código SIG pero versión desactualizada)
- [ ] **[P-05]** Módulo Capas: integrar con proyectos ISO27001/ENS (filtrar herramientas por proyecto)
- [ ] **[P-06]** Módulo Capas: logo upload funcionando en todas las herramientas base
- [ ] **[P-11]** Ejecutar /init en los 7 proyectos restantes para crear AGENTS.md
- [ ] **[P-12]** Subir los otros 7+ proyectos a GitHub — requiere P-11

### Prioridad Baja
- [ ] **[P-13]** Activar apps en preparación: ISO9001:2026, NIS2
- [ ] **[P-14]** Integrar Gestion_Riesgos_ISO14001, ISO9001, ISO42001 en RISK_DIRS Flask — requiere P-07
- [ ] **[P-15]** Ingestar documentos en 9 KBs restantes Wiki_CODANOR
- [x] ~~Módulo Capas de Ciberseguridad v1.1.0~~ — 11 capas, 50 controles, 178 herramientas, SVG anillos, leyenda, informe HTML (2026-10-21/27)
- [x] ~~Módulo SIG v1.0~~ — app standalone, 14 endpoints, 8 módulos, 9 apps integradas con badge + toast, 678 correspondencias (2026-10-20)
- [x] ~~Groq como proveedor corporativo por defecto~~ (commits `27049f0` + `885e667` 2026-10-07)
- [x] ~~Fix LLM LAN: key corporativa + modal + Ollama ENS~~ (commit `ef5f302` 2026-10-03)
- [x] ~~Módulo Análisis de Riesgos v1.0~~ (commit `2957632` 2026-10-02)
- [x] ~~Módulo IA/LLM v3.0~~ (2026-09-25)
- [x] ~~Wiki_CODANOR v1.0~~ (2026-09-30)
- [x] ~~PROPAGATION_RULES.md~~ (2026-10-01)

## Notas técnicas

- **Capas Ciberseguridad — SVG técnica**: `<circle fill="none" stroke="color" stroke-width="step">` — cada anillo completamente independiente, no afecta a los demás.
- **Capas Ciberseguridad — orden**: `orden=0` es IA (exterior, radio=270px). `orden=10` es Información (interior, radio≈25px). `step = (270-14)/11 ≈ 23.3px`.
- **Groq proveedor corporativo**: modelos `openai/gpt-oss-20b` y `openai/gpt-oss-120b` son propios de Groq — no rotan. Key `gsk_...` en plataforma.db settings, compartida en LAN.
- **LAN**: servidor Flask HOST 0.0.0.0:5001. IP: 192.168.0.81. Todos los módulos usan `window.location.hostname` o `window.location.origin`.
- **BD 23 tablas**: +1 tabla nueva `capas_herramientas` vs. versión anterior (19 tablas + 3 SIG = 22 + sqlite_sequence = 23).
- **server.py 5377 líneas / 111 endpoints**: +5 endpoints `/api/capas/herramientas*` + ruta estática `/capas-seguridad/`.
- **app.js versión ISO27001/ENS/ISO42001**: `v=20261021a` — incluye enlace sidebar "🔒 Capas Ciberseguridad".
- **I18n.t() devuelve clave literal**: si una clave no existe, `t('phase2.x')` devuelve `"phase2.x"` (truthy). El patrón `|| 'fallback'` nunca activa. Siempre añadir la clave al JSON.
- **Safari/WebKit**: fetch con `hostname:puerto` explícito → `TypeError: Load failed`. Usar `window.location.origin`.



