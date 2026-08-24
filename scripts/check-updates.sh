#!/usr/bin/env bash

# ==========================================================
# Fedora & Development Tools Update Checker
# Checks for available updates: DNF, Flatpak, Starship, AGY, Rustup
# (Read-only: Does NOT install or modify any packages)
# ==========================================================

set -uo pipefail

# ANSI color codes
BOLD="\033[1m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
YELLOW="\033[0;33m"
CYAN="\033[0;36m"
RED="\033[0;31m"
NC="\033[0m" # No Color

UPDATES_AVAILABLE=0

print_step() {
    echo -e "\n${BOLD}${BLUE}==>${NC} ${BOLD}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✔ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✖ $1${NC}"
}

# Warn if executed directly as root
if [ "${EUID}" -eq 0 ]; then
    print_warning "Running the entire script as root is not recommended."
    print_warning "User-level tools (AGY, Rustup) should be checked under your regular user account."
fi

# 1. Check Fedora packages via DNF
print_step "Checking Fedora packages (DNF)..."
if command -v dnf &>/dev/null; then
    dnf_output=""
    dnf_status=0
    dnf_output=$(dnf check-update 2>&1) || dnf_status=$?

    if [ "${dnf_status}" -eq 100 ]; then
        print_warning "Updates available for Fedora packages (DNF):"
        echo "${dnf_output}"
        UPDATES_AVAILABLE=1
    elif [ "${dnf_status}" -eq 0 ]; then
        print_success "Fedora packages (DNF) are up to date."
    else
        print_error "Failed to check DNF updates (exit code: ${dnf_status})."
        echo "${dnf_output}"
    fi
else
    print_warning "dnf command not found. Skipping DNF check."
fi

# 2. Check Flatpak packages
print_step "Checking Flatpak packages..."
if command -v flatpak &>/dev/null; then
    flatpak_updates=$(flatpak remote-ls --updates 2>/dev/null || true)
    if [ -n "${flatpak_updates}" ]; then
        print_warning "Updates available for Flatpak packages:"
        echo "${flatpak_updates}"
        UPDATES_AVAILABLE=1
    else
        print_success "Flatpak packages are up to date."
    fi
else
    print_warning "flatpak command not found. Skipping Flatpak check."
fi

# 3. Check Starship Prompt
print_step "Checking Starship prompt..."
if command -v starship &>/dev/null; then
    current_starship_version=$(starship --version 2>/dev/null | head -n 1 | awk '{print $2}')
    latest_starship_version=$(curl -sI https://github.com/starship/starship/releases/latest 2>/dev/null | grep -i "^location:" | sed -E 's/.*tag\/v?([0-9.]+).*/\1/' | tr -d '\r\n')

    if [ -n "${latest_starship_version}" ]; then
        if [ "${current_starship_version}" != "${latest_starship_version}" ]; then
            print_warning "Update available for Starship prompt: ${current_starship_version} -> ${latest_starship_version}"
            UPDATES_AVAILABLE=1
        else
            print_success "Starship prompt is up to date (version: ${current_starship_version})."
        fi
    else
        print_warning "Could not check latest Starship version (network/offline). Current: ${current_starship_version}"
    fi
else
    print_warning "starship command not found. Skipping Starship check."
fi

# 4. Check Antigravity CLI (AGY)
print_step "Checking Antigravity CLI (AGY)..."
if command -v agy &>/dev/null; then
    current_agy_version=$(agy --version 2>/dev/null || echo "unknown")
    print_info "Current Antigravity CLI (AGY) version: ${current_agy_version}"
    print_info "Run './update.sh' or 'agy update' to check and install updates."
else
    print_warning "agy command not found. Skipping AGY check."
fi

# 5. Check Rust toolchains (Rustup)
print_step "Checking Rust toolchains (Rustup)..."
if command -v rustup &>/dev/null; then
    rustup_output=""
    rustup_status=0
    rustup_output=$(rustup check 2>&1) || rustup_status=$?

    echo "${rustup_output}"
    if [ "${rustup_status}" -eq 100 ] || echo "${rustup_output}" | grep -qi "Update available"; then
        print_warning "Updates available for Rust toolchains (Rustup)."
        UPDATES_AVAILABLE=1
    elif [ "${rustup_status}" -eq 0 ]; then
        print_success "Rust toolchains (Rustup) are up to date."
    else
        print_warning "Rustup check completed with warnings/errors."
    fi
else
    print_warning "rustup command not found. Skipping Rustup check."
fi

# Summary Banner
if [ "${UPDATES_AVAILABLE}" -eq 1 ]; then
    echo -e "\n${BOLD}${YELLOW}==========================================================${NC}"
    echo -e "${BOLD}${YELLOW}  Updates are available!                                  ${NC}"
    echo -e "${BOLD}  Run ${GREEN}./update.sh${NC}${BOLD} to install them.                            ${NC}"
    echo -e "${BOLD}${YELLOW}==========================================================${NC}\n"
else
    echo -e "\n${BOLD}${GREEN}==========================================================${NC}"
    echo -e "${BOLD}${GREEN}  All system and tools are up to date!                    ${NC}"
    echo -e "${BOLD}${GREEN}==========================================================${NC}\n"
fi
