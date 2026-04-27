# Memory.md — PLATAFORMA_OpenCode
> Ultima actualizacion: 2026-04-27

## Estado actual

- **Fase**: Produccion / mantenimiento activo
- **Version**: Manual v2.4 (19 capitulos)
- **Ultimo cambio significativo**: Centralizacion de 8 proyectos a ~/Proyectos/, integracion SonarCloud
- **Issues abiertos**: 72 bugs de reliability + 3 security hotspots detectados por SonarCloud

## Infraestructura

| Elemento | Estado | Detalle |
|----------|--------|---------|
| Git | Si | 6 commits, rama principal |
| GitHub | Si | github.com/Jfajeda/PLATAFORMA_OpenCode |
| SonarCloud | Si | Security A, Reliability B, Maintainability A, 3.5% duplications |
| .gitignore | Si | Excluye .DS_Store, backups, __pycache__ |
| AGENTS.md | Si | Instrucciones para agentes IA |
| opencode.json | Si | MCP SonarQube configurado |
| Memory.md | Si | Este archivo |

## Componentes del proyecto

| Archivo | Descripcion | Tamano |
|---------|-------------|--------|
| Manual_OpenCode_Codanor.html | Manual v2.4, 19 capitulos | ~99 KB |
| plataforma-seguimiento.html | Dashboard + Kanban + Docs Hub + Changelog | ~62 KB |
| analisis-codigo.html | Panel SonarCloud exportable, 5 pestanas | ~46 KB |
| backup-opencode.sh | Script backup con 8 modos | ~10 KB |
| sonar-project.properties | Config scanner SonarCloud | 762 B |
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
- [ ] Automatizar backup con cron (diario a las 2am)
- [ ] Regenerar token SonarCloud (el actual de 39 chars puede estar truncado)

## Notas y descubrimientos

- **OpenCode queda bloqueado** si su directorio de trabajo se elimina o mueve. Todos los comandos bash fallan con `NotFound: FileSystem.access`. La unica solucion es cerrar y reabrir desde la nueva ubicacion.
- **El usuario NO tiene Node.js, Homebrew ni GitHub CLI (`gh`)**. Git push requiere autenticacion manual (username + Personal Access Token).
- **SonarCloud token**: `03bc00c8a603f92ebf11716085ada571a639851` (39 chars, posiblemente truncado — puede necesitar regenerarse).
- **Puerto 5000** en macOS puede estar ocupado por AirPlay Receiver.
- **El usuario confundio** inicialmente sonarcloud.io con my.qt.io (Qt Group). Ser explicito con URLs.
