# Memory.md — PLATAFORMA_OpenCode
> Ultima actualizacion: 2026-09-04

## Estado actual

- **Fase**: Produccion / mantenimiento activo
- **Version**: Manual v3.0 (20 capitulos)
- **Ultimo cambio significativo**: Fix sintetización actas Fase-2 en 5 apps (botón siempre visible + fallback manual sin API Key) + Manual Configuración IA Word (2026-09-04, commit `95f0e86`)
- **Issues abiertos**: 72 bugs de reliability + 3 security hotspots detectados por SonarCloud

## Infraestructura

| Elemento | Estado | Detalle |
|----------|--------|---------|
| Git | Si | rama principal |
| GitHub | Si | github.com/Jfajeda/PLATAFORMA_OpenCode |
| SonarCloud | Si | Security A, Reliability B, Maintainability A, 3.5% duplications |
| .gitignore | Si | Excluye .DS_Store, backups, __pycache__ |
| AGENTS.md | Si | Actualizado 2026-09-04 — sección Mapa de Procesos v1.0 + fix sintetización actas Fase-2 |
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
| ARQUITECTURA_DB_SQLITE.html | Documentacion BD **unificada v1.4** — portada + TOC + 16 secciones + branding CODANOR | 116 KB |
| requirements.txt | flask>=3.0.0, flask-cors>=4.0.0, python-docx>=1.0.0, openpyxl>=3.0.0 | — |
| DOCS/informes/Manual_Configuracion_IA_LLM.docx | Manual Word configuración IA v1.0 (13 caps, 44 KB) | — |

### Plataforma_Seguimiento_Proyectos — 9 apps ISO/ENS

| App | app_id | tiquets.js version | mapa-procesos.js version |
|-----|--------|--------------------|--------------------------|
| ISO27001-SGSI | iso27001 | v=20260829f | v=20260903a |
| ISO27701-SGP | iso27701 | v=20260829f | v=20260903a |
| ISO42001-SGIA | iso42001 | v=20260829f | v=20260903a |
| TISAX | tisax | v=20260829f | v=20260903a |
| RGPD-LOPD-GDD | rgpd | v=20260829f | v=20260903a |
| ENS-RD311-2022 | ens | v=20260829f | v=20260903a |
| ISO9001-SGQ_2015 | iso9001 | v=20260829f | v=20260903a |
| ISO14001-SGMA_2015 | iso14001 | v=20260829f | v=20260903a |
| ISO14001-SGMA_2026_NEW | iso14001-2026 | v=20260829f | v=20260903a |

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
| 2026-08-29 | Crear ARQUITECTURA_DB_SQLITE.html unificado (116 KB, 1698 líneas) | Fusión de ambos documentos v1+v2: portada hero, TOC navegable sticky, 16 secciones, DDL completo, 39 endpoints, flujos, mejoras prescriptivas con prioridad, branding codanor.com |
| 2026-09-04 | Módulo Mapa de Procesos via phase_data (no IndexedDB) | IndexedDB es local al navegador — no funciona en LAN multiusuario |
| 2026-09-04 | appId hardcodeado en mapa-procesos.js por app | Mismo patrón que tiquets.js — propagación con sed |
| 2026-09-04 | Tab "Mapa de Procesos" entre "Diseño SGSI" y "Puntos de Norma" | Posición natural en el flujo de consultoría |
| 2026-09-03 | appId hardcodeado a 'iso27001' en tiquets.js de ISO9001/ISO14001/ISO14001-2026 | El template de propagación del modulo tiquets no actualizaba este valor al copiar entre apps |
| 2026-09-04 | Botón "Generar Resumen IA" visible siempre (no solo con API Key) | Con `hasFile && LLMUtil.hasApiKey()` el botón no existía en DOM sin key → no pasaba nada al pulsar |
| 2026-09-04 | Fallback modal manual en generateActaSummary/generateGlobalSummary | Sin API Key derivar a showPromptModal() igual que synthesizeMeeting — mismo patrón consistente |
| 2026-09-04 | showPromptModal + showErrorModal añadidos a RGPD e ISO42001 | Métodos llamados pero no definidos en esas dos apps — ReferenceError silencioso |
| 2026-09-04 | guardia typeof LLMUtil movida antes de su primer uso en synthesizeMeeting | La comprobación era imposible (línea 2842 ya usaba LLMUtil antes del typeof check) |

## Bugs criticos corregidos (2026-08-29)

| Bug | Causa | Solucion |
|-----|-------|----------|
| Metodo _exportarTiquet duplicado en tiquets.js | Insercion incorrecta de funciones wiki rompia el objeto | Eliminar declaracion fantasma sin cuerpo |
| nav.tiquets literal en sidebar | I18n.t() devuelve la clave si no la encuentra (truthy, || no activa) | Hardcodear "Gestor de Tiquets" directamente en el HTML del sidebar |
| Categorias wiki desaparecidas | Insercion de resolved_ticket fuera del array + falta } de cierre de glossary | Insertar correctamente con },{ entre items |
| "Ya en Wiki" sin articulo real | wiki_test_12345 insertado manualmente en BD durante pruebas | Limpiar wiki_article_id=NULL + reescribir _confirmarPasarAConocimiento con Store.initDB() |
| Boton Anadir acciones no funcionaba | tiquet_id con guiones rompia string interpolado en onclick | Usar data-attributes + addEventListener |

## Bugs criticos corregidos (2026-09-03)

| Bug | App | Archivo | Causa | Solucion | Commit |
|-----|-----|---------|-------|----------|--------|
| "Cargando..." infinito al entrar en ISO9001 | ISO9001-SGQ_2015 | js/app.js L206 | SyntaxError: comilla simple extra `'</span>'Gestor` rompia el parser JS — todo app.js descartado | Eliminar la comilla extra: `'</span>Gestor` | deed56f |
| "Cargando..." infinito al entrar en ISO14001 | ISO14001-SGMA_2015 | js/app.js L204 | Mismo SyntaxError | Mismo fix | deed56f |
| Tiquets de ISO9001 guardados con app_id='iso27001' | ISO9001-SGQ_2015 | js/modules/tiquets.js L76 | `this.appId = 'iso27001'` hardcodeado — comentario de template nunca actualizado | Cambiar a `'iso9001'` | deed56f |
| Tiquets de ISO14001-2015 con app_id='iso27001' | ISO14001-SGMA_2015 | js/modules/tiquets.js L76 | Mismo | Cambiar a `'iso14001'` | deed56f |
| Tiquets de ISO14001-2026 con app_id='iso27001' | ISO14001-SGMA_2026_NEW | js/modules/tiquets.js L76 | Mismo | Cambiar a `'iso14001-2026'` | deed56f |

## Bugs criticos corregidos (2026-09-04)

| Bug | App | Archivo | Causa | Solucion | Commit |
|-----|-----|---------|-------|----------|--------|
| "Cargando..." infinito (regresión) | ISO14001-SGMA_2015 | js/app.js L203 | `\'tiquets\'` en expresión ternaria JS fuera de string → SyntaxError | `'tiquets'` sin escape (patrón idéntico a 'formacion' adyacente) | eb628fe |
| "Cargando..." infinito (regresión) | ISO9001-SGQ_2015 | js/app.js L205 | Mismo bug | Mismo fix | eb628fe |

## Bugs criticos corregidos (2026-09-04 — sintetización actas Fase-2)

| Bug | Apps afectadas | Archivo | Causa | Solucion | Commit |
|-----|---------------|---------|-------|----------|--------|
| Botón "Sintetizar" no hacía nada | ISO27001, ISO27701, ENS, RGPD, ISO42001 | phase2-consulting.js | Botón solo se renderizaba si `hasFile && LLMUtil.hasApiKey()` — sin API Key el botón no existía en DOM | Quitar `LLMUtil.hasApiKey()` del condicional del render | 95f0e86 |
| generateActaSummary sin fallback manual | ISO27001, ISO27701, ENS, RGPD, ISO42001 | phase2-consulting.js | Llamaba `callLLM()` directamente sin comprobar API Key → error silencioso | Añadir `if (!LLMUtil.hasApiKey()) { showPromptModal(prompt); return; }` | 95f0e86 |
| generateGlobalSummary sin fallback manual | ISO27001, ISO27701, ENS, RGPD, ISO42001 | phase2-consulting.js | Mismo que arriba | Mismo patrón | 95f0e86 |
| showPromptModal y showErrorModal no definidos | RGPD-LOPD-GDD | phase2-consulting.js | Métodos llamados pero no existían en este archivo | Añadir definición completa de ambos métodos | 95f0e86 |
| showErrorModal no definido | ISO42001-SGIA | phase2-consulting.js | Ídem | Añadir showErrorModal + openLLMConfigFromError | 95f0e86 |
| typeof LLMUtil check imposible | ISO27001, ISO27701, ENS | phase2-consulting.js synthesizeMeeting | Guard en línea 2845 cuando LLMUtil ya se había usado en 2842 | Mover guard antes del primer uso | 95f0e86 |

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
- [x] ~~ARQUITECTURA_DB_SQLITE.html~~ (unificada v1.4 portada+TOC+16 secciones 2026-09-03)
- [x] ~~Bug ISO9001/ISO14001 "Cargando infinito"~~ (SyntaxError app.js + appId incorrecto tiquets.js — commit deed56f 2026-09-03)
- [x] ~~Módulo Mapa de Procesos v1.0~~ (tab Fase 2 Consultoría, persistencia LAN Flask/SQLite, 9 apps — commit eb628fe 2026-09-04)
- [ ] Probar Mapa de Procesos en LAN desde segundo PC
- [ ] Verificar exportación PDF del mapa (jsPDF CDN) en cada app

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
- **Mapa de Procesos**: el módulo usa `phase_data` (clave `'mapa_procesos'`) para persistir en plataforma.db. `phase_data` es un store clave-valor JSON libre — el servidor no valida su contenido. El mapa original (`mapa_procesos.html`) usaba IndexedDB (local al navegador), incompatible con LAN multiusuario.
- **SyntaxError con \'**: el escape `\'` solo es válido dentro de strings JS. En expresiones ternarias `(a === \'b\')` produce SyntaxError silencioso que descarta todo el script. Siempre usar comillas simples sin escape en expresiones: `(a === 'b')`.
