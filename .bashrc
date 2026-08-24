# ==============================================================================
#  ~/.bashrc - User Bash Configuration
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. Global Definitions
# ------------------------------------------------------------------------------
if [ -f /etc/bashrc ]; then
    . /etc/bashrc
fi

# ------------------------------------------------------------------------------
# 2. Environment Variables & PATH Configuration
# ------------------------------------------------------------------------------
# User binaries ($HOME/.local/bin, $HOME/bin)
if ! [[ "$PATH" =~ "$HOME/.local/bin:$HOME/bin:" ]]; then
    PATH="$HOME/.local/bin:$HOME/bin:$PATH"
fi
export PATH

# Default Terminal
export TERMINAL=kitty

# Rust / Cargo Environment
if [ -f "$HOME/.cargo/env" ]; then
    . "$HOME/.cargo/env"
fi

# ARM GNU Toolchain
if [ -d "/opt/toolchains/arm-gnu-toolchain-13.2.Rel1-x86_64-arm-none-eabi/bin" ]; then
    export PATH="$PATH:/opt/toolchains/arm-gnu-toolchain-13.2.Rel1-x86_64-arm-none-eabi/bin"
fi

# ------------------------------------------------------------------------------
# 3. Modular Configurations (~/.bashrc.d)
# ------------------------------------------------------------------------------
if [ -d ~/.bashrc.d ]; then
    for rc in ~/.bashrc.d/*; do
        if [ -f "$rc" ]; then
            . "$rc"
        fi
    done
    unset rc
fi

# ------------------------------------------------------------------------------
# 4. Shell Prompt (Starship)
# ------------------------------------------------------------------------------
if command -v starship &>/dev/null; then
    eval "$(starship init bash)"
fi
