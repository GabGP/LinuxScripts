#!/usr/bin/env bash
# ==============================================================================
#  scripts/lib/colors.sh - Standard ANSI Color Codes & Styles
# ==============================================================================

# Reset
COLOR_RESET="\033[0m"

# Text Styles
COLOR_BOLD="\033[1m"
COLOR_DIM="\033[2m"
COLOR_ITALIC="\033[3m"
COLOR_UNDERLINE="\033[4m"

# Foreground Colors
COLOR_BLACK="\033[30m"
COLOR_RED="\033[31m"
COLOR_GREEN="\033[32m"
COLOR_YELLOW="\033[33m"
COLOR_BLUE="\033[34m"
COLOR_MAGENTA="\033[35m"
COLOR_CYAN="\033[36m"
COLOR_WHITE="\033[37m"

# High-Intensity Foreground
COLOR_BRIGHT_BLACK="\033[90m"
COLOR_BRIGHT_RED="\033[91m"
COLOR_BRIGHT_GREEN="\033[92m"
COLOR_BRIGHT_YELLOW="\033[93m"
COLOR_BRIGHT_BLUE="\033[94m"
COLOR_BRIGHT_MAGENTA="\033[95m"
COLOR_BRIGHT_CYAN="\033[96m"
COLOR_BRIGHT_WHITE="\033[97m"

# Backward-Compatibility Aliases
BOLD="${COLOR_BOLD}"
DIM="${COLOR_DIM}"
ITALIC="${COLOR_ITALIC}"
UNDERLINE="${COLOR_UNDERLINE}"
RED="${COLOR_RED}"
GREEN="${COLOR_GREEN}"
YELLOW="${COLOR_YELLOW}"
BLUE="${COLOR_BLUE}"
MAGENTA="${COLOR_MAGENTA}"
CYAN="${COLOR_CYAN}"
WHITE="${COLOR_WHITE}"
NC="${COLOR_RESET}"
