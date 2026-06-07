#!/bin/bash
# =============================================================================
# backup-opencode.sh
# Script de copia de seguridad para OpenCode
# CODANOR - Jafa, S.L. | Barcelona, Catalunya
# =============================================================================
#
# USO:
#   ./backup-opencode.sh              # Backup completo al NAS (proyectos + datos + config)
#   ./backup-opencode.sh --proyectos  # Backup de TODOS los proyectos (~/Proyectos/)
#   ./backup-opencode.sh --sessions   # Solo sesiones + DB (consistente)
#   ./backup-opencode.sh --config     # Solo configuracion
#   ./backup-opencode.sh --export     # Exportar sesiones a JSON individual
#   ./backup-opencode.sh --restore <archivo.tar.gz>  # Restaurar backup
#
# DESTINO POR DEFECTO: NAS CODANOR (/Volumes/CODANOR/opencode-backups)
#   Los snapshots internos (~19 GB), cache, log y bin se EXCLUYEN del backup.
#   La base de datos opencode.db se copia de forma CONSISTENTE con sqlite3.
#
# AUTOMATIZAR (launchd recomendado en macOS, ver seccion al final del repo).
# Alternativa cron diario a las 2am:
#   crontab -e
#   0 2 * * * /ruta/a/backup-opencode.sh >> /ruta/a/backup.log 2>&1
#
# IMPORTANTE (macOS / NAS por SMB):
#   El proceso que ejecuta este script (Terminal o launchd) necesita permiso
#   TCC para escribir en volumenes de red. Concede "Acceso total al disco" en:
#   Ajustes del Sistema > Privacidad y seguridad > Acceso total al disco.
#
# =============================================================================

set -euo pipefail

# --- CONFIGURACION ---
BACKUP_DIR="${OPENCODE_BACKUP_DIR:-/Volumes/CODANOR/opencode-backups}"
PROYECTOS_DIR="${OPENCODE_PROYECTOS_DIR:-$HOME/Proyectos}"
DATA_DIR="$HOME/.local/share/opencode"
CONFIG_DIR="$HOME/.config/opencode"
CACHE_DIR="$HOME/.cache/opencode"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
MAX_BACKUPS=30
# Espacio libre minimo requerido en el destino (en MB) antes de respaldar
MIN_FREE_MB="${OPENCODE_MIN_FREE_MB:-8000}"
COLOR_GREEN='\033[0;32m'
COLOR_BLUE='\033[0;34m'
COLOR_RED='\033[0;31m'
COLOR_YELLOW='\033[1;33m'
COLOR_RESET='\033[0m'

# --- FUNCIONES ---
info() { echo -e "${COLOR_BLUE}[INFO]${COLOR_RESET} $1"; }
ok() { echo -e "${COLOR_GREEN}[OK]${COLOR_RESET} $1"; }
warn() { echo -e "${COLOR_YELLOW}[WARN]${COLOR_RESET} $1"; }
error() { echo -e "${COLOR_RED}[ERROR]${COLOR_RESET} $1"; exit 1; }

show_help() {
  echo ""
  echo "  backup-opencode.sh - Copia de seguridad para OpenCode"
  echo "  CODANOR - Jafa, S.L."
  echo ""
  echo "  Uso:"
  echo "    ./backup-opencode.sh              Backup completo al NAS (proyectos + datos + config)"
  echo "    ./backup-opencode.sh --proyectos  Backup de TODOS los proyectos en ~/Proyectos/"
  echo "    ./backup-opencode.sh --sessions   Datos OpenCode (storage + DB consistente)"
  echo "    ./backup-opencode.sh --config     Solo archivos de configuracion"
  echo "    ./backup-opencode.sh --export     Exportar cada sesion a JSON individual"
  echo "    ./backup-opencode.sh --list       Listar backups existentes"
  echo "    ./backup-opencode.sh --restore <archivo.tar.gz>  Restaurar un backup"
  echo "    ./backup-opencode.sh --clean      Eliminar backups antiguos (>$MAX_BACKUPS)"
  echo "    ./backup-opencode.sh --help       Mostrar esta ayuda"
  echo ""
  echo "  NOTA: los snapshots internos (~19 GB), cache, log y bin se EXCLUYEN."
  echo ""
  echo "  Variables de entorno:"
  echo "    OPENCODE_BACKUP_DIR   Directorio destino (default: /Volumes/CODANOR/opencode-backups)"
  echo "    OPENCODE_PROYECTOS_DIR Directorio de proyectos (default: ~/Proyectos)"
  echo "    OPENCODE_MIN_FREE_MB  Espacio libre minimo en MB (default: 8000)"
  echo ""
}

check_dirs() {
  if [ ! -d "$DATA_DIR" ]; then
    warn "No se encontro directorio de datos: $DATA_DIR"
    warn "OpenCode puede no estar instalado o no haberse ejecutado aun."
  fi
}

# Verifica que el destino (NAS) este montado y sea escribible.
# Si BACKUP_DIR apunta a /Volumes/..., comprueba el volumen y permisos TCC.
ensure_backup_dir() {
  # Detectar si el destino esta en un volumen externo/red (/Volumes/...)
  case "$BACKUP_DIR" in
    /Volumes/*)
      local VOLUME
      VOLUME=$(echo "$BACKUP_DIR" | awk -F/ '{print "/"$2"/"$3}')
      if [ ! -d "$VOLUME" ]; then
        error "El volumen de destino no esta montado: $VOLUME
       Monta el NAS CODANOR (Finder > Ir > Conectar al servidor) y reintenta."
      fi
      # Comprobar acceso real (TCC en macOS bloquea volumenes de red)
      if ! ls "$VOLUME" >/dev/null 2>&1; then
        error "Sin acceso al volumen $VOLUME (permiso denegado).
       En macOS concede 'Acceso total al disco' al proceso que ejecuta este
       script: Ajustes del Sistema > Privacidad y seguridad > Acceso total al disco."
      fi
      ;;
  esac

  mkdir -p "$BACKUP_DIR" 2>/dev/null || error "No se pudo crear el directorio de backups: $BACKUP_DIR"

  # Prueba de escritura real
  local WTEST="$BACKUP_DIR/.write_test_$$"
  if ! touch "$WTEST" 2>/dev/null; then
    error "No hay permiso de escritura en: $BACKUP_DIR
       Revisa los permisos del NAS y el 'Acceso total al disco' en macOS."
  fi
  rm -f "$WTEST"
}

# Comprueba que haya al menos MIN_FREE_MB libres en el destino.
check_free_space() {
  local FREE_MB
  FREE_MB=$(df -m "$BACKUP_DIR" 2>/dev/null | awk 'NR==2 {print $4}')
  if [ -n "${FREE_MB:-}" ] && [ "$FREE_MB" -lt "$MIN_FREE_MB" ]; then
    error "Espacio insuficiente en $BACKUP_DIR: ${FREE_MB} MB libres (minimo ${MIN_FREE_MB} MB)."
  fi
}

# Copia consistente de la DB SQLite usando el comando .backup (evita corrupcion
# por el modo WAL). Devuelve la ruta del fichero temporal copiado.
backup_db_consistent() {
  local DEST="$1"
  local DB="$DATA_DIR/opencode.db"
  [ -f "$DB" ] || return 1
  if command -v sqlite3 >/dev/null 2>&1; then
    sqlite3 "$DB" ".backup '$DEST'" 2>/dev/null && return 0
    warn "sqlite3 .backup fallo; usando copia directa (menos segura)."
  else
    warn "sqlite3 no disponible; usando copia directa de la DB."
  fi
  cp "$DB" "$DEST" 2>/dev/null || return 1
  return 0
}

get_size() {
  if [ -f "$1" ]; then
    du -sh "$1" | cut -f1
  else
    echo "0B"
  fi
}

# --- BACKUP COMPLETO ---
# Respalda, en archivos SEPARADOS, los tres bloques relevantes:
#   1) proyectos   2) datos OpenCode (storage + DB consistente)   3) config
# EXCLUYE snapshots (~19 GB), cache, log y bin por ser pesados/regenerables.
backup_full() {
  info "Iniciando backup COMPLETO al NAS (snapshots/cache/log/bin EXCLUIDOS)..."
  ensure_backup_dir
  check_free_space
  check_dirs

  backup_proyectos
  backup_sessions
  backup_config

  ok "Backup completo finalizado en: $BACKUP_DIR"
  show_summary
}

# --- BACKUP DATOS OPENCODE (sesiones + DB consistente) ---
backup_sessions() {
  info "Iniciando backup de DATOS OpenCode (storage + DB consistente)..."
  ensure_backup_dir
  check_dirs

  local STORAGE_DIR="$DATA_DIR/storage"
  if [ ! -d "$STORAGE_DIR" ]; then
    error "No se encontro directorio de sesiones: $STORAGE_DIR"
  fi

  local BACKUP_FILE="$BACKUP_DIR/opencode_data_$TIMESTAMP.tar.gz"

  # Copia consistente de la DB en un area temporal
  local TMP_DIR
  TMP_DIR=$(mktemp -d)
  trap 'rm -rf "$TMP_DIR"' RETURN
  local DB_OK=0
  if [ -f "$DATA_DIR/opencode.db" ]; then
    info "Copiando opencode.db de forma consistente (sqlite3 .backup)..."
    if backup_db_consistent "$TMP_DIR/opencode.db"; then
      DB_OK=1
      ok "DB copiada de forma consistente."
    else
      warn "No se pudo copiar la DB; el backup continuara sin ella."
    fi
  fi

  # Empaquetar: storage/ + auth/account + DB consistente
  local FILES=".local/share/opencode/storage/"
  [ -f "$DATA_DIR/auth.json" ] && FILES="$FILES .local/share/opencode/auth.json"
  [ -f "$DATA_DIR/account.json" ] && FILES="$FILES .local/share/opencode/account.json"

  if [ "$DB_OK" -eq 1 ]; then
    # Incluir la DB consistente bajo la misma ruta relativa que tendria en HOME
    mkdir -p "$TMP_DIR/.local/share/opencode"
    mv "$TMP_DIR/opencode.db" "$TMP_DIR/.local/share/opencode/opencode.db"
    tar -czf "$BACKUP_FILE" -C "$HOME" $FILES -C "$TMP_DIR" .local/share/opencode/opencode.db 2>/dev/null || true
  else
    tar -czf "$BACKUP_FILE" -C "$HOME" $FILES 2>/dev/null || true
  fi

  local SIZE=$(get_size "$BACKUP_FILE")
  local SESSION_COUNT=$(find "$STORAGE_DIR" -name "*.json" -path "*/session/*" 2>/dev/null | wc -l | tr -d ' ')
  ok "Backup de datos creado: $BACKUP_FILE ($SIZE)"
  info "Sesiones encontradas: $SESSION_COUNT"

  cleanup_old_backups "opencode_data_"
}

# --- BACKUP SOLO CONFIG ---
backup_config() {
  info "Iniciando backup de CONFIGURACION..."
  ensure_backup_dir
  check_free_space

  if [ ! -d "$CONFIG_DIR" ]; then
    error "No se encontro directorio de configuracion: $CONFIG_DIR"
  fi

  local BACKUP_FILE="$BACKUP_DIR/opencode_config_$TIMESTAMP.tar.gz"
  tar -czf "$BACKUP_FILE" -C "$HOME" .config/opencode/ 2>/dev/null || true

  local SIZE=$(get_size "$BACKUP_FILE")
  ok "Backup de configuracion creado: $BACKUP_FILE ($SIZE)"

  cleanup_old_backups "opencode_config_"
}

# --- EXPORTAR SESIONES A JSON ---
export_sessions() {
  info "Exportando sesiones individuales a JSON..."
  ensure_backup_dir

  # Verificar que opencode CLI esta disponible
  if ! command -v opencode &> /dev/null; then
    error "opencode CLI no encontrado. Instala OpenCode primero."
  fi

  local EXPORT_DIR="$BACKUP_DIR/exports_$TIMESTAMP"
  mkdir -p "$EXPORT_DIR"

  # Obtener lista de sesiones
  info "Obteniendo lista de sesiones..."
  local SESSION_LIST
  SESSION_LIST=$(opencode session list --format json 2>/dev/null || echo "[]")

  if [ "$SESSION_LIST" = "[]" ] || [ -z "$SESSION_LIST" ]; then
    warn "No se encontraron sesiones para exportar."
    warn "Puedes exportar manualmente con: opencode export <sessionID>"
    return
  fi

  local COUNT=0
  # Intentar exportar cada sesion
  echo "$SESSION_LIST" | while IFS= read -r line; do
    local SID=$(echo "$line" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4 2>/dev/null || true)
    if [ -n "$SID" ]; then
      info "  Exportando $SID..."
      opencode export "$SID" > "$EXPORT_DIR/$SID.json" 2>/dev/null || warn "  No se pudo exportar $SID"
      COUNT=$((COUNT + 1))
    fi
  done

  ok "Sesiones exportadas en: $EXPORT_DIR/"
}

# --- RESTAURAR ---
restore_backup() {
  local BACKUP_FILE="$1"

  if [ ! -f "$BACKUP_FILE" ]; then
    error "Archivo no encontrado: $BACKUP_FILE"
  fi

  warn "ATENCION: Esto restaurara los datos de OpenCode."
  warn "Los datos actuales seran sobreescritos."
  echo ""
  read -p "Continuar? (s/N): " CONFIRM

  if [ "$CONFIRM" != "s" ] && [ "$CONFIRM" != "S" ]; then
    info "Restauracion cancelada."
    exit 0
  fi

  # Crear backup del estado actual antes de restaurar
  info "Creando backup de seguridad del estado actual..."
  local SAFETY_BACKUP="$BACKUP_DIR/opencode_pre_restore_$TIMESTAMP.tar.gz"
  mkdir -p "$BACKUP_DIR"

  local DIRS=""
  [ -d "$DATA_DIR" ] && DIRS="$DIRS .local/share/opencode/"
  [ -d "$CONFIG_DIR" ] && DIRS="$DIRS .config/opencode/"

  if [ -n "$DIRS" ]; then
    tar -czf "$SAFETY_BACKUP" -C "$HOME" $DIRS 2>/dev/null || true
    ok "Backup de seguridad creado: $SAFETY_BACKUP"
  fi

  # Restaurar
  info "Restaurando desde: $BACKUP_FILE"
  tar -xzf "$BACKUP_FILE" -C "$HOME"

  ok "Restauracion completada."
  info "Si algo falla, puedes volver al estado anterior con:"
  info "  ./backup-opencode.sh --restore $SAFETY_BACKUP"
}

# --- LISTAR BACKUPS ---
list_backups() {
  ensure_backup_dir
  info "Backups en: $BACKUP_DIR"
  echo ""

  if [ -z "$(ls -A "$BACKUP_DIR" 2>/dev/null)" ]; then
    warn "No hay backups."
    return
  fi

  printf "  %-45s %8s  %s\n" "ARCHIVO" "TAMANO" "FECHA"
  printf "  %-45s %8s  %s\n" "-------" "------" "-----"

  for f in "$BACKUP_DIR"/opencode_*.tar.gz; do
    [ -f "$f" ] || continue
    local NAME=$(basename "$f")
    local SIZE=$(get_size "$f")
    local DATE=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$f" 2>/dev/null || stat --format="%y" "$f" 2>/dev/null | cut -d'.' -f1)
    printf "  %-45s %8s  %s\n" "$NAME" "$SIZE" "$DATE"
  done

  echo ""
  local TOTAL=$(ls "$BACKUP_DIR"/opencode_*.tar.gz 2>/dev/null | wc -l | tr -d ' ')
  info "Total: $TOTAL backups"
}

# --- LIMPIEZA ---
cleanup_old_backups() {
  local PREFIX="${1:-opencode_}"
  local COUNT=$(ls "$BACKUP_DIR"/${PREFIX}*.tar.gz 2>/dev/null | wc -l | tr -d ' ')

  if [ "$COUNT" -gt "$MAX_BACKUPS" ]; then
    local TO_DELETE=$((COUNT - MAX_BACKUPS))
    info "Limpiando $TO_DELETE backups antiguos (maximo: $MAX_BACKUPS)..."
    ls -t "$BACKUP_DIR"/${PREFIX}*.tar.gz | tail -n "$TO_DELETE" | xargs rm -f
    ok "Backups antiguos eliminados."
  fi
}

clean_backups() {
  ensure_backup_dir
  cleanup_old_backups "opencode_full_"
  cleanup_old_backups "opencode_sessions_"
  cleanup_old_backups "opencode_config_"
  ok "Limpieza completada."
}

# --- BACKUP PROYECTOS ---
backup_proyectos() {
  info "Iniciando backup de TODOS los proyectos en $PROYECTOS_DIR..."
  ensure_backup_dir
  check_free_space

  if [ ! -d "$PROYECTOS_DIR" ]; then
    error "No se encontro directorio de proyectos: $PROYECTOS_DIR"
  fi

  local BACKUP_FILE="$BACKUP_DIR/proyectos_$TIMESTAMP.tar.gz"
  local PROJECT_COUNT=$(ls -d "$PROYECTOS_DIR"/*/ 2>/dev/null | wc -l | tr -d ' ')

  info "Proyectos encontrados: $PROJECT_COUNT"
  for d in "$PROYECTOS_DIR"/*/; do
    local NAME=$(basename "$d")
    local SIZE=$(du -sh "$d" 2>/dev/null | cut -f1)
    info "  - $NAME ($SIZE)"
  done

  info "Creando archivo de backup..."
  tar -czf "$BACKUP_FILE" -C "$HOME" Proyectos/ 2>/dev/null || true

  local SIZE=$(get_size "$BACKUP_FILE")
  ok "Backup de proyectos creado: $BACKUP_FILE ($SIZE)"
  info "Proyectos incluidos: $PROJECT_COUNT"

  cleanup_old_backups "proyectos_"
}

# --- RESUMEN ---
show_summary() {
  echo ""
  info "=== Resumen de datos de OpenCode ==="

  if [ -d "$DATA_DIR/storage/session" ]; then
    local SESSIONS=$(find "$DATA_DIR/storage/session" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
    info "  Sesiones almacenadas: $SESSIONS"
  fi

  if [ -d "$DATA_DIR/storage/message" ]; then
    local MESSAGES=$(find "$DATA_DIR/storage/message" -type f 2>/dev/null | wc -l | tr -d ' ')
    info "  Archivos de mensajes: $MESSAGES"
  fi

  if [ -d "$CONFIG_DIR/agents" ]; then
    local AGENTS=$(find "$CONFIG_DIR/agents" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    info "  Agentes globales: $AGENTS"
  fi

  if [ -d "$CONFIG_DIR/commands" ]; then
    local COMMANDS=$(find "$CONFIG_DIR/commands" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    info "  Comandos globales: $COMMANDS"
  fi

  local DATA_SIZE=$(du -sh "$DATA_DIR" 2>/dev/null | cut -f1 || echo "N/A")
  local CONFIG_SIZE=$(du -sh "$CONFIG_DIR" 2>/dev/null | cut -f1 || echo "N/A")
  local BACKUP_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1 || echo "0B")

  info "  Tamano datos: $DATA_SIZE"
  info "  Tamano config: $CONFIG_SIZE"
  info "  Tamano backups: $BACKUP_SIZE"
  echo ""
}

# --- MAIN ---
case "${1:-}" in
  --proyectos)  backup_proyectos ;;
  --sessions)   backup_sessions ;;
  --config)     backup_config ;;
  --export)     export_sessions ;;
  --list)       list_backups ;;
  --restore)
    if [ -z "${2:-}" ]; then
      error "Especifica el archivo a restaurar: --restore <archivo.tar.gz>"
    fi
    restore_backup "$2"
    ;;
  --clean)      clean_backups ;;
  --help|-h)    show_help ;;
  "")           backup_full ;;
  *)            error "Opcion desconocida: $1. Usa --help para ver las opciones." ;;
esac
