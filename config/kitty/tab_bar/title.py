# ==============================================================================
#  config/kitty/tab_bar/title.py - Tab Title Formatter & Command Icon Resolver
# ==============================================================================

import functools
import os
import re
import shutil
from typing import Optional
from tab_bar.config import CONFIG


@functools.lru_cache(maxsize=128)
def _is_executable(cmd: str) -> bool:
    """Fast cached check to determine if a command string exists in $PATH."""
    if not cmd or "/" in cmd or cmd.startswith("."):
        return False
    return shutil.which(cmd) is not None


def _resolve_cmd_prefix(first_word: str) -> Optional[str]:
    """Returns formatted command icon and prefix if first_word is recognized."""
    if first_word in CONFIG.command_icons:
        return f"{CONFIG.command_icons[first_word]} {first_word}: "
    if CONFIG.auto_detect_commands and _is_executable(first_word):
        return f"{CONFIG.default_cmd_icon} {first_word}: "
    return None


def format_tab_title(title: str, max_depth: Optional[int] = None) -> str:
    """Formats and truncates tab titles with dynamic path segments and Nerd Font glyphs."""
    if not title:
        return ""
    if max_depth is None:
        max_depth = CONFIG.max_title_depth

    # 1. Strip user@hostname prefix (e.g. 'admin@fedora: ')
    title = re.sub(r"^[a-zA-Z0-9_\-\.]+@[a-zA-Z0-9_\-\.]+:\s*", "", title).strip()

    # 2. Detect running command prefix
    cmd_prefix = ""
    target_path = title
    if " " in title and not os.path.exists(title):
        parts = title.split(" ", 1)
        prefix = _resolve_cmd_prefix(parts[0])
        if prefix:
            cmd_prefix = prefix
            target_path = parts[1].strip()
    elif title in CONFIG.command_icons and not os.path.exists(title):
        return f"{CONFIG.command_icons[title]} {title}"

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
