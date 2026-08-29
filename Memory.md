# Memory.md — PLATAFORMA_OpenCode
> Ultima actualizacion: 2026-08-29

## Estado actual

- **Fase**: Produccion / mantenimiento activo
- **Version**: Manual v3.0 (20 capitulos)
- **Ultimo cambio significativo**: Modulo de Tiquets v1.4 completo — wiki, adjuntos, exportacion Word/Excel, base de conocimiento (2026-08-29)
- **Issues abiertos**: 72 bugs de reliability + 3 security hotspots detectados por SonarCloud

## Infraestructura

| Elemento | Estado | Detalle |
|----------|--------|---------|
| Git | Si | rama principal |
| GitHub | Si | github.com/Jfajeda/PLATAFORMA_OpenCode |
| SonarCloud | Si | Security A, Reliability B, Maintainability A, 3.5% duplications |
| .gitignore | Si | Excluye .DS_Store, backups, __pycache__ |
| AGENTS.md | Si | Actualizado 2026-08-29 con arquitectura tiquets completa |
| opencode.json | Si | MCP SonarQube configurado |
| Memory.md | Si | Este archivo |
| plataforma.db | Activa | 10 tablas, WAL mode, 298 clientes, 32 proyectos |
| server.py | Activo | Puerto 5001, HOST 0.0.0.0, 2559 lineas, 19 endpoints tiquets |

## Componentes del proyecto

### PLATAFORMA_OpenCode-NEW

| Archivo | Descripcion | Version |
|---------|-------------|---------|
| Manual_OpenCode_Codanor.html | Manual v3.0, 20 capitulos | ~137 KB |
| plataforma-seguimiento.html | Dashboard + Kanban + Gestor de Tiquets | ~98 KB |
| analisis-codigo.html | Panel SonarCloud exportable, 5 pestanas | ~46 KB |
| plan-homogeneizacion-modulos.html | Plan de homogeneizacion (14 caps) | ~72 KB |
| homogeneizacion-proyectos.html | Dashboard homogeneizacion (5 pestanas) | ~46 KB |
| propuesta-herramienta-tiquets.html | Propuesta tecnica tiquets **v1.2** | ~98 KB |
| backup-opencode.sh | Script backup NAS CODANOR (8 modos) | ~14 KB |

### Plataforma_Seguimiento_Proyectos/servidor/

| Archivo | Descripcion | Estado |
|---------|-------------|--------|
| server.py | Flask app: motor proyectos + 19 endpoints tiquets | 2559 lineas |
| plataforma.db | SQLite WAL: 10 tablas, 11 indices explícitos | Activa |
| migration_tiquets.sql | DDL standalone v1.0→v1.4 con instrucciones backup | 147 lineas |
| uploads/tiquets/ | Archivos adjuntos de tiquets (max 10 MB por fichero) | Excluido Git |
| ARQUITECTURA_DB_SQLITE.html | Documentacion arquitectura BD **actualizada v1.4** | 57 KB |
| requirements.txt | flask>=3.0.0, flask-cors>=4.0.0, python-docx>=1.0.0, openpyxl>=3.0.0 | — |

### Plataforma_Seguimiento_Proyectos — 9 apps ISO/ENS

| App | app_id | tiquets.js version |
|-----|--------|--------------------|
| ISO27001-SGSI | iso27001 | v=20260829f |
| ISO27701-SGP | iso27701 | v=20260829f |
| ISO42001-SGIA | iso42001 | v=20260829f |
| TISAX | tisax | v=20260829f |
| RGPD-LOPD-GDD | rgpd | v=20260829f |
| ENS-RD311-2022 | ens | v=20260829f |
| ISO9001-SGQ_2015 | iso9001 | v=20260829f |
| ISO14001-SGMA_2015 | iso14001 | v=20260829f |
| ISO14001-SGMA_2026_NEW | iso14001-2026 | v=20260829f |

## Herramienta de Tiquets — Arquitectura completa (v1.0→v1.4)

### BD: plataforma.db — 10 tablas

**Tablas originales (4):**
- `clients` (298 filas) — clientes CODANOR × 9 normas
- `projects` (32 filas) — proyectos activos por norma
- `phase_data` (35 filas) — datos de fases en JSON
- `settings` (0 filas) — configuracion por app

**Tablas modulo tiquets (6):**

| Tabla | Version | Filas | Descripcion |
|-------|---------|-------|-------------|
| `contadores_tiquets` | v1.0 | 2 | NNN atomico por (client_id, app_id) |
| `tiquets` | v1.0+v1.4 | 2 | Tabla principal, 22 columnas, incl. wiki_article_id |
| `tiquets_historial` | v1.0 | 9 | Auditoria campo a campo (ISO 27001 A.16) |
| `tiquets_comentarios` | v1.0 | 1 | Log de seguimiento libre |
| `tiquets_acciones` | v1.2 | 4 | Acciones: pendiente→en_curso→resuelta |
| `tiquets_adjuntos` | v1.3 | 1 | Ficheros en uploads/tiquets/ |

**Formato ID tiquet:** `TIK-{NNN:03d}-{client_id}-{app_id}-{DD-MM-AAAA}`

### Historial de migraciones

| Version | Fecha | Cambio |
|---------|-------|--------|
| v1.0 | 2026-08-28 | Tablas base: contadores, tiquets, historial, comentarios + 6 indices |
| v1.2 | 2026-08-28 | Tabla tiquets_acciones + logica auto-cierre/reapertura tiquet |
| v1.3 | 2026-08-29 | Tabla tiquets_adjuntos + uploads/tiquets/ + exportar Word/Excel |
| v1.4 | 2026-08-29 | ALTER TABLE tiquets ADD COLUMN wiki_article_id + endpoint /enviar-wiki |

### Endpoints API REST (19 en total, puerto 5001)

| Metodo | URL | Version |
|--------|-----|---------|
| GET | /api/tiquets/clientes | v1.0 |
| GET | /api/tiquets/proyectos | v1.0 |
| GET | /api/tiquets | v1.0 |
| POST | /api/tiquets | v1.0 |
| GET | /api/tiquets/\<id\> | v1.0 |
| PUT | /api/tiquets/\<id\> | v1.0 |
| POST | /api/tiquets/\<id\>/comentarios | v1.0 |
| GET | /api/tiquets/exportar | v1.0 |
| GET | /api/tiquets/\<id\>/exportar/word | v1.3 |
| GET | /api/tiquets/\<id\>/exportar/excel | v1.3 |
| GET | /api/tiquets/\<id\>/acciones | v1.2 |
| POST | /api/tiquets/\<id\>/acciones | v1.2 |
| PUT | /api/tiquets/\<id\>/acciones/\<id\> | v1.2 |
| DELETE | /api/tiquets/\<id\>/acciones/\<id\> | v1.2 |
| GET | /api/tiquets/\<id\>/adjuntos | v1.3 |
| POST | /api/tiquets/\<id\>/adjuntos | v1.3 |
| DELETE | /api/tiquets/\<id\>/adjuntos/\<id\> | v1.3 |
| GET | /api/uploads/tiquets/\<filename\> | v1.3 |
| POST | /api/tiquets/\<id\>/enviar-wiki | v1.4 |

### Frontend — tiquets.js (9 apps, version 20260829f)

**Funcionalidades implementadas:**
- Panel expandible horizontal debajo de cada fila (click para abrir/colapsar)
- 3 columnas: Info del tiquet | Acciones de seguimiento | Historial + Comentarios + Adjuntos
- Botones de estado por accion: Pendiente → [En curso] [Resolver] | En curso → [← Pendiente] [Resolver] | Resuelta → fecha [↺ Reabrir]
- Boton "✓ Cerrar Tiquet" (estado=resuelto → cerrado)
- Boton "↺ Reabrir" (estado=cerrado → resuelto)
- Boton "📚 Pasar a Conocimiento" (solo cuando cerrado, una sola vez)
- Botones "↓ Word" y "↓ Excel" para exportar tiquet individual
- Adjuntos: subir, ver, eliminar ficheros en el panel
- Auto-deteccion de IP para LAN (`window.location.hostname`)
- Fallback offline con localStorage (`codanor_tiquets_v2`)
- Sincronizacion automatica offline→online al recuperar conexion
- Descripcion editable inline (click en el texto → input)

### Integracion Base de Conocimiento (v1.4)

- Campo `wiki_article_id TEXT DEFAULT NULL` en tabla `tiquets`
- Boton "📚 Pasar a Conocimiento" visible solo en tiquets cerrados
- Control "solo una vez": HTTP 409 si ya fue enviado
- Modal de etiquetado con campos prellenados del tiquet
- Genera articulo en Markdown estructurado con: cabecera, descripcion, acciones, comentarios, referencias
- Crea articulo en IndexedDB via `Store.saveWikiArticle()` (modulo Conocimiento)
- Categoria nueva "🎟 BD de Tiquets Resueltos" (`resolved_ticket`) en wiki-categories.js de las 9 apps
- `Store.initDB()` se llama explicitamente antes de `saveWikiArticle()` para garantizar IndexedDB lista

### Exportacion Word (.docx) — python-docx

**Estructura del documento:**
- Pagina 1 — Portada: logo CODANOR + linea azul + "INFORME DE TIQUET" + ID + tabla metadatos
- Pagina 2 — Indice TOC automatico de Word (updateFields=1, dirty=1)
- Paginas 3+ — 6 secciones con headings azules + tablas con cabecera #178DC2 + filas alternas
- Header (pag 2+): logo pequeno + ID tiquet
- Footer: "CODANOR | Confidencial | Pagina X"
- Logo: descarga online codanor.com → fallback local ENS-RD311-2022/img/logo-codanor.png
- Nombres legibles: iso27001→"ISO 27001 — SGSI", en_progreso→"En Progreso", etc.

### Exportacion Excel (.xlsx) — openpyxl

**5 hojas:** Tiquet | Acciones | Historial | Comentarios | Adjuntos
**Estilo:** cabeceras fondo #178DC2 + filas alternas #F0F4F8

## Historial de decisiones

| Fecha | Decision | Razon |
|-------|----------|-------|
| 2026-04-26 | Mover proyectos a ~/Proyectos/ | iCloud causaba conflictos con Git |
| 2026-04-26 | SonarCloud Automatic Analysis | Sin Node.js local |
| 2026-07-05 | Herramienta Homogeneizacion de Proyectos | Comparar 17 subproyectos vs patron ISO27001 |
| 2026-08-28 | Integrar tiquets en plataforma.db (no BD nueva) | Reutilizar clients (298) y projects (32) |
| 2026-08-28 | Endpoints /api/tiquets/* en server.py existente | Sin servidor nuevo |
| 2026-08-28 | Panel expandible horizontal debajo de la fila | Mejor UX que panel lateral estrecho |
| 2026-08-28 | Botones con data-attributes en lugar de onclick inline | IDs de tiquets con guiones rompian onclick |
| 2026-08-29 | ALTER TABLE wiki_article_id en init_db() | Idempotente, safe para BD existentes |
| 2026-08-29 | Store.initDB() explicito antes de saveWikiArticle | Race condition: IndexedDB puede no estar lista |
| 2026-08-29 | resolved_ticket como item del array WIKI_CATEGORIES | La coma separadora es critica para JSON valido |
| 2026-08-29 | TK_API con window.location.hostname | localhost no funciona en equipos LAN remotos |
| 2026-08-29 | Documentar ARQUITECTURA_DB_SQLITE.html v1.4 | Referencia autoritativa del schema de plataforma.db |

## Bugs criticos corregidos (2026-08-29)

| Bug | Causa | Solucion |
|-----|-------|----------|
| Metodo _exportarTiquet duplicado en tiquets.js | Insercion incorrecta de funciones wiki rompia el objeto | Eliminar declaracion fantasma sin cuerpo |
| nav.tiquets literal en sidebar | I18n.t() devuelve la clave si no la encuentra (truthy, || no activa) | Hardcodear "Gestor de Tiquets" directamente en el HTML del sidebar |
| Categorias wiki desaparecidas | Insercion de resolved_ticket fuera del array + falta } de cierre de glossary | Insertar correctamente con },{ entre items |
| "Ya en Wiki" sin articulo real | wiki_test_12345 insertado manualmente en BD durante pruebas | Limpiar wiki_article_id=NULL + reescribir _confirmarPasarAConocimiento con Store.initDB() |
| Boton Anadir acciones no funcionaba | tiquet_id con guiones rompia string interpolado en onclick | Usar data-attributes + addEventListener |

## Pendiente

- [x] ~~Corregir bugs de reliability de SonarCloud~~ (37 de ~55 corregidos)
- [ ] Corregir los 18 innerHTML restantes (security hotspots de SonarCloud)
- [ ] Instalar Node.js en el Mac
- [ ] Ejecutar /init en los 7 proyectos restantes para crear AGENTS.md
- [ ] Subir los otros 7+ proyectos a GitHub
- [x] ~~Automatizar backup launchd diario~~ (falta conceder TCC al NAS)
- [ ] Conceder "Acceso total al disco" en Ajustes → Privacidad para backup NAS
- [ ] Regenerar token SonarCloud
- [x] ~~Herramienta de Tiquets v1.0~~ (implementada 2026-08-28)
- [x] ~~Herramienta de Tiquets v1.2~~ (acciones de seguimiento 2026-08-28)
- [x] ~~Herramienta de Tiquets v1.3~~ (adjuntos + exportar Word/Excel 2026-08-29)
- [x] ~~Herramienta de Tiquets v1.4~~ (integracion base de conocimiento 2026-08-29)
- [x] ~~ARQUITECTURA_DB_SQLITE.html~~ (actualizada a v1.4 con 10 tablas 2026-08-29)

## Herramienta Homogeneizacion de Proyectos (2026-07-05)

Herramienta de analisis **read-only** que compara subproyectos contra patron **ISO27001-SGSI**.

### Ficheros (scripts en Plataforma_Seguimiento/_homogeneizacion/)
| Fichero | Descripcion |
|---------|-------------|
| patron_iso27001.json | Gold standard: 7 bloques, pesos |
| scan_proyectos.py | Scanner read-only |
| estado_proyectos.json | Salida del scan |
| generar_informe_docx.py | Informe Word |
| generar_informe_xlsx.py | Informe Excel 5 hojas |

### Resultados ultimo scan (17 proyectos)
Score medio apps: **85%** — ISO27001 100% · ISO42001 93% · ISO27701 89% · ISO9001/RGPD 85% · ISO14001-2015 82% · ISO14001-2026 76% · TISAX 67%

## Sistema de copias de seguridad (2026-06-06)

### Estrategia (2 capas)
1. **NAS CODANOR** (`/Volumes/CODANOR/opencode-backups`) — destino principal
2. **Time Machine** — capa horaria del sistema

### BLOQUEO PENDIENTE
TCC de macOS impide escribir en NAS. Solucion: **Ajustes del Sistema → Privacidad → Acceso total al disco** → anadir Terminal y /bin/bash.

## Notas y descubrimientos

- **OpenCode queda bloqueado** si su directorio de trabajo se elimina o mueve.
- **El usuario NO tiene Node.js, Homebrew ni GitHub CLI**. Git push requiere autenticacion manual.
- **SonarCloud token**: regenerar desde sonarcloud.io > My Account > Security.
- **Puerto 5000** en macOS puede estar ocupado por AirPlay Receiver. Usar 5001.
- **python-docx 1.2.0 y openpyxl 3.1.5** instalados en el sistema (no en requirements.txt original, ya anadidos).
- **IndexedDB de la wiki** vive exclusivamente en el navegador — no se sincroniza con plataforma.db. El campo wiki_article_id en plataforma.db solo registra que el articulo fue creado, no el contenido.
- **LAN**: el servidor Flask sirve en HOST 0.0.0.0:5001. IP actual: 192.168.0.81. tiquets.js usa window.location.hostname para auto-detectar la IP correcta desde cualquier equipo de la red.
