# AGENTS.md — PLATAFORMA_OpenCode

> Instructions for AI coding agents operating in this repository.
> Maintained by Jafa, S.L. (CODANOR), Barcelona, Catalunya.
> Last updated: 2026-09-25

## Project Overview

This repository contains documentation and tooling for the OpenCode platform
used internally at CODANOR. It includes a corporate HTML manual (20 chapters),
a Kanban issue tracker, a SonarCloud analysis panel, a module homogenization
plan, a backup script, OpenCode slash commands, and the technical proposal for
the Tiquets tool (v1.2).

The **Tiquets module** is the most active component: a full-stack ticketing
system integrated into `plataforma.db` (SQLite) served by Flask on port 5001,
deployed across all 9 ISO/ENS apps and in `plataforma-seguimiento.html`.

The **IA/LLM module** (v3.0 — 2026-09-25) is the second most active component:
full integration of LLM providers (Groq, OpenAI, OpenRouter, Google, Anthropic,
Ollama) for meeting synthesis, acta summaries and wiki document queries across
all 9 apps, with corporate key sharing via Flask.

## Build / Lint / Test Commands

```bash
# Start the Plataforma backend (required for Tiquets, Exports, Uploads, Corp LLM)
cd ~/Proyectos/Plataforma_Seguimiento_Proyectos/servidor
python3 server.py
# → http://localhost:5001  (HOST 0.0.0.0 — LAN accessible)
# → http://192.168.3.168:5001 (current LAN IP)

# Verify DB integrity
sqlite3 servidor/plataforma.db "PRAGMA integrity_check;"

# Check all 10 tables exist
sqlite3 servidor/plataforma.db \
  "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"

# Verify tiquets module (9 apps)
python3 -c "
import re, os
from collections import Counter
BASE='~/Proyectos/Plataforma_Seguimiento_Proyectos'
for app in ['ISO27001-SGSI','RGPD-LOPD-GDD','ENS-RD311-2022']:
    src=open(f'{BASE}/{app}/js/modules/tiquets.js').read()
    dups={k:v for k,v in Counter([m[1] for m in re.findall(r'^\s{2}(async\s+)?(\w+)\s*\(',src,re.MULTILINE)]).items() if v>1}
    print(app, 'dups:', dups if dups else 'NONE')
"

# Verify LLM module versions across 9 apps
python3 -c "
import re
BASE='/Users/jaimefajeda/Proyectos/Plataforma_Seguimiento_Proyectos'
APPS = {
    'ENS-RD311-2022': 'phase2-consulting.js',
    'ISO27001-SGSI': 'phase2-consulting.js',
    'ISO14001-SGMA_2015': 'phase2-implementation.js',
    'ISO9001-SGQ_2015': 'phase2-implementation.js',
    'TISAX': 'phase2-isms.js',
}
for app, mod in APPS.items():
    idx = open(f'{BASE}/{app}/index.html').read()
    m = re.search(rf'{re.escape(mod)}\?v=([^\"]+)', idx)
    fix = open(f'{BASE}/{app}/js/modules/{mod}').read().count('isOllamaKey')
    print(f'{app}: {m.group(1) if m else \"NO VER\"} | ollama_fix={fix}')
"

# Test Ollama LAN connectivity
curl -s http://localhost:11434/api/version
curl -s http://localhost:11434/api/tags | python3 -c \
  'import json,sys; [print(m[\"name\"]) for m in json.load(sys.stdin).get(\"models\",[])]'

# Test Corp LLM endpoint
curl -s http://localhost:5001/api/corp/llm-config
```

## Repository Structure

```
PLATAFORMA_OpenCode-NEW/
  AGENTS.md                               # This file — agent instructions
  Memory.md                               # Project state, history, pending tasks
  opencode.json                           # OpenCode config (MCP SonarQube)
  .gitignore                              # Git exclusions
  Manual_OpenCode_Codanor.html            # Corporate manual v3.0 (20 chapters, ~137 KB)
  Manual_IA_Actas_Codanor.html            # Manual IA módulo actas v1.0 (~99 KB, 10 secciones)
  plataforma-seguimiento.html             # Dashboard + Kanban + Tiquets + Config IA Corp (~98 KB)
  analisis-codigo.html                    # SonarCloud analysis panel (~46 KB)
  plan-homogeneizacion-modulos.html       # Module homogenization plan (~72 KB)
  homogeneizacion-proyectos.html          # Project homogenization dashboard (~46 KB)
  propuesta-herramienta-tiquets.html      # Tiquets tool proposal v1.2 (~98 KB)
  backup-opencode.sh                      # Backup script (8 modes, executable)
  sonar-project.properties                # SonarCloud scanner config
  Prompt.docx                             # Project prompt specification
  Estructura_PROYECTOS.pdf                # Module hierarchy diagram
  Biblioteca/                             # Screenshots and reference images
  .opencode/
    commands/
      sonar.md                            # Slash command /sonar
      sonar-report.md                     # Slash command /sonar-report
    package.json                          # OpenCode plugin dependency
```

## Critical Architecture — Tiquets Module

### Backend (Plataforma_Seguimiento_Proyectos/servidor/)

| File | Role |
|---|---|
| `server.py` | Flask app, port 5001, HOST 0.0.0.0. Contains ALL routes including 19 tiquets endpoints + 3 corp LLM endpoints. **~3000 lines** — do NOT create a separate file. |
| `plataforma.db` | SQLite WAL. **10 tables**: 4 original + 6 tiquets. See ARQUITECTURA_DB_SQLITE.html. |
| `migration_tiquets.sql` | DDL standalone v1.0→v1.4. Safe to re-run (IF NOT EXISTS). |
| `uploads/tiquets/` | Physical files for ticket attachments. Max 10 MB. Excluded from Git. |

### DB Tables — plataforma.db (10 tables)

**Original (4):** `clients` (298) · `projects` (32) · `phase_data` (35) · `settings` (corp LLM config stored here under app_id='_global', key='corp_llm_config')

**Tiquets module (6):**

| Table | Version | Description |
|---|---|---|
| `contadores_tiquets` | v1.0 | Atomic NNN counter per (client_id, app_id) |
| `tiquets` | v1.0+v1.4 | Main table. 22 columns incl. `wiki_article_id` (ALTER TABLE v1.4) |
| `tiquets_historial` | v1.0 | Field-by-field audit log (ISO 27001 A.16) |
| `tiquets_comentarios` | v1.0 | Free-text follow-up log |
| `tiquets_acciones` | v1.2 | Resolution actions: pendiente→en_curso→resuelta |
| `tiquets_adjuntos` | v1.3 | File attachments stored in uploads/tiquets/ |

**Ticket ID format:** `TIK-{NNN:03d}-{client_id}-{app_id}-{DD-MM-AAAA}`

### Frontend — 9 ISO/ENS apps

Each app under `Plataforma_Seguimiento_Proyectos/` has:

| File | Role |
|---|---|
| `js/modules/tiquets.js` | TiquetsModule object. **Do NOT create duplicated methods.** Always check for duplicates after editing. Current version: `v=20260829f` |
| `js/wiki-categories.js` | Category definitions. **Balance of `{}`  in WIKI_CATEGORIES array MUST be 0.** Category `resolved_ticket` added as last item with proper `,` after previous item. |
| `index.html` | References `tiquets.js?v=20260829f`. Bump version letter on every change. |

### Frontend — plataforma-seguimiento.html

- Sidebar section **ACCIONES** → "Gestor de Tiquets" + "Configuración IA"
- Page `#page-tickets` outside the SPA container (uses `visibility:hidden` trick)
- Page `#page-llm-admin` outside the SPA container — corporate LLM key panel
- `TK_API` auto-detects host for LAN: `window.location.hostname + ':5001'`
- Offline fallback: `localStorage` key `codanor_tiquets_v2`

### Key tiquets.js methods (DO NOT DUPLICATE)

```
_apiBase(), _loadLocal(), _saveLocal(), _detectar(), init(),
_cargar(), _filtrarLocal(), _crear(), _actualizar(), _comentar(),
_cargarDetalle(), _actualizarContador(), _sincronizar(),
_renderSelectores(), _renderSelectorProyecto(), _renderTabla(),
_toggleDetalle(), _renderDetalle(), _crearAccion(),
_actualizarAccion(), _eliminarAccion(), _subirAdjuntos(),
_eliminarAdjunto(), _exportarTiquet(), _exportar(),
_actualizarEstadoTiquet(), _abrirModalWiki(), _cerrarModalWiki(),
_confirmarPasarAConocimiento(), _generarMarkdownWiki(),
_abrirModal(), _cerrarModal(), _guardarModal(), _recargar()
```

### Wiki / Knowledge Base integration (v1.4)

- `wiki_article_id TEXT DEFAULT NULL` in `tiquets` table (ALTER TABLE)
- Button "📚 Pasar a Conocimiento" appears **only when `estado === 'cerrado'`**
- Button "✓ Cerrar Tiquet" appears when `estado === 'resuelto'`
- `Store.saveWikiArticle()` creates article in IndexedDB (browser)
- `POST /api/tiquets/<id>/enviar-wiki` registers the wiki ID server-side (HTTP 409 if already sent)
- Category `resolved_ticket` "BD de Tiquets Resueltos" added to `wiki-categories.js` in all 9 apps
- **IMPORTANT**: `wiki_article_id` balance in `wiki-categories.js` WIKI_CATEGORIES array must be 0. The `resolved_ticket` item must be inserted INSIDE the array with proper `,` separator.

## Módulo IA/LLM (v3.0 — 2026-09-25)

### Arquitectura — 3 capas

```
llm-models.js   → Catálogo de proveedores y modelos. GROQ_FALLBACK_CHAIN + OLLAMA_FALLBACK_CHAIN.
llm.js          → Motor de llamadas. getConfig() con prioridad: personal > corporativa > default.
phase2-*.js     → UI: panel de configuración, presets, synthesizeMeeting, generateActaSummary.
```

### Proveedores soportados (llm-models.js)

| ID | Nombre | URL base | Gratuito | Notas |
|---|---|---|---|---|
| `groq` | Groq (Gratis) | `https://api.groq.com/openai/v1` | ✅ | Key `gsk_...`. Modelos: `openai/gpt-oss-20b`, `openai/gpt-oss-120b` |
| `openrouter` | OpenRouter (Gratis) | `https://openrouter.ai/api/v1` | ✅ | Key `sk-or-...`. Alias `openrouter/free` con fallback automático |
| `google` | Google Gemini | generativelanguage.googleapis.com | ✅ | Key `AIza...`. Modelos: `gemini-2.0-flash` |
| `openai` | OpenAI (GPT) | `https://api.openai.com/v1` | ❌ | Key `sk-...`. CORS solo desde servidor web |
| `anthropic` | Anthropic (Claude) | `https://api.anthropic.com` | ❌ | Key `sk-ant-...`. API format distinto |
| `ollama` | Ollama (Local) | `http://localhost:11434/v1` | ✅ | Sin key. URL auto-adapta a `window.location.hostname` para LAN |

### Cadenas de fallback automático

```javascript
GROQ_FALLBACK_CHAIN: [
  'openai/gpt-oss-20b',      // 1º — gratuito, 1000 t/s
  'openai/gpt-oss-120b',     // 2º — gratuito, 500 t/s
  'llama-3.3-70b-versatile', // 3º — Enterprise
  'llama-3.1-8b-instant',    // 4º — Enterprise
]

FREE_FALLBACK_CHAIN (OpenRouter):  // 5 modelos :free
OLLAMA_FALLBACK_CHAIN: [
  'qwen2.5-coder:14b',       // 1º — mejor calidad
  'qwen3:8b',                // 2º — uso general
  'llama3.1:latest',         // 3º — estable
  'gemma3:4b',               // 4º — ligero
]
```

### Prioridad de API Key (llm.js getConfig())

```
1º localStorage personal (key > 10 chars, o provider === 'ollama')
2º Config corporativa del servidor (GET /api/corp/llm-config, XOR ofuscada)
3º Default vacío (muestra panel de configuración)
```

### Config corporativa — server.py

```python
GET  /api/corp/llm-config   → devuelve config con key XOR+base64 ofuscada
POST /api/corp/llm-config   → guarda config (key ofuscada antes de guardar)
DELETE /api/corp/llm-config → elimina (vuelve a localStorage)
# Almacenada en: settings WHERE app_id='_global' AND key='corp_llm_config'
```

**Panel admin en `plataforma-seguimiento.html`:** sidebar "Configuración IA" → abre `#page-llm-admin`.

### Reglas críticas del módulo LLM

1. **Nunca hardcodear `localhost`** en URLs de LLM — usar `window.location.hostname` para LAN.

2. **`_syncLLMConfigFromForm()`** — la condición de guardado de API Key **debe incluir Ollama**:
   ```javascript
   // CORRECTO (las 9 apps deben tener este patrón):
   if (key && key.value) {
     const isOllamaKey = cfg.provider === 'ollama' || key.value.trim() === 'ollama';
     if (isOllamaKey || key.value.trim().length > 10) cfg.apiKey = key.value.trim();
   }
   ```
   Si se usa `length > 10` sin el guard `isOllamaKey`, Ollama falla silenciosamente (su key `'ollama'` tiene 6 chars).

3. **Auto-corrección de modelo incompatible** — `renderLLMConfig()` y `callLLM()` corrigen automáticamente si el modelo guardado no pertenece al proveedor configurado. La tabla de fallbacks está en `llm.js` callLLM():
   ```javascript
   const fallbacks = {
     groq: LLMModels.GROQ_FALLBACK_CHAIN[0],
     openrouter: 'openrouter/free',
     google: 'gemini-2.0-flash',
     openai: 'gpt-4o-mini',
     anthropic: 'claude-3-5-haiku-20241022',
     ollama: LLMModels.OLLAMA_FALLBACK_CHAIN[0]
   };
   ```

4. **`retryable` en `callLLM`** — usa `e.httpStatus` (preservado en `callOpenAICompatible`) para detectar 400/404/429. La regex sobre el mensaje traducido es insuficiente porque `_friendlyHttpError` transforma el texto antes del retry.

5. **Ollama en LAN** requiere `OLLAMA_HOST=0.0.0.0 ollama serve`. Por defecto solo escucha en `localhost:11434`.

6. **Versión actual** de los archivos LLM en las 9 apps:
   - `llm-models.js?v=20260911g`
   - `llm.js?v=20260911h`
   - `phase2-consulting.js?v=20260925c` (5 apps consulting)
   - `phase2-implementation.js?v=20260925c` (3 apps implementation)
   - `phase2-isms.js?v=20260925c` (TISAX)
   - `phase3-audit.js?v=20260913a` (9 apps)

7. **Al propagar `phase2-consulting.js`** entre las 5 apps consulting, usar Python (no `cp`) para preservar las diferencias de `appId` y claves específicas de cada norma.

8. **`phase2-implementation.js`** — ISO9001 usa `ACTIVITY_GROUPS`; ISO14001 usa `CLAUSE_GROUPS`. **NUNCA propagar con `cp`** entre ambas apps — siempre editar quirúrgicamente.

### Funciones IA disponibles en actas

| Función | Módulo | Descripción |
|---|---|---|
| `generateActaSummary(idx)` | phase2-consulting.js | Resumen 3-5 puntos de un acta .docx subida (pestaña Diseño) |
| `generateGlobalSummary()` | phase2-consulting.js | Resumen ejecutivo de todas las actas del proyecto |
| `synthesizeMeeting(idx)` | phase2-consulting/isms/implementation.js | JSON con info + acuerdos + tareas de una reunión (pestaña Seguimiento) |
| `detectOllamaModels()` | phase2-consulting/isms.js | Consulta `http://{hostname}:11434/api/tags` y actualiza datalist |
| `checkOllamaLAN()` | phase2-consulting.js | Verifica si Ollama es accesible desde la IP de LAN |
| `consultarWikiDoc(id)` | phase3-audit.js | Modal "Consultar documento con IA" (WIKI Experiencias Fase 3) |
| `_ejecutarConsultaWiki(id)` | phase3-audit.js | Descarga doc → extrae texto → llama LLM. 25k chars, 2000 tokens, detección intención NC |

### Manual de usuario — Manual_IA_Actas_Codanor.html

Ubicación: `/Users/jaimefajeda/Proyectos/Plataforma_Seguimiento_Proyectos/Manual_IA_Actas_Codanor.html`

10 secciones: qué es la IA, proveedores, obtener key, configurar, actas Diseño, sintetizar Seguimiento, flujo sin key, errores frecuentes, FAQ, glosario. Portada fullscreen + TOC sidebar fijo + cabecera fija + pie de página + `@media print` A4.

## Módulo Mapa de Procesos (v1.0 — 2026-09-04)

### Arquitectura

- **Archivo**: `js/modules/mapa-procesos.js` en cada una de las 9 apps (commit `eb628fe`)
- **Origen**: motor visual portado de `~/Proyectos/Mapa_Procesos/mapa_procesos.html` v1.0.0
- **Persistencia**: Flask SQLite via `phase_data` — **NO usar IndexedDB** (local al navegador, no funciona en LAN multiusuario)
  - Clave: `(project_id, app_id, 'mapa_procesos')`
  - Endpoint: `GET/POST /api/{appId}/phase/{projectId}/mapa_procesos`
  - El servidor ya lo soporta sin cambios — `phase_data` acepta clave libre
- **Versión en index.html**: `mapa-procesos.js?v=20260903a`

### appId por app

| App | appId | Módulo phase2 |
|---|---|---|
| ISO27001-SGSI | `iso27001` | phase2-consulting.js |
| ENS-RD311-2022 | `ens` | phase2-consulting.js |
| ISO27701-SGP | `iso27701` | phase2-consulting.js |
| ISO42001-SGIA | `iso42001` | phase2-consulting.js |
| RGPD-LOPD-GDD | `rgpd` | phase2-consulting.js |
| ISO14001-SGMA_2015 | `iso14001` | phase2-implementation.js (IIFE) |
| ISO14001-SGMA_2026_NEW | `iso14001-2026` | phase2-implementation.js (IIFE) |
| ISO9001-SGQ_2015 | `iso9001` | phase2-implementation.js (IIFE) |
| TISAX | `tisax` | phase2-isms.js (sin tabs, sección independiente) |

### Reglas críticas

1. **Nunca usar IndexedDB** para el mapa — siempre Flask/SQLite via `phase_data`.
2. Al modificar `mapa-procesos.js`, propagar a las 9 apps cambiando solo `appId`:
   ```bash
   sed "s/appId:     'iso27001'/appId:     '$AID'/" ISO27001-SGSI/js/modules/mapa-procesos.js > $APP/js/modules/mapa-procesos.js
   ```
3. Bump versión en `index.html` de todas las apps afectadas: `?v=20260903a` → letra siguiente.
4. El CSS del módulo está **embebido** en el JS (IIFE al final del archivo) con prefijo `mp-`. No editar `styles.css` para estilos del mapa.
5. La plantilla por defecto para cada app se determina en `_normaParaPlantilla()` dentro del módulo.

### Bug conocido (evitar repetirlo)

**`SyntaxError` por `\'` en expresiones JS**: el escape `\'` SOLO es válido dentro de un string delimitado por `'`. En expresiones ternarias JS (`a === \'b\'`) fuera de un string produce `SyntaxError` que rompe todo el script → pantalla "Cargando..." infinita.

```javascript
// INCORRECTO — rompe app.js completo:
(this.currentPhase === \'tiquets\' ? \'active\' : \'\')

// CORRECTO:
(this.currentPhase === 'tiquets' ? 'active' : '')
```

Este bug estaba en `ISO14001-SGMA_2015/js/app.js` L203 e `ISO9001-SGQ_2015/js/app.js` L205. Corregido en `eb628fe`.

## Code Style Guidelines

### Language & Encoding

- All source files must use **UTF-8** encoding.
- Comments and documentation should be written in **Spanish** unless the
  surrounding codebase or library convention requires English.

### Formatting

- **Indentation**: 2 spaces (no tabs).
- **Line length**: max 100 characters for code, 80 for markdown/comments.
- **Trailing whitespace**: remove it.
- **Final newline**: every file must end with exactly one newline.
- **Semicolons** (JS/TS): always use them.
- **Quotes** (JS/TS): prefer single quotes (`'`) for strings; use backticks
  for template literals only when interpolation is needed.

### Naming Conventions

| Element            | Convention         | Example                |
| ------------------ | ------------------ | ---------------------- |
| Files/directories  | kebab-case         | `user-profile.ts`     |
| Variables/funcs    | camelCase          | `getUserName()`        |
| Constants          | UPPER_SNAKE_CASE   | `MAX_RETRY_COUNT`      |
| Classes/types      | PascalCase         | `UserProfile`          |
| CSS classes        | kebab-case / BEM   | `card__title--active`  |
| HTML IDs           | camelCase          | `sidebarNav`           |
| Env variables      | UPPER_SNAKE_CASE   | `DATABASE_URL`         |

### HTML / CSS

- Use semantic HTML5 elements (`<header>`, `<nav>`, `<main>`, `<section>`).
- Follow the CODANOR brand palette:
  - Primary: `#178DC2`
  - Accent: `#12A79D`
  - Dark: `#1a1a2e`
  - Fonts: Poppins (headings), Nunito Sans (body).
- Keep CSS specificity low; prefer class selectors over IDs.
- Use CSS custom properties for colors and spacing tokens.

### Error Handling

- Always catch errors at the boundary (API handler, event listener, main).
- Never swallow errors silently — at minimum, log them.
- Async functions: prefer `try/catch` over `.catch()` chains.
- Return early on error conditions to reduce nesting.
- In tiquets.js: always show `App.toast(error.message)` on catch blocks.

### Git Practices

- Branch names: `feature/short-description`, `fix/issue-number`.
- Commit messages: imperative mood, max 72 chars for the subject line.
- Keep commits atomic — one logical change per commit.
- Do not commit secrets, `.env` files, or credentials.
- **Regular commit prompting**: When the user makes changes during a session,
  proactively ask (in Spanish) whether they want to commit and push to GitHub.
  Ask at natural checkpoints (after completing a logical unit of work), not on
  every single edit. Never commit or push without explicit confirmation.

## Agent-Specific Instructions

### Context Management

- This workspace may be used with long-running OpenCode sessions. If the
  conversation grows large, suggest `/compact` or starting a new session.
- When creating or editing HTML files, preserve CODANOR corporate branding.

### Critical Rules for Tiquets Module

1. **Never duplicate methods** in `tiquets.js`. Always verify with:
   ```python
   python3 -c "import re; from collections import Counter; src=open('tiquets.js').read(); print({k:v for k,v in Counter([m[1] for m in re.findall(r'^\s{2}(async\s+)?(\w+)\s*\(',src,re.MULTILINE)]).items() if v>1})"
   ```

2. **wiki-categories.js**: after any edit, verify `{` balance = 0 in WIKI_CATEGORIES array.

3. **Propagation**: after editing `ISO27001-SGSI/js/modules/tiquets.js`, always copy to 8 other apps using `sed "s/appId:      'iso27001'/appId:      '$AID'/"` and bump version in all 9 `index.html`.

4. **Version bumping pattern**: `tiquets.js?v=2026082Xa` → increment letter (a→b→c...).

5. **plataforma.db**: `wiki_article_id` column added via `ALTER TABLE` in `init_db()`. Safe to run multiple times (try/except ignores duplicate column error).

6. **Never hardcode `localhost`** in `TK_API` — use `window.location.hostname` for LAN support.

7. **Store.initDB()**: always call `await Store.initDB()` before `Store.saveWikiArticle()` to ensure IndexedDB is ready.

### File Operations

- Prefer editing existing files over creating new ones.
- Never overwrite `Manual_OpenCode_Codanor.html` without explicit user consent.
- When generating new documentation, use the same branding and styles.
- `ARQUITECTURA_DB_SQLITE.html` is the authoritative reference for plataforma.db schema.

### Communication

- Respond in **Spanish** unless the user switches to another language.
- Be concise; avoid unnecessary praise or filler.
- Reference specific file paths and line numbers when discussing code.

### Performance

- Avoid scanning the entire filesystem; target specific directories.
- Use `/compact` if the session history causes slowness or API errors.
- For large tasks, break work into smaller steps using a todo list.

## Módulo Seguimiento de Tareas (v2.0 — 2026-09-06, commit `e0c1a08`)

### Mejoras implementadas

- **Modelo de tarea ampliado**: campo `acciones[]` por tarea. Cada acción tiene:
  `id`, `descripcion`, `responsable`, `estado` (pendiente|en_curso|resuelta),
  `fechaCreacion`, `fechaCierre`.
- **Nuevos métodos en phase2-*.js** (9 apps):
  `addTaskAction`, `updateTaskAction`, `removeTaskAction`,
  `toggleTaskActions`, `_renderTaskActionsRow`, `_normalizeAccion`
- **UI mejorada**: inputs inline editables para `responsable` y `fechaLimite`
  directamente en la tabla del panel "Seguimiento de tareas". Botón 📋 por fila
  con contador de acciones pendientes (amarillo) o resueltas (verde).
- **Exportación Word** (`report-builders.js`): 8ª columna "Acciones de resolución"
  con resumen de pendientes/resueltas. `meetingNotesToList` incluye acciones con
  estado, responsable y fecha de cierre. Anchos: `[1800,900,2600,1200,900,900,1000,2100]`
  (12400 twips total, sin cambiar ancho de página).

### Reglas críticas para el módulo de tareas

1. **`acciones[]` es solo lectura cuando la tarea está cerrada** (`completada`
   o `desestimada`). No permitir añadir ni editar acciones en ese estado.
2. Al modificar `phase2-consulting.js` (ISO27001 como base), propagar a las
   4 apps consulting restantes con `sed` cambiando solo `MapaProcesosModule.init()`.
3. **ISO9001 y ISO14001 tienen `phase2-implementation.js` propio** — no sobrescribir
   con el de la otra app: usan `ACTIVITY_GROUPS` (ISO9001) o `CLAUSE_GROUPS`
   (ISO14001) como variables globales distintas.
4. Verificar siempre métodos duplicados tras cualquier edición:
   ```python
   python3 -c "import re; from collections import Counter; src=open('phase2-consulting.js').read(); print({k:v for k,v in Counter([m[1] for m in re.findall(r'^\s{2}(async\s+)?(\w+)\s*\(',src,re.MULTILINE)]).items() if v>1})"
   ```
5. **`updateTaskAction` y `_refreshTasksPanel`**: el refresco del DOM solo debe
   ocurrir para los campos `estado`, `tipo` y `prioridad`. Para campos de texto
   libre (`titulo`, `descripcion`, `responsable`, `notaCierre`, `verificadoPor`,
   `fechaLimite`) solo ejecutar `save()` — si se llama `_refreshTasksPanel()` el
   subpanel se cierra y el usuario pierde el foco y lo que estaba escribiendo.
   ```javascript
   // CORRECTO:
   this.save();
   if (['estado', 'tipo', 'prioridad'].includes(field)) {
     this._refreshTasksPanel();
   }
   ```
6. **Badge CODANOR**: las tareas generadas por LLM tienen `origen: 'ia'` en BD.
   El badge visible es `>C<` con `title="CODANOR"` (no `>IA<`). El campo `origen`
   en BD NO debe cambiarse — solo la presentación visual. En exportación Word: `[C]`.

## Pantalla de inicio del servidor Flask (2026-09-21)

### Arquitectura

- **Función**: `index()` en `servidor/server.py` — ruta `GET /`
- **Genera**: HTML completo con grid de tarjetas por app (no usa templates Jinja2)
- **Tarjetas**: definidas en `APPS_META` (lista de dicts) + función `make_card()`
- **Iconos**: bloque CSS puro con `icon_line1` (número grande) + `icon_line2` (sigla)
- **Tooltip**: `data-tooltip` en cada `<a class="card">` + JS global `#global-tooltip`
  en `<body>` (fuera del DOM de tarjetas para evitar bug `position:fixed` con `transform`)

### Bug conocido — `position:fixed` dentro de `transform`

Si el ancestro tiene `transform` (`.card:hover` tiene `transform: translateY(-4px)`),
un `position:fixed` hijo queda contenido en ese contexto — no se posiciona respecto
al viewport. Solución: mover el tooltip a `<body>` y controlarlo con JS
(`mouseenter`/`mouseleave` en `document.querySelectorAll('.card[data-tooltip]')`).

### APPS_META — campos por app

| Campo | Descripción |
|---|---|
| `id` | app_id (ens, iso27001, iso14001, etc.) |
| `label` | Nombre completo para accesibilidad |
| `sublabel` | Descripción corta visible en la zona blanca |
| `icon_line1` | Texto grande en el bloque de color (ISO 27001, E.N.S., RGPD...) |
| `icon_line2` | Texto pequeño secundario (SGSI, RD 311/2022, LOPD-GDD...) |
| `color` | Color corporativo HEX del fondo del bloque |
| `tooltip` | Descripción extendida (aparece al hover, panel flotante inferior) |
   ```

## Fix LAN — Persistencia desde BD (v2.0 — 2026-09-06, commit `e0c1a08`)

### Problema corregido

`store.js` usaba `localhost:5001` como fallback de URL y `'_phase2'` como sonda
de caché para TODAS las apps, incluyendo ISO9001 e ISO14001 que usan la clave
`'implementation'` (no `'phase2'`). Resultado: en cualquier PC de la LAN distinto
del servidor, la Consultoría de ISO9001/ISO14001 aparecía vacía.

### Cambios aplicados (store.js × 9 apps)

1. **`_apiBase()`**: `localhost:5001` → `window.location.hostname + ':5001'`
2. **`PHASE_KEYS`**: nueva constante en cada `store.js` con las fases reales de la norma:

| App | PHASE_KEYS |
|---|---|
| ISO27001, ENS, ISO27701, ISO42001 | `phase1-5, soa, norma, documents, formacion, mapa_procesos` |
| RGPD | ídem + `rat, eipd, brechas, derechos` |
| ISO14001-2015, ISO14001-2026, ISO9001 | `gap, implementation, audit, certification, evidence, documents, formacion, mapa_procesos` |
| TISAX | `phase2, documents, formacion, mapa_procesos` |

3. **`_preloadProject`, `exportProject`, `importProject`**: usan `this.PHASE_KEYS`
   en lugar de lista hardcoded.
4. **`app.js` × 9 apps**: `hasLocalData` y `_cacheHasData` usan `Store.PHASE_KEYS[0]`
   (primera fase real de la app) en lugar de `'_phase2'` hardcoded.

### Reglas críticas

- **`PHASE_KEYS[0]`** es la clave de sonda de caché en `app.js`. Debe ser la primera
  fase que el proyecto realmente usa. Para ISO9001/ISO14001 es `'gap'`.
- Al añadir una nueva norma/app: definir `PHASE_KEYS` en su `store.js` con todas
  las fases que usa. El GET al servidor de fases vacías devuelve `{}` — sin coste.
- `mapa_procesos` está en `PHASE_KEYS` aunque el módulo hace fetch directo a Flask
  (no pasa por `Store.getPhaseData`). Se incluye para que `exportProject` e
  `importProject` cubran esta clave.
- **Versiones bumpeadas**: `store.js` y `app.js` → `?v=20260904c` en los 9 `index.html`.

### Documento generado

`DOCS/informes/Estructura_Funcional_Fases_Plataforma.docx` (135 KB, A4 landscape):
mapa funcional completo de las 9 apps con todas las fases, subtabs y diferencias.
Portada + índice + cabecera/pie corporativos CODANOR. 7 secciones, 18 tablas.

### Bugs corregidos en phase2-consulting.js (5 apps: ISO27001, ISO27701, ENS, RGPD, ISO42001)

1. **Botón "Generar Resumen IA" siempre visible** cuando hay fichero subido.
   - Antes: `${hasFile && LLMUtil.hasApiKey() ? ...}` → botón no existía sin API Key.
   - Ahora: `${hasFile ? ...}` — el botón siempre existe y deriva al flujo manual si no hay key.

2. **Fallback manual en `generateActaSummary()` y `generateGlobalSummary()`**:
   ```javascript
   if (!LLMUtil.hasApiKey()) {
     try { await LLMUtil.copyToClipboard(prompt); } catch (e) { /* ignore */ }
     this.showPromptModal(prompt);
     return;
   }
   ```

3. **`showPromptModal` + `showErrorModal` + `closePromptModal` + `openLLMConfigFromError`
   añadidos a RGPD-LOPD-GDD** (no estaban definidos).

4. **`showErrorModal` + `openLLMConfigFromError` añadidos a ISO42001-SGIA**.

5. **Guard `typeof LLMUtil` movido antes del primer uso** en `synthesizeMeeting()`.

### Versión tras el fix
Todos los `phase2-consulting.js` actualizados a `?v=20260904a` en sus respectivos `index.html`.

### Documentación generada
`DOCS/informes/Manual_Configuracion_IA_LLM.docx` — manual Word corporativo (44 KB, 13 capítulos):
API Keys gratuitas (OpenRouter/Groq/Google), de pago (OpenAI/Anthropic), presets, fallback chain,
flujo manual sin API Key, errores frecuentes y FAQ.

## Módulo NotebookLM (v1.0 — 2026-09-17)

### Arquitectura

- **Ubicación**: botón `🤖 NotebookLM` en la toolbar de la vista **Conocimiento** (`wiki.js`) de cada app, al final de la barra junto a "Importar Wiki".
- **Implementación**: `window.open('<URL>','_blank')` — enlace externo a Google NotebookLM, sin integración programática.
- **Archivo modificado**: `js/modules/wiki.js` en cada app (línea ~195, tras el botón `importWikiAll`).

### URLs por app

| App | Notebook ID |
|---|---|
| ISO27001-SGSI | `08a653c8-a16a-4e44-b137-597e9fd8a495` |
| RGPD-LOPD-GDD | `c29543b1-d6af-4885-bc93-e0de44b1d692` |
| ENS-RD311-2022 | `cc64cac9-f7d9-46bd-a37a-23ce7b074a8c` |
| ISO27701-SGP | `712c0d43-711a-4667-9c29-33a62fefa5aa` |
| ISO42001-SGIA | `5aa74c2f-138d-4a17-bd54-274df893f3bb` |
| ISO14001-SGMA_2026_NEW | `1ffdd2cc-52b7-496a-97fc-943c5e732cbf` |
| ISO9001-SGQ_2015 | `9acf987b-d7f3-4d45-80dc-0ca8483f82eb` |
| TISAX | `cc0bc464-5651-4d05-b996-73f9574cbb91` |
| ISO14001-SGMA_2015 | `aee7844a-021b-4519-aa9d-d020ae27bc53` *(notebook genérico CODANOR)* |

### Reglas críticas

1. El botón está **dentro de `wiki.js`**, NO en `app.js` (sidebar). No volver a añadirlo al sidebar raíz.
2. Al actualizar una URL, modificar únicamente `js/modules/wiki.js` de la app correspondiente — buscar `notebook.google.com/notebook/` en ese archivo.
3. `ISO14001-SGMA_2015` usa el notebook genérico hasta que se cree uno específico para esa norma.
4. `ISO9001-SGQ_2026` (en preparación) usará la misma URL que `ISO9001-SGQ_2015` cuando se implemente.

---

No `.cursor/rules/`, `.cursorrules`, or `.github/copilot-instructions.md`
files exist in this repository. When any are added, incorporate their
contents into this section.

---

*Last updated: 2026-09-25*


## Project Overview

This repository contains documentation and tooling for the OpenCode platform
used internally at CODANOR. It includes a corporate HTML manual (20 chapters),
a Kanban issue tracker, a SonarCloud analysis panel, a module homogenization
plan, a backup script, OpenCode slash commands, and the technical proposal for
the Tiquets tool (v1.2).

The **Tiquets module** is the most active component: a full-stack ticketing
system integrated into `plataforma.db` (SQLite) served by Flask on port 5001,
deployed across all 9 ISO/ENS apps and in `plataforma-seguimiento.html`.

## Build / Lint / Test Commands

```bash
# Start the Plataforma backend (required for Tiquets, Exports, Uploads)
cd ~/Proyectos/Plataforma_Seguimiento_Proyectos/servidor
python3 server.py
# → http://localhost:5001  (HOST 0.0.0.0 — LAN accessible)

# Verify DB integrity
sqlite3 servidor/plataforma.db "PRAGMA integrity_check;"

# Check all 10 tables exist
sqlite3 servidor/plataforma.db \
  "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"

# Verify tiquets module (9 apps)
python3 -c "
import re, os
from collections import Counter
BASE='~/Proyectos/Plataforma_Seguimiento_Proyectos'
for app in ['ISO27001-SGSI','RGPD-LOPD-GDD','ENS-RD311-2022']:
    src=open(f'{BASE}/{app}/js/modules/tiquets.js').read()
    dups={k:v for k,v in Counter([m[1] for m in re.findall(r'^\s{2}(async\s+)?(\w+)\s*\(',src,re.MULTILINE)]).items() if v>1}
    print(app, 'dups:', dups if dups else 'NONE')
"
```

## Repository Structure

```
PLATAFORMA_OpenCode-NEW/
  AGENTS.md                               # This file — agent instructions
  Memory.md                               # Project state, history, pending tasks
  opencode.json                           # OpenCode config (MCP SonarQube)
  .gitignore                              # Git exclusions
  Manual_OpenCode_Codanor.html            # Corporate manual v3.0 (20 chapters, ~137 KB)
  plataforma-seguimiento.html             # Dashboard + Kanban + Gestor de Tiquets (~98 KB)
  analisis-codigo.html                    # SonarCloud analysis panel (~46 KB)
  plan-homogeneizacion-modulos.html       # Module homogenization plan (~72 KB)
  homogeneizacion-proyectos.html          # Project homogenization dashboard (~46 KB)
  propuesta-herramienta-tiquets.html      # Tiquets tool proposal v1.2 (~98 KB)
  backup-opencode.sh                      # Backup script (8 modes, executable)
  sonar-project.properties                # SonarCloud scanner config
  Prompt.docx                             # Project prompt specification
  Estructura_PROYECTOS.pdf                # Module hierarchy diagram
  Biblioteca/                             # Screenshots and reference images
  .opencode/
    commands/
      sonar.md                            # Slash command /sonar
      sonar-report.md                     # Slash command /sonar-report
    package.json                          # OpenCode plugin dependency
```

## Critical Architecture — Tiquets Module

### Backend (Plataforma_Seguimiento_Proyectos/servidor/)

| File | Role |
|---|---|
| `server.py` | Flask app, port 5001, HOST 0.0.0.0. Contains ALL routes including 19 tiquets endpoints. **2559 lines** — do NOT create a separate file. |
| `plataforma.db` | SQLite WAL. **10 tables**: 4 original + 6 tiquets. See ARQUITECTURA_DB_SQLITE.html. |
| `migration_tiquets.sql` | DDL standalone v1.0→v1.4. Safe to re-run (IF NOT EXISTS). |
| `uploads/tiquets/` | Physical files for ticket attachments. Max 10 MB. Excluded from Git. |

### DB Tables — plataforma.db (10 tables)

**Original (4):** `clients` (298) · `projects` (32) · `phase_data` (35) · `settings` (0)

**Tiquets module (6):**

| Table | Version | Description |
|---|---|---|
| `contadores_tiquets` | v1.0 | Atomic NNN counter per (client_id, app_id) |
| `tiquets` | v1.0+v1.4 | Main table. 22 columns incl. `wiki_article_id` (ALTER TABLE v1.4) |
| `tiquets_historial` | v1.0 | Field-by-field audit log (ISO 27001 A.16) |
| `tiquets_comentarios` | v1.0 | Free-text follow-up log |
| `tiquets_acciones` | v1.2 | Resolution actions: pendiente→en_curso→resuelta |
| `tiquets_adjuntos` | v1.3 | File attachments stored in uploads/tiquets/ |

**Ticket ID format:** `TIK-{NNN:03d}-{client_id}-{app_id}-{DD-MM-AAAA}`

### Frontend — 9 ISO/ENS apps

Each app under `Plataforma_Seguimiento_Proyectos/` has:

| File | Role |
|---|---|
| `js/modules/tiquets.js` | TiquetsModule object. **Do NOT create duplicated methods.** Always check for duplicates after editing. Current version: `v=20260829f` |
| `js/wiki-categories.js` | Category definitions. **Balance of `{}`  in WIKI_CATEGORIES array MUST be 0.** Category `resolved_ticket` added as last item with proper `,` after previous item. |
| `index.html` | References `tiquets.js?v=20260829f`. Bump version letter on every change. |

### Frontend — plataforma-seguimiento.html

- Sidebar section **ACCIONES** → "Gestor de Tiquets"
- Page `#page-tickets` outside the SPA container (uses `visibility:hidden` trick)
- `TK_API` auto-detects host for LAN: `window.location.hostname + ':5001'`
- Offline fallback: `localStorage` key `codanor_tiquets_v2`
- Version bump: `?v=20260829f` in tiquets.js references

### Key tiquets.js methods (DO NOT DUPLICATE)

```
_apiBase(), _loadLocal(), _saveLocal(), _detectar(), init(),
_cargar(), _filtrarLocal(), _crear(), _actualizar(), _comentar(),
_cargarDetalle(), _actualizarContador(), _sincronizar(),
_renderSelectores(), _renderSelectorProyecto(), _renderTabla(),
_toggleDetalle(), _renderDetalle(), _crearAccion(),
_actualizarAccion(), _eliminarAccion(), _subirAdjuntos(),
_eliminarAdjunto(), _exportarTiquet(), _exportar(),
_actualizarEstadoTiquet(), _abrirModalWiki(), _cerrarModalWiki(),
_confirmarPasarAConocimiento(), _generarMarkdownWiki(),
_abrirModal(), _cerrarModal(), _guardarModal(), _recargar()
```

### Wiki / Knowledge Base integration (v1.4)

- `wiki_article_id TEXT DEFAULT NULL` in `tiquets` table (ALTER TABLE)
- Button "📚 Pasar a Conocimiento" appears **only when `estado === 'cerrado'`**
- Button "✓ Cerrar Tiquet" appears when `estado === 'resuelto'`
- `Store.saveWikiArticle()` creates article in IndexedDB (browser)
- `POST /api/tiquets/<id>/enviar-wiki` registers the wiki ID server-side (HTTP 409 if already sent)
- Category `resolved_ticket` "BD de Tiquets Resueltos" added to `wiki-categories.js` in all 9 apps
- **IMPORTANT**: `wiki_article_id` balance in `wiki-categories.js` WIKI_CATEGORIES array must be 0. The `resolved_ticket` item must be inserted INSIDE the array with proper `,` separator.

## Módulo Mapa de Procesos (v1.0 — 2026-09-04)

### Arquitectura

- **Archivo**: `js/modules/mapa-procesos.js` en cada una de las 9 apps (commit `eb628fe`)
- **Origen**: motor visual portado de `~/Proyectos/Mapa_Procesos/mapa_procesos.html` v1.0.0
- **Persistencia**: Flask SQLite via `phase_data` — **NO usar IndexedDB** (local al navegador, no funciona en LAN multiusuario)
  - Clave: `(project_id, app_id, 'mapa_procesos')`
  - Endpoint: `GET/POST /api/{appId}/phase/{projectId}/mapa_procesos`
  - El servidor ya lo soporta sin cambios — `phase_data` acepta clave libre
- **Versión en index.html**: `mapa-procesos.js?v=20260903a`

### appId por app

| App | appId | Módulo phase2 |
|---|---|---|
| ISO27001-SGSI | `iso27001` | phase2-consulting.js |
| ENS-RD311-2022 | `ens` | phase2-consulting.js |
| ISO27701-SGP | `iso27701` | phase2-consulting.js |
| ISO42001-SGIA | `iso42001` | phase2-consulting.js |
| RGPD-LOPD-GDD | `rgpd` | phase2-consulting.js |
| ISO14001-SGMA_2015 | `iso14001` | phase2-implementation.js (IIFE) |
| ISO14001-SGMA_2026_NEW | `iso14001-2026` | phase2-implementation.js (IIFE) |
| ISO9001-SGQ_2015 | `iso9001` | phase2-implementation.js (IIFE) |
| TISAX | `tisax` | phase2-isms.js (sin tabs, sección independiente) |

### Reglas críticas

1. **Nunca usar IndexedDB** para el mapa — siempre Flask/SQLite via `phase_data`.
2. Al modificar `mapa-procesos.js`, propagar a las 9 apps cambiando solo `appId`:
   ```bash
   sed "s/appId:     'iso27001'/appId:     '$AID'/" ISO27001-SGSI/js/modules/mapa-procesos.js > $APP/js/modules/mapa-procesos.js
   ```
3. Bump versión en `index.html` de todas las apps afectadas: `?v=20260903a` → letra siguiente.
4. El CSS del módulo está **embebido** en el JS (IIFE al final del archivo) con prefijo `mp-`. No editar `styles.css` para estilos del mapa.
5. La plantilla por defecto para cada app se determina en `_normaParaPlantilla()` dentro del módulo.

### Bug conocido (evitar repetirlo)

**`SyntaxError` por `\'` en expresiones JS**: el escape `\'` SOLO es válido dentro de un string delimitado por `'`. En expresiones ternarias JS (`a === \'b\'`) fuera de un string produce `SyntaxError` que rompe todo el script → pantalla "Cargando..." infinita.

```javascript
// INCORRECTO — rompe app.js completo:
(this.currentPhase === \'tiquets\' ? \'active\' : \'\')

// CORRECTO:
(this.currentPhase === 'tiquets' ? 'active' : '')
```

Este bug estaba en `ISO14001-SGMA_2015/js/app.js` L203 e `ISO9001-SGQ_2015/js/app.js` L205. Corregido en `eb628fe`.

## Code Style Guidelines

### Language & Encoding

- All source files must use **UTF-8** encoding.
- Comments and documentation should be written in **Spanish** unless the
  surrounding codebase or library convention requires English.

### Formatting

- **Indentation**: 2 spaces (no tabs).
- **Line length**: max 100 characters for code, 80 for markdown/comments.
- **Trailing whitespace**: remove it.
- **Final newline**: every file must end with exactly one newline.
- **Semicolons** (JS/TS): always use them.
- **Quotes** (JS/TS): prefer single quotes (`'`) for strings; use backticks
  for template literals only when interpolation is needed.

### Naming Conventions

| Element            | Convention         | Example                |
| ------------------ | ------------------ | ---------------------- |
| Files/directories  | kebab-case         | `user-profile.ts`     |
| Variables/funcs    | camelCase          | `getUserName()`        |
| Constants          | UPPER_SNAKE_CASE   | `MAX_RETRY_COUNT`      |
| Classes/types      | PascalCase         | `UserProfile`          |
| CSS classes        | kebab-case / BEM   | `card__title--active`  |
| HTML IDs           | camelCase          | `sidebarNav`           |
| Env variables      | UPPER_SNAKE_CASE   | `DATABASE_URL`         |

### HTML / CSS

- Use semantic HTML5 elements (`<header>`, `<nav>`, `<main>`, `<section>`).
- Follow the CODANOR brand palette:
  - Primary: `#178DC2`
  - Accent: `#12A79D`
  - Dark: `#1a1a2e`
  - Fonts: Poppins (headings), Nunito Sans (body).
- Keep CSS specificity low; prefer class selectors over IDs.
- Use CSS custom properties for colors and spacing tokens.

### Error Handling

- Always catch errors at the boundary (API handler, event listener, main).
- Never swallow errors silently — at minimum, log them.
- Async functions: prefer `try/catch` over `.catch()` chains.
- Return early on error conditions to reduce nesting.
- In tiquets.js: always show `App.toast(error.message)` on catch blocks.

### Git Practices

- Branch names: `feature/short-description`, `fix/issue-number`.
- Commit messages: imperative mood, max 72 chars for the subject line.
- Keep commits atomic — one logical change per commit.
- Do not commit secrets, `.env` files, or credentials.
- **Regular commit prompting**: When the user makes changes during a session,
  proactively ask (in Spanish) whether they want to commit and push to GitHub.
  Ask at natural checkpoints (after completing a logical unit of work), not on
  every single edit. Never commit or push without explicit confirmation.

## Agent-Specific Instructions

### Context Management

- This workspace may be used with long-running OpenCode sessions. If the
  conversation grows large, suggest `/compact` or starting a new session.
- When creating or editing HTML files, preserve CODANOR corporate branding.

### Critical Rules for Tiquets Module

1. **Never duplicate methods** in `tiquets.js`. Always verify with:
   ```python
   python3 -c "import re; from collections import Counter; src=open('tiquets.js').read(); print({k:v for k,v in Counter([m[1] for m in re.findall(r'^\s{2}(async\s+)?(\w+)\s*\(',src,re.MULTILINE)]).items() if v>1})"
   ```

2. **wiki-categories.js**: after any edit, verify `{` balance = 0 in WIKI_CATEGORIES array.

3. **Propagation**: after editing `ISO27001-SGSI/js/modules/tiquets.js`, always copy to 8 other apps using `sed "s/appId:      'iso27001'/appId:      '$AID'/"` and bump version in all 9 `index.html`.

4. **Version bumping pattern**: `tiquets.js?v=2026082Xa` → increment letter (a→b→c...).

5. **plataforma.db**: `wiki_article_id` column added via `ALTER TABLE` in `init_db()`. Safe to run multiple times (try/except ignores duplicate column error).

6. **Never hardcode `localhost`** in `TK_API` — use `window.location.hostname` for LAN support.

7. **Store.initDB()**: always call `await Store.initDB()` before `Store.saveWikiArticle()` to ensure IndexedDB is ready.

### File Operations

- Prefer editing existing files over creating new ones.
- Never overwrite `Manual_OpenCode_Codanor.html` without explicit user consent.
- When generating new documentation, use the same branding and styles.
- `ARQUITECTURA_DB_SQLITE.html` is the authoritative reference for plataforma.db schema.

### Communication

- Respond in **Spanish** unless the user switches to another language.
- Be concise; avoid unnecessary praise or filler.
- Reference specific file paths and line numbers when discussing code.

### Performance

- Avoid scanning the entire filesystem; target specific directories.
- Use `/compact` if the session history causes slowness or API errors.
- For large tasks, break work into smaller steps using a todo list.

## Módulo Seguimiento de Tareas (v2.0 — 2026-09-06, commit `e0c1a08`)

### Mejoras implementadas

- **Modelo de tarea ampliado**: campo `acciones[]` por tarea. Cada acción tiene:
  `id`, `descripcion`, `responsable`, `estado` (pendiente|en_curso|resuelta),
  `fechaCreacion`, `fechaCierre`.
- **Nuevos métodos en phase2-*.js** (9 apps):
  `addTaskAction`, `updateTaskAction`, `removeTaskAction`,
  `toggleTaskActions`, `_renderTaskActionsRow`, `_normalizeAccion`
- **UI mejorada**: inputs inline editables para `responsable` y `fechaLimite`
  directamente en la tabla del panel "Seguimiento de tareas". Botón 📋 por fila
  con contador de acciones pendientes (amarillo) o resueltas (verde).
- **Exportación Word** (`report-builders.js`): 8ª columna "Acciones de resolución"
  con resumen de pendientes/resueltas. `meetingNotesToList` incluye acciones con
  estado, responsable y fecha de cierre. Anchos: `[1800,900,2600,1200,900,900,1000,2100]`
  (12400 twips total, sin cambiar ancho de página).

### Reglas críticas para el módulo de tareas

1. **`acciones[]` es solo lectura cuando la tarea está cerrada** (`completada`
   o `desestimada`). No permitir añadir ni editar acciones en ese estado.
2. Al modificar `phase2-consulting.js` (ISO27001 como base), propagar a las
   4 apps consulting restantes con `sed` cambiando solo `MapaProcesosModule.init()`.
3. **ISO9001 y ISO14001 tienen `phase2-implementation.js` propio** — no sobrescribir
   con el de la otra app: usan `ACTIVITY_GROUPS` (ISO9001) o `CLAUSE_GROUPS`
   (ISO14001) como variables globales distintas.
4. Verificar siempre métodos duplicados tras cualquier edición:
   ```python
   python3 -c "import re; from collections import Counter; src=open('phase2-consulting.js').read(); print({k:v for k,v in Counter([m[1] for m in re.findall(r'^\s{2}(async\s+)?(\w+)\s*\(',src,re.MULTILINE)]).items() if v>1})"
   ```
5. **`updateTaskAction` y `_refreshTasksPanel`**: el refresco del DOM solo debe
   ocurrir para los campos `estado`, `tipo` y `prioridad`. Para campos de texto
   libre (`titulo`, `descripcion`, `responsable`, `notaCierre`, `verificadoPor`,
   `fechaLimite`) solo ejecutar `save()` — si se llama `_refreshTasksPanel()` el
   subpanel se cierra y el usuario pierde el foco y lo que estaba escribiendo.
   ```javascript
   // CORRECTO:
   this.save();
   if (['estado', 'tipo', 'prioridad'].includes(field)) {
     this._refreshTasksPanel();
   }
   ```
6. **Badge CODANOR**: las tareas generadas por LLM tienen `origen: 'ia'` en BD.
   El badge visible es `>C<` con `title="CODANOR"` (no `>IA<`). El campo `origen`
   en BD NO debe cambiarse — solo la presentación visual. En exportación Word: `[C]`.

## Pantalla de inicio del servidor Flask (2026-09-21)

### Arquitectura

- **Función**: `index()` en `servidor/server.py` — ruta `GET /`
- **Genera**: HTML completo con grid de tarjetas por app (no usa templates Jinja2)
- **Tarjetas**: definidas en `APPS_META` (lista de dicts) + función `make_card()`
- **Iconos**: bloque CSS puro con `icon_line1` (número grande) + `icon_line2` (sigla)
- **Tooltip**: `data-tooltip` en cada `<a class="card">` + JS global `#global-tooltip`
  en `<body>` (fuera del DOM de tarjetas para evitar bug `position:fixed` con `transform`)

### Bug conocido — `position:fixed` dentro de `transform`

Si el ancestro tiene `transform` (`.card:hover` tiene `transform: translateY(-4px)`),
un `position:fixed` hijo queda contenido en ese contexto — no se posiciona respecto
al viewport. Solución: mover el tooltip a `<body>` y controlarlo con JS
(`mouseenter`/`mouseleave` en `document.querySelectorAll('.card[data-tooltip]')`).

### APPS_META — campos por app

| Campo | Descripción |
|---|---|
| `id` | app_id (ens, iso27001, iso14001, etc.) |
| `label` | Nombre completo para accesibilidad |
| `sublabel` | Descripción corta visible en la zona blanca |
| `icon_line1` | Texto grande en el bloque de color (ISO 27001, E.N.S., RGPD...) |
| `icon_line2` | Texto pequeño secundario (SGSI, RD 311/2022, LOPD-GDD...) |
| `color` | Color corporativo HEX del fondo del bloque |
| `tooltip` | Descripción extendida (aparece al hover, panel flotante inferior) |
   ```

## Fix LAN — Persistencia desde BD (v2.0 — 2026-09-06, commit `e0c1a08`)

### Problema corregido

`store.js` usaba `localhost:5001` como fallback de URL y `'_phase2'` como sonda
de caché para TODAS las apps, incluyendo ISO9001 e ISO14001 que usan la clave
`'implementation'` (no `'phase2'`). Resultado: en cualquier PC de la LAN distinto
del servidor, la Consultoría de ISO9001/ISO14001 aparecía vacía.

### Cambios aplicados (store.js × 9 apps)

1. **`_apiBase()`**: `localhost:5001` → `window.location.hostname + ':5001'`
2. **`PHASE_KEYS`**: nueva constante en cada `store.js` con las fases reales de la norma:

| App | PHASE_KEYS |
|---|---|
| ISO27001, ENS, ISO27701, ISO42001 | `phase1-5, soa, norma, documents, formacion, mapa_procesos` |
| RGPD | ídem + `rat, eipd, brechas, derechos` |
| ISO14001-2015, ISO14001-2026, ISO9001 | `gap, implementation, audit, certification, evidence, documents, formacion, mapa_procesos` |
| TISAX | `phase2, documents, formacion, mapa_procesos` |

3. **`_preloadProject`, `exportProject`, `importProject`**: usan `this.PHASE_KEYS`
   en lugar de lista hardcoded.
4. **`app.js` × 9 apps**: `hasLocalData` y `_cacheHasData` usan `Store.PHASE_KEYS[0]`
   (primera fase real de la app) en lugar de `'_phase2'` hardcoded.

### Reglas críticas

- **`PHASE_KEYS[0]`** es la clave de sonda de caché en `app.js`. Debe ser la primera
  fase que el proyecto realmente usa. Para ISO9001/ISO14001 es `'gap'`.
- Al añadir una nueva norma/app: definir `PHASE_KEYS` en su `store.js` con todas
  las fases que usa. El GET al servidor de fases vacías devuelve `{}` — sin coste.
- `mapa_procesos` está en `PHASE_KEYS` aunque el módulo hace fetch directo a Flask
  (no pasa por `Store.getPhaseData`). Se incluye para que `exportProject` e
  `importProject` cubran esta clave.
- **Versiones bumpeadas**: `store.js` y `app.js` → `?v=20260904c` en los 9 `index.html`.

### Documento generado

`DOCS/informes/Estructura_Funcional_Fases_Plataforma.docx` (135 KB, A4 landscape):
mapa funcional completo de las 9 apps con todas las fases, subtabs y diferencias.
Portada + índice + cabecera/pie corporativos CODANOR. 7 secciones, 18 tablas.

### Bugs corregidos en phase2-consulting.js (5 apps: ISO27001, ISO27701, ENS, RGPD, ISO42001)

1. **Botón "Generar Resumen IA" siempre visible** cuando hay fichero subido.
   - Antes: `${hasFile && LLMUtil.hasApiKey() ? ...}` → botón no existía sin API Key.
   - Ahora: `${hasFile ? ...}` — el botón siempre existe y deriva al flujo manual si no hay key.

2. **Fallback manual en `generateActaSummary()` y `generateGlobalSummary()`**:
   ```javascript
   if (!LLMUtil.hasApiKey()) {
     try { await LLMUtil.copyToClipboard(prompt); } catch (e) { /* ignore */ }
     this.showPromptModal(prompt);
     return;
   }
   ```

3. **`showPromptModal` + `showErrorModal` + `closePromptModal` + `openLLMConfigFromError`
   añadidos a RGPD-LOPD-GDD** (no estaban definidos).

4. **`showErrorModal` + `openLLMConfigFromError` añadidos a ISO42001-SGIA**.

5. **Guard `typeof LLMUtil` movido antes del primer uso** en `synthesizeMeeting()`.

### Versión tras el fix
Todos los `phase2-consulting.js` actualizados a `?v=20260904a` en sus respectivos `index.html`.

### Documentación generada
`DOCS/informes/Manual_Configuracion_IA_LLM.docx` — manual Word corporativo (44 KB, 13 capítulos):
API Keys gratuitas (OpenRouter/Groq/Google), de pago (OpenAI/Anthropic), presets, fallback chain,
flujo manual sin API Key, errores frecuentes y FAQ.

## Módulo NotebookLM (v1.0 — 2026-09-17)

### Arquitectura

- **Ubicación**: botón `🤖 NotebookLM` en la toolbar de la vista **Conocimiento** (`wiki.js`) de cada app, al final de la barra junto a "Importar Wiki".
- **Implementación**: `window.open('<URL>','_blank')` — enlace externo a Google NotebookLM, sin integración programática.
- **Archivo modificado**: `js/modules/wiki.js` en cada app (línea ~195, tras el botón `importWikiAll`).

### URLs por app

| App | Notebook ID |
|---|---|
| ISO27001-SGSI | `08a653c8-a16a-4e44-b137-597e9fd8a495` |
| RGPD-LOPD-GDD | `c29543b1-d6af-4885-bc93-e0de44b1d692` |
| ENS-RD311-2022 | `cc64cac9-f7d9-46bd-a37a-23ce7b074a8c` |
| ISO27701-SGP | `712c0d43-711a-4667-9c29-33a62fefa5aa` |
| ISO42001-SGIA | `5aa74c2f-138d-4a17-bd54-274df893f3bb` |
| ISO14001-SGMA_2026_NEW | `1ffdd2cc-52b7-496a-97fc-943c5e732cbf` |
| ISO9001-SGQ_2015 | `9acf987b-d7f3-4d45-80dc-0ca8483f82eb` |
| TISAX | `cc0bc464-5651-4d05-b996-73f9574cbb91` |
| ISO14001-SGMA_2015 | `aee7844a-021b-4519-aa9d-d020ae27bc53` *(notebook genérico CODANOR)* |

### Reglas críticas

1. El botón está **dentro de `wiki.js`**, NO en `app.js` (sidebar). No volver a añadirlo al sidebar raíz.
2. Al actualizar una URL, modificar únicamente `js/modules/wiki.js` de la app correspondiente — buscar `notebook.google.com/notebook/` en ese archivo.
3. `ISO14001-SGMA_2015` usa el notebook genérico hasta que se cree uno específico para esa norma.
4. `ISO9001-SGQ_2026` (en preparación) usará la misma URL que `ISO9001-SGQ_2015` cuando se implemente.

---



No `.cursor/rules/`, `.cursorrules`, or `.github/copilot-instructions.md`
files exist in this repository. When any are added, incorporate their
contents into this section.

---

*Last updated: 2026-09-21*
