# ==============================================================================
#  config/kitty/tab_bar/modules/clock.py - Clock Status Widget
# ==============================================================================

import datetime
from tab_bar.config import CONFIG
from tab_bar.registry import register_widget


@register_widget("clock", style="active")
def get_time(fmt: str | None = None) -> str:
    """Formats current time with a Nerd Font clock glyph using configured strftime pattern."""
    clock_fmt = fmt if fmt else CONFIG.clock_format
    return datetime.datetime.now().strftime(f" {clock_fmt}")
