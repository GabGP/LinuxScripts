#!/usr/bin/env bash
# ==============================================================================
#  Fresh-install entry point
# ==============================================================================
#  Installs Ansible and its collection, clones this repo (if needed), and runs
#  the playbook. Use it for every run, not only the first: running
#  ansible-playbook directly can miss the community.general collection.
#
#  Fresh install, from a logged-in Plasma session:
#    curl -fsSL https://raw.githubusercontent.com/GabGP/LinuxScripts/main/bootstrap.sh | bash
#  Existing checkout (extra args go to ansible-playbook):
#    ./bootstrap.sh -t kde --check --diff
# ==============================================================================

set -euo pipefail

REPO_URL="https://github.com/GabGP/LinuxScripts.git"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-.}")" && pwd)"
DEPS=(git-core ansible-core ansible-collection-community-general)

if ! rpm -q "${DEPS[@]}" &>/dev/null; then
    sudo dnf install -y "${DEPS[@]}"
fi

if [[ -f "${SCRIPT_DIR}/ansible/site.yml" ]]; then
    REPO_DIR="${SCRIPT_DIR}"
else
    REPO_DIR="${REPO_DIR:-$HOME/Desktop/LinuxScripts}"
    [[ -d "${REPO_DIR}/.git" ]] || git clone "${REPO_URL}" "${REPO_DIR}"
fi

cd "${REPO_DIR}/ansible"

# Personal values stay out of git: ask once, keep them in personal.yml
ask() {  # ask <prompt> <default>; reads the terminal even under curl | bash
    local reply
    read -rp "$1 [$2]: " reply < /dev/tty
    printf '%s' "${reply:-$2}"
}

yaml_quote() {  # single-quoted YAML scalar
    local q="'"
    printf "'%s'" "${1//$q/$q$q}"
}

if [[ ! -f personal.yml ]]; then
    echo "First run: personal values go to ansible/personal.yml (gitignored)."
    name="$(ask "Git name" "$(git config --global user.name || true)")"
    email="$(ask "Git email (GitHub noreply recommended)" "$(git config --global user.email || true)")"
    (
        umask 077
        printf -- "---\n# Written by bootstrap.sh; edit to change. See personal.example.yml.\n" > personal.yml
        printf "git_user_name: %s\ngit_user_email: %s\n" "$(yaml_quote "$name")" "$(yaml_quote "$email")" >> personal.yml
    )
fi

# Reads the sudo password once; extra args pass through (e.g. -t kde, --check)
ansible-playbook -K site.yml "$@" < /dev/tty
