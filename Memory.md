# Memory.md — PLATAFORMA_OpenCode
> Ultima actualizacion: 2026-07-05

## Estado actual

- **Fase**: Produccion / mantenimiento activo
- **Version**: Manual v3.0 (20 capitulos)
- **Ultimo cambio significativo**: Herramienta "Homogeneizacion de Proyectos" (analisis read-only vs patron ISO27001-SGSI, dashboard web + informes Word/Excel)
- **Issues abiertos**: 72 bugs de reliability + 3 security hotspots detectados por SonarCloud

## Infraestructura

| Elemento | Estado | Detalle |
|----------|--------|---------|
| Git | Si | 7 commits, rama principal |
| GitHub | Si | github.com/Jfajeda/PLATAFORMA_OpenCode |
| SonarCloud | Si | Security A, Reliability B, Maintainability A, 3.5% duplications |
| .gitignore | Si | Excluye .DS_Store, backups, __pycache__ |
| AGENTS.md | Si | Instrucciones para agentes IA |
| opencode.json | Si | MCP SonarQube configurado |
| Memory.md | Si | Este archivo |

## Componentes del proyecto

| Archivo | Descripcion | Tamano |
|---------|-------------|--------|
| Manual_OpenCode_Codanor.html | Manual v3.0, 20 capitulos | ~137 KB |
| plataforma-seguimiento.html | Dashboard + Kanban + Docs Hub + Changelog | ~63 KB |
| analisis-codigo.html | Panel SonarCloud exportable, 5 pestanas | ~46 KB |
| plan-homogeneizacion-modulos.html | Plan de homogeneizacion de modulos (14 caps) | ~72 KB |
| homogeneizacion-proyectos.html | Dashboard herramienta homogeneizacion (5 pestanas, JSON embebido, export Word/Excel) | ~46 KB |
| backup-opencode.sh | Script backup -> NAS CODANOR (DB consistente, snapshots excluidos) | ~14 KB |
| com.codanor.opencode-backup.plist | Agente launchd backup diario 02:00 | ~2 KB |
| documento-copias-seguridad.html | Doc corporativo opciones de backup (enfasis NAS Synology) | ~26 KB |
| documento-copias-seguridad.docx | Version Word del doc de backup (generada por tools/generar-docx.py) | ~41 KB |
| tools/generar-docx.py | Generador del .docx con branding CODANOR (python-docx) | ~16 KB |
| sonar-project.properties | Config scanner SonarCloud | 762 B |
| Prompt.docx | Especificacion del proyecto | ~22 KB |
| Estructura_PROYECTOS.pdf | Diagrama jerarquico de modulos | ~386 KB |
| .opencode/commands/sonar.md | Comando /sonar | 562 B |
| .opencode/commands/sonar-report.md | Comando /sonar-report | 526 B |

## Historial de decisiones

| Fecha | Decision | Razon |
|-------|----------|-------|
| 2026-04-26 | Mover todos los proyectos de ~/Documents/ y ~/Desktop/ a ~/Proyectos/ | iCloud sincroniza ~/Documents/ causando conflictos con Git y OpenCode |
| 2026-04-26 | Usar SonarCloud Automatic Analysis en vez de scanner manual | No requiere Node.js ni configuracion local; cada git push lanza analisis |
| 2026-04-26 | Project key: Jfajeda_PLATAFORMA_OpenCode (case-sensitive) | SonarCloud asigna este formato automaticamente, no el que propusimos |
| 2026-04-26 | Crear AGENTS.md solo en PLATAFORMA_OpenCode (no en los 7 restantes) | Se creara en cada proyecto al ejecutar /init desde OpenCode |
| 2026-04-26 | Eliminar originales del Desktop despues de mover a ~/Proyectos/ | Aprobado por el usuario, evita confusion y duplicados |
| 2026-04-26 | 190 .DS_Store + 11 .pyc eliminados de todos los proyectos | Limpieza previa a versionado en Git |
| 2026-07-05 | Crear herramienta "Homogeneizacion de Proyectos" (7 pasos) | Analizar/comparar los 17 subproyectos contra patron ISO27001-SGSI |
| 2026-07-05 | Scripts Python en Plataforma_Seguimiento/_homogeneizacion; HTML en OpenCode-NEW | Separar logica de scan (read-only) de la visualizacion |
| 2026-07-05 | Score global ponderado (estructura 25, js_modules 20, js_core/utils/plantillas 15, idiomas/menus 5) | Reflejar importancia relativa de cada bloque del CSV guia |
| 2026-07-05 | Proyectos documentales y pendientes con score null (no penalizan) | No tiene sentido comparar carpetas sin app o aun no creadas |

## Revisiones de calidad/seguridad

| Fecha | Herramienta | Resultado | Detalle |
|-------|-------------|-----------|---------|
| 2026-04-26 | SonarCloud | Security A, Reliability B, Maintainability A | 72 bugs reliability, 3 security hotspots, 3.5% duplications |
| 2026-04-27 | Revision manual (OpenCode) | 34 target_blank + 18 innerHTML + 2 alt + 1 console = 55 bugs identificados | 37 corregidos (34 target_blank + 2 alt + 1 console.warn) |

### Correcciones aplicadas (2026-04-27)
1. **34x** `target="_blank"` sin `rel="noopener noreferrer"` corregidos (23 Manual + 8 Plataforma + 3 Analisis)
2. **2x** `<img alt="">` cambiados a `alt="Logo corporativo"` en analisis-codigo.html
3. **1x** `console.warn` eliminado en analisis-codigo.html

### Pendiente de corregir
- 18 usos de innerHTML con datos de localStorage (security hotspots)
- Patron de addActivity() que almacena HTML en localStorage y lo inyecta sin escape

## Pendiente

- [x] ~~Corregir bugs de reliability de SonarCloud~~ (37 de ~55 corregidos el 2026-04-27)
- [ ] Corregir los 18 innerHTML restantes (security hotspots de SonarCloud)
- [ ] Instalar Node.js en el Mac (necesario para MCP server SonarQube y npx @sonar/scan)
- [ ] Ejecutar /init en los 7 proyectos restantes para crear AGENTS.md
- [ ] Subir los otros 7+ proyectos a GitHub
- [x] ~~Automatizar backup (launchd diario 02:00 -> NAS CODANOR)~~ (2026-06-06, falta conceder TCC)
- [ ] Conceder "Acceso total al disco" al shell/launchd para escribir en el NAS (accion usuario)
- [ ] Regenerar token SonarCloud (el actual de 39 chars puede estar truncado)

## Herramienta "Homogeneizacion de Proyectos" (2026-07-05)

Herramienta de analisis **read-only** que compara los subproyectos de
`~/Proyectos/Plataforma_Seguimiento_Proyectos/` contra el patron gold standard
**ISO27001-SGSI**, y genera dashboard web + informes Word/Excel.

### Ficheros (scripts en Plataforma_Seguimiento/_homogeneizacion/)
| Fichero | Descripcion |
|---------|-------------|
| patron_iso27001.json | Gold standard: 7 bloques, pesos, clasificacion |
| scan_proyectos.py | Scanner read-only, tolerante a variantes de nombres |
| estado_proyectos.json | Salida del scan (datos que consume la web) |
| generar_informe_docx.py | Informe Word (python-docx + fallback .doc HTML) |
| generar_informe_xlsx.py | Informe Excel 5 hojas (openpyxl + fallback .xls HTML) |
| README.md | Instrucciones de uso |
| .gitignore | Excluye informes generados (regenerables) |

Visualizacion: `PLATAFORMA_OpenCode-NEW/homogeneizacion-proyectos.html`
(accesible desde sidebar "Herramientas" de plataforma-seguimiento.html).

### Bloques comparados y pesos
estructura 25% | js_modules 20% | js_core 15% | js_utils 15% |
plantillas 15% | idiomas 5% | menus 5%.

### Resultados del ultimo scan (17 proyectos)
7 apps, 3 documentales, 6 pendientes. Score medio apps: **85%**.
- ISO27001-SGSI 100% (patron) · ISO42001-SGIA 93% · ISO27701-SGP 89%
- ISO9001 85% · RGPD-LOPD 85% · ISO14001-2015 82%
- ISO14001-2026_NEW 76% · TISAX 67%
- Documentales y pendientes: score null (no penalizan).

### Notas clave
- El scanner NUNCA modifica los proyectos analizados; solo escribe en `_homogeneizacion/`.
- El HTML lleva datos embebidos (`var DATA_EMBEBIDA`) como fallback para `file://`.
  Para actualizar: ejecutar scan + re-embeber (script en README).
- Comparacion por presencia de ficheros, no por contenido.
- python-docx y openpyxl estan instalados (informes nativos, no fallback).
- Commit HTML: `e963377` en PLATAFORMA_OpenCode-NEW.
- Scripts Python quedan sin commitear en Plataforma_Seguimiento (repo con
  cambios pendientes del usuario; decidira cuando commitear ahi).

## Sistema de copias de seguridad (2026-06-06)

### Estrategia (2 capas, regla 3-2-1 adaptada)
1. **NAS CODANOR** (`/Volumes/CODANOR/opencode-backups`) — destino principal del
   script `backup-opencode.sh`. Es el destino por defecto (var `OPENCODE_BACKUP_DIR`).
2. **Time Machine** — ya activo en el Mac (disco 1.8 TB), capa horaria del sistema
   completo. No requiere configuracion adicional.
   *(GitHub descartado por ahora como tercera capa, por decision del usuario.)*

### Que se respalda y que se EXCLUYE
| Bloque | Origen | Tamano aprox. |
|--------|--------|---------------|
| Proyectos | `~/Proyectos` (18 proyectos) | 5.6 GB |
| Datos OpenCode | `storage/` + `opencode.db` (consistente) + `auth.json` + `account.json` | ~640 MB |
| Config | `~/.config/opencode` | 6.5 MB |

**EXCLUIDO** (decision del usuario, ahorro de espacio/tiempo):
`snapshot/` (~19 GB), `cache/` (102 MB), `log/`, `bin/`.

### Mejoras introducidas en backup-opencode.sh
- Destino por defecto cambiado a NAS CODANOR.
- `opencode.db` se copia de forma **consistente** con `sqlite3 ".backup"` (evita
  corrupcion por modo WAL). Validado con `PRAGMA integrity_check` = ok.
- Modo `--sessions` renombrado conceptualmente a "datos" (genera `opencode_data_*.tar.gz`)
  e incluye la DB + auth + account, no solo `storage/`.
- `--full` ya NO arrastra los 19 GB de snapshots; ejecuta proyectos + datos + config.
- Validacion de volumen montado, **prueba de escritura real** y chequeo de espacio
  libre (`OPENCODE_MIN_FREE_MB`, default 8000 MB) antes de copiar.
- Rotacion de 30 backups por tipo (ya existente).

### Automatizacion (launchd)
Archivo `com.codanor.opencode-backup.plist` (diario 02:00). Instalacion:
```bash
cp com.codanor.opencode-backup.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.codanor.opencode-backup.plist
```
Alternativa cron: `0 2 * * * /ruta/backup-opencode.sh >> backup.log 2>&1`

### Restauracion
```bash
./backup-opencode.sh --list                          # ver backups
./backup-opencode.sh --restore <archivo.tar.gz>      # restaura (crea safety backup antes)
```
Desastre total (Mac nuevo): instalar OpenCode -> montar NAS -> conceder TCC ->
restaurar `opencode_config_*`, `opencode_data_*` y `proyectos_*`.

### BLOQUEO PENDIENTE (accion del usuario)
El shell recibe **"Operation not permitted"** al escribir en `/Volumes/CODANOR`.
Es un permiso **TCC de macOS**, NO del NAS ni del script. Para activarlo:
- **Ajustes del Sistema > Privacidad y seguridad > Acceso total al disco** ->
  anadir la app de Terminal (y `/bin/bash` para launchd).
Sin este permiso el backup al NAS aborta con mensaje claro. La logica del script
ya esta validada en local (backup + restauracion + integridad DB = ok).

## Notas y descubrimientos

- **OpenCode queda bloqueado** si su directorio de trabajo se elimina o mueve. Todos los comandos bash fallan con `NotFound: FileSystem.access`. La unica solucion es cerrar y reabrir desde la nueva ubicacion.
- **El usuario NO tiene Node.js, Homebrew ni GitHub CLI (`gh`)**. Git push requiere autenticacion manual (username + Personal Access Token).
- **SonarCloud token**: ELIMINADO de este fichero (seguridad). Regenerar desde sonarcloud.io > My Account > Security. El token anterior (39 chars) estaba posiblemente truncado.
- **Puerto 5000** en macOS puede estar ocupado por AirPlay Receiver.
- **El usuario confundio** inicialmente sonarcloud.io con my.qt.io (Qt Group). Ser explicito con URLs.
