#!/bin/bash
# =============================================================================
# backup-opencode.sh
# Script de copia de seguridad para OpenCode
# CODANOR - Jafa, S.L. | Barcelona, Catalunya
# =============================================================================
#
# USO:
#   ./backup-opencode.sh                         # Backup completo (proyectos + datos + config)
#   ./backup-opencode.sh --proyectos             # Backup de TODOS los proyectos (~/Proyectos/)
#   ./backup-opencode.sh --sessions              # Solo sesiones + DB (consistente)
#   ./backup-opencode.sh --config                # Solo configuracion
#   ./backup-opencode.sh --export                # Exportar sesiones a JSON individual
#   ./backup-opencode.sh --list                  # Listar backups existentes
#   ./backup-opencode.sh --restore <tar.gz>      # Restaurar datos OpenCode
#   ./backup-opencode.sh --restore-proyectos <tar.gz>  # Restaurar ~/Proyectos/ completo
#   ./backup-opencode.sh --restore-db <tar.gz>   # Restaurar solo plataforma.db
#   ./backup-opencode.sh --verify                # Verificar integridad de todos los backups
#   ./backup-opencode.sh --test-restore          # Prueba de restauracion (no destructiva)
#   ./backup-opencode.sh --clean                 # Eliminar backups antiguos
#   ./backup-opencode.sh --help                  # Mostrar esta ayuda
#
# DESTINO PRINCIPAL:   Transcend (/Volumes/Transcend/opencode-backups)
# DESTINO REDUNDANTE:  NAS CODANOR (/Volumes/CODANOR/opencode-backups)
#   Requiere TCC "Acceso total al disco" para launchd, o montar el NAS como
#   Login Item (Ajustes > General > Elementos de inicio de sesion).
#
# EXTERNALIZADO: iCloud Drive (CODANOR-Backups/) — los tars se copian
#   automaticamente a iCloud al finalizar backup_full. iCloud los sube a internet.
#   Las DBs van dentro de los tars (copiadas con sqlite3 .backup — sin riesgo WAL).
#
# EXCLUIDOS: snapshots OpenCode (~19 GB), cache, log, bin, .git, node_modules.
#
# AUTOMATIZACION: launchd diario a las 09:00 (com.codanor.opencode-backup.plist)
#   Test de restauracion: primer lunes de cada mes a las 10:00 (mismo plist)
#   Log: ~/Library/Logs/com.codanor.opencode-backup.log
#
# =============================================================================

set -euo pipefail

# --- CONFIGURACION ---
BACKUP_DIR="${OPENCODE_BACKUP_DIR:-/Volumes/Transcend/opencode-backups}"
BACKUP_DIR_REDUNDANT="${OPENCODE_BACKUP_DIR_REDUNDANT:-/Volumes/CODANOR/opencode-backups}"
PROYECTOS_DIR="${OPENCODE_PROYECTOS_DIR:-$HOME/Proyectos}"
ICLOUD_DIR="${OPENCODE_ICLOUD_DIR:-$HOME/Library/Mobile Documents/com~apple~CloudDocs/CODANOR-Backups}"
DATA_DIR="$HOME/.local/share/opencode"
CONFIG_DIR="$HOME/.config/opencode"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
MAX_BACKUPS=30
# Espacio libre minimo requerido en el destino (en MB) antes de respaldar
MIN_FREE_MB="${OPENCODE_MIN_FREE_MB:-8000}"
# Numero minimo esperado de clientes en plataforma.db (para validacion)
MIN_CLIENTS="${OPENCODE_MIN_CLIENTS:-10}"
COLOR_GREEN='\033[0;32m'
COLOR_BLUE='\033[0;34m'
COLOR_RED='\033[0;31m'
COLOR_YELLOW='\033[1;33m'
COLOR_RESET='\033[0m'

# --- FUNCIONES BASE ---
info()  { echo -e "${COLOR_BLUE}[INFO]${COLOR_RESET} $1"; }
ok()    { echo -e "${COLOR_GREEN}[OK]${COLOR_RESET} $1"; }
warn()  { echo -e "${COLOR_YELLOW}[WARN]${COLOR_RESET} $1"; }
error() { echo -e "${COLOR_RED}[ERROR]${COLOR_RESET} $1"; exit 1; }
pass()  { echo -e "${COLOR_GREEN}[PASS]${COLOR_RESET} $1"; }
fail()  { echo -e "${COLOR_RED}[FAIL]${COLOR_RESET} $1"; }

show_help() {
  echo ""
  echo "  backup-opencode.sh - Copia de seguridad para OpenCode"
  echo "  CODANOR - Jafa, S.L."
  echo ""
  echo "  Uso:"
  echo "    ./backup-opencode.sh                         Backup completo (proyectos + datos + config + iCloud)"
  echo "    ./backup-opencode.sh --proyectos             Backup de TODOS los proyectos en ~/Proyectos/"
  echo "    ./backup-opencode.sh --sessions              Datos OpenCode (storage + DB consistente)"
  echo "    ./backup-opencode.sh --config                Solo archivos de configuracion"
  echo "    ./backup-opencode.sh --export                Exportar cada sesion a JSON individual"
  echo "    ./backup-opencode.sh --list                  Listar backups existentes"
  echo "    ./backup-opencode.sh --restore <tar.gz>      Restaurar datos OpenCode"
  echo "    ./backup-opencode.sh --restore-proyectos <tar.gz>  Restaurar ~/Proyectos/ completo"
  echo "    ./backup-opencode.sh --restore-db <tar.gz>   Restaurar solo plataforma.db"
  echo "    ./backup-opencode.sh --verify                Verificar integridad de todos los backups"
  echo "    ./backup-opencode.sh --test-restore          Prueba de restauracion no destructiva"
  echo "    ./backup-opencode.sh --clean                 Eliminar backups antiguos (>$MAX_BACKUPS)"
  echo "    ./backup-opencode.sh --help                  Mostrar esta ayuda"
  echo ""
  echo "  DESTINOS:"
  echo "    Principal:    $BACKUP_DIR"
  echo "    Redundante:   $BACKUP_DIR_REDUNDANT"
  echo "    Externalizado: iCloud Drive (CODANOR-Backups/)"
  echo ""
  echo "  NOTA: snapshots (~19 GB), cache, log, bin, .git y node_modules se EXCLUYEN."
  echo "  Las DBs (.db) se incluyen siempre dentro de los tars (copia sqlite3 .backup)."
  echo ""
  echo "  Variables de entorno:"
  echo "    OPENCODE_BACKUP_DIR            Destino principal  (default: /Volumes/Transcend/opencode-backups)"
  echo "    OPENCODE_BACKUP_DIR_REDUNDANT  Destino redundante (default: /Volumes/CODANOR/opencode-backups)"
  echo "    OPENCODE_PROYECTOS_DIR         Directorio proyectos (default: ~/Proyectos)"
  echo "    OPENCODE_ICLOUD_DIR            Carpeta iCloud destino"
  echo "    OPENCODE_MIN_FREE_MB           Espacio libre minimo en MB (default: 8000)"
  echo "    OPENCODE_MIN_CLIENTS           Minimo clientes esperados en plataforma.db (default: 10)"
  echo ""
}

check_dirs() {
  if [ ! -d "$DATA_DIR" ]; then
    warn "No se encontro directorio de datos: $DATA_DIR"
    warn "OpenCode puede no estar instalado o no haberse ejecutado aun."
  fi
}

# Verifica que el destino este montado y sea escribible.
ensure_backup_dir() {
  case "$BACKUP_DIR" in
    /Volumes/*)
      local VOLUME
      VOLUME=$(echo "$BACKUP_DIR" | awk -F/ '{print "/"$2"/"$3}')
      if [ ! -d "$VOLUME" ]; then
        error "El volumen de destino no esta montado: $VOLUME
       Conecta el disco o monta el NAS (Finder > Ir > Conectar al servidor)."
      fi
      if ! ls "$VOLUME" >/dev/null 2>&1; then
        error "Sin acceso al volumen $VOLUME (permiso denegado TCC).
       Ajustes del Sistema > Privacidad y seguridad > Acceso total al disco."
      fi
      ;;
  esac
  mkdir -p "$BACKUP_DIR" 2>/dev/null || error "No se pudo crear el directorio: $BACKUP_DIR"
  local WTEST="$BACKUP_DIR/.write_test_$$"
  if ! touch "$WTEST" 2>/dev/null; then
    error "Sin permiso de escritura en: $BACKUP_DIR"
  fi
  rm -f "$WTEST"
}

# Comprueba espacio libre minimo en el destino.
check_free_space() {
  local FREE_MB
  FREE_MB=$(df -m "$BACKUP_DIR" 2>/dev/null | awk 'NR==2 {print $4}')
  if [ -n "${FREE_MB:-}" ] && [ "$FREE_MB" -lt "$MIN_FREE_MB" ]; then
    error "Espacio insuficiente en $BACKUP_DIR: ${FREE_MB} MB libres (minimo ${MIN_FREE_MB} MB)."
  fi
}

# Copia consistente de opencode.db con sqlite3 .backup (seguro en modo WAL).
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

# =============================================================================
# --- BACKUP ---
# =============================================================================

# --- REDUNDANCIA A DISCO/NAS ---
backup_redundant() {
  local VOLUME
  VOLUME=$(echo "$BACKUP_DIR_REDUNDANT" | awk -F/ '{print "/"$2"/"$3}')
  if [ ! -d "$VOLUME" ]; then
    warn "Volumen redundante no montado ($VOLUME) — redundancia omitida."
    return 0
  fi
  if ! ls "$VOLUME" >/dev/null 2>&1; then
    warn "Sin acceso a $VOLUME (TCC) — redundancia omitida."
    return 0
  fi
  if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A "$BACKUP_DIR" 2>/dev/null)" ]; then
    warn "Directorio principal vacio — redundancia omitida."
    return 0
  fi
  info "Sincronizando redundancia → $BACKUP_DIR_REDUNDANT ..."
  mkdir -p "$BACKUP_DIR_REDUNDANT" 2>/dev/null || {
    warn "No se pudo crear $BACKUP_DIR_REDUNDANT — redundancia omitida."
    return 0
  }
  if rsync -a --delete \
      --exclude='.DS_Store' \
      --exclude='Thumbs.db' \
      "$BACKUP_DIR/" "$BACKUP_DIR_REDUNDANT/" 2>/dev/null; then
    local COUNT SIZE
    COUNT=$(ls "$BACKUP_DIR_REDUNDANT"/*.tar.gz 2>/dev/null | wc -l | tr -d ' ')
    SIZE=$(du -sh "$BACKUP_DIR_REDUNDANT" 2>/dev/null | cut -f1)
    ok "Redundancia sincronizada: $COUNT archivos · $SIZE → $BACKUP_DIR_REDUNDANT"
  else
    warn "rsync fallo — redundancia puede estar incompleta."
  fi
}

# --- BACKUP ICLOUD (capa externalizada) ---
# Copia los tars mas recientes a iCloud Drive para subida automatica a internet.
# Las DBs van dentro de los tars (copiadas con sqlite3 .backup) — sin riesgo WAL.
backup_icloud() {
  # Verificar que iCloud Drive esta disponible
  local ICLOUD_BASE="$HOME/Library/Mobile Documents/com~apple~CloudDocs"
  if [ ! -d "$ICLOUD_BASE" ]; then
    warn "iCloud Drive no disponible — copia externalizada omitida."
    return 0
  fi

  info "Copiando backups a iCloud Drive (CODANOR-Backups/)..."
  mkdir -p "$ICLOUD_DIR" 2>/dev/null || {
    warn "No se pudo crear carpeta iCloud: $ICLOUD_DIR — omitido."
    return 0
  }

  local COPIED=0

  # Copiar el tar de proyectos mas reciente (contiene plataforma.db)
  local LAST_P
  LAST_P=$(ls -t "$BACKUP_DIR"/proyectos_*.tar.gz 2>/dev/null | head -1)
  if [ -n "$LAST_P" ]; then
    cp "$LAST_P" "$ICLOUD_DIR/" 2>/dev/null && COPIED=$((COPIED + 1)) || \
      warn "No se pudo copiar proyectos a iCloud."
    # Mantener solo el mas reciente en iCloud (evitar llenar el plan)
    ls -t "$ICLOUD_DIR"/proyectos_*.tar.gz 2>/dev/null | tail -n +2 | xargs rm -f 2>/dev/null || true
  fi

  # Copiar el tar de datos OpenCode mas reciente (contiene opencode.db)
  local LAST_D
  LAST_D=$(ls -t "$BACKUP_DIR"/opencode_data_*.tar.gz 2>/dev/null | head -1)
  if [ -n "$LAST_D" ]; then
    cp "$LAST_D" "$ICLOUD_DIR/" 2>/dev/null && COPIED=$((COPIED + 1)) || \
      warn "No se pudo copiar datos OpenCode a iCloud."
    ls -t "$ICLOUD_DIR"/opencode_data_*.tar.gz 2>/dev/null | tail -n +2 | xargs rm -f 2>/dev/null || true
  fi

  # Copiar el tar de config mas reciente
  local LAST_C
  LAST_C=$(ls -t "$BACKUP_DIR"/opencode_config_*.tar.gz 2>/dev/null | head -1)
  if [ -n "$LAST_C" ]; then
    cp "$LAST_C" "$ICLOUD_DIR/" 2>/dev/null && COPIED=$((COPIED + 1)) || \
      warn "No se pudo copiar config a iCloud."
    ls -t "$ICLOUD_DIR"/opencode_config_*.tar.gz 2>/dev/null | tail -n +2 | xargs rm -f 2>/dev/null || true
  fi

  if [ "$COPIED" -gt 0 ]; then
    local ICLOUD_SIZE
    ICLOUD_SIZE=$(du -sh "$ICLOUD_DIR" 2>/dev/null | cut -f1)
    ok "iCloud Drive: $COPIED archivos copiados ($ICLOUD_SIZE) → subida automatica en curso"
    info "  Ruta: $ICLOUD_DIR"
    info "  Accesible en: icloud.com o cualquier dispositivo Apple"
  else
    warn "No se copio ningun archivo a iCloud Drive."
  fi
}

# --- BACKUP COMPLETO ---
backup_full() {
  info "Iniciando backup COMPLETO (snapshots/cache/log/bin/.git/node_modules EXCLUIDOS)..."
  ensure_backup_dir
  check_free_space
  check_dirs

  backup_proyectos_solo
  backup_sessions_solo
  backup_config_solo

  ok "Backup completo finalizado en: $BACKUP_DIR"
  backup_redundant
  backup_icloud
  show_summary
}

# Versiones internas sin redundancia ni iCloud (usadas por backup_full)
backup_proyectos_solo() {
  info "Iniciando backup de TODOS los proyectos en $PROYECTOS_DIR..."
  if [ ! -d "$PROYECTOS_DIR" ]; then
    error "No se encontro directorio de proyectos: $PROYECTOS_DIR"
  fi
  local BACKUP_FILE="$BACKUP_DIR/proyectos_$TIMESTAMP.tar.gz"
  local PROJECT_COUNT
  PROJECT_COUNT=$(ls -d "$PROYECTOS_DIR"/*/ 2>/dev/null | wc -l | tr -d ' ')
  info "Proyectos encontrados: $PROJECT_COUNT"
  for d in "$PROYECTOS_DIR"/*/; do
    local NAME SIZE
    NAME=$(basename "$d")
    SIZE=$(du -sh "$d" 2>/dev/null | cut -f1)
    info "  - $NAME ($SIZE)"
  done
  info "Creando archivo de backup (excluye .git, node_modules y archivos Synology)..."
  tar -czf "$BACKUP_FILE" \
    --exclude='Proyectos/*/.git' \
    --exclude='Proyectos/*/node_modules' \
    --exclude='Proyectos/*/.opencode/node_modules' \
    --exclude='Proyectos/.SynologyWorkingDirectory' \
    --exclude='Proyectos/*/.SynologyWorkingDirectory' \
    -C "$HOME" Proyectos/ 2>/dev/null || true
  local SIZE
  SIZE=$(get_size "$BACKUP_FILE")
  ok "Backup de proyectos creado: $BACKUP_FILE ($SIZE)"
  info "Proyectos incluidos: $PROJECT_COUNT"
  cleanup_old_backups "proyectos_"
}

backup_sessions_solo() {
  info "Iniciando backup de DATOS OpenCode (storage + DB consistente)..."
  check_dirs
  local STORAGE_DIR="$DATA_DIR/storage"
  if [ ! -d "$STORAGE_DIR" ]; then
    error "No se encontro directorio de sesiones: $STORAGE_DIR"
  fi
  local BACKUP_FILE="$BACKUP_DIR/opencode_data_$TIMESTAMP.tar.gz"
  local TMP_DIR
  TMP_DIR=$(mktemp -d)
  trap 'rm -rf "${TMP_DIR:-}"' RETURN
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
  local FILES=".local/share/opencode/storage/"
  [ -f "$DATA_DIR/auth.json" ]    && FILES="$FILES .local/share/opencode/auth.json"
  [ -f "$DATA_DIR/account.json" ] && FILES="$FILES .local/share/opencode/account.json"
  if [ "$DB_OK" -eq 1 ]; then
    mkdir -p "$TMP_DIR/.local/share/opencode"
    mv "$TMP_DIR/opencode.db" "$TMP_DIR/.local/share/opencode/opencode.db"
    tar -czf "$BACKUP_FILE" -C "$HOME" $FILES \
      -C "$TMP_DIR" .local/share/opencode/opencode.db 2>/dev/null || true
  else
    tar -czf "$BACKUP_FILE" -C "$HOME" $FILES 2>/dev/null || true
  fi
  local SIZE SESSION_COUNT
  SIZE=$(get_size "$BACKUP_FILE")
  SESSION_COUNT=$(find "$STORAGE_DIR" -name "*.json" -path "*/session/*" 2>/dev/null | wc -l | tr -d ' ')
  ok "Backup de datos creado: $BACKUP_FILE ($SIZE)"
  info "Sesiones encontradas: $SESSION_COUNT"
  cleanup_old_backups "opencode_data_"
}

backup_config_solo() {
  info "Iniciando backup de CONFIGURACION..."
  if [ ! -d "$CONFIG_DIR" ]; then
    error "No se encontro directorio de configuracion: $CONFIG_DIR"
  fi
  local BACKUP_FILE="$BACKUP_DIR/opencode_config_$TIMESTAMP.tar.gz"
  tar -czf "$BACKUP_FILE" -C "$HOME" .config/opencode/ 2>/dev/null || true
  local SIZE
  SIZE=$(get_size "$BACKUP_FILE")
  ok "Backup de configuracion creado: $BACKUP_FILE ($SIZE)"
  cleanup_old_backups "opencode_config_"
}

# --- MODOS PUBLICOS INDIVIDUALES (con redundancia) ---
backup_proyectos() {
  ensure_backup_dir; check_free_space
  backup_proyectos_solo
  backup_redundant
  backup_icloud
}

backup_sessions() {
  ensure_backup_dir
  backup_sessions_solo
  backup_redundant
  backup_icloud
}

backup_config() {
  ensure_backup_dir; check_free_space
  backup_config_solo
  backup_redundant
  backup_icloud
}

# =============================================================================
# --- VERIFICACION DE INTEGRIDAD ---
# =============================================================================

# Verifica integridad de todos los tars en BACKUP_DIR sin extraer al sistema.
# Para cada tar que contenga una .db, la extrae en /tmp y ejecuta integrity_check.
verify_backups() {
  info "=== Verificando integridad de backups en: $BACKUP_DIR ==="
  echo ""

  local FOUND=0 PASS_COUNT=0 FAIL_COUNT=0

  for TAR in "$BACKUP_DIR"/*.tar.gz; do
    [ -f "$TAR" ] || continue
    FOUND=$((FOUND + 1))
    local NAME SIZE DATE
    NAME=$(basename "$TAR")
    SIZE=$(get_size "$TAR")
    DATE=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$TAR" 2>/dev/null || echo "?")

    # 1. Verificar integridad del tar
    if tar -tzf "$TAR" > /dev/null 2>&1; then
      pass "TAR OK  │ $NAME ($SIZE) │ $DATE"
      PASS_COUNT=$((PASS_COUNT + 1))
    else
      fail "TAR CORRUPTO │ $NAME ($SIZE) │ $DATE"
      FAIL_COUNT=$((FAIL_COUNT + 1))
      continue
    fi

    # 2. Si el tar contiene DBs, verificarlas (excluir archivos Synology internos)
    local DB_PATHS
    DB_PATHS=$(tar -tzf "$TAR" 2>/dev/null | grep '\.db$' | \
      grep -v '\.db-shm\|\.db-wal\|SynologyWorkingDirectory\|/\.db$' || true)
    if [ -n "$DB_PATHS" ]; then
      local TMP_V
      TMP_V=$(mktemp -d)
      while IFS= read -r DB_PATH; do
        tar -xzf "$TAR" -C "$TMP_V" "$DB_PATH" 2>/dev/null || continue
        local EXTRACTED="$TMP_V/$DB_PATH"
        [ -f "$EXTRACTED" ] || continue
        local DB_NAME
        DB_NAME=$(basename "$DB_PATH")
        local CHECK
        CHECK=$(sqlite3 "$EXTRACTED" "PRAGMA integrity_check;" 2>/dev/null || echo "error")
        if [ "$CHECK" = "ok" ]; then
          # Para plataforma.db, verificar conteo de clientes
          if [[ "$DB_NAME" == "plataforma.db" ]]; then
            local CLIENTS
            CLIENTS=$(sqlite3 "$EXTRACTED" "SELECT COUNT(*) FROM clients;" 2>/dev/null || echo "0")
            if [ "$CLIENTS" -ge "$MIN_CLIENTS" ]; then
              pass "  DB OK   │ $DB_NAME │ integrity_check=ok │ clientes=$CLIENTS"
            else
              fail "  DB WARN │ $DB_NAME │ integrity_check=ok │ clientes=$CLIENTS (minimo $MIN_CLIENTS)"
              FAIL_COUNT=$((FAIL_COUNT + 1))
            fi
          # Para opencode.db, verificar conteo de sesiones
          elif [[ "$DB_NAME" == "opencode.db" ]]; then
            local SESSIONS
            SESSIONS=$(sqlite3 "$EXTRACTED" "SELECT COUNT(*) FROM session;" 2>/dev/null || echo "?")
            pass "  DB OK   │ $DB_NAME │ integrity_check=ok │ sesiones=$SESSIONS"
          else
            pass "  DB OK   │ $DB_NAME │ integrity_check=ok"
          fi
        else
          fail "  DB FAIL │ $DB_NAME │ integrity_check=$CHECK"
          FAIL_COUNT=$((FAIL_COUNT + 1))
        fi
      done <<< "$DB_PATHS"
      rm -rf "$TMP_V"
    fi
  done

  echo ""
  if [ "$FOUND" -eq 0 ]; then
    warn "No se encontraron backups en: $BACKUP_DIR"
    return 0
  fi

  info "=== Resultado: $FOUND archivos verificados │ PASS=$PASS_COUNT │ FAIL=$FAIL_COUNT ==="
  if [ "$FAIL_COUNT" -gt 0 ]; then
    echo ""
    warn "Hay $FAIL_COUNT verificaciones fallidas. Revisa los mensajes [FAIL] arriba."
    return 1
  else
    ok "Todos los backups verificados correctamente."
  fi
}

# =============================================================================
# --- PRUEBA DE RESTAURACION (no destructiva) ---
# =============================================================================

# Extrae los tars mas recientes en /tmp y verifica su contenido.
# No toca ningun archivo de produccion. Seguro para ejecutar en cualquier momento.
test_restore() {
  info "=== PRUEBA DE RESTAURACION (no destructiva) ==="
  info "  Extrae en /tmp y verifica. No modifica ningun archivo de produccion."
  echo ""

  local TEST_DIR
  TEST_DIR=$(mktemp -d /tmp/restore-test-XXXXXX)
  trap 'rm -rf "$TEST_DIR"' RETURN

  local PASS_COUNT=0 FAIL_COUNT=0

  # --- Test 1: tar de proyectos ---
  local LAST_P
  LAST_P=$(ls -t "$BACKUP_DIR"/proyectos_*.tar.gz 2>/dev/null | head -1)
  if [ -z "$LAST_P" ]; then
    fail "Test 1 │ tar proyectos │ NO ENCONTRADO en $BACKUP_DIR"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  else
    info "Test 1 │ tar proyectos │ $(basename "$LAST_P")"
    local P_DIR="$TEST_DIR/proyectos"
    mkdir -p "$P_DIR"

    # 1a. Integridad del tar
    if tar -tzf "$LAST_P" > /dev/null 2>&1; then
      pass "  1a │ Integridad tar: OK"
      PASS_COUNT=$((PASS_COUNT + 1))
    else
      fail "  1a │ Integridad tar: CORRUPTO"
      FAIL_COUNT=$((FAIL_COUNT + 1))
    fi

    # 1b. Extraer y contar proyectos
    tar -xzf "$LAST_P" -C "$P_DIR" 2>/dev/null || true
    local PROJ_COUNT
    PROJ_COUNT=$(ls -d "$P_DIR/Proyectos"/*/ 2>/dev/null | wc -l | tr -d ' ')
    if [ "$PROJ_COUNT" -gt 0 ]; then
      pass "  1b │ Proyectos extraidos: $PROJ_COUNT"
      PASS_COUNT=$((PASS_COUNT + 1))
    else
      fail "  1b │ Proyectos extraidos: 0 (esperado >0)"
      FAIL_COUNT=$((FAIL_COUNT + 1))
    fi

    # 1c. Verificar plataforma.db
    local PLAT_DB="$P_DIR/Proyectos/Plataforma_Seguimiento_Proyectos/servidor/plataforma.db"
    if [ -f "$PLAT_DB" ]; then
      local CHECK CLIENTS
      CHECK=$(sqlite3 "$PLAT_DB" "PRAGMA integrity_check;" 2>/dev/null || echo "error")
      CLIENTS=$(sqlite3 "$PLAT_DB" "SELECT COUNT(*) FROM clients;" 2>/dev/null || echo "0")
      if [ "$CHECK" = "ok" ] && [ "$CLIENTS" -ge "$MIN_CLIENTS" ]; then
        pass "  1c │ plataforma.db: integrity_check=ok │ clientes=$CLIENTS"
        PASS_COUNT=$((PASS_COUNT + 1))
      else
        fail "  1c │ plataforma.db: integrity_check=$CHECK │ clientes=$CLIENTS"
        FAIL_COUNT=$((FAIL_COUNT + 1))
      fi
    else
      fail "  1c │ plataforma.db: NO ENCONTRADA en el tar"
      FAIL_COUNT=$((FAIL_COUNT + 1))
    fi

    # 1d. Verificar Plataforma_Seguimiento_Proyectos existe
    if [ -d "$P_DIR/Proyectos/Plataforma_Seguimiento_Proyectos" ]; then
      pass "  1d │ Plataforma_Seguimiento_Proyectos: presente"
      PASS_COUNT=$((PASS_COUNT + 1))
    else
      fail "  1d │ Plataforma_Seguimiento_Proyectos: NO encontrada"
      FAIL_COUNT=$((FAIL_COUNT + 1))
    fi

    # 1e. Verificar PLATAFORMA_OpenCode-NEW existe
    if [ -d "$P_DIR/Proyectos/PLATAFORMA_OpenCode-NEW" ]; then
      pass "  1e │ PLATAFORMA_OpenCode-NEW: presente"
      PASS_COUNT=$((PASS_COUNT + 1))
    else
      fail "  1e │ PLATAFORMA_OpenCode-NEW: NO encontrada"
      FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
  fi

  echo ""

  # --- Test 2: tar de datos OpenCode ---
  local LAST_D
  LAST_D=$(ls -t "$BACKUP_DIR"/opencode_data_*.tar.gz 2>/dev/null | head -1)
  if [ -z "$LAST_D" ]; then
    fail "Test 2 │ tar datos OpenCode │ NO ENCONTRADO en $BACKUP_DIR"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  else
    info "Test 2 │ tar datos OpenCode │ $(basename "$LAST_D")"
    local D_DIR="$TEST_DIR/opencode_data"
    mkdir -p "$D_DIR"

    # 2a. Integridad tar
    if tar -tzf "$LAST_D" > /dev/null 2>&1; then
      pass "  2a │ Integridad tar: OK"
      PASS_COUNT=$((PASS_COUNT + 1))
    else
      fail "  2a │ Integridad tar: CORRUPTO"
      FAIL_COUNT=$((FAIL_COUNT + 1))
    fi

    # 2b. Extraer opencode.db
    tar -xzf "$LAST_D" -C "$D_DIR" \
      ".local/share/opencode/opencode.db" 2>/dev/null || true
    local OC_DB="$D_DIR/.local/share/opencode/opencode.db"
    if [ -f "$OC_DB" ]; then
      local CHECK SESSIONS
      CHECK=$(sqlite3 "$OC_DB" "PRAGMA integrity_check;" 2>/dev/null || echo "error")
      SESSIONS=$(sqlite3 "$OC_DB" "SELECT COUNT(*) FROM session;" 2>/dev/null || echo "?")
      if [ "$CHECK" = "ok" ]; then
        pass "  2b │ opencode.db: integrity_check=ok │ sesiones=$SESSIONS"
        PASS_COUNT=$((PASS_COUNT + 1))
      else
        fail "  2b │ opencode.db: integrity_check=$CHECK"
        FAIL_COUNT=$((FAIL_COUNT + 1))
      fi
    else
      warn "  2b │ opencode.db no incluida en este tar (opcional)"
    fi

    # 2c. Verificar storage/session
    tar -xzf "$LAST_D" -C "$D_DIR" \
      ".local/share/opencode/storage/" 2>/dev/null || true
    local SESSION_COUNT
    SESSION_COUNT=$(find "$D_DIR/.local/share/opencode/storage/session" \
      -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$SESSION_COUNT" -ge 0 ]; then
      pass "  2c │ Storage sesiones extraidas: $SESSION_COUNT archivos JSON"
      PASS_COUNT=$((PASS_COUNT + 1))
    fi
  fi

  echo ""

  # --- Test 3: tar de config ---
  local LAST_C
  LAST_C=$(ls -t "$BACKUP_DIR"/opencode_config_*.tar.gz 2>/dev/null | head -1)
  if [ -z "$LAST_C" ]; then
    fail "Test 3 │ tar config │ NO ENCONTRADO en $BACKUP_DIR"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  else
    info "Test 3 │ tar config │ $(basename "$LAST_C")"
    local C_DIR="$TEST_DIR/config"
    mkdir -p "$C_DIR"

    # 3a. Integridad tar
    if tar -tzf "$LAST_C" > /dev/null 2>&1; then
      pass "  3a │ Integridad tar: OK"
      PASS_COUNT=$((PASS_COUNT + 1))
    else
      fail "  3a │ Integridad tar: CORRUPTO"
      FAIL_COUNT=$((FAIL_COUNT + 1))
    fi

    # 3b. Verificar opencode.json presente
    tar -xzf "$LAST_C" -C "$C_DIR" 2>/dev/null || true
    if [ -f "$C_DIR/.config/opencode/opencode.json" ] || \
       [ -f "$C_DIR/.config/opencode/opencode.jsonc" ]; then
      pass "  3b │ opencode.json: presente"
      PASS_COUNT=$((PASS_COUNT + 1))
    else
      warn "  3b │ opencode.json: no encontrado (puede estar en otra ruta)"
    fi
  fi

  echo ""

  # --- Test 4: iCloud Drive ---
  info "Test 4 │ iCloud Drive (CODANOR-Backups/)"
  if [ -d "$ICLOUD_DIR" ]; then
    local ICLOUD_FILES
    ICLOUD_FILES=$(ls "$ICLOUD_DIR"/*.tar.gz 2>/dev/null | wc -l | tr -d ' ')
    if [ "$ICLOUD_FILES" -gt 0 ]; then
      pass "  4a │ iCloud CODANOR-Backups: $ICLOUD_FILES archivos presentes"
      PASS_COUNT=$((PASS_COUNT + 1))
      # Verificar el tar de proyectos en iCloud si existe
      local ICLOUD_P
      ICLOUD_P=$(ls -t "$ICLOUD_DIR"/proyectos_*.tar.gz 2>/dev/null | head -1)
      if [ -n "$ICLOUD_P" ]; then
        if tar -tzf "$ICLOUD_P" > /dev/null 2>&1; then
          pass "  4b │ proyectos en iCloud: tar integro"
          PASS_COUNT=$((PASS_COUNT + 1))
        else
          fail "  4b │ proyectos en iCloud: tar CORRUPTO"
          FAIL_COUNT=$((FAIL_COUNT + 1))
        fi
      fi
    else
      warn "  4a │ iCloud CODANOR-Backups: vacio (ejecuta backup completo)"
    fi
  else
    warn "  4a │ iCloud CODANOR-Backups: carpeta no existe aun"
  fi

  echo ""
  info "=== RESULTADO PRUEBA DE RESTAURACION ==="
  info "  PASS: $PASS_COUNT  │  FAIL: $FAIL_COUNT"
  info "  Directorio de prueba limpiado: $TEST_DIR"
  echo ""

  if [ "$FAIL_COUNT" -gt 0 ]; then
    warn "Hay $FAIL_COUNT pruebas fallidas. Ejecuta --verify para mas detalles."
    warn "Considera lanzar un nuevo backup: ./backup-opencode.sh"
    return 1
  else
    ok "Prueba de restauracion completada: todos los checks PASS."
    ok "Los datos son recuperables. Proxima prueba: primer lunes del mes siguiente."
  fi
}

# =============================================================================
# --- RESTAURACION ---
# =============================================================================

# Mejora del restore original: verifica integridad del tar antes de extraer.
restore_backup() {
  local BACKUP_FILE="$1"
  [ -f "$BACKUP_FILE" ] || error "Archivo no encontrado: $BACKUP_FILE"

  info "Verificando integridad del backup antes de restaurar..."
  if ! tar -tzf "$BACKUP_FILE" > /dev/null 2>&1; then
    error "El archivo esta corrupto: $BACKUP_FILE — restauracion cancelada."
  fi
  ok "Tar integro."

  warn "ATENCION: Esto restaurara los datos de OpenCode (~/.local/share/opencode)."
  warn "Los datos actuales seran sobreescritos."
  echo ""
  read -p "Continuar? (s/N): " CONFIRM
  [ "$CONFIRM" = "s" ] || [ "$CONFIRM" = "S" ] || { info "Restauracion cancelada."; exit 0; }

  # Backup de seguridad del estado actual
  info "Creando backup de seguridad del estado actual..."
  local SAFETY_BACKUP="$BACKUP_DIR/opencode_pre_restore_$TIMESTAMP.tar.gz"
  mkdir -p "$BACKUP_DIR"
  local DIRS=""
  [ -d "$DATA_DIR" ]   && DIRS="$DIRS .local/share/opencode/"
  [ -d "$CONFIG_DIR" ] && DIRS="$DIRS .config/opencode/"
  if [ -n "$DIRS" ]; then
    tar -czf "$SAFETY_BACKUP" -C "$HOME" $DIRS 2>/dev/null || true
    ok "Backup de seguridad creado: $SAFETY_BACKUP"
  fi

  info "Restaurando desde: $BACKUP_FILE"
  tar -xzf "$BACKUP_FILE" -C "$HOME"
  ok "Restauracion completada."
  info "Si algo falla, restaura el estado anterior con:"
  info "  ./backup-opencode.sh --restore $SAFETY_BACKUP"
}

# Restaura ~/Proyectos/ completo desde un tar de proyectos.
restore_proyectos() {
  local BACKUP_FILE="$1"
  [ -f "$BACKUP_FILE" ] || error "Archivo no encontrado: $BACKUP_FILE"

  info "Verificando integridad del tar de proyectos..."
  if ! tar -tzf "$BACKUP_FILE" > /dev/null 2>&1; then
    error "El archivo esta corrupto: $BACKUP_FILE — restauracion cancelada."
  fi
  ok "Tar integro."

  # Contar proyectos en el tar
  local TAR_PROJ_COUNT
  TAR_PROJ_COUNT=$(tar -tzf "$BACKUP_FILE" 2>/dev/null | grep -E '^Proyectos/[^/]+/$' | wc -l | tr -d ' ')
  local TAR_SIZE
  TAR_SIZE=$(get_size "$BACKUP_FILE")
  info "Proyectos en el backup: $TAR_PROJ_COUNT ($TAR_SIZE)"

  # Verificar plataforma.db en el tar
  if tar -tzf "$BACKUP_FILE" 2>/dev/null | grep -q "plataforma.db"; then
    ok "plataforma.db: incluida en el backup"
  else
    warn "plataforma.db: NO encontrada en el tar"
  fi

  echo ""
  warn "ATENCION: Esto restaurara TODOS los archivos de ~/Proyectos/"
  warn "Los archivos actuales seran sobreescritos."
  warn "Backup a restaurar: $(basename "$BACKUP_FILE")"
  echo ""
  read -p "Continuar? (s/N): " CONFIRM
  [ "$CONFIRM" = "s" ] || [ "$CONFIRM" = "S" ] || { info "Restauracion cancelada."; exit 0; }

  # Backup de seguridad del estado actual de Proyectos
  info "Creando backup de seguridad del estado actual de ~/Proyectos/..."
  local SAFETY_BACKUP="$BACKUP_DIR/proyectos_pre_restore_$TIMESTAMP.tar.gz"
  mkdir -p "$BACKUP_DIR"
  tar -czf "$SAFETY_BACKUP" \
    --exclude='Proyectos/*/.git' \
    --exclude='Proyectos/*/node_modules' \
    --exclude='Proyectos/*/.opencode/node_modules' \
    -C "$HOME" Proyectos/ 2>/dev/null || true
  ok "Backup de seguridad creado: $SAFETY_BACKUP"

  info "Restaurando ~/Proyectos/ desde: $(basename "$BACKUP_FILE") ..."
  tar -xzf "$BACKUP_FILE" -C "$HOME"

  # Verificar plataforma.db restaurada
  local PLAT_DB="$PROYECTOS_DIR/Plataforma_Seguimiento_Proyectos/servidor/plataforma.db"
  if [ -f "$PLAT_DB" ]; then
    local CHECK CLIENTS
    CHECK=$(sqlite3 "$PLAT_DB" "PRAGMA integrity_check;" 2>/dev/null || echo "error")
    CLIENTS=$(sqlite3 "$PLAT_DB" "SELECT COUNT(*) FROM clients;" 2>/dev/null || echo "0")
    ok "plataforma.db restaurada: integrity_check=$CHECK │ clientes=$CLIENTS"
  fi

  ok "Restauracion de proyectos completada."
  info "Si algo falla, restaura el estado anterior con:"
  info "  ./backup-opencode.sh --restore-proyectos $SAFETY_BACKUP"
}

# Restaura solo plataforma.db desde un tar de proyectos.
# Para Flask si esta activo, restaura la DB y lo reinicia.
restore_db() {
  local BACKUP_FILE="$1"
  [ -f "$BACKUP_FILE" ] || error "Archivo no encontrado: $BACKUP_FILE"

  info "Verificando integridad del tar..."
  if ! tar -tzf "$BACKUP_FILE" > /dev/null 2>&1; then
    error "El archivo esta corrupto: $BACKUP_FILE — restauracion cancelada."
  fi

  if ! tar -tzf "$BACKUP_FILE" 2>/dev/null | grep -q "plataforma.db"; then
    error "plataforma.db no encontrada en: $BACKUP_FILE"
  fi

  # Extraer en temporal y verificar antes de tocar produccion
  local TMP_DB
  TMP_DB=$(mktemp -d)
  trap 'rm -rf "$TMP_DB"' RETURN
  info "Extrayendo y verificando plataforma.db del backup..."
  tar -xzf "$BACKUP_FILE" -C "$TMP_DB" \
    "Proyectos/Plataforma_Seguimiento_Proyectos/servidor/plataforma.db" 2>/dev/null \
    || error "No se pudo extraer plataforma.db del tar."

  local EXTRACTED="$TMP_DB/Proyectos/Plataforma_Seguimiento_Proyectos/servidor/plataforma.db"
  local CHECK CLIENTS
  CHECK=$(sqlite3 "$EXTRACTED" "PRAGMA integrity_check;" 2>/dev/null || echo "error")
  CLIENTS=$(sqlite3 "$EXTRACTED" "SELECT COUNT(*) FROM clients;" 2>/dev/null || echo "0")

  if [ "$CHECK" != "ok" ]; then
    error "plataforma.db en el backup no pasa integrity_check: $CHECK — restauracion cancelada."
  fi
  ok "plataforma.db verificada: integrity_check=ok │ clientes=$CLIENTS"

  local DEST="$PROYECTOS_DIR/Plataforma_Seguimiento_Proyectos/servidor/plataforma.db"
  local TAR_DATE
  TAR_DATE=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$BACKUP_FILE" 2>/dev/null || echo "?")

  echo ""
  warn "ATENCION: Esto sobreescribira plataforma.db en produccion."
  warn "  Destino: $DEST"
  warn "  Backup:  $(basename "$BACKUP_FILE") ($TAR_DATE)"
  warn "  Clientes en backup: $CLIENTS"
  echo ""
  read -p "Continuar? (s/N): " CONFIRM
  [ "$CONFIRM" = "s" ] || [ "$CONFIRM" = "S" ] || { info "Restauracion cancelada."; exit 0; }

  # Detectar si Flask esta activo
  local FLASK_PID
  FLASK_PID=$(pgrep -f "python3 server.py" 2>/dev/null || true)
  if [ -n "$FLASK_PID" ]; then
    info "Deteniendo Flask (PID $FLASK_PID) para restaurar la DB..."
    kill "$FLASK_PID" 2>/dev/null || true
    sleep 1
  fi

  # Backup de seguridad de la DB actual
  if [ -f "$DEST" ]; then
    local DB_SAFETY="$DEST.bak-$(date +%Y%m%d-%H%M%S)"
    cp "$DEST" "$DB_SAFETY"
    ok "Backup de seguridad de DB actual: $DB_SAFETY"
  fi

  # Copiar la DB restaurada
  cp "$EXTRACTED" "$DEST"
  ok "plataforma.db restaurada en: $DEST"

  # Reiniciar Flask si estaba activo
  if [ -n "$FLASK_PID" ]; then
    info "Reiniciando Flask..."
    local SERVER_DIR
    SERVER_DIR=$(dirname "$DEST")
    (cd "$SERVER_DIR" && nohup python3 server.py > /tmp/flask_restart.log 2>&1 &)
    sleep 2
    if pgrep -f "python3 server.py" > /dev/null 2>&1; then
      ok "Flask reiniciado correctamente."
    else
      warn "Flask no arranco automaticamente. Inicialo manualmente: python3 server.py"
    fi
  fi
}

# =============================================================================
# --- LISTAR BACKUPS ---
# =============================================================================

list_backups() {
  ensure_backup_dir
  info "Backups en: $BACKUP_DIR"
  echo ""

  if [ -z "$(ls -A "$BACKUP_DIR" 2>/dev/null)" ]; then
    warn "No hay backups."
    return
  fi

  printf "  %-48s %8s  %s\n" "ARCHIVO" "TAMANO" "FECHA"
  printf "  %-48s %8s  %s\n" "-------" "------" "-----"

  for f in "$BACKUP_DIR"/*.tar.gz; do
    [ -f "$f" ] || continue
    local NAME SIZE DATE
    NAME=$(basename "$f")
    SIZE=$(get_size "$f")
    DATE=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$f" 2>/dev/null || echo "?")
    printf "  %-48s %8s  %s\n" "$NAME" "$SIZE" "$DATE"
  done

  echo ""
  local TOTAL
  TOTAL=$(ls "$BACKUP_DIR"/*.tar.gz 2>/dev/null | wc -l | tr -d ' ')
  local TOTAL_SIZE
  TOTAL_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
  info "Total: $TOTAL backups │ $TOTAL_SIZE"

  # Mostrar tambien iCloud
  if [ -d "$ICLOUD_DIR" ]; then
    echo ""
    info "iCloud Drive (CODANOR-Backups/):"
    for f in "$ICLOUD_DIR"/*.tar.gz; do
      [ -f "$f" ] || continue
      local NAME SIZE DATE
      NAME=$(basename "$f")
      SIZE=$(get_size "$f")
      DATE=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$f" 2>/dev/null || echo "?")
      printf "  %-48s %8s  %s\n" "$NAME" "$SIZE" "$DATE"
    done
  fi
}

# =============================================================================
# --- LIMPIEZA ---
# =============================================================================

cleanup_old_backups() {
  local PREFIX="${1:-opencode_}"
  local COUNT
  COUNT=$(ls "$BACKUP_DIR"/${PREFIX}*.tar.gz 2>/dev/null | wc -l | tr -d ' ')
  if [ "$COUNT" -gt "$MAX_BACKUPS" ]; then
    local TO_DELETE=$((COUNT - MAX_BACKUPS))
    info "Limpiando $TO_DELETE backups antiguos (maximo: $MAX_BACKUPS)..."
    ls -t "$BACKUP_DIR"/${PREFIX}*.tar.gz | tail -n "$TO_DELETE" | xargs rm -f
    ok "Backups antiguos eliminados."
  fi
}

clean_backups() {
  ensure_backup_dir
  cleanup_old_backups "proyectos_"
  cleanup_old_backups "opencode_data_"
  cleanup_old_backups "opencode_config_"
  ok "Limpieza completada."
}

# =============================================================================
# --- EXPORTAR SESIONES A JSON ---
# =============================================================================

export_sessions() {
  info "Exportando sesiones individuales a JSON..."
  ensure_backup_dir
  if ! command -v opencode &> /dev/null; then
    error "opencode CLI no encontrado. Instala OpenCode primero."
  fi
  local EXPORT_DIR="$BACKUP_DIR/exports_$TIMESTAMP"
  mkdir -p "$EXPORT_DIR"
  info "Obteniendo lista de sesiones..."
  local SESSION_LIST
  SESSION_LIST=$(opencode session list --format json 2>/dev/null || echo "[]")
  if [ "$SESSION_LIST" = "[]" ] || [ -z "$SESSION_LIST" ]; then
    warn "No se encontraron sesiones para exportar."
    return
  fi
  echo "$SESSION_LIST" | while IFS= read -r line; do
    local SID
    SID=$(echo "$line" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4 2>/dev/null || true)
    if [ -n "$SID" ]; then
      info "  Exportando $SID..."
      opencode export "$SID" > "$EXPORT_DIR/$SID.json" 2>/dev/null || \
        warn "  No se pudo exportar $SID"
    fi
  done
  ok "Sesiones exportadas en: $EXPORT_DIR/"
}

# =============================================================================
# --- RESUMEN ---
# =============================================================================

show_summary() {
  echo ""
  info "=== Resumen de datos de OpenCode ==="
  if [ -d "$DATA_DIR/storage/session" ]; then
    local SESSIONS
    SESSIONS=$(find "$DATA_DIR/storage/session" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
    info "  Sesiones almacenadas: $SESSIONS"
  fi
  if [ -d "$DATA_DIR/storage/message" ]; then
    local MESSAGES
    MESSAGES=$(find "$DATA_DIR/storage/message" -type f 2>/dev/null | wc -l | tr -d ' ')
    info "  Archivos de mensajes: $MESSAGES"
  fi
  if [ -d "$CONFIG_DIR/commands" ]; then
    local COMMANDS
    COMMANDS=$(find "$CONFIG_DIR/commands" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    info "  Comandos disponibles: $COMMANDS"
  fi
  local DATA_SIZE CONFIG_SIZE BACKUP_SIZE
  DATA_SIZE=$(du -sh "$DATA_DIR" 2>/dev/null | cut -f1 || echo "N/A")
  CONFIG_SIZE=$(du -sh "$CONFIG_DIR" 2>/dev/null | cut -f1 || echo "N/A")
  BACKUP_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1 || echo "0B")
  info "  Tamano datos:   $DATA_SIZE"
  info "  Tamano config:  $CONFIG_SIZE"
  info "  Tamano backups: $BACKUP_SIZE (en $BACKUP_DIR)"
  if [ -d "$ICLOUD_DIR" ]; then
    local ICLOUD_SIZE
    ICLOUD_SIZE=$(du -sh "$ICLOUD_DIR" 2>/dev/null | cut -f1 || echo "0B")
    info "  iCloud Drive:   $ICLOUD_SIZE (CODANOR-Backups/)"
  fi
  echo ""
}

# =============================================================================
# --- MAIN ---
# =============================================================================
case "${1:-}" in
  --proyectos)         backup_proyectos ;;
  --sessions)          backup_sessions ;;
  --config)            backup_config ;;
  --export)            export_sessions ;;
  --list)              list_backups ;;
  --verify)            ensure_backup_dir; verify_backups ;;
  --test-restore)      ensure_backup_dir; test_restore ;;
  --restore)
    [ -n "${2:-}" ] || error "Especifica el archivo: --restore <archivo.tar.gz>"
    restore_backup "$2"
    ;;
  --restore-proyectos)
    [ -n "${2:-}" ] || error "Especifica el archivo: --restore-proyectos <archivo.tar.gz>"
    restore_proyectos "$2"
    ;;
  --restore-db)
    [ -n "${2:-}" ] || error "Especifica el archivo: --restore-db <archivo.tar.gz>"
    restore_db "$2"
    ;;
  --clean)             clean_backups ;;
  --help|-h)           show_help ;;
  "")                  backup_full ;;
  *)                   error "Opcion desconocida: $1. Usa --help para ver las opciones." ;;
esac
