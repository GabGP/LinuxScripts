#!/usr/bin/env bash
# ==============================================================================
#  scripts/lib/backup.sh - Safe Timestamped Backup Engine
# ==============================================================================

# Ensure logger & colors are available
_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "${_LIB_DIR}/logger.sh" ]]; then
    # shellcheck source=scripts/lib/logger.sh
    . "${_LIB_DIR}/logger.sh"
fi

backup_path() {
    local target="$1"
    local backup_root="${2:-$(pwd)/backups/$(date +%Y%m%d_%H%M%S)}"

    if [[ -e "$target" || -L "$target" ]]; then
        mkdir -p "${backup_root}"
        local rel_path="${target#${HOME}/}"
        local dest="${backup_root}/${rel_path}"
        mkdir -p "$(dirname "${dest}")"
        cp -a "$target" "$dest"
        log_warn "Backed up existing: $target -> $dest"
    fi
}
