#!/usr/bin/env bash
# ==============================================================================
#  Save Plasma Layout
# ==============================================================================
#  Dumps the live panel and desktop layout (panels, widgets, widget settings,
#  wallpaper) to config/plasma/layout.js. The Ansible kde role replays that
#  file on other installs. Run it after changing the panel, then commit.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${SCRIPT_DIR}/../config/plasma/layout.js"
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/linuxscripts"

mkdir -p "$(dirname "$OUT")" "$STATE_DIR"

# plasmashell returns the script as a byte array
busctl --user --json=short call org.kde.plasmashell /PlasmaShell \
    org.kde.PlasmaShell dumpCurrentLayoutJS \
    | python3 -c 'import json, sys; sys.stdout.write(bytes(json.load(sys.stdin)["data"][0]).decode())' \
    > "$OUT"

# This machine already has the layout, so the playbook should not replay it here
sha256sum "$OUT" | cut -d' ' -f1 > "${STATE_DIR}/plasma-layout.sha256"

echo "Saved Plasma layout to config/plasma/layout.js"
