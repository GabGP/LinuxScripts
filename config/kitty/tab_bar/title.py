# ==============================================================================
#  config/kitty/tab_bar/title.py - Tab Title Formatter & Path Truncation
# ==============================================================================

import os
import re

KNOWN_COMMANDS = (
    "nvim",
    "vim",
    "vi",
    "nano",
    "emacs",
    "git",
    "python",
    "python3",
    "bash",
    "zsh",
    "cargo",
    "less",
    "man",
    "ssh",
)


def format_tab_title(title: str, max_depth: int = 3) -> str:
    """
    Formats and truncates a tab title to at most `max_depth` directory levels,
    replicating Starship's directory segment truncation behavior.
    """
    if not title:
        return ""

    # 1. Strip user@hostname prefix (e.g. 'admin@fedora: ')
    title = re.sub(r"^[a-zA-Z0-9_\-\.]+@[a-zA-Z0-9_\-\.]+:\s*", "", title).strip()

    # 2. Detect running command prefix
    cmd_prefix = ""
    target_path = title
    if " " in title and not os.path.exists(title):
        parts = title.split(" ", 1)
        if parts[0] in KNOWN_COMMANDS:
            cmd_prefix = f"{parts[0]}: "
            target_path = parts[1].strip()

    # 3. Normalize home directory
    home = os.path.expanduser("~")
    if target_path.startswith(home):
        target_path = "~" + target_path[len(home):]

    # 4. Truncate path segments if depth exceeds max_depth
    if "/" in target_path or target_path.startswith("~"):
        is_home_rooted = target_path.startswith("~/")
        raw_path = target_path[2:] if is_home_rooted else target_path.lstrip("/")
        segments = [s for s in raw_path.split("/") if s]

        if is_home_rooted:
            if not segments:
                formatted_path = "~"
            elif len(segments) <= max_depth - 1:
                formatted_path = "~/" + "/".join(segments)
            else:
                formatted_path = "…/" + "/".join(segments[-max_depth:])
        else:
            if len(segments) <= max_depth:
                formatted_path = "/" + "/".join(segments) if target_path.startswith("/") else "/".join(segments)
            else:
                formatted_path = "…/" + "/".join(segments[-max_depth:])
        return f"{cmd_prefix}{formatted_path}"

    return f"{cmd_prefix}{target_path}"
