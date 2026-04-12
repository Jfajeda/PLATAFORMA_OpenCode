#!/bin/bash
# =============================================================================
# backup-opencode.sh
# Script de copia de seguridad para OpenCode
# CODANOR - Jafa, S.L. | Barcelona, Catalunya
# =============================================================================
#
# USO:
#   ./backup-opencode.sh              # Backup completo
#   ./backup-opencode.sh --sessions   # Solo sesiones
#   ./backup-opencode.sh --config     # Solo configuracion
#   ./backup-opencode.sh --export     # Exportar sesiones a JSON individual
#   ./backup-opencode.sh --restore <archivo.tar.gz>  # Restaurar backup
#
# AUTOMATIZAR (cron diario a las 2am):
#   crontab -e
#   0 2 * * * /ruta/a/backup-opencode.sh >> /ruta/a/backup.log 2>&1
#
# =============================================================================

set -euo pipefail

# --- CONFIGURACION ---
BACKUP_DIR="${OPENCODE_BACKUP_DIR:-$HOME/Documents/opencode-backups}"
DATA_DIR="$HOME/.local/share/opencode"
CONFIG_DIR="$HOME/.config/opencode"
CACHE_DIR="$HOME/.cache/opencode"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
MAX_BACKUPS=30
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
  echo "    ./backup-opencode.sh              Backup completo (sesiones + config + cache)"
  echo "    ./backup-opencode.sh --sessions   Solo sesiones y mensajes"
  echo "    ./backup-opencode.sh --config     Solo archivos de configuracion"
  echo "    ./backup-opencode.sh --export     Exportar cada sesion a JSON individual"
  echo "    ./backup-opencode.sh --list       Listar backups existentes"
  echo "    ./backup-opencode.sh --restore <archivo.tar.gz>  Restaurar un backup"
  echo "    ./backup-opencode.sh --clean      Eliminar backups antiguos (>$MAX_BACKUPS)"
  echo "    ./backup-opencode.sh --help       Mostrar esta ayuda"
  echo ""
  echo "  Variables de entorno:"
  echo "    OPENCODE_BACKUP_DIR   Directorio de backups (default: ~/Documents/opencode-backups)"
  echo ""
}

check_dirs() {
  if [ ! -d "$DATA_DIR" ]; then
    warn "No se encontro directorio de datos: $DATA_DIR"
    warn "OpenCode puede no estar instalado o no haberse ejecutado aun."
  fi
}

ensure_backup_dir() {
  mkdir -p "$BACKUP_DIR"
}

get_size() {
  if [ -f "$1" ]; then
    du -sh "$1" | cut -f1
  else
    echo "0B"
  fi
}

# --- BACKUP COMPLETO ---
backup_full() {
  info "Iniciando backup COMPLETO de OpenCode..."
  ensure_backup_dir
  check_dirs

  local BACKUP_FILE="$BACKUP_DIR/opencode_full_$TIMESTAMP.tar.gz"
  local DIRS_TO_BACKUP=""

  # Construir lista de directorios existentes
  [ -d "$DATA_DIR" ] && DIRS_TO_BACKUP="$DIRS_TO_BACKUP .local/share/opencode/"
  [ -d "$CONFIG_DIR" ] && DIRS_TO_BACKUP="$DIRS_TO_BACKUP .config/opencode/"
  [ -d "$CACHE_DIR" ] && DIRS_TO_BACKUP="$DIRS_TO_BACKUP .cache/opencode/"

  if [ -z "$DIRS_TO_BACKUP" ]; then
    error "No se encontraron directorios de OpenCode para respaldar."
  fi

  info "Directorios a respaldar:"
  [ -d "$DATA_DIR" ] && info "  - $DATA_DIR (datos, sesiones, auth)"
  [ -d "$CONFIG_DIR" ] && info "  - $CONFIG_DIR (configuracion, agentes, comandos)"
  [ -d "$CACHE_DIR" ] && info "  - $CACHE_DIR (cache de proveedores)"

  tar -czf "$BACKUP_FILE" -C "$HOME" $DIRS_TO_BACKUP 2>/dev/null || true

  local SIZE=$(get_size "$BACKUP_FILE")
  ok "Backup completo creado: $BACKUP_FILE ($SIZE)"

  cleanup_old_backups "opencode_full_"
  show_summary
}

# --- BACKUP SOLO SESIONES ---
backup_sessions() {
  info "Iniciando backup de SESIONES..."
  ensure_backup_dir
  check_dirs

  local STORAGE_DIR="$DATA_DIR/storage"
  if [ ! -d "$STORAGE_DIR" ]; then
    error "No se encontro directorio de sesiones: $STORAGE_DIR"
  fi

  local BACKUP_FILE="$BACKUP_DIR/opencode_sessions_$TIMESTAMP.tar.gz"

  # Incluir storage + auth.json si existe
  local FILES=".local/share/opencode/storage/"
  [ -f "$DATA_DIR/auth.json" ] && FILES="$FILES .local/share/opencode/auth.json"

  tar -czf "$BACKUP_FILE" -C "$HOME" $FILES 2>/dev/null || true

  local SIZE=$(get_size "$BACKUP_FILE")
  local SESSION_COUNT=$(find "$STORAGE_DIR" -name "*.json" -path "*/session/*" 2>/dev/null | wc -l | tr -d ' ')
  ok "Backup de sesiones creado: $BACKUP_FILE ($SIZE)"
  info "Sesiones encontradas: $SESSION_COUNT"

  cleanup_old_backups "opencode_sessions_"
}

# --- BACKUP SOLO CONFIG ---
backup_config() {
  info "Iniciando backup de CONFIGURACION..."
  ensure_backup_dir

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
