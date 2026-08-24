#!/usr/bin/env bash
# ==============================================================================
#  Fedora LinuxScripts Setup & Configuration Manager
# ==============================================================================
#  Interactive menu for installing/symlinking dotfiles and automation scripts.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="${SCRIPT_DIR}/backups/$(date +%Y%m%d_%H%M%S)"

# Color formatting
COLOR_RESET="\033[0m"
COLOR_BOLD="\033[1m"
COLOR_GREEN="\033[32m"
COLOR_BLUE="\033[34m"
COLOR_YELLOW="\033[33m"
COLOR_CYAN="\033[36m"
COLOR_RED="\033[31m"

print_header() {
    clear 2>/dev/null || true
    echo -e "${COLOR_CYAN}${COLOR_BOLD}"
    echo "============================================================"
    echo "       Fedora LinuxScripts & Dotfiles Setup Manager         "
    echo "============================================================"
    echo -e "${COLOR_RESET}"
}

backup_file() {
    local target="$1"
    if [[ -e "$target" || -L "$target" ]]; then
        mkdir -p "${BACKUP_DIR}"
        local rel_path="${target#${HOME}/}"
        local dest="${BACKUP_DIR}/${rel_path}"
        mkdir -p "$(dirname "${dest}")"
        cp -a "$target" "$dest"
        echo -e "  ${COLOR_YELLOW}Backed up existing:${COLOR_RESET} $target -> $dest"
    fi
}

install_config_item() {
    local name="$1"
    local src="$2"
    local dest="$3"

    mkdir -p "$(dirname "$dest")"
    backup_file "$dest"
    rm -f "$dest"
    ln -sf "$src" "$dest"
    echo -e "  ${COLOR_GREEN}✔ Installed ${name}:${COLOR_RESET} $dest -> $src"
}

install_script_item() {
    local name="$1"
    local src="$2"
    local dest_bin="${HOME}/.local/bin/${name}"

    mkdir -p "${HOME}/.local/bin"
    chmod +x "$src"
    rm -f "$dest_bin"
    ln -sf "$src" "$dest_bin"
    echo -e "  ${COLOR_GREEN}✔ Linked executable:${COLOR_RESET} ~/.local/bin/${name} -> $src"
}

# ------------------------------------------------------------------------------
# Configuration Installation Menu
# ------------------------------------------------------------------------------
menu_install_configs() {
    print_header
    echo -e "${COLOR_BOLD}Select configurations to install (Symlink with auto-backup):${COLOR_RESET}\n"
    echo "  1) All Configurations (Kitty, Starship, Bash)"
    echo "  2) Kitty Terminal (~/.config/kitty/kitty.conf)"
    echo "  3) Starship Prompt (~/.config/starship.toml)"
    echo "  4) Bash Shell (~/.bashrc)"
    echo "  5) Back to Main Menu"
    echo ""
    read -rp "Enter choice [1-5]: " config_choice

    case "$config_choice" in
        1)
            echo -e "\n${COLOR_BOLD}Installing all configurations...${COLOR_RESET}"
            install_config_item "Kitty" "${SCRIPT_DIR}/config/kitty/kitty.conf" "${HOME}/.config/kitty/kitty.conf"
            install_config_item "Starship" "${SCRIPT_DIR}/config/starship/starship.toml" "${HOME}/.config/starship.toml"
            install_config_item "Bash" "${SCRIPT_DIR}/config/bash/.bashrc" "${HOME}/.bashrc"
            ;;
        2)
            echo -e "\n${COLOR_BOLD}Installing Kitty configuration...${COLOR_RESET}"
            install_config_item "Kitty" "${SCRIPT_DIR}/config/kitty/kitty.conf" "${HOME}/.config/kitty/kitty.conf"
            ;;
        3)
            echo -e "\n${COLOR_BOLD}Installing Starship configuration...${COLOR_RESET}"
            install_config_item "Starship" "${SCRIPT_DIR}/config/starship/starship.toml" "${HOME}/.config/starship.toml"
            ;;
        4)
            echo -e "\n${COLOR_BOLD}Installing Bash configuration...${COLOR_RESET}"
            install_config_item "Bash" "${SCRIPT_DIR}/config/bash/.bashrc" "${HOME}/.bashrc"
            ;;
        5)
            return 0
            ;;
        *)
            echo -e "\n${COLOR_RED}Invalid option selected.${COLOR_RESET}"
            ;;
    esac

    echo ""
    read -rp "Press [Enter] to continue..."
}

# ------------------------------------------------------------------------------
# Script Installation Menu
# ------------------------------------------------------------------------------
menu_install_scripts() {
    print_header
    echo -e "${COLOR_BOLD}Select automation scripts to link to ~/.local/bin:${COLOR_RESET}\n"
    echo "  1) All Scripts (update, check-updates, ezin)"
    echo "  2) System Updater (update.sh -> ~/.local/bin/update)"
    echo "  3) Update Checker (check-updates.sh -> ~/.local/bin/check-updates)"
    echo "  4) Archive Installer (ezin.sh -> ~/.local/bin/ezin)"
    echo "  5) Back to Main Menu"
    echo ""
    read -rp "Enter choice [1-5]: " script_choice

    # Ensure scripts directory has execute bits
    chmod +x "${SCRIPT_DIR}/scripts/"*.sh

    case "$script_choice" in
        1)
            echo -e "\n${COLOR_BOLD}Linking all scripts to ~/.local/bin...${COLOR_RESET}"
            install_script_item "update" "${SCRIPT_DIR}/scripts/update.sh"
            install_script_item "check-updates" "${SCRIPT_DIR}/scripts/check-updates.sh"
            install_script_item "ezin" "${SCRIPT_DIR}/scripts/ezin.sh"
            ;;
        2)
            echo -e "\n${COLOR_BOLD}Linking update script...${COLOR_RESET}"
            install_script_item "update" "${SCRIPT_DIR}/scripts/update.sh"
            ;;
        3)
            echo -e "\n${COLOR_BOLD}Linking check-updates script...${COLOR_RESET}"
            install_script_item "check-updates" "${SCRIPT_DIR}/scripts/check-updates.sh"
            ;;
        4)
            echo -e "\n${COLOR_BOLD}Linking ezin installer...${COLOR_RESET}"
            install_script_item "ezin" "${SCRIPT_DIR}/scripts/ezin.sh"
            ;;
        5)
            return 0
            ;;
        *)
            echo -e "\n${COLOR_RED}Invalid option selected.${COLOR_RESET}"
            ;;
    esac

    echo ""
    read -rp "Press [Enter] to continue..."
}

# ------------------------------------------------------------------------------
# Full Setup (Both Configs & Scripts)
# ------------------------------------------------------------------------------
install_both() {
    print_header
    echo -e "${COLOR_BOLD}Performing Full Setup (Configurations + Scripts)...${COLOR_RESET}\n"

    echo -e "${COLOR_BOLD}1. Installing configurations...${COLOR_RESET}"
    install_config_item "Kitty" "${SCRIPT_DIR}/config/kitty/kitty.conf" "${HOME}/.config/kitty/kitty.conf"
    install_config_item "Starship" "${SCRIPT_DIR}/config/starship/starship.toml" "${HOME}/.config/starship.toml"
    install_config_item "Bash" "${SCRIPT_DIR}/config/bash/.bashrc" "${HOME}/.bashrc"

    echo -e "\n${COLOR_BOLD}2. Linking scripts to ~/.local/bin...${COLOR_RESET}"
    chmod +x "${SCRIPT_DIR}/scripts/"*.sh
    install_script_item "update" "${SCRIPT_DIR}/scripts/update.sh"
    install_script_item "check-updates" "${SCRIPT_DIR}/scripts/check-updates.sh"
    install_script_item "ezin" "${SCRIPT_DIR}/scripts/ezin.sh"

    echo -e "\n${COLOR_GREEN}${COLOR_BOLD}✔ Full setup completed successfully!${COLOR_RESET}"
    if [[ -d "${BACKUP_DIR:-}" ]]; then
        echo -e "  Backups saved to: ${COLOR_CYAN}${BACKUP_DIR}${COLOR_RESET}"
    fi

    echo ""
    read -rp "Press [Enter] to continue..."
}

# ------------------------------------------------------------------------------
# Main Interactive Menu Loop
# ------------------------------------------------------------------------------
main_menu() {
    while true; do
        print_header
        echo -e "${COLOR_BOLD}What would you like to install?${COLOR_RESET}\n"
        echo "  1) Configurations (Kitty, Starship, Bash)"
        echo "  2) Automation Scripts (Link to ~/.local/bin)"
        echo "  3) Both (Full Installation)"
        echo "  4) Exit"
        echo ""
        read -rp "Enter choice [1-4]: " main_choice

        case "$main_choice" in
            1) menu_install_configs ;;
            2) menu_install_scripts ;;
            3) install_both ;;
            4)
                echo -e "\n${COLOR_GREEN}Exiting setup. Goodbye!${COLOR_RESET}\n"
                exit 0
                ;;
            *)
                echo -e "\n${COLOR_RED}Invalid choice. Please choose 1, 2, 3, or 4.${COLOR_RESET}"
                sleep 1
                ;;
        esac
    done
}

main_menu
