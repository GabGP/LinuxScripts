# ==============================================================================
#  config/kitty/tab_bar/renderer.py - Powerline Tab Bar & Widget Renderer
# ==============================================================================

import os
import re
from typing import List, Tuple
from kitty.fast_data_types import Screen, wcswidth
from kitty.tab_bar import (
    DrawData,
    ExtraData,
    TabBarData,
    as_rgb,
    draw_tab_with_powerline,
)
from tab_bar.modules import get_battery, get_cpu, get_ram, get_time, get_weather


def _fmt(text: str) -> str:
    """Normalizes internal whitespace to guarantee strict uniform padding."""
    return f" {' '.join(text.split())} "


def _format_tab_title(title: str, max_depth: int = 3) -> str:
    """
    Formats and truncates a tab title to at most `max_depth` directory levels,
    replicating Starship's directory segment truncation behavior.
    """
    if not title:
        return ""

    # 1. Strip user@hostname prefix (e.g. 'admin@fedora: ')
    title = re.sub(r"^[a-zA-Z0-9_\-\.]+@[a-zA-Z0-9_\-\.]+:\s*", "", title).strip()

    # 2. Detect running command prefix
    cmd_prefix = ""
    target_path = title
    if " " in title and not os.path.exists(title):
        parts = title.split(" ", 1)
        known_cmds = (
            "nvim",
            "vim",
            "vi",
            "nano",
            "emacs",
            "git",
            "python",
            "python3",
            "bash",
            "zsh",
            "cargo",
            "less",
            "man",
            "ssh",
        )
        if parts[0] in known_cmds:
            cmd_prefix = f"{parts[0]}: "
            target_path = parts[1].strip()

    # 3. Normalize home directory
    home = os.path.expanduser("~")
    if target_path.startswith(home):
        target_path = "~" + target_path[len(home):]

    # 4. Truncate path segments if depth exceeds max_depth
    if "/" in target_path or target_path.startswith("~"):
        is_home_rooted = target_path.startswith("~/")
        raw_path = target_path[2:] if is_home_rooted else target_path.lstrip("/")
        segments = [s for s in raw_path.split("/") if s]

        if is_home_rooted:
            if not segments:
                formatted_path = "~"
            elif len(segments) <= max_depth - 1:
                formatted_path = "~/" + "/".join(segments)
            else:
                formatted_path = "…/" + "/".join(segments[-max_depth:])
        else:
            if len(segments) <= max_depth:
                formatted_path = "/" + "/".join(segments) if target_path.startswith("/") else "/".join(segments)
            else:
                formatted_path = "…/" + "/".join(segments[-max_depth:])
        return f"{cmd_prefix}{formatted_path}"

    return f"{cmd_prefix}{target_path}"


def _build_widgets(draw_data: DrawData) -> List[Tuple[str, int, int]]:
    """Constructs status widgets with theme-derived colors."""
    active_bg = as_rgb(int(draw_data.active_bg))
    active_fg = as_rgb(int(draw_data.active_fg))
    inactive_bg = as_rgb(int(draw_data.inactive_bg))
    inactive_fg = as_rgb(int(draw_data.inactive_fg))

    widgets: List[Tuple[str, int, int]] = []

    # 1. Weather Widget (Lowest priority in extreme collapse)
    weather = get_weather()
    if weather:
        widgets.append((_fmt(weather), inactive_fg, inactive_bg))

    # 2. RAM Usage Widget
    ram = get_ram()
    if ram:
        widgets.append((_fmt(ram), inactive_fg, inactive_bg))

    # 3. CPU Load & Temperature Widget
    cpu = get_cpu()
    if cpu:
        widgets.append((_fmt(cpu), inactive_fg, inactive_bg))

    # 4. Battery Widget
    battery = get_battery()
    if battery:
        widgets.append((_fmt(battery), inactive_fg, inactive_bg))

    # 5. Clock Widget (Highest priority / anchor)
    time_str = get_time()
    widgets.append((_fmt(time_str), active_fg, active_bg))

    return widgets


def _calc_widgets_width(widgets: List[Tuple[str, int, int]]) -> int:
    """Calculates column width required for a list of widgets with powerline separators."""
    if not widgets:
        return 0
    return sum(1 + wcswidth(text) for text, _, _ in widgets)


def _draw_right_status(screen: Screen, draw_data: DrawData) -> None:
    """Renders right-aligned status widgets with seamless Powerline transitions matching left tabs."""
    default_bg = as_rgb(int(draw_data.default_bg))
    widgets = _build_widgets(draw_data)
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
    while widgets and _calc_widgets_width(widgets) > available_space:
        widgets.pop(0)

    if not widgets:
        return

    total_width = _calc_widgets_width(widgets)

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
    clean_title = _format_tab_title(tab.title, max_depth=3)
    tab = tab._replace(title=clean_title)

    # Reserve guaranteed space for right status widgets so long tab titles never crowd them out
    # Calculate required width of all active widgets (~50 columns)
    status_width = _calc_widgets_width(_build_widgets(draw_data))
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
