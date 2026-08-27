# ==============================================================================
#  config/kitty/tab_bar/widgets.py - Status Widget Collector & Palette Extractor
# ==============================================================================

from typing import List, Tuple

from kitty.fast_data_types import wcswidth
from kitty.tab_bar import DrawData, as_rgb
from tab_bar.modules import get_battery, get_cpu, get_ram, get_time, get_weather


def fmt_widget_text(text: str) -> str:
    """Normalizes internal whitespace to guarantee strict uniform padding."""
    return f" {' '.join(text.split())} "


def build_widgets(draw_data: DrawData) -> List[Tuple[str, int, int]]:
    """Constructs status widgets with theme-derived colors."""
    active_bg = as_rgb(int(draw_data.active_bg))
    active_fg = as_rgb(int(draw_data.active_fg))
    inactive_bg = as_rgb(int(draw_data.inactive_bg))
    inactive_fg = as_rgb(int(draw_data.inactive_fg))

    widgets: List[Tuple[str, int, int]] = []

    # 1. Weather Widget (Lowest priority in extreme collapse)
    weather = get_weather()
    if weather:
        widgets.append((fmt_widget_text(weather), inactive_fg, inactive_bg))

    # 2. RAM Usage Widget
    ram = get_ram()
    if ram:
        widgets.append((fmt_widget_text(ram), inactive_fg, inactive_bg))

    # 3. CPU Load & Temperature Widget
    cpu = get_cpu()
    if cpu:
        widgets.append((fmt_widget_text(cpu), inactive_fg, inactive_bg))

    # 4. Battery Widget
    battery = get_battery()
    if battery:
        widgets.append((fmt_widget_text(battery), inactive_fg, inactive_bg))

    # 5. Clock Widget (Highest priority / anchor)
    time_str = get_time()
    widgets.append((fmt_widget_text(time_str), active_fg, active_bg))

    return widgets


def calc_widgets_width(widgets: List[Tuple[str, int, int]]) -> int:
    """Calculates column width required for a list of widgets with powerline separators."""
    if not widgets:
        return 0
    return sum(1 + wcswidth(text) for text, _, _ in widgets)
