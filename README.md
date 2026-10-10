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
| **Configurations** | Symlinks dotfiles (Kitty, Starship, Bash, Claude, AGY) to their expected locations. Existing files are automatically backed up to `backups/`. You can install all configs or pick individually. |
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
│   ├── agy/
│   │   ├── statusline.js        # → ~/.gemini/antigravity-cli/statusline.js (AGY CLI statusline)
│   │   ├── statusline.test.js   # Automated unit test suite (28 tests + lifecycle)
│   │   └── README.md            # Statusline guide & activation instructions
│   ├── bash/.bashrc             # → ~/.bashrc
│   ├── claude/
│   │   ├── statusline.js        # → ~/.claude/statusline.js (Claude Code CLI statusline)
│   │   ├── statusline.test.js   # Automated unit test suite (36 tests + lifecycle)
│   │   ├── skills/gemini-worker/ # → ~/.claude/skills/gemini-worker/ (Claude Code skill: runs agy tasks)
│   │   └── README.md            # Statusline guide & activation instructions
│   ├── kitty/
│   │   ├── kitty.conf           # → ~/.config/kitty/kitty.conf
│   │   ├── current-theme.conf   # → Active theme managed by Kitty theme switcher
│   │   ├── tab_bar.conf         # → Declarative tab bar settings & 197+ command icons
│   │   ├── tab_bar.py           # → ~/.config/kitty/tab_bar.py (status bar entry point)
│   │   ├── themes/              # Custom theme preset catalog (dimidium, kokiri_dark)
│   │   └── tab_bar/             # Modular status bar package (registry, timer, renderer, widgets)
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

- **Kitty** — Uses MesloLGS Nerd Font with declarative configuration (`tab_bar.conf`), custom Powerline tabs, and right-aligned live status widgets (Open-Meteo Weather, RAM usage, CPU load & temperature, Battery status, and 24-hour Clock), plus F1 `btop` overlay shortcut. Features plug-and-play widget auto-discovery, frame-scoped render memoization, and zero-polling kernel interrupt timers. See [tab_bar/README.md](config/kitty/tab_bar/README.md) for architecture and widget development guide.
- **Starship** — Continuous Powerline capsule layout inspired by [Gruvbox-Rainbow](https://starship.rs/presets/gruvbox-rainbow), with a modular color palette. All 101 default Starship modules are preserved. Edit the color variables at the top of [starship.toml](config/starship/starship.toml) to swap palettes easily.
- **Bash** — User environment variables, path exports, and Starship shell hook.
- **Claude Code** — Custom zero-dependency Node.js statusline displaying current model colored by tier (Haiku green → Sonnet yellow → Opus orange), effort level colored by intensity (`max` as a red badge) / fast mode (`⚡`), visual 4-bar context window usage meter (`▮▮▯▯`) with threshold color scaling, real-time session cost in USD, turn execution timer that starts on prompt and pauses on response (`⏱ 14s` / `✓ 14s`), and 5h/7d rate limit trackers with automatic reset countdown timers. Includes an automated unit test suite with 36 test cases and dynamic prompt lifecycle verification (`statusline.test.js`). To activate, configure your local `~/.claude/settings.json` (see [config/claude/README.md](config/claude/README.md)).
- **Claude Code skill (`gemini-worker`)** — Lets any Claude Code session hand a task to Antigravity CLI (`agy`, Gemini 3.8 Flash) as a background shell command. The brief is piped in from a file (`bash ~/.claude/skills/gemini-worker/gemini.sh accept-edits < brief.md`), Gemini works in the current directory, and the report comes back with a call footer. Every call is logged to `~/.claude/gemini-calls.log`. Needs `agy` and `node` on the PATH.
- **Antigravity CLI (`agy`)** — Companion custom statusline faithfully mirroring the Claude Code statusline architecture and aesthetics. Displays active model name (`Gemini 3.8 Flash`), normalized effort level, fast mode badge (`⚡`), visual 4-bar context window meter (`▮▮▯▯`) with dynamic threshold color grading, turn execution timer that starts on prompt and pauses on response (`⏱ 14s` / `✓ 14s`), dual 5-hour and 7-day rate-limit countdown timers (`5h 9% ↻4h30m · 7d 45% ↻3d08h`), and Git branch indicator (` main`). Includes an automated unit test suite with 28 test cases and dynamic prompt lifecycle verification (`statusline.test.js`). To activate, configure your local `~/.gemini/antigravity-cli/settings.json` (see [config/agy/README.md](config/agy/README.md)).

## License

MIT — see [LICENSE](LICENSE).
