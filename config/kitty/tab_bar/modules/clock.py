# ==============================================================================
#  config/kitty/tab_bar/modules/clock.py - Clock Status Widget
# ==============================================================================

import datetime


def get_time() -> str:
    """Formats current 24-hour time with a Nerd Font clock glyph."""
    return datetime.datetime.now().strftime(" %H:%M")
