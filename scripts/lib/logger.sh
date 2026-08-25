#!/usr/bin/env bash
# ==============================================================================
#  scripts/lib/logger.sh - Standardized Logging Functions
# ==============================================================================

# Ensure colors are available
_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "${_LIB_DIR}/colors.sh" ]]; then
    # shellcheck source=scripts/lib/colors.sh
    . "${_LIB_DIR}/colors.sh"
fi

log_info() {
    echo -e "${COLOR_CYAN}${COLOR_BOLD}[INFO]${COLOR_RESET} $*"
}

log_success() {
    echo -e "${COLOR_GREEN}${COLOR_BOLD}[OK]${COLOR_RESET} $*"
}

log_warn() {
    echo -e "${COLOR_YELLOW}${COLOR_BOLD}[WARN]${COLOR_RESET} $*"
}

log_error() {
    echo -e "${COLOR_RED}${COLOR_BOLD}[ERROR]${COLOR_RESET} $*" >&2
}

log_step() {
    echo -e "\n${COLOR_BLUE}${COLOR_BOLD}==>${COLOR_RESET} ${COLOR_BOLD}$*${COLOR_RESET}"
}
