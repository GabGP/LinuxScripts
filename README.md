# Personal Linux Scripts (Fedora)

A collection of personal Bash automation and maintenance scripts tailored for **Fedora Linux**.

> [!NOTE]
> These scripts are intended for **personal use** and are optimized specifically for a Fedora development environment with tools like DNF, Flatpak, Rust (`rustup`), and Antigravity CLI (`agy`).

---

## 📂 Scripts Overview

| Script | Purpose | Privileges |
| :--- | :--- | :--- |
| **`update.sh`** | Sequentially updates Fedora system packages, Flatpaks, and developer toolchains. | Regular user (prompts for `sudo` for DNF) |
| **`check-updates.sh`** | Checks for available updates across all tools without making changes. | Regular user |
| **`ezin.sh`** | Automates installing pre-compiled software archives (`.tar`, `.zip`) into system paths. | Root (`sudo`) |

---

## 🛠 Prerequisites & Setup

Ensure the scripts have executable permissions before running them:

```bash
chmod +x *.sh
```

### Dependencies

For full functionality across all scripts (particularly `ezin.sh`), make sure standard system utilities are installed:

```bash
sudo dnf install file tar unzip sed desktop-file-utils
```

---

## 📖 Script Usage & Expected Behaviors

### 1. `update.sh` — System & Tools Updater

Upgrades all packages and developer toolchains in a single command.

#### Usage:
```bash
./update.sh
```

> [!IMPORTANT]
> Run this script as your **regular user**, not directly with `sudo`. The script will request `sudo` credentials when needed for `dnf`, ensuring that user-specific tools like `rustup` and `agy` update properly inside your user environment (`$HOME`).

#### What it does:
1. **DNF**: Refreshes repositories and updates all Fedora RPM packages (`sudo dnf upgrade --refresh -y`).
2. **Flatpak**: Updates all system and user Flatpak applications and runtimes (`flatpak update -y`).
3. **Antigravity CLI (AGY)**: Updates the `agy` CLI binary (`agy update`).
4. **Rustup**: Updates installed Rust toolchains and rustup manager (`rustup update`).
5. Displays a green summary banner upon completion.

---

### 2. `check-updates.sh` — Update Checker (Read-Only)

Queries repositories and tool managers to check if updates are available without applying any modifications.

#### Usage:
```bash
./check-updates.sh
```

#### What it does:
1. **DNF**: Runs `dnf check-update` to verify if any Fedora package updates are pending.
2. **Flatpak**: Queries `flatpak remote-ls --updates` for pending application/runtime updates.
3. **Antigravity CLI (AGY)**: Reports current version and provides upgrade guidance.
4. **Rustup**: Runs `rustup check` to check for newer toolchains or compiler versions.
5. **Summary Banner**: Displays whether everything is up to date or if updates are pending with a suggestion to run `./update.sh`.

---

### 3. `ezin.sh` — Easy Install for Archives

An interactive installer designed to automate extracting and installing pre-compiled Linux software distributed as `.tar.gz`, `.tar.xz`, `.tar.bz2`, or `.zip` archives.

#### Features:
- **Archive Protection**: Handles nested and flat archive structures safely.
- **Desktop Integration**: Detects and configures `.desktop` files and updates desktop database (`update-desktop-database`).
- **Path Setup**: Links binaries to `/usr/local/bin` or standard paths.

#### Usage:
```bash
# Pass archive path as an argument
sudo ./ezin.sh /path/to/software-1.2.3.tar.xz

# Or run interactively (will prompt for file path)
sudo ./ezin.sh
```
