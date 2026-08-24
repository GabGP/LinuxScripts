# Fedora Linux Scripts & Dotfiles

A modular collection of personal Bash automation scripts, maintenance utilities, and terminal configurations crafted for **Fedora Linux**.

> [!NOTE]
> This project is intended for **personal use** and is tailored specifically for my personal **Fedora Linux** setup, integrating **DNF**, **Flatpak**, **Kitty**, **Starship**, **Rust (`rustup`)**, and **Antigravity CLI (`agy`)**.

---

## 📂 Repository Layout

```text
LinuxScripts/
├── config/                      # Dotfiles & tool configurations
│   ├── bash/.bashrc             # Shell environment & aliases (~/.bashrc)
│   ├── kitty/kitty.conf         # Kitty terminal & Nerd Font (~/.config/kitty/kitty.conf)
│   └── starship/starship.toml   # Starship prompt (~/.config/starship.toml)
├── scripts/                     # Maintenance & automation scripts
│   ├── update.sh                # Automated system & tool updater
│   ├── check-updates.sh         # Read-only pending updates checker
│   └── ezin.sh                  # Universal archive installer (.tar, .zip)
├── setup.sh                     # Interactive setup & configuration manager
├── .gitignore                   # Ignores local backups/
├── LICENSE                      # MIT License
└── README.md
```

---

## 🚀 Quick Setup (`setup.sh`)

The **`setup.sh`** script provides an interactive menu to deploy configurations and link automation scripts without needing complex flags.

```bash
# 1. Clone and enter repository
git clone https://github.com/GabGP/LinuxScripts.git
cd LinuxScripts

# 2. Run the interactive setup manager:
./setup.sh
```

### Menu Options:
* **1) Configurations:** Install all or selective configs (Kitty, Starship, Bash) as symlinks with automated backups to `backups/` (gitignored).
* **2) Automation Scripts:** Link all or selective scripts (`update`, `check-updates`, `ezin`) to `~/.local/bin/` for direct terminal execution.
* **3) Both (Full Installation):** Deploys all dotfiles and links all scripts in one step.

### Prerequisites

1. **System packages:**
   ```bash
   sudo dnf install file tar unzip sed desktop-file-utils curl
   chmod +x scripts/*.sh setup.sh
   ```

2. **Font: [MesloLGS Nerd Font](https://github.com/ryanoasis/nerd-fonts/releases/latest/download/Meslo.tar.xz)** (Recommended for Kitty & Starship):
   ```bash
   mkdir -p ~/.local/share/fonts/Meslo
   curl -fLo /tmp/Meslo.tar.xz https://github.com/ryanoasis/nerd-fonts/releases/latest/download/Meslo.tar.xz
   tar -xf /tmp/Meslo.tar.xz -C ~/.local/share/fonts/Meslo/
   rm -f /tmp/Meslo.tar.xz
   fc-cache -f ~/.local/share/fonts/Meslo
   ```

---

## 📖 Scripts

### 1. `scripts/update.sh`
Performs automated sequential updates across all Fedora packages and toolchains:
* **Updates:** DNF RPMs, Flatpaks, Starship binary, Antigravity CLI (`agy`), and Rust toolchains (`rustup`).
* **Usage:** `./scripts/update.sh` *(Run as regular user; prompts for `sudo` only when needed for DNF).*

### 2. `scripts/check-updates.sh`
Queries package managers and GitHub releases for pending updates without modifying the system:
* **Checks:** DNF, Flatpak, Starship, AGY CLI, and Rustup.
* **Usage:** `./scripts/check-updates.sh`

### 3. `scripts/ezin.sh`
Interactive installer that extracts pre-compiled archive packages into `/opt`, creates `.desktop` menu entries, and links binaries to `/usr/local/bin`:
* **Usage:** `sudo ./scripts/ezin.sh [path-to-archive.tar.xz]`

---

## 🎨 Configurations

| Configuration | Destination | Features |
| :--- | :--- | :--- |
| **`config/kitty/kitty.conf`** | `~/.config/kitty/kitty.conf` | `MesloLGS Nerd Font` font family, clean optical prompt alignment, and theme integration. |
| **`config/starship/starship.toml`** | `~/.config/starship.toml` | **Gruvbox-Rainbow** continuous capsule layout with **Kokiri by Chuck** color palette. |
| **`config/bash/.bashrc`** | `~/.bashrc` | User environment variables, path exports, and Starship shell hook. |

### 🌟 Starship Prompt Details

* **Theme Design:** Continuous Powerline capsules (inspired by Gruvbox-Rainbow) with Chuck's earthy **Kokiri** palette (Dark Gold, Warm Amber, Forest Teal, Slate Blue, Plum, Forest Green).
* **Readability:** Deep espresso font (`#1a1005`) for high contrast against colored capsules.
* **100% Feature Completeness:** Preserves all **101 Starship default modules** (languages, runtimes, containers, cloud contexts, diagnostics).
* **Diagnostics Order:** Command duration and exit code status appear after the clock inside the final capsule.
* **Standardized Palette:** Edit only 8 semantic hex variables at the top of [config/starship/starship.toml](config/starship/starship.toml) to swap color themes anytime.

---

## 📄 License

MIT License — see the [LICENSE](LICENSE) file for details.
