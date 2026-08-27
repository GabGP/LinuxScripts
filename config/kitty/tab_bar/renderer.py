# ==============================================================================
#  config/kitty/tab_bar/renderer.py - Powerline Tab Bar & Widget Renderer
# ==============================================================================

from kitty.fast_data_types import Screen
from kitty.tab_bar import (
    DrawData,
    ExtraData,
    TabBarData,
    as_rgb,
    draw_tab_with_powerline,
)
from tab_bar.title import format_tab_title
from tab_bar.widgets import build_widgets, calc_widgets_width


def _draw_right_status(screen: Screen, draw_data: DrawData) -> None:
    """Renders right-aligned status widgets with seamless Powerline transitions matching left tabs."""
    default_bg = as_rgb(int(draw_data.default_bg))
    widgets = build_widgets(draw_data)
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

    available_space = screen.columns - screen.cursor.x

    # Graceful degradation: drop leftmost widgets if terminal window is extremely narrow
    while widgets and calc_widgets_width(widgets) > available_space:
        widgets.pop(0)

    if not widgets:
        return

    total_width = calc_widgets_width(widgets)

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
    # Clean and truncate title to 3 directory levels
    clean_title = format_tab_title(tab.title, max_depth=3)
    tab = tab._replace(title=clean_title)

    # Reserve guaranteed space for right status widgets so long tab titles never crowd them out
    # Calculate required width of all active widgets (~50 columns)
    status_width = calc_widgets_width(build_widgets(draw_data))
    max_allowed_for_tabs = screen.columns - status_width
    remaining_for_this_tab = max_allowed_for_tabs - before - 2

    # Cap max_tab_length so Kitty automatically truncates long titles with '…'
    if remaining_for_this_tab > 6:
        max_tab_length = min(max_tab_length, remaining_for_this_tab)

    # Draw left tab with Kitty built-in powerline function
    end = draw_tab_with_powerline(
        draw_data, screen, tab, before, max_tab_length, index, is_last, extra_data
    )

    # When the final tab is reached, draw the right status bar
    if is_last:
        _draw_right_status(screen, draw_data)

    return end
