#!/usr/bin/env bash

# ==========================================================
# Fedora & Development Tools Update Script
# Updates: DNF, Flatpak, AGY, Rustup
# ==========================================================

set -euo pipefail

# ANSI color codes
BOLD="\033[1m"
GREEN="\033[0;32m"
BLUE="\033[0;34m"
YELLOW="\033[0;33m"
CYAN="\033[0;36m"
RED="\033[0;31m"
NC="\033[0m" # No Color

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
    print_warning "User-level tools (AGY, Rustup) should be updated under your regular user account."
fi

# Validate sudo privileges early
if command -v sudo &>/dev/null && [ "${EUID}" -ne 0 ]; then
    sudo -v
fi

# 1. Update Fedora packages via DNF
print_step "Updating Fedora packages (DNF)..."
if command -v dnf &>/dev/null; then
    if [ "${EUID}" -eq 0 ]; then
        dnf upgrade --refresh -y
    else
        sudo dnf upgrade --refresh -y
    fi
    print_success "Fedora packages (DNF) updated successfully."
else
    print_warning "dnf command not found. Skipping DNF update."
fi

# 2. Update Flatpak packages
print_step "Updating Flatpak packages..."
if command -v flatpak &>/dev/null; then
    flatpak update -y
    print_success "Flatpak packages updated successfully."
else
    print_warning "flatpak command not found. Skipping Flatpak update."
fi

# 3. Update Antigravity CLI (AGY)
print_step "Updating Antigravity CLI (AGY)..."
if command -v agy &>/dev/null; then
    agy update
    print_success "Antigravity CLI (AGY) updated successfully."
else
    print_warning "agy command not found. Skipping AGY update."
fi

# 4. Update Rust toolchains (Rustup)
print_step "Updating Rust toolchains (Rustup)..."
if command -v rustup &>/dev/null; then
    rustup update
    print_success "Rust toolchains (Rustup) updated successfully."
else
    print_warning "rustup command not found. Skipping Rustup update."
fi

# Summary Banner
echo -e "\n${BOLD}${GREEN}==========================================================${NC}"
echo -e "${BOLD}${GREEN}  All system and tool updates complete!                   ${NC}"
echo -e "${BOLD}${GREEN}==========================================================${NC}\n"
