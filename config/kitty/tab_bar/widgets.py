# ==============================================================================
#  config/kitty/tab_bar/widgets.py - Status Widget Collector & Palette Extractor
# ==============================================================================

import time

from kitty.fast_data_types import wcswidth
from kitty.tab_bar import DrawData, as_rgb
from tab_bar.config import CONFIG
from tab_bar.registry import WIDGET_REGISTRY, discover_and_load_widgets

# Ensure all widget modules are discovered and loaded into WIDGET_REGISTRY
discover_and_load_widgets()

# Frame-scoped cache to eliminate redundant I/O reads during multi-tab render cycles
_cache_timestamp: float = 0.0
_cache_palette: tuple[int, int, int, int] = (0, 0, 0, 0)
_cached_widgets: list[tuple[str, int, int]] = []


def fmt_widget_text(text: str) -> str:
    """Normalizes internal whitespace to guarantee strict uniform padding."""
    return f" {' '.join(text.split())} "


def build_widgets(draw_data: DrawData) -> list[tuple[str, int, int]]:
    """Constructs status widgets dynamically with frame-scoped memoization."""
    global _cache_timestamp, _cache_palette, _cached_widgets

    now = time.time()
    active_bg = as_rgb(int(draw_data.active_bg))
    active_fg = as_rgb(int(draw_data.active_fg))
    inactive_bg = as_rgb(int(draw_data.inactive_bg))
    inactive_fg = as_rgb(int(draw_data.inactive_fg))
    current_palette = (active_fg, active_bg, inactive_fg, inactive_bg)

    # Return cached widgets if evaluated within the same render frame (< 250ms)
    if (now - _cache_timestamp < 0.25) and (_cache_palette == current_palette):
        return _cached_widgets

    palette = {
        "active": (active_fg, active_bg),
        "inactive": (inactive_fg, inactive_bg),
    }

    widgets: list[tuple[str, int, int]] = []
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

    _cache_timestamp = now
    _cache_palette = current_palette
    _cached_widgets = widgets
    return widgets


def calc_widgets_width(widgets: list[tuple[str, int, int]]) -> int:
    """Calculates column width required for a list of widgets with powerline separators."""
    if not widgets:
        return 0
    return sum(1 + wcswidth(text) for text, _, _ in widgets)
