# ==============================================================================
#  config/kitty/tab_bar/renderer.py - Powerline Tab Bar & Widget Renderer
# ==============================================================================

from kitty.fast_data_types import Screen, get_options, wcswidth
from kitty.tab_bar import (
    DrawData,
    ExtraData,
    TabBarData,
    as_rgb,
    draw_tab_with_powerline,
)
from kitty.utils import color_as_int
from tab_bar.modules import get_battery, get_time, get_weather


def _fmt(text: str) -> str:
    """Normalizes internal whitespace to guarantee strict uniform padding."""
    return f" {' '.join(text.split())} "


def _draw_right_status(screen: Screen, draw_data: DrawData) -> None:
    """Renders right-aligned status widgets with seamless Powerline transitions matching left tabs."""
    # Inherit colors directly from Kitty theme palette matching left tabs
    default_bg = as_rgb(int(draw_data.default_bg))
    active_bg = as_rgb(int(draw_data.active_bg))
    active_fg = as_rgb(int(draw_data.active_fg))
    inactive_bg = as_rgb(int(draw_data.inactive_bg))
    inactive_fg = as_rgb(int(draw_data.inactive_fg))

    # Build status widgets: (text, fg_color, bg_color)
    widgets = []

    # 1. Weather Widget (Matching Inactive Tab Colors)
    weather = get_weather()
    if weather:
        widgets.append((_fmt(weather), inactive_fg, inactive_bg))

    # 2. Battery Widget (Matching Inactive Tab Colors)
    battery = get_battery()
    if battery:
        widgets.append((_fmt(battery), inactive_fg, inactive_bg))

    # 3. Clock Widget (Matching Active Tab Colors)
    time_str = get_time()
    widgets.append((_fmt(time_str), active_fg, active_bg))

    if not widgets:
        return

    # Mirror the left powerline separator symbols (hard and soft)
    # Left: '' / '' (angled)  -> Right: '' / ''
    # Left: '' / '╱' (slanted) -> Right: '' / '╱'
    # Left: '' / '' (round)   -> Right: '' / ''
    if draw_data.powerline_style == "slanted":
        sep_symbol = ""
        soft_sep_symbol = "╱"
    elif draw_data.powerline_style == "round":
        sep_symbol = ""
        soft_sep_symbol = ""
    else:  # angled (default)
        sep_symbol = ""
        soft_sep_symbol = ""

    # Calculate total width required for seamless transitions
    total_width = 0
    prev_bg = default_bg
    for text, _, bg in widgets:
        total_width += 1 + wcswidth(text)
        prev_bg = bg

    available_space = screen.columns - screen.cursor.x
    if available_space <= total_width:
        return

    # Fill gap between left tabs and right status bar
    gap = screen.columns - total_width - screen.cursor.x
    if gap > 0:
        screen.cursor.bg = default_bg
        screen.cursor.fg = default_bg
        screen.draw(" " * gap)

    # Draw each widget with seamless powerline and soft separators
    prev_bg = default_bg
    for text, fg, bg in widgets:
        if bg == prev_bg:
            # Seamless soft separator matching Kitty left tab styling
            screen.cursor.fg = default_bg
            screen.cursor.bg = bg
            screen.draw(soft_sep_symbol)
        else:
            # Seamless hard powerline arrow transition
            screen.cursor.fg = bg
            screen.cursor.bg = prev_bg
            screen.draw(sep_symbol)

        # Draw widget content in uniform bold for sharp contrast
        screen.cursor.bold = True
        screen.cursor.fg = fg
        screen.cursor.bg = bg
        screen.draw(text)
        screen.cursor.bold = False

        prev_bg = bg

    # Reset cursor colors
    screen.cursor.bg = default_bg
    screen.cursor.fg = default_bg


def draw_tab(
    draw_data: DrawData,
    screen: Screen,
    tab: TabBarData,
    before: int,
    max_tab_length: int,
    index: int,
    is_last: bool,
    extra_data: ExtraData,
) -> int:
    """Main tab drawing callback executed by Kitty for each tab."""
    # Draw left tab with Kitty built-in powerline function
    end = draw_tab_with_powerline(
        draw_data, screen, tab, before, max_tab_length, index, is_last, extra_data
    )

    # When the final tab is reached, draw the right status bar
    if is_last:
        _draw_right_status(screen, draw_data)

    return end
