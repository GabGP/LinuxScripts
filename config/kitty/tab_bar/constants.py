# ==============================================================================
#  config/kitty/tab_bar/constants.py - Paths, Cache Locations & Diagnostics
# ==============================================================================

import datetime
import os
from tab_bar.config import CONFIG

# Resolve repository root directory or standard XDG cache directory
_REAL_FILE = os.path.realpath(__file__)
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_REAL_FILE))))

if os.path.isdir(os.path.join(_REPO_ROOT, ".git")) or os.path.isfile(os.path.join(_REPO_ROOT, "setup.sh")):
    CACHE_DIR = os.path.join(_REPO_ROOT, ".cache")
else:
    xdg_cache = os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))
    CACHE_DIR = os.path.join(xdg_cache, "kitty-tab-bar")

try:
    os.makedirs(CACHE_DIR, exist_ok=True)
except Exception:
    CACHE_DIR = "/tmp"

WEATHER_CACHE = os.path.join(CACHE_DIR, "weather.cache")
GEO_CACHE = os.path.join(CACHE_DIR, "geo.cache")
DIAG_LOG = os.path.join(CACHE_DIR, "tab_bar.log")
WEATHER_REFRESH_SECONDS = CONFIG.weather_refresh_seconds
_MAX_LOG_BYTES = 512 * 1024  # 512 KB rotation threshold


def log_diag(msg: str) -> None:
    """Appends timestamped diagnostic messages to tab_bar.log with auto-rotation."""
    if not CONFIG.enable_logging:
        return

    try:
        if os.path.isfile(DIAG_LOG) and os.path.getsize(DIAG_LOG) > _MAX_LOG_BYTES:
            backup_log = f"{DIAG_LOG}.1"
            if os.path.isfile(backup_log):
                os.remove(backup_log)
            os.rename(DIAG_LOG, backup_log)

        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        with open(DIAG_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {msg}\n")
    except Exception:
        pass
