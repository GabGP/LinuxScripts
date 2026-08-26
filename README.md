# Fedora Linux Scripts & Dotfiles

Personal Bash scripts and terminal configs for **Fedora Linux**.

> [!NOTE]
> Tailored for my setup: DNF, Flatpak, Kitty, Starship, Rust (`rustup`), and Antigravity CLI (`agy`).

## Setup

```bash
git clone https://github.com/GabGP/LinuxScripts.git
cd LinuxScripts
./setup.sh
```

`setup.sh` opens an interactive menu with three options:

| Option | What it does |
| :--- | :--- |
| **Configurations** | Symlinks dotfiles (Kitty, Starship, Bash) to their expected locations. Existing files are automatically backed up to `backups/`. You can install all configs or pick individually. |
| **Automation Scripts** | Symlinks scripts from `scripts/` into `~/.local/bin/` so they're available as commands (`update`, `check-updates`, `ezin`). You can link all or pick individually. |
| **Both** | Runs both of the above in one step. |

### Prerequisites

**System packages:**
```bash
sudo dnf install file tar unzip sed desktop-file-utils curl
```

**Font** ([MesloLGS Nerd Font](https://github.com/ryanoasis/nerd-fonts/releases/latest/download/Meslo.tar.xz) — recommended for Kitty & Starship):
```bash
mkdir -p ~/.local/share/fonts/Meslo
curl -fLo /tmp/Meslo.tar.xz https://github.com/ryanoasis/nerd-fonts/releases/latest/download/Meslo.tar.xz
tar -xf /tmp/Meslo.tar.xz -C ~/.local/share/fonts/Meslo/
rm -f /tmp/Meslo.tar.xz
fc-cache -f ~/.local/share/fonts/Meslo
```

## Repository Layout

```text
LinuxScripts/
├── config/
│   ├── bash/.bashrc             # → ~/.bashrc
│   ├── kitty/
│   │   ├── kitty.conf           # → ~/.config/kitty/kitty.conf
│   │   ├── tab_bar.py           # → ~/.config/kitty/tab_bar.py (custom status bar entry point)
│   │   └── tab_bar/             # Modular status bar package (timer, renderer, widgets)
│   └── starship/starship.toml   # → ~/.config/starship.toml
├── scripts/
│   ├── lib/                     # Shared modular libraries (colors, logger, backup)
│   │   ├── colors.sh
│   │   ├── logger.sh
│   │   └── backup.sh
│   ├── update.sh                # Updates DNF, Flatpak, Starship, agy, Rust
│   ├── check-updates.sh         # Checks for pending updates (read-only)
│   └── ezin.sh                  # Installs archive packages into /opt
├── setup.sh                     # Interactive setup manager
└── backups/                     # Auto-generated config backups (gitignored)
```

## Configurations

- **Kitty** — Uses MesloLGS Nerd Font with custom Powerline tabs and right-aligned live status widgets (Weather in Celsius, Battery level/status, and 24-hour Clock). Powered by an aligned zero-polling kernel interrupt timer. See [tab_bar/README.md](config/kitty/tab_bar/README.md) for architecture and widget development guide.
- **Starship** — Continuous Powerline capsule layout inspired by [Gruvbox-Rainbow](https://starship.rs/presets/gruvbox-rainbow), using Chuck's earthy **Kokiri** color palette. All 101 default Starship modules are preserved. Edit 8 hex variables at the top of [starship.toml](config/starship/starship.toml) to swap themes.
- **Bash** — User environment variables, path exports, and Starship shell hook.

## License

MIT — see [LICENSE](LICENSE).
