# ==============================================================================
#  config/kitty/tab_bar/modules/clock.py - Clock Status Widget
# ==============================================================================

import datetime
from typing import Optional


def get_time(fmt: Optional[str] = None) -> str:
    """Formats current time with a Nerd Font clock glyph using configured strftime pattern."""
    clock_fmt = fmt if fmt else "%H:%M"
    return datetime.datetime.now().strftime(f" {clock_fmt}")
