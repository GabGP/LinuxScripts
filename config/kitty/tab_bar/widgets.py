# ==============================================================================
#  config/kitty/tab_bar/widgets.py - Status Widget Collector & Palette Extractor
# ==============================================================================

from typing import Callable, Dict, List, Optional, Tuple

from kitty.fast_data_types import wcswidth
from kitty.tab_bar import DrawData, as_rgb
from tab_bar.config import CONFIG
from tab_bar.modules import get_battery, get_cpu, get_ram, get_time, get_weather


def fmt_widget_text(text: str) -> str:
    """Normalizes internal whitespace to guarantee strict uniform padding."""
    return f" {' '.join(text.split())} "


# Registry mapping widget identifier to (getter_function, style_mode)
# "inactive": uses inactive tab palette (secondary telemetry)
# "active": uses active tab palette (anchor widget)
WIDGET_REGISTRY: Dict[str, Tuple[Callable[[], Optional[str]], str]] = {
    "weather": (get_weather, "inactive"),
    "ram": (get_ram, "inactive"),
    "cpu": (get_cpu, "inactive"),
    "battery": (get_battery, "inactive"),
    "clock": (lambda: get_time(CONFIG.clock_format), "active"),
}


def build_widgets(draw_data: DrawData) -> List[Tuple[str, int, int]]:
    """Constructs status widgets dynamically based on tab_bar.conf active_widgets."""
    active_bg = as_rgb(int(draw_data.active_bg))
    active_fg = as_rgb(int(draw_data.active_fg))
    inactive_bg = as_rgb(int(draw_data.inactive_bg))
    inactive_fg = as_rgb(int(draw_data.inactive_fg))

    palette = {
        "active": (active_fg, active_bg),
        "inactive": (inactive_fg, inactive_bg),
    }

    widgets: List[Tuple[str, int, int]] = []

    for name in CONFIG.active_widgets:
        clean_name = name.strip().lower()
        if clean_name in WIDGET_REGISTRY:
            getter_fn, style_key = WIDGET_REGISTRY[clean_name]
            try:
                val = getter_fn()
                if val:
                    fg, bg = palette.get(style_key, (inactive_fg, inactive_bg))
                    widgets.append((fmt_widget_text(val), fg, bg))
            except Exception:
                pass

    return widgets


def calc_widgets_width(widgets: List[Tuple[str, int, int]]) -> int:
    """Calculates column width required for a list of widgets with powerline separators."""
    if not widgets:
        return 0
    return sum(1 + wcswidth(text) for text, _, _ in widgets)
