# ==============================================================================
#  config/kitty/tab_bar/config.py - Declarative Configuration Engine & Parser
# ==============================================================================

import os
from typing import Dict, List


class TabBarConfig:
    def __init__(self) -> None:
        self.max_title_depth: int = 3
        self.auto_detect_commands: bool = True
        self.default_cmd_icon: str = ""
        self.active_widgets: List[str] = ["weather", "ram", "cpu", "battery", "clock"]
        self.clock_format: str = "%H:%M"
        self.weather_refresh_seconds: int = 1800
        self.command_icons: Dict[str, str] = {}


def _find_conf_path() -> str:
    """Locates tab_bar.conf in config directory or user home."""
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(os.path.realpath(__file__))))
    candidate = os.path.join(pkg_dir, "tab_bar.conf")
    if os.path.isfile(candidate):
        return candidate
    user_kitty = os.path.expanduser("~/.config/kitty/tab_bar.conf")
    if os.path.isfile(user_kitty):
        return user_kitty
    return candidate


def load_config() -> TabBarConfig:
    """Parses tab_bar.conf with safe fallback defaults."""
    cfg = TabBarConfig()
    conf_path = _find_conf_path()

    if not os.path.isfile(conf_path):
        return cfg

    try:
        with open(conf_path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue

                parts = line.split(None, 2)
                if not parts:
                    continue

                key = parts[0].lower()
                if key == "cmd_icon" and len(parts) >= 3:
                    cfg.command_icons[parts[1]] = parts[2]
                elif key == "active_widgets" and len(parts) >= 2:
                    raw_widgets = line.split()[1:]
                    cfg.active_widgets = [w.strip(",") for w in raw_widgets if w.strip(",")]
                elif key == "max_title_depth" and len(parts) >= 2:
                    cfg.max_title_depth = int(parts[1])
                elif key == "auto_detect_commands" and len(parts) >= 2:
                    cfg.auto_detect_commands = parts[1].lower() in ("yes", "true", "1", "on")
                elif key == "default_cmd_icon" and len(parts) >= 2:
                    cfg.default_cmd_icon = parts[1]
                elif key == "clock_format" and len(parts) >= 2:
                    cfg.clock_format = " ".join(line.split()[1:])
                elif key == "weather_refresh_seconds" and len(parts) >= 2:
                    cfg.weather_refresh_seconds = int(parts[1])
    except Exception:
        pass

    return cfg


# Global singleton instance loaded once per tab bar evaluation
CONFIG = load_config()
