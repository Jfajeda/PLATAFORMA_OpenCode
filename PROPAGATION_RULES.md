# PROPAGATION_RULES.md — Reglas de propagación entre apps CODANOR

> Cargado automáticamente por OpenCode junto con AGENTS.md.
> Este archivo es la fuente de verdad para cualquier operación de propagación
> entre las 9 apps ISO/ENS de Plataforma_Seguimiento_Proyectos.
> Última actualización: 2026-10-01

## REGLA FUNDAMENTAL

**Antes de propagar cualquier archivo JS entre apps, identificar su TIPO en
las tablas siguientes. Nunca asumir que todas las apps son iguales.**

---

## Clasificación de archivos por tipo

### TIPO A — BASE
Archivo master. Se edita directamente. Se propaga a los CLONES.

| Archivo | App base |
|---|---|
| `js/modules/phase2-consulting.js` | `ISO27001-SGSI` |
| `js/modules/tiquets.js` | `ISO27001-SGSI` |
| `js/modules/mapa-procesos.js` | `ISO27001-SGSI` |
| `js/modules/phase3-audit.js` | `ISO27001-SGSI` |

---

### TIPO B — CLON SEGURO
Idéntico al BASE excepto el `appId`. Propagación con `sed` es segura.

| Archivo | Apps | Única diferencia respecto al BASE |
|---|---|---|
| `js/modules/phase2-consulting.js` | RGPD-LOPD-GDD, ISO27701-SGP, ISO42001-SGIA | Solo `MapaProcesosModule.init(projectId, 'appId')` |
| `js/modules/tiquets.js` | 8 apps restantes | Solo `this.appId = 'appId'` |
| `js/modules/mapa-procesos.js` | 8 apps restantes | Solo `appId: 'appId'` |
| `js/modules/phase3-audit.js` | 8 apps restantes | Idéntico — propagar con `cp` |

**Comando seguro para TIPO B:**
```bash
sed "s/MapaProcesosModule\.init('[a-z0-9-]*'/MapaProcesosModule.init('$AID'/" BASE > DESTINO
```

---

### TIPO C — DIVERGENTE ⚠️
Comparte la misma base pero tiene código exclusivo añadido.
**NUNCA propagar el archivo completo desde BASE. Siempre patch quirúrgico con Python.**

| Archivo | App | Código exclusivo | Líneas exclusivas mínimas |
|---|---|---|---|
| `js/modules/phase2-consulting.js` | `ENS-RD311-2022` | CCN-808 (Seguimiento + Evidencias), pestaña Evolució, Snapshots, gestión documental F2 (`_visibleDocs`, `desglosarLineaCSV`) | **≥ 580** |

**Cómo aplicar un fix en un archivo TIPO C (ENS):**
```python
# CORRECTO — patch quirúrgico:
path = 'ENS-RD311-2022/js/modules/phase2-consulting.js'
src = open(path).read()
src = src.replace(OLD_SNIPPET, NEW_SNIPPET)
open(path, 'w').write(src)

# INCORRECTO — destruye el código exclusivo:
# cp ISO27001-SGSI/js/modules/phase2-consulting.js ENS-RD311-2022/js/modules/
# sed ... ISO27001-SGSI/... > ENS-RD311-2022/...
```

---

### TIPO D — PROPIO
Archivo sin equivalente en otra app. No tiene BASE. No propagar entre apps del mismo tipo.

| Archivo | App | Motivo — NO propagar con |
|---|---|---|
| `js/modules/phase2-implementation.js` | `ISO9001-SGQ_2015` | `ACTIVITY_GROUPS` (11 grupos), patrón IIFE, nomenclatura propia (`renderMeetingsTable`, `_renderMtgTaskCard`) |
| `js/modules/phase2-implementation.js` | `ISO14001-SGMA_2015` | `CLAUSE_GROUPS` (cláusulas objeto), `ISO14001_CLAUSES_DETAIL`, prefijo `MA-` |
| `js/modules/phase2-implementation.js` | `ISO14001-SGMA_2026_NEW` | Igual que ISO14001-2015 — norma 2026 |
| `js/modules/phase2-isms.js` | `TISAX` | Módulo único sin base. Sin tabs, sin LLM, clave persistencia `'phase2'` |

**Regla TIPO D:** Editar cada archivo por separado. Nunca copiar de uno al otro.
Aplicar fixes con patch quirúrgico Python sobre el archivo específico de cada app.

---

## Workflow de propagación — paso a paso

### Caso 1 — Fix en `phase2-consulting.js`

```
PASO 1: Editar ISO27001-SGSI/js/modules/phase2-consulting.js (BASE)
PASO 2: Propagar a RGPD, ISO27701, ISO42001 con sed (TIPO B — CLON SEGURO)
PASO 3: Aplicar el mismo fix quirúrgicamente en ENS (TIPO C — DIVERGENTE)
         → Nunca copiar el archivo completo
PASO 4: Ejecutar verificación de integridad ENS (ver script abajo)
PASO 5: Bump versión en 5 index.html (consulting × 5)
```

### Caso 2 — Fix en `tiquets.js` o `mapa-procesos.js`

```
PASO 1: Editar ISO27001-SGSI (BASE)
PASO 2: Propagar a las 8 apps con sed (todas son TIPO B — CLON SEGURO)
PASO 3: Bump versión en 9 index.html
```

### Caso 3 — Fix en `phase2-implementation.js`

```
PASO 1: Identificar qué apps requieren el fix
PASO 2: Editar CADA app por separado (ISO9001, ISO14001-2015, ISO14001-2026)
         → Son TIPO D — PROPIO: nunca copiar entre ellas
PASO 3: Bump versión en los index.html afectados
```

### Caso 4 — Fix en `phase3-audit.js`

```
PASO 1: Editar ISO27001-SGSI/js/modules/phase3-audit.js (BASE)
PASO 2: Copiar con cp a las 8 apps restantes (TIPO B — idéntico en todas)
PASO 3: Bump versión en 9 index.html
```

### Caso 5 — Fix en `phase2-isms.js`

```
PASO 1: Editar TISAX/js/modules/phase2-isms.js directamente (TIPO D — PROPIO)
PASO 2: Bump versión en TISAX/index.html
```

---

## Script de verificación de integridad ENS (OBLIGATORIO)

Ejecutar antes de cualquier commit que toque `phase2-consulting.js`:

```python
python3 -c "
import subprocess, sys
BASE = 'Plataforma_Seguimiento_Proyectos'
r = subprocess.run([
    'diff',
    f'{BASE}/ISO27001-SGSI/js/modules/phase2-consulting.js',
    f'{BASE}/ENS-RD311-2022/js/modules/phase2-consulting.js'
], capture_output=True, text=True)
lines = r.stdout.count('\n>')
if lines < 580:
    print(f'ERROR: ENS ha perdido codigo exclusivo ({lines} lineas, minimo 580)')
    sys.exit(1)
print(f'OK — ENS tiene {lines} lineas exclusivas (minimo 580)')
"
```

---

## Funciones exclusivas de ENS que NUNCA deben perderse

Al verificar `phase2-consulting.js` de ENS, estas funciones deben existir:

| Función | Propósito |
|---|---|
| `_seg808Data(kind, itemId)` | Datos Seguimiento CCN-STIC 808 |
| `_evid808Data(kind, itemId)` | Datos Evidencias 808 |
| `renderEvolucion()` | Pestaña Evolución con gráfico Chart.js |
| `takeSnapshot()` | Snapshot periódico de progreso |
| `desglosarLineaCSV(kind, itemId, index)` | Divide línea CSV de documentos propuestos |
| `_visibleDocs(arr)` | Devuelve arr sin filtrar (índices deben coincidir con reales) |

```bash
# Verificación rápida:
grep -c "_seg808Data\|renderEvolucion\|takeSnapshot\|desglosarLineaCSV" \
  Plataforma_Seguimiento_Proyectos/ENS-RD311-2022/js/modules/phase2-consulting.js
# Resultado esperado: >= 4
```

---

## Variables globales críticas por app (TIPO D)

| App | Variable | Archivo que la define | NO confundir con |
|---|---|---|---|
| ISO9001 | `ACTIVITY_GROUPS` | `iso9001-clauses-detailed.js` | `CLAUSE_GROUPS` de ISO14001 |
| ISO9001 | `ISO9001_CLAUSES_DETAIL` | `iso9001-clauses-detailed.js` | `ISO27001_CLAUSES_DETAIL` |
| ISO9001 | `CLAUSE_GROUPS_GAP` | `iso9001-subclauses-detail.js` | `ACTIVITY_GROUPS` |
| ISO14001 | `CLAUSE_GROUPS` | `iso14001-clauses-detailed.js` | `ACTIVITY_GROUPS` de ISO9001 |
| ISO14001 | `ISO14001_CLAUSES_DETAIL` | `iso14001-clauses-detailed.js` | `ISO27001_CLAUSES_DETAIL` |
| ENS | `ENS_808_CHECKLIST` | `ens-808-checklist.js` (AUTO-GEN) | `ens-measures-detailed.js` |
| ISO27701 | `organizationRole` | campo en cada proyecto | no existe en ISO27001 |
| ISO42001 | `AIIA` module | `aiia-data.js` | no existe en ISO27001 |

---

## Reglas de mantenimiento de este archivo

Actualizar `PROPAGATION_RULES.md` cuando:
1. Se añade código exclusivo nuevo a ENS u otra app → añadir/actualizar TIPO C
2. Se crea una app nueva → añadir a la tabla correspondiente
3. Se extrae código exclusivo de una app a un archivo JS separado → actualizar clasificación
4. Cambia el umbral de líneas exclusivas de ENS → actualizar el script de verificación

---

## Referencias — AGENTS.md específicos de cada app

Para información técnica detallada de cada app (arquitectura, gotchas, pitfalls),
consultar el `AGENTS.md` específico de cada app en su carpeta:

| App | AGENTS.md específico | Aspectos documentados |
|---|---|---|
| ENS-RD311-2022 | `ENS-RD311-2022/AGENTS.md` (334 L) | CCN-808, Categorización ENS, Plantillas 69 medidas, Seguimiento F2, Pitfalls F3 |
| ISO27001-SGSI | `ISO27001-SGSI/AGENTS.md` (360 L) | SoA, TaskHistory v2, LAN race condition, Plantillas 44 |
| ISO9001-SGQ_2015 | `ISO9001-SGQ_2015/AGENTS.md` (494 L) | ACTIVITY_GROUPS, IIFE pattern, migración IDs, DB v5, Wiki Grupo B |
| ISO14001-SGMA_2015 | `ISO14001-SGMA_2015/AGENTS.md` (406 L) | CLAUSE_GROUPS, unificación corporativa ISO9001, portada CODANOR Word |
| ISO14001-SGMA_2026_NEW | `ISO14001-SGMA_2026_NEW/AGENTS.md` (384 L) | Norma ISO 14001:2026, diferencias vs 2015 |
| TISAX | `TISAX/AGENTS.md` (361 L) | ISA catalog 80 controles, phase2-isms.js sin tabs, sin LLM |
| ISO27701-SGP | `ISO27701-SGP/AGENTS.md` (435 L) | organizationRole, 78 controles Anexo A, privacy-tests-data.js |
| ISO42001-SGIA | `ISO42001-SGIA/AGENTS.md` (298 L) | AIIA module, 46 tests forenses IA, aiia-data.js |
| RGPD-LOPD-GDD | `RGPD-LOPD-GDD/AGENTS.md` (164 L) | WebCheck RGPD/LOPDGDD/LSSI, forensic-tests RGPD |
