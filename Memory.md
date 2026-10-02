# Memory.md — PLATAFORMA_OpenCode
> Ultima actualizacion: 2026-10-02

## Estado actual

- **Fase**: Produccion / mantenimiento activo
- **Version**: Manual v3.0 (20 capitulos) + Manual IA Actas v1.0
- **Ultimo cambio significativo**: Módulo Análisis de Riesgos v1.0 — migración IndexedDB→Flask, integración Fase 2 (commit `2957632` 2026-10-02)
- **Issues abiertos**: 72 bugs de reliability + 3 security hotspots detectados por SonarCloud

## Infraestructura

| Elemento | Estado | Detalle |
|----------|--------|---------|
| Git | Si | rama principal |
| GitHub | Si | github.com/Jfajeda/PLATAFORMA_OpenCode |
| SonarCloud | Si | Security A, Reliability B, Maintainability A, 3.5% duplications |
| .gitignore | Si | Excluye .DS_Store, backups, __pycache__ |
| AGENTS.md | Si | Actualizado 2026-10-02 — módulo riesgos + nuevas tablas + versiones phase2 |
| PROPAGATION_RULES.md | Si | 2026-10-01 — clasificación BASE/CLON/DIVERGENTE/PROPIO + workflows + script verificación ENS |
| opencode.json | Si | MCP SonarQube + instructions: AGENTS.md + PROPAGATION_RULES.md |
| Memory.md | Si | Este archivo |
| plataforma.db | Activa | 19 tablas, WAL mode, 298 clientes, 32 proyectos |
| server.py | Activo | Puerto 5001, HOST 0.0.0.0, ~4272 lineas, 22 endpoints riesgos/EIPD + 19 tiquets + 3 corp LLM |
| Ollama | Activo | localhost:11434, v0.34.4. Modelos: qwen2.5-coder:14b, qwen3:8b, llama3.1:latest, gemma3:4b |
| Wiki_CODANOR | Activa | Open WebUI :3000 (Docker), ChromaDB vectordb/, 10 KBs, Ollama + OpenRouter conectados |

## Componentes del proyecto

### PLATAFORMA_OpenCode-NEW

| Archivo | Descripcion | Version |
|---------|-------------|---------|
| Manual_OpenCode_Codanor.html | Manual v3.0, 20 capitulos | ~137 KB |
| Manual_IA_Actas_Codanor.html | Manual IA módulo actas v1.0, 10 secciones | ~99 KB |
| plataforma-seguimiento.html | Dashboard + Kanban + Tiquets + Config IA Corp | ~98 KB |
| analisis-codigo.html | Panel SonarCloud exportable, 5 pestanas | ~46 KB |
| plan-homogeneizacion-modulos.html | Plan de homogeneizacion (14 caps) | ~72 KB |
| homogeneizacion-proyectos.html | Dashboard homogeneizacion (5 pestanas) | ~46 KB |
| propuesta-herramienta-tiquets.html | Propuesta tecnica tiquets **v1.2** | ~98 KB |
| backup-opencode.sh | Script backup NAS CODANOR (8 modos) | ~14 KB |
| Guia_Wiki_CODANOR_OpenWebUI.docx | Guia configuracion Wiki CODANOR + Open WebUI (13 secciones, 43 tablas) | 139 KB — commit `1195855` |
| PROPAGATION_RULES.md | Reglas propagación entre 9 apps — BASE/CLON/DIVERGENTE/PROPIO + workflows | commit `2026-10-01` |

### Plataforma_Seguimiento_Proyectos/servidor/

| Archivo | Descripcion | Estado |
|---------|-------------|--------|
| server.py | Flask app: motor proyectos + 22 endpoints riesgos/EIPD + 19 tiquets + 3 corp LLM | ~4272 lineas |
| plataforma.db | SQLite WAL: 19 tablas, WAL mode | Activa |
| migration_tiquets.sql | DDL standalone v1.0→v1.4 con instrucciones backup | 147 lineas |
| uploads/tiquets/ | Archivos adjuntos de tiquets (max 10 MB por fichero) | Excluido Git |
| ARQUITECTURA_DB_SQLITE.html | Documentacion BD **unificada v1.4** | 116 KB |
| requirements.txt | flask>=3.0.0, flask-cors>=4.0.0, python-docx>=1.0.0, openpyxl>=3.0.0 | — |

### Plataforma_Seguimiento_Proyectos — 9 apps ISO/ENS (versiones actuales)

| App | app_id | tiquets.js | phase2-*.js | llm.js | phase3-audit.js |
|-----|--------|------------|-------------|--------|-----------------|
| ISO27001-SGSI | iso27001 | v=20260829f | v=20260930e | v=20260911h | v=20260930b |
| ENS-RD311-2022 | ens | v=20260829f | v=20260930e | v=20260911h | v=20260930b |
| RGPD-LOPD-GDD | rgpd | v=20260829f | v=20260930e | v=20260911h | v=20260930b |
| ISO27701-SGP | iso27701 | v=20260829f | v=20260930e | v=20260911h | v=20260930b |
| ISO42001-SGIA | iso42001 | v=20260829f | v=20260930e | v=20260911h | v=20260930b |
| ISO9001-SGQ_2015 | iso9001 | v=20260829f | v=20260930f | v=20260911h | v=20260930b |
| ISO14001-SGMA_2015 | iso14001 | v=20260829f | v=20260930f | v=20260911h | v=20260930b |
| ISO14001-SGMA_2026_NEW | iso14001-2026 | v=20260829f | v=20260930f | v=20260911h | v=20260930b |
| TISAX | tisax | v=20260829f | v=20260925c | v=20260911h | v=20260930b |

## Módulo Análisis de Riesgos (v1.0 — 2026-10-02, commit `2957632`)

### Arquitectura

```
Plataforma Fase 2 (Diseño SGSI)
  └── Botón "Análisis de Riesgos" → window.open con ?project=&client=
        ↓
  http://IP:5001/riesgos/{iso27001|ens|lopd}/dashboard_riesgos_*.html
        ↓
  fetch a window.location.origin/api/riesgos/{app_id}/proyectos
        ↓
  plataforma.db → risk_projects / risk_assets / risk_seguimiento
  (o /api/eipd/* → eipd_projects / eipd_data para EIPD)
```

### Dashboards de riesgos — rutas Flask

| URL Flask | Dashboard | app_id API |
|---|---|---|
| `/riesgos/iso27001/` | `Gestion_Riesgos_ISO27001/dashboard_riesgos_codanor.html` | `iso27001` |
| `/riesgos/ens/` | `Gestion_Riesgos_ENS/dashboard_riesgos_codanor_ens.html` | `ens` |
| `/riesgos/lopd/` | `Gestion_Riesgos_LOPD-RGPD/dashboard_riesgos_codanor.html` | `lopd` |
| `/riesgos/lopd/dashboard_eipd_rgpd_codanor.html` | EIPD RGPD | `/api/eipd/*` |

### Endpoints API REST — Riesgos (17 rutas)

| Método | URL | Descripción |
|---|---|---|
| GET | `/api/riesgos/<app_id>/proyectos` | Listar proyectos de riesgo |
| POST | `/api/riesgos/<app_id>/proyectos` | Crear/actualizar proyecto (upsert) |
| GET | `/api/riesgos/<app_id>/proyectos/<id>` | Proyecto completo + activos + seguimiento |
| DELETE | `/api/riesgos/<app_id>/proyectos/<id>` | Eliminar proyecto |
| GET | `/api/riesgos/<app_id>/proyectos/<id>/activos` | Listar activos |
| POST | `/api/riesgos/<app_id>/proyectos/<id>/activos` | Crear activo |
| PUT | `/api/riesgos/<app_id>/proyectos/<id>/activos/<rowid>` | Actualizar activo |
| DELETE | `/api/riesgos/<app_id>/proyectos/<id>/activos/<rowid>` | Eliminar activo |
| GET | `/api/riesgos/<app_id>/proyectos/<id>/seguimiento` | Listar seguimientos |
| POST | `/api/riesgos/<app_id>/proyectos/<id>/seguimiento` | Crear seguimiento |
| PUT | `/api/riesgos/<app_id>/proyectos/<id>/seguimiento/<rowid>` | Actualizar seguimiento |
| DELETE | `/api/riesgos/<app_id>/proyectos/<id>/seguimiento/<rowid>` | Eliminar seguimiento |
| GET | `/api/eipd/proyectos` | Listar proyectos EIPD |
| POST | `/api/eipd/proyectos` | Crear/actualizar proyecto EIPD |
| GET | `/api/eipd/proyectos/<id>` | Proyecto EIPD completo con secciones |
| PUT | `/api/eipd/proyectos/<id>/<seccion>` | Actualizar sección EIPD |
| DELETE | `/api/eipd/proyectos/<id>` | Eliminar proyecto EIPD |

### Tablas plataforma.db — Módulo Riesgos (5 nuevas)

| Tabla | PK | Descripción |
|---|---|---|
| `risk_projects` | `(id, app_id)` | Proyectos por norma. `categoria_ens` NULL en no-ENS |
| `risk_assets` | `INTEGER AUTOINCREMENT` | 37 columnas Magerit v3. `impacto_aut/traz` NULL en no-ENS |
| `risk_seguimiento` | `INTEGER AUTOINCREMENT` | 6 campos: seg_id, activo_id, accion, fechas, responsables |
| `eipd_projects` | `id TEXT` | Proyectos EIPD (formato EIPD-NNN-CLIENTE) |
| `eipd_data` | `(project_id, seccion)` | Secciones EIPD como JSON: rat_rt, rat_et, pre_evaluacion, descripcion, necesidad, factores, medidas, conclusion, consulta_previa |

### Reglas críticas del módulo de riesgos

1. **`window.location.origin`** en `_riskApi()` y `_eipdApi()` — NO usar `window.location.hostname:5001` (causa `TypeError: Load failed` en Safari/WebKit).

2. **`app_id` válidos para riesgos**: `iso27001`, `ens`, `lopd` — definidos en `RISK_APP_IDS` en `server.py`. Son distintos de los `app_id` de la Plataforma (no existe `lopd` en `APP_DIRS`, solo `rgpd`).

3. **Botón en Fase 2**: `_renderRiskLink()` se llama desde `renderDesignTab()`. El tab `design` se re-renderiza en `switchTab` → el botón aparece siempre al activar la pestaña.

4. **Migración IDB→servidor**: cada dashboard detecta automáticamente proyectos en IndexedDB local y ofrece migrarlos con un clic (banner superior). Función `_checkAndOfferMigration()`.

5. **Pre-carga por URL**: el botón pasa `?project=PRJ-NNN-CLIENTE&client=NOMBRE&_t=TIMESTAMP`. El timestamp evita caché de navegador. El dashboard carga el proyecto directamente si existe en BD.

6. **Apps sin dashboard propio**: ISO27701, ISO42001, ISO9001, ISO14001-2015, ISO14001-2026 muestran botón desactivado "Próximamente". TISAX no tiene botón.

7. **`generateProjectId()` offline**: si el servidor no responde, usa `Date.now().slice(-6)` como número de proyecto. El usuario puede iniciar un nuevo análisis sin servidor disponible y sincronizar después.

## BD: plataforma.db — 19 tablas (total actual)

**Originales (4):** `clients` · `projects` · `phase_data` · `settings`

**Tiquets (6):** `contadores_tiquets` · `tiquets` · `tiquets_historial` · `tiquets_comentarios` · `tiquets_acciones` · `tiquets_adjuntos`

**Wiki (2):** `wiki_documents` · `wiki_articles`

**Sonar (1):** `sonar_history`

**Riesgos/EIPD (5):** `risk_projects` · `risk_assets` · `risk_seguimiento` · `eipd_projects` · `eipd_data`

**+ 1:** `sqlite_sequence` (gestionada por SQLite automáticamente)

## Módulo Wiki_CODANOR (v1.0 — 2026-09-30)

### Arquitectura

```
Usuarios
   ↓
Open WebUI :3000 (Docker — contenedor wiki-codanor)
   ├── Ollama :11434 (macOS nativo — host.docker.internal:11434)
   │     ├── qwen3:8b          ← chat general (PREDETERMINADO)
   │     ├── qwen2.5-coder:14b ← análisis técnico
   │     ├── llama3.1:latest   ← actas y redacción
   │     ├── gemma3:4b         ← respuestas rápidas
   │     └── nomic-embed-text  ← embeddings RAG (NO usar para chat)
   ├── OpenRouter (nube — https://openrouter.ai/api/v1)
   │     └── GPT-3.5/GPT-4, Claude, Gemini, Mistral, 100+ modelos
   └── ChromaDB vectordb/ (embebido en Open WebUI)
         └── 10 Knowledge Bases CODANOR
```

### Arranque tras reinicio

```bash
cd ~/Proyectos/Wiki_CODANOR && docker compose up -d
# → http://localhost:3000
```

### Reglas criticas

1. **RAG no es automatico** — adjuntar KB al chat: `+` → `Adjuntar coneixement`.
2. **`nomic-embed-text`** solo para embeddings — NUNCA como modelo de chat.
3. **No PostgreSQL+pgvector** — decisión 2026-09-30, RAM insuficiente.

## Módulo IA/LLM — Arquitectura completa (v3.0 — 2026-09-25)

### Proveedores y modelos activos

| Proveedor | ID | Modelo por defecto | Gratuito | Key prefix |
|---|---|---|---|---|
| Groq | groq | openai/gpt-oss-20b | ✅ | gsk_... |
| OpenRouter | openrouter | openrouter/free | ✅ | sk-or-... |
| Google Gemini | google | gemini-2.0-flash | ✅ | AIza... |
| OpenAI | openai | gpt-4o-mini | ❌ | sk-... |
| Anthropic | anthropic | claude-3-5-haiku-20241022 | ❌ | sk-ant-... |
| Ollama (Local) | ollama | qwen2.5-coder:14b | ✅ | ollama |

### Config corporativa (server.py endpoints)

```
GET  /api/corp/llm-config   → config con key XOR+base64
POST /api/corp/llm-config   → guarda (key ofuscada)
DELETE /api/corp/llm-config → elimina
```

## Herramienta de Tiquets — Arquitectura completa (v1.0→v1.4)

**Formato ID tiquet:** `TIK-{NNN:03d}-{client_id}-{app_id}-{DD-MM-AAAA}`

**Tablas:** `contadores_tiquets` · `tiquets` (22 cols + `wiki_article_id`) · `tiquets_historial` · `tiquets_comentarios` · `tiquets_acciones` · `tiquets_adjuntos`

**19 endpoints** en `/api/tiquets/*` — ver AGENTS.md para lista completa.

## Historial de decisiones

| Fecha | Decision | Razon |
|-------|----------|-------|
| 2026-04-26 | Mover proyectos a ~/Proyectos/ | iCloud causaba conflictos con Git |
| 2026-08-28 | Integrar tiquets en plataforma.db (no BD nueva) | Reutilizar clients (298) y projects (32) |
| 2026-08-29 | TK_API con window.location.hostname | localhost no funciona en equipos LAN remotos |
| 2026-09-04 | Módulo Mapa de Procesos via phase_data (no IndexedDB) | IndexedDB es local al navegador |
| 2026-09-06 | acciones[] en modelo de tarea | Registrar pasos concretos de resolución por tarea |
| 2026-09-06 | PHASE_KEYS constante en store.js × 9 apps | ISO9001/ISO14001 usan gap/implementation, no phase1-5 |
| 2026-09-11 | LLM: dos campos API Key → un solo campo | Campo duplicado desincronizado causaba "Missing Auth header" |
| 2026-09-11 | Key corporativa LAN vía Flask settings | localStorage no se comparte entre PCs de la LAN |
| 2026-09-11 | isOllamaKey guard en _syncLLMConfigFromForm | 'ollama' tiene 6 chars → length>10 bloqueaba el guardado |
| 2026-09-17 | Botón NotebookLM dentro de wiki.js (no sidebar) | Acceso contextual al módulo Conocimiento |
| 2026-09-21 | Badge IA→C (CODANOR) en phase2-*.js | Imagen corporativa — no mostrar "IA" a clientes |
| 2026-09-30 | Wiki_CODANOR v1.0 (Open WebUI + ChromaDB + RAG) | Base de conocimiento corporativa con LLM |
| 2026-10-01 | PROPAGATION_RULES.md como segunda instruction | Incidente: propagación ISO27001→ENS destruyó +608 líneas exclusivas |
| 2026-10-02 | Riesgos: IndexedDB→Flask/SQLite (plataforma.db) | IndexedDB es local al navegador — no accesible en LAN multiusuario |
| 2026-10-02 | window.location.origin en _riskApi() | `hostname:5001` explícito causa TypeError: Load failed en Safari/WebKit |
| 2026-10-02 | Re-render tab 'design' en switchTab() × 8 apps | Tab se renderizaba 1 sola vez en init() — botón riesgos no aparecía al volver al tab |
| 2026-10-02 | _t=Date.now() en URL botón riesgos | Evita caché agresiva de Safari para el HTML del dashboard |
| 2026-10-02 | generateProjectId() con fallback offline | Si Flask no responde, el NNN se genera con timestamp local — botón no queda deshabilitado |

## Pendiente

- [ ] Corregir los 18 innerHTML restantes (security hotspots de SonarCloud)
- [ ] Ejecutar /init en los 7 proyectos restantes para crear AGENTS.md
- [ ] Subir los otros 7+ proyectos a GitHub
- [ ] Conceder "Acceso total al disco" en Ajustes → Privacidad para backup NAS
- [ ] Regenerar token SonarCloud
- [x] ~~Módulo Análisis de Riesgos v1.0~~ (migración IndexedDB→Flask, Fase 2 integrada — commit `2957632` 2026-10-02)
- [x] ~~Herramienta de Tiquets v1.0→v1.4~~ (implementada 2026-08-28/29)
- [x] ~~Módulo Mapa de Procesos v1.0~~ (commit eb628fe 2026-09-04)
- [x] ~~Mejora Seguimiento de Tareas v2.0~~ (commit e0c1a08 2026-09-06)
- [x] ~~Fix LAN persistencia BD~~ (commit e0c1a08 2026-09-06)
- [x] ~~Módulo IA/LLM v3.0~~ (2026-09-25 — Ollama local + isOllamaKey fix × 9 apps)
- [x] ~~Wiki_CODANOR v1.0~~ (Open WebUI :3000 + Ollama + ChromaDB + RAG — 2026-09-30)
- [x] ~~PROPAGATION_RULES.md~~ (clasificación BASE/CLON/DIVERGENTE/PROPIO — 2026-10-01)
- [ ] Probar Mapa de Procesos en LAN desde segundo PC
- [ ] Verificar exportación PDF del mapa (jsPDF CDN) en cada app
- [ ] Activar Ollama en LAN (`OLLAMA_HOST=0.0.0.0 ollama serve`) — bloqueado por firewall MDM
- [ ] Probar acciones de tarea desde segundo PC LAN
- [ ] Dashboard de riesgos para ISO9001, ISO14001, ISO42001, ISO27701 (actualmente "Próximamente")
- [ ] Ingestar documentos en 9 KBs restantes (ISO27001, LOPD-RGPD, NIS2, OSINT, Logs-SIEM...)

## Notas y descubrimientos

- **OpenCode queda bloqueado** si su directorio de trabajo se elimina o mueve.
- **El usuario NO tiene Node.js, Homebrew ni GitHub CLI**. Git push requiere autenticacion manual.
- **SonarCloud token**: regenerar desde sonarcloud.io > My Account > Security.
- **Puerto 5000** en macOS puede estar ocupado por AirPlay Receiver. Usar 5001.
- **python-docx 1.2.0 y openpyxl 3.1.5** instalados en el sistema.
- **IndexedDB de la wiki** vive exclusivamente en el navegador — no se sincroniza con plataforma.db.
- **LAN**: servidor Flask sirve en HOST 0.0.0.0:5001. IP actual: 192.168.0.81. Todos los módulos usan `window.location.hostname` o `window.location.origin` para auto-detectar la IP.
- **Ollama**: escucha en localhost:11434 por defecto. Para LAN requiere `OLLAMA_HOST=0.0.0.0`. Modelos: qwen2.5-coder:14b (8.5GB), qwen3:8b (5GB), llama3.1:latest (4.7GB), gemma3:4b (3.2GB). Versión: v0.34.4.
- **Safari/WebKit**: fetch a URLs con `hostname:puerto` explícito puede causar `TypeError: Load failed` aunque sea mismo origen. Usar siempre `window.location.origin` para construir URLs de API.
- **ISO9001 ≠ ISO14001 en phase2-implementation.js**: ISO9001 usa `ACTIVITY_GROUPS`; ISO14001 usa `CLAUSE_GROUPS`. NUNCA propagar con cp/sed entre ellas — TIPO D PROPIO.
- **Re-render tab design**: `switchTab` re-renderiza siempre el tab `design` cuando se activa. Necesario porque `renderDesignTab()` contiene el botón de riesgos y otros elementos dinámicos. Sin este re-render el botón no aparece si el módulo ya estaba inicializado.
- **Riesgos app_id**: los dashboards de riesgos usan `iso27001`, `ens`, `lopd` como app_id en la API. Son distintos de los app_id de la Plataforma (donde RGPD usa `rgpd`, no `lopd`).
- **Key corporativa LLM**: guardada ofuscada (XOR+base64) en `settings` WHERE `app_id='_global'` AND `key='corp_llm_config'`.
- **isOllamaKey guard**: la key de Ollama es la cadena `'ollama'` (6 chars). `length > 10` sin el guard bloqueará el guardado → `hasApiKey()` devuelve false.
- **Groq sept-2026**: modelos gratuitos: `openai/gpt-oss-20b` y `openai/gpt-oss-120b`. Los Llama pasaron a Enterprise.
