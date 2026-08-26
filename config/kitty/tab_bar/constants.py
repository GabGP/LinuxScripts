# ==============================================================================
#  config/kitty/tab_bar/constants.py - Paths, Cache Locations & Diagnostics
# ==============================================================================

import datetime
import os

# Resolve repository root directory and runtime cache directory
_REAL_FILE = os.path.realpath(__file__)
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_REAL_FILE))))
CACHE_DIR = os.path.join(_REPO_ROOT, ".cache")

try:
    os.makedirs(CACHE_DIR, exist_ok=True)
except Exception:
    CACHE_DIR = "/tmp"

WEATHER_CACHE = os.path.join(CACHE_DIR, "weather.cache")
DIAG_LOG = os.path.join(CACHE_DIR, "tabbar.log")
WEATHER_REFRESH_SECONDS = 1800  # 30 minutes


def log_diag(msg: str) -> None:
    """Appends timestamped diagnostic messages to tabbar.log."""
    try:
        with open(DIAG_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {msg}\n")
    except Exception:
        pass
