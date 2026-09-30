# Memory.md — PLATAFORMA_OpenCode
> Ultima actualizacion: 2026-09-30

## Estado actual

- **Fase**: Produccion / mantenimiento activo
- **Version**: Manual v3.0 (20 capitulos) + Manual IA Actas v1.0
- **Ultimo cambio significativo**: Wiki_CODANOR v1.0 — Open WebUI + Ollama + ChromaDB + 10 KBs + RAG verificado + OpenRouter configurado (2026-09-30)
- **Issues abiertos**: 72 bugs de reliability + 3 security hotspots detectados por SonarCloud

## Infraestructura

| Elemento | Estado | Detalle |
|----------|--------|---------|
| Git | Si | rama principal |
| GitHub | Si | github.com/Jfajeda/PLATAFORMA_OpenCode |
| SonarCloud | Si | Security A, Reliability B, Maintainability A, 3.5% duplications |
| .gitignore | Si | Excluye .DS_Store, backups, __pycache__ |
| AGENTS.md | Si | Actualizado 2026-09-30 — Wiki_CODANOR v1.0 + Open WebUI + OpenRouter |
| opencode.json | Si | MCP SonarQube configurado |
| Memory.md | Si | Este archivo |
| plataforma.db | Activa | 10 tablas, WAL mode, 298 clientes, 32 proyectos |
| server.py | Activo | Puerto 5001, HOST 0.0.0.0, ~3000 lineas, 19 endpoints tiquets + 3 endpoints corp LLM |
| dashboard_server.py | Activo | Puerto 5003, HOST 0.0.0.0, Panel de Control Dashboard |
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
| servidor/dashboard_server.py | Flask :5003 — Panel de Control Dashboard | ~4 KB |

### Plataforma_Seguimiento_Proyectos/servidor/

| Archivo | Descripcion | Estado |
|---------|-------------|--------|
| server.py | Flask app: motor proyectos + 19 endpoints tiquets + 3 endpoints corp LLM | ~3000 lineas |
| plataforma.db | SQLite WAL: 10 tablas, 11 indices explícitos | Activa |
| migration_tiquets.sql | DDL standalone v1.0→v1.4 con instrucciones backup | 147 lineas |
| uploads/tiquets/ | Archivos adjuntos de tiquets (max 10 MB por fichero) | Excluido Git |
| ARQUITECTURA_DB_SQLITE.html | Documentacion BD **unificada v1.4** — portada + TOC + 16 secciones + branding CODANOR | 116 KB |
| Manual_IA_Actas_Codanor.html | Manual usuario módulo IA en actas v1.0 | ~99 KB |
| requirements.txt | flask>=3.0.0, flask-cors>=4.0.0, python-docx>=1.0.0, openpyxl>=3.0.0 | — |

### Plataforma_Seguimiento_Proyectos — 9 apps ISO/ENS

| App | app_id | tiquets.js | phase2-*.js | llm.js | llm-models.js | phase3-audit.js |
|-----|--------|------------|-------------|--------|---------------|-----------------|
| ISO27001-SGSI | iso27001 | v=20260829f | v=20260925c | v=20260911h | v=20260911g | v=20260913a |
| ISO27701-SGP | iso27701 | v=20260829f | v=20260925c | v=20260911h | v=20260911g | v=20260913a |
| ISO42001-SGIA | iso42001 | v=20260829f | v=20260925c | v=20260911h | v=20260911g | v=20260913a |
| TISAX | tisax | v=20260829f | v=20260925c | v=20260911h | v=20260911g | v=20260913a |
| RGPD-LOPD-GDD | rgpd | v=20260829f | v=20260925c | v=20260911h | v=20260911g | v=20260913a |
| ENS-RD311-2022 | ens | v=20260829f | v=20260925c | v=20260911h | v=20260911g | v=20260913a |
| ISO9001-SGQ_2015 | iso9001 | v=20260829f | v=20260925c | v=20260911h | v=20260911g | v=20260913a |
| ISO14001-SGMA_2015 | iso14001 | v=20260829f | v=20260925c | v=20260911h | v=20260911g | v=20260913a |
| ISO14001-SGMA_2026_NEW | iso14001-2026 | v=20260829f | v=20260925c | v=20260911h | v=20260911g | v=20260913a |

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

### Archivos clave

| Archivo | Ruta | Descripcion |
|---------|------|-------------|
| `docker-compose.yml` | `~/Proyectos/Wiki_CODANOR/` | Compose: Open WebUI :3000, Ollama via host.docker.internal, nomic-embed-text embeddings |
| `vectordb/` | `~/Proyectos/Wiki_CODANOR/vectordb/` | ChromaDB persistente — contiene las 10 KBs |
| `webui.db` | `~/Proyectos/Wiki_CODANOR/vectordb/webui.db` | SQLite Open WebUI — usuarios, chats, configuracion |
| `Guia_Wiki_CODANOR_OpenWebUI.docx` | `PLATAFORMA_OpenCode-NEW/` | Guia corporativa completa (13 secciones, 43 tablas, 139 KB) |

### Arranque tras reinicio

```bash
# 1. Abrir Docker Desktop (Spotlight → Docker → esperar 🐳 estática)
# 2. En Terminal:
cd ~/Proyectos/Wiki_CODANOR && docker compose up -d
# 3. Abrir http://localhost:3000
```

El contenedor tiene `restart: unless-stopped` — si Docker Desktop estaba abierto antes del reinicio, arranca automaticamente.

### 10 Knowledge Bases

| KB | ID | Descripcion | Docs ingestados |
|----|-----|-------------|-----------------|
| ENS | a7874ff0-d216-4015-bf98-aa6fa67240b5 | Normas ENS RD 311/2022 — CCN-STIC, medidas Anexo II | 3 (CCN-STIC 808, 809, 819) ✅ RAG verificado |
| ISO27001 | — | ISO 27001 SGSI — controles, politicas, SOA | 0 |
| LOPD-RGPD | — | LOPD, RGPD, DPIA, derechos de interesados | 0 |
| NIS2 | — | Directiva NIS2, resiliencia cibernetica | 0 |
| Legislacion | — | Normativa legal aplicable (LSSI, LOPDGDD...) | 0 |
| Licitaciones | — | Pliegos, criterios adjudicacion, modelos | 0 |
| Logs-SIEM | — | Informes ciberseguridad, analisis logs | 0 |
| Actas | — | Actas de reunion, sintetizaciones IA | 0 |
| Plantilles | — | Plantillas Word/Excel corporativas CODANOR | 0 |
| OSINT | — | Informes OSINT, investigaciones | 0 |

### Configuracion LLM en Open WebUI

| Conexion | URL | Estado |
|----------|-----|--------|
| Ollama | `http://host.docker.internal:11434` | ✅ ON |
| OpenRouter | `https://openrouter.ai/api/v1` | ✅ ON |
| OpenAI default | `https://api.openai.com/v1` | ⚫ OFF (desactivado) |

### Reglas criticas

1. **RAG no es automatico** — hay que adjuntar la KB al chat: `+` → `Adjuntar coneixement` → seleccionar KB → ENTONCES escribir la pregunta. Sin este paso el modelo responde desde su conocimiento general.
2. **`nomic-embed-text` es solo para embeddings** — NUNCA seleccionarlo como modelo de chat. Usar `qwen3:8b` (predeterminado) o cualquier otro.
3. **Las KBs se conservan tras reinicio** — `vectordb/` es persistente en disco. Solo es necesario arrancar el contenedor.
4. **No migrar a PostgreSQL+pgvector** — decision tomada 2026-09-30: RAM insuficiente (0.4 GB libre), ChromaDB mas que suficiente para 10 KBs + equipo pequeno CODANOR. Revisar cuando haya 50+ usuarios concurrentes o 100k+ documentos.
5. **Modelo predeterminado**: `qwen3:8b` — configurado via "Establir com a predeterminat" en el selector.

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
Panel admin: `plataforma-seguimiento.html` → sidebar "Configuración IA" → `#page-llm-admin`

### Ollama local — modelos instalados

| Modelo | Tamaño | Uso recomendado |
|---|---|---|
| qwen2.5-coder:14b | 8.5 GB | Análisis técnico ISO/ENS — modelo por defecto |
| qwen3:8b | 5.0 GB | Uso general, resúmenes |
| llama3.1:latest | 4.7 GB | Actas, síntesis general |
| gemma3:4b | 3.2 GB | Rápido, bajo consumo RAM |

Para LAN: `OLLAMA_HOST=0.0.0.0 ollama serve` (actualmente solo localhost)

## Herramienta de Tiquets — Arquitectura completa (v1.0→v1.4)

### BD: plataforma.db — 10 tablas

**Tablas originales (4):**
- `clients` (298 filas) — clientes CODANOR × 9 normas
- `projects` (32 filas) — proyectos activos por norma
- `phase_data` (35 filas) — datos de fases en JSON
- `settings` — configuracion por app + config corp LLM (`app_id='_global'`, `key='corp_llm_config'`)

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

### Endpoints API REST (22 en total, puerto 5001)

19 endpoints tiquets (v1.0→v1.4) + 3 endpoints corp LLM (v3.0):

| Metodo | URL | Version |
|--------|-----|---------|
| GET | /api/corp/llm-config | v3.0 |
| POST | /api/corp/llm-config | v3.0 |
| DELETE | /api/corp/llm-config | v3.0 |
| GET | /api/tiquets/clientes | v1.0 |
| GET | /api/tiquets | v1.0 |
| POST | /api/tiquets | v1.0 |
| PUT | /api/tiquets/\<id\> | v1.0 |
| GET | /api/tiquets/\<id\>/acciones | v1.2 |
| POST | /api/tiquets/\<id\>/acciones | v1.2 |
| PUT | /api/tiquets/\<id\>/acciones/\<id\> | v1.2 |
| DELETE | /api/tiquets/\<id\>/acciones/\<id\> | v1.2 |
| GET | /api/tiquets/\<id\>/adjuntos | v1.3 |
| POST | /api/tiquets/\<id\>/adjuntos | v1.3 |
| DELETE | /api/tiquets/\<id\>/adjuntos/\<id\> | v1.3 |
| GET | /api/tiquets/\<id\>/exportar/word | v1.3 |
| GET | /api/tiquets/\<id\>/exportar/excel | v1.3 |
| POST | /api/tiquets/\<id\>/enviar-wiki | v1.4 |

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
| 2026-09-11 | llm.js: e.httpStatus preservado en callOpenAICompatible | _friendlyHttpError traduce antes del retry → regex no matchea |
| 2026-09-11 | GROQ_FALLBACK_CHAIN con modelos disponibles sept-2026 | llama-3.3-70b-versatile retirado de plan gratuito Groq |
| 2026-09-11 | Key corporativa LAN vía Flask settings | localStorage no se comparte entre PCs de la LAN |
| 2026-09-11 | Ollama como 4º proveedor local | Sin internet, sin coste, modelos locales instalados |
| 2026-09-11 | isOllamaKey guard en _syncLLMConfigFromForm | 'ollama' tiene 6 chars → length>10 bloqueaba el guardado |
| 2026-09-13 | phase3-audit.js: prompt 10k→25k chars, maxTokens 1200→2000 | Las NC suelen estar en la segunda mitad del informe |
| 2026-09-13 | phase3-audit.js: detección de intención NC (regex) | Prompt genérico devolvía respuestas vagas para preguntas sobre NC |
| 2026-09-13 | phase3-audit.js: render Markdown en respuesta wiki | white-space:pre-wrap no formateaba listas ni negritas |
| 2026-09-13 | checkOllamaLAN() en phase2-consulting.js | Verificar conectividad Ollama desde IP de LAN en tiempo real |
| 2026-09-17 | Botón NotebookLM dentro de wiki.js (no sidebar) | El acceso a NotebookLM es contextual al módulo Conocimiento |
| 2026-09-21 | Badge IA→C (CODANOR) en phase2-*.js | Imagen corporativa — no mostrar "IA" a clientes |
| 2026-09-25 | isOllamaKey en _syncLLMConfigFromForm × 9 apps | Bug en actas ENS: synthesizeMeeting activaba flujo manual con Ollama |
| 2026-09-30 | Wiki_CODANOR con ChromaDB embebido (no PostgreSQL+pgvector) | RAM insuficiente (0.4 GB libre), complejidad innecesaria para 10 KBs y equipo pequeño. Migrar solo si hay 50+ usuarios o 100k+ documentos |
| 2026-09-30 | Flask :5003 en dashboard_server.py dedicado | Separar el Dashboard del servidor principal :5001 para independencia de despliegue |
| 2026-09-30 | Modelo predeterminado Open WebUI: qwen3:8b | Mejor equilibrio calidad/velocidad para uso general CODANOR |
| 2026-09-30 | OpenRouter desactiva https://api.openai.com/v1 en Open WebUI | El endpoint OpenAI por defecto no tiene key válida — causa errores al cargar lista de modelos |

## Bugs criticos corregidos (2026-09-11 — Módulo LLM)

| Bug | Apps | Archivo | Causa | Solucion |
|-----|------|---------|-------|----------|
| "Missing Authentication header" con Groq | 5 consulting | phase2-consulting.js | Dos campos API Key desincronizados — _syncLLMConfigFromForm leía el campo oculto (dentro de `<details>`) en lugar del visible | Fix `#llm-key-main` + `#llm-key-advanced` + querySelector prioriza `#llm-key-main` |
| Retry automático nunca se activaba | 9 apps | llm.js | `_friendlyHttpError` traduce el mensaje antes del check `retryable` → la regex nunca matchea | Preservar `e.httpStatus` en el objeto Error + check numérico `[400,404,429].includes(e.httpStatus)` |
| Modelo incompatible con proveedor | 9 apps | llm.js + phase2-*.js | localStorage tenía `{provider:'groq', model:'gpt-4o-mini'}` — modelo de OpenAI enviado a Groq | Auto-corrección en `callLLM()` y `renderLLMConfig()` con tabla de fallbacks por proveedor |
| Groq retira modelos sin aviso | 9 apps | llm-models.js | llama-3.3-70b-versatile descomisionado; llama3-8b-8192 también retirado | GROQ_FALLBACK_CHAIN actualizada: openai/gpt-oss-20b (1º), openai/gpt-oss-120b (2º) |
| Key corporativa no disponible en LAN | 9 apps | llm.js + server.py | Config LLM en localStorage — no se comparte entre PCs | 3 endpoints Flask + deofuscación XOR+base64 en cliente |

## Bugs criticos corregidos (2026-09-11 — Ollama)

| Bug | Apps | Archivo | Causa | Solucion |
|-----|------|---------|-------|----------|
| Ollama falla con "Missing Auth" | 9 apps | llm.js | `baseCfg.apiKey` enviaba key antigua de Groq aunque proveedor fuera ollama | `apiKey: effectiveProvider === 'ollama' ? 'ollama' : cfg.apiKey.trim()` |
| Preset Ollama no borraba key anterior | 5+3 apps | phase2-consulting/implementation.js | `if (!cfg.apiKey || length <= 10)` no borraba keys largas de otros proveedores | `if (providerId === 'ollama') { cfg.apiKey = 'ollama'; }` siempre |
| Claves i18n no traducidas en modal Ollama | 9 apps | lang/es.json | `llmTagLocal` y `llmDescOllama` no definidas | Añadir a es.json de las 9 apps |

## Bugs criticos corregidos (2026-09-13 — Wiki consulta IA)

| Bug | Apps | Archivo | Causa | Solucion |
|-----|------|---------|-------|----------|
| Respuesta vaga para "No Conformidades" | 9 apps | phase3-audit.js | Texto truncado a 10k chars (NC en segunda mitad); prompt genérico | Ampliar a 25k chars + detección intención NC + systemPrompt especializado |
| Respuesta en texto plano sin formato | 9 apps | phase3-audit.js | `this._escape() + white-space:pre-wrap` ignoraba Markdown | `MarkdownUtil.toHtml()` + clase `markdown-body` |
| Claves i18n del modal no traducidas | 9 apps | lang/es.json | 8 claves `phase3.wikiConsult*` sin definir en ningún JSON | Añadir 21 claves wiki a es.json de las 9 apps |

## Bugs criticos corregidos (2026-09-25 — Actas con Ollama)

| Bug | Apps | Archivo | Causa | Solucion |
|-----|------|---------|-------|----------|
| `synthesizeMeeting` activa flujo manual con Ollama | 9 apps | phase2-consulting/implementation/isms.js | `_syncLLMConfigFromForm` no guardaba `'ollama'` (6 chars) porque `length > 10` era false → `hasApiKey()` devolvía false | Guard `isOllamaKey` en la condición de guardado de apiKey |

## Pendiente

- [x] ~~Corregir bugs de reliability de SonarCloud~~ (37 de ~55 corregidos)
- [ ] Corregir los 18 innerHTML restantes (security hotspots de SonarCloud)
- [x] ~~Instalar Node.js en el Mac~~ (v24.21.0 instalado)
- [ ] Ejecutar /init en los 7 proyectos restantes para crear AGENTS.md
- [ ] Subir los otros 7+ proyectos a GitHub
- [ ] Conceder "Acceso total al disco" en Ajustes → Privacidad para backup NAS
- [ ] Regenerar token SonarCloud
- [x] ~~Herramienta de Tiquets v1.0→v1.4~~ (implementada 2026-08-28/29)
- [x] ~~ARQUITECTURA_DB_SQLITE.html~~ (unificada v1.4 2026-09-03)
- [x] ~~Módulo Mapa de Procesos v1.0~~ (commit eb628fe 2026-09-04)
- [x] ~~Mejora Seguimiento de Tareas v2.0~~ (commit e0c1a08 2026-09-06)
- [x] ~~Fix LAN persistencia BD~~ (commit e0c1a08 2026-09-06)
- [x] ~~Fix navegabilidad Acciones de Resolución~~ (commit 688fead 2026-09-21)
- [x] ~~Badge IA→C (CODANOR)~~ (commit 688fead 2026-09-21)
- [x] ~~Módulo IA/LLM v1.0~~ (2026-09-04 — flujo manual + fallback)
- [x] ~~Módulo IA/LLM v2.0~~ (2026-09-11 — fix retry + key corp + GROQ_FALLBACK_CHAIN)
- [x] ~~Módulo IA/LLM v3.0~~ (2026-09-25 — Ollama local + isOllamaKey fix × 9 apps)
- [x] ~~Key corporativa LAN~~ (2026-09-11 — servidor Flask + panel admin plataforma-seguimiento)
- [x] ~~Manual IA Actas~~ (2026-09-10 — Manual_IA_Actas_Codanor.html en Plataforma_Seguimiento)
- [x] ~~Mejora consulta Wiki con IA~~ (2026-09-13 — 25k chars, detección NC, Markdown, sugerencias)
- [x] ~~Wiki_CODANOR v1.0~~ (Open WebUI :3000 + Ollama + ChromaDB + 10 KBs + RAG verificado + OpenRouter — 2026-09-30)
- [x] ~~Guia_Wiki_CODANOR_OpenWebUI.docx~~ (13 secciones, 43 tablas, 139 KB — commit `1195855` 2026-09-30)
- [x] ~~Flask :5003 dashboard_server.py~~ (Panel de Control en puerto dedicado — 2026-09-30)
- [ ] Probar Mapa de Procesos en LAN desde segundo PC
- [ ] Verificar exportación PDF del mapa (jsPDF CDN) en cada app
- [ ] Activar Ollama en LAN (`OLLAMA_HOST=0.0.0.0 ollama serve`) — bloqueado por firewall MDM
- [ ] Configurar Key corporativa desde panel `plataforma-seguimiento.html` → "Configuración IA"
- [ ] Probar acciones de tarea desde segundo PC LAN
- [ ] Verificar exportación Word con columna Acciones en proyectos con datos reales
- [ ] Ingestar documentos en 9 KBs restantes (ISO27001, LOPD-RGPD, NIS2, OSINT, Logs-SIEM...)
- [ ] Script automático de ingesta por API Open WebUI (ingest_nas.py en Wiki_CODANOR/scripts/)

## Notas y descubrimientos

- **OpenCode queda bloqueado** si su directorio de trabajo se elimina o mueve.
- **El usuario NO tiene Node.js, Homebrew ni GitHub CLI**. Git push requiere autenticacion manual.
- **SonarCloud token**: regenerar desde sonarcloud.io > My Account > Security.
- **Puerto 5000** en macOS puede estar ocupado por AirPlay Receiver. Usar 5001.
- **python-docx 1.2.0 y openpyxl 3.1.5** instalados en el sistema.
- **IndexedDB de la wiki** vive exclusivamente en el navegador — no se sincroniza con plataforma.db.
- **LAN**: servidor Flask sirve en HOST 0.0.0.0:5001. IP actual: 192.168.98.44. Todos los módulos usan `window.location.hostname` para auto-detectar la IP.
- **Ollama**: escucha en localhost:11434 por defecto. Para LAN requiere `OLLAMA_HOST=0.0.0.0`. Modelos instalados: qwen2.5-coder:14b (8.5GB), qwen3:8b (5GB), llama3.1:latest (4.7GB), gemma3:4b (3.2GB). Versión: v0.34.4.
- **Wiki_CODANOR**: Open WebUI :3000 en Docker (contenedor `wiki-codanor`). ChromaDB vectordb/ persistente en disco — las KBs sobreviven reinicios. Arranque: `cd ~/Proyectos/Wiki_CODANOR && docker compose up -d`. RAG requiere adjuntar KB explícitamente en el chat (`+` → `Adjuntar coneixement`). `nomic-embed-text` solo para embeddings — NO para chat.
- **OpenRouter en Open WebUI**: configurado en Paràmetres → Connexions → API d'OpenAI → `https://openrouter.ai/api/v1`. `https://api.openai.com/v1` desactivado (sin key válida).
- **No PostgreSQL+pgvector** para Wiki_CODANOR: decision tomada 2026-09-30. RAM disponible insuficiente (0.4 GB libre), ChromaDB embebido cubre el caso de uso actual. Revisar si hay 50+ usuarios concurrentes o 100k+ documentos.
- **Key corporativa LLM**: guardada ofuscada (XOR+base64) en `settings` WHERE `app_id='_global'` AND `key='corp_llm_config'`. La clave de ofuscación es el hostname del servidor (socket.gethostname()). El cliente JS deofusca usando `window.location.hostname`.
- **`isOllamaKey` guard**: la key de Ollama es la cadena literal `'ollama'` (6 chars). Cualquier condición `length > 10` sin el guard `isOllamaKey` bloqueará el guardado → `hasApiKey()` devolverá false → flujo manual incorrecto. **Afecta a los 3 tipos de phase2**: consulting, implementation e isms.
- **Groq sept-2026**: los modelos Llama (llama-3.3-70b-versatile, llama-3.1-8b-instant) pasaron a plan Enterprise. Los únicos modelos gratuitos ahora son `openai/gpt-oss-20b` y `openai/gpt-oss-120b`.
- **phase3-audit.js**: el modal "Consultar documento con IA" usa 25.000 chars de contexto y detecta automáticamente preguntas sobre NC para activar un systemPrompt especializado. La respuesta se renderiza con MarkdownUtil.
- **SyntaxError con \'**: el escape `\'` solo es válido dentro de strings JS. Siempre usar comillas simples sin escape en expresiones.
- **localStorage es por origen**: `localhost:5001` y `127.0.0.1:5001` son orígenes distintos. Con PHASE_KEYS el servidor Flask es siempre la fuente de verdad.
- **ISO9001 ≠ ISO14001 en phase2-implementation.js**: ISO9001 usa `window.ACTIVITY_GROUPS`; ISO14001 usa `window.CLAUSE_GROUPS`. NUNCA propagar con cp/sed entre ambas apps.


## Estado actual

- **Fase**: Produccion / mantenimiento activo
- **Version**: Manual v3.0 (20 capitulos)
- **Ultimo cambio significativo**: Fix navegabilidad Acciones de Resolución + badge IA→C (CODANOR) en phase2-*.js + report-builders.js × 9 apps + rediseño pantalla de inicio servidor (commit `688fead` 2026-09-21)
- **Issues abiertos**: 72 bugs de reliability + 3 security hotspots detectados por SonarCloud

## Infraestructura

| Elemento | Estado | Detalle |
|----------|--------|---------|
| Git | Si | rama principal |
| GitHub | Si | github.com/Jfajeda/PLATAFORMA_OpenCode |
| SonarCloud | Si | Security A, Reliability B, Maintainability A, 3.5% duplications |
| .gitignore | Si | Excluye .DS_Store, backups, __pycache__ |
| AGENTS.md | Si | Actualizado 2026-09-21 — fix navegabilidad acciones + badge IA→C + diseño inicio |
| opencode.json | Si | MCP SonarQube configurado |
| Memory.md | Si | Este archivo |
| plataforma.db | Activa | 10 tablas, WAL mode, 298 clientes, 32 proyectos, 11 reuniones ISO9001 |
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
| DOCS/informes/Estructura_Funcional_Fases_Plataforma.docx | Mapa funcional 9 apps — fases, subtabs, PHASE_KEYS (135 KB, A4 landscape, 18 tablas) | — |

### Plataforma_Seguimiento_Proyectos — 9 apps ISO/ENS

| App | app_id | tiquets.js version | phase2-*.js version | store.js / app.js version |
|-----|--------|--------------------|--------------------|---------------------------|
| ISO27001-SGSI | iso27001 | v=20260829f | v=20260904d | v=20260904c | wiki: 08a653c8 |
| ISO27701-SGP | iso27701 | v=20260829f | v=20260904d | v=20260904c | wiki: 712c0d43 |
| ISO42001-SGIA | iso42001 | v=20260829f | v=20260904d | v=20260904c | wiki: 5aa74c2f |
| TISAX | tisax | v=20260829f | v=20260904d | v=20260904c | wiki: cc0bc464 |
| RGPD-LOPD-GDD | rgpd | v=20260829f | v=20260904d | v=20260904c | wiki: c29543b1 |
| ENS-RD311-2022 | ens | v=20260829f | v=20260904d | v=20260904c | wiki: cc64cac9 |
| ISO9001-SGQ_2015 | iso9001 | v=20260829f | v=20260904d | v=20260904c | wiki: 9acf987b |
| ISO14001-SGMA_2015 | iso14001 | v=20260829f | v=20260904d | v=20260904c | wiki: aee7844a |
| ISO14001-SGMA_2026_NEW | iso14001-2026 | v=20260829f | v=20260904d | v=20260904c | wiki: 1ffdd2cc |

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
| 2026-09-06 | acciones[] en modelo de tarea (phase2-*.js) | Necesidad de registrar pasos concretos de resolución por tarea, más allá del historial de estados |
| 2026-09-06 | PHASE_KEYS constante en store.js × 9 apps | Lista hardcoded de fases era genérica — ISO9001/ISO14001 usan gap/implementation/audit, no phase1-5. Sin PHASE_KEYS los datos del servidor nunca se precargaban en LAN |
| 2026-09-06 | Store.PHASE_KEYS[0] como sonda de caché en app.js | '_phase2' hardcoded nunca tenía datos en ISO9001/ISO14001 — shortcut de navegación siempre fallaba y _preloadProject se llamaba innecesariamente en cada clic |
| 2026-09-06 | ISO9001 phase2-implementation.js restaurado desde HEAD y modificado quirúrgicamente | Propagación directa desde ISO14001 sobreescribía ACTIVITY_GROUPS → Error: No se encontraron datos de actividades |
| 2026-09-06 | Documento Estructura_Funcional_Fases_Plataforma.docx | Referencia completa de arquitectura funcional de las 9 apps — necesaria para onboarding y nuevas normas |

| 2026-09-17 | Botón NotebookLM dentro de la toolbar de Conocimiento (wiki.js) | El botón en el sidebar raíz era incorrecto — el acceso a NotebookLM es contextual al módulo Conocimiento |
| 2026-09-17 | URL NotebookLM específica por norma | Cada norma tiene su propio Notebook en Google NotebookLM con documentación especializada; ISO14001-2015 usa el notebook genérico CODANOR |

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

## Bugs criticos corregidos (2026-09-06, commit `e0c1a08`)

| Bug | App | Archivo | Causa | Solucion |
|-----|-----|---------|-------|----------|
| "Sin datos" en Consultoría al abrir desde otro PC LAN | ISO9001, ISO14001-2015, ISO14001-2026 | store.js + app.js | store.js precargaba `phase2` pero los datos reales están en `implementation`. app.js usaba `'_phase2'` como sonda de caché → siempre vacío → datos nunca sincronizados del servidor | PHASE_KEYS por norma + Store.PHASE_KEYS[0] en app.js |
| "Sin datos" en módulos RGPD desde otro PC LAN | RGPD-LOPD-GDD | store.js | rat, eipd, brechas, derechos no estaban en la lista de preload | Añadir a PHASE_KEYS de RGPD |
| "Error: No se encontraron datos de actividades" | ISO9001-SGQ_2015 | phase2-implementation.js | Propagación desde ISO14001 sobreescribió `ACTIVITY_GROUPS` por `CLAUSE_GROUPS` | Restaurar desde HEAD y aplicar cambios quirúrgicamente |
| Datos de Consultoría ISO9001 vacíos tras cambio localhost→127.0.0.1 | ISO9001-SGQ_2015 | store.js | localStorage es por origen — `localhost:5001` ≠ `127.0.0.1:5001`. Sin PHASE_KEYS el servidor tampoco se consultaba | Fix _apiBase + PHASE_KEYS carga siempre del servidor |

## Bugs criticos corregidos (2026-09-21, commit `688fead`)

| Bug | App | Archivo | Causa | Solucion |
|-----|-----|---------|-------|----------|
| Subpanel "Acciones de resolución" se cierra al editar | Todas × 9 | phase2-*.js `updateTaskAction` | `_refreshTasksPanel()` se llamaba para CUALQUIER campo incluyendo texto libre → DOM reconstruido → subpanel vuelve a `display:none` → usuario pierde foco y datos en edición | Condicionar refresco a `['estado','tipo','prioridad']`. Para texto libre (`titulo`, `descripcion`, `responsable`, `notaCierre`, `verificadoPor`, `fechaLimite`) solo `save()` — sin refresco DOM |
| Badge "IA" visible para clientes (imagen corporativa) | Todas × 9 | phase2-*.js + report-builders.js | El badge mostraba "IA" (Inteligencia Artificial) junto al título de tareas extraídas por LLM — algunos clientes no ven con buenos ojos la intervención de IA | Cambiar badge `>IA<` → `>C<` con `title="CODANOR"` en todos los archivos. En exportación Word: `[IA]` → `[C]` |

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
- [x] ~~Mejora Seguimiento de Tareas v2.0~~ (acciones[], inputs inline, exportación Word — commit e0c1a08 2026-09-06)
- [x] ~~Fix LAN persistencia BD~~ (PHASE_KEYS en store.js × 9 apps, app.js sonda correcta — commit e0c1a08 2026-09-06)
- [x] ~~Documento Estructura Funcional Fases~~ (DOCS/informes/Estructura_Funcional_Fases_Plataforma.docx — commit e0c1a08 2026-09-06)
- [ ] Probar acciones de tarea desde segundo PC LAN
- [ ] Verificar exportación Word con columna Acciones en proyectos con datos reales
- [x] ~~Fix navegabilidad Acciones de Resolución~~ (subpanel no se cierra al editar — commit 688fead 2026-09-21)
- [x] ~~Badge IA→C (CODANOR) en phase2-*.js + report-builders.js × 9 apps~~ (commit 688fead 2026-09-21)
- [x] ~~Rediseño tarjetas pantalla de inicio servidor~~ (tooltip flotante JS, iconos texto corporativos — commits 8b12a42 5e2c70a 32c43cd b2486c5 e1272bf 2026-09-21)

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
- **LAN**: el servidor Flask sirve en HOST 0.0.0.0:5001. IP actual: 192.168.98.44. tiquets.js usa window.location.hostname para auto-detectar la IP correcta desde cualquier equipo de la red.
- **Mapa de Procesos**: el módulo usa `phase_data` (clave `'mapa_procesos'`) para persistir en plataforma.db. `phase_data` es un store clave-valor JSON libre — el servidor no valida su contenido. El mapa original (`mapa_procesos.html`) usaba IndexedDB (local al navegador), incompatible con LAN multiusuario.
- **SyntaxError con \'**: el escape `\'` solo es válido dentro de strings JS. En expresiones ternarias `(a === \'b\')` produce SyntaxError silencioso que descarta todo el script. Siempre usar comillas simples sin escape en expresiones: `(a === 'b')`.
- **localStorage es por origen**: `localhost:5001` y `127.0.0.1:5001` son orígenes distintos para el navegador. Los datos guardados en uno NO son visibles desde el otro. Con PHASE_KEYS el servidor Flask es siempre la fuente de verdad independientemente del origen.
- **PHASE_KEYS[0] como sonda de caché**: la primera fase de PHASE_KEYS determina si hay datos en caché al abrir un proyecto. Para ISO9001/ISO14001 es `'gap'`; para consulting es `'phase1'`; para TISAX es `'phase2'`. Si se añade una nueva norma, asegurarse de que PHASE_KEYS[0] sea una fase que tenga datos desde el principio del proyecto.
- **ISO9001 ≠ ISO14001 en phase2-implementation.js**: ISO9001 usa `window.ACTIVITY_GROUPS`; ISO14001 usa `window.CLAUSE_GROUPS`. NUNCA propagar un archivo completo de uno al otro con cp/sed — siempre aplicar cambios quirúrgicos.
- **updateTaskAction y _refreshTasksPanel**: el refresco del DOM solo debe ocurrir para los campos `estado`, `tipo` y `prioridad` (cambian elementos visibles en la tabla exterior). Para campos de texto libre (`titulo`, `descripcion`, `responsable`, `notaCierre`, `verificadoPor`, `fechaLimite`) solo ejecutar `save()` — si se llama `_refreshTasksPanel()` el subpanel se inicializa con `display:none` y el usuario pierde el foco y lo que estaba escribiendo.
- **Badge IA→C**: el campo `origen: 'ia'` en las tareas se conserva intacto en la BD. Solo cambia la presentación visual del badge (texto y tooltip). Al exportar Word: `[C]` en lugar de `[IA]`.
