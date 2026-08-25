# ==============================================================================
#  Kitty Custom Tab Bar Extension (Slanted Powerline + Right Status Widgets)
# ==============================================================================
#  Renders slanted powerline tabs on the left and live status widgets on the right:
#  - Weather (Condition + Temperature in Celsius, asynchronously cached)
#  - Battery (Level + Charging status from /sys/class/power_supply/BAT0)
#  - Clock (24-Hour Time with Nerd Font clock icon)
# ==============================================================================

import datetime
import os
import threading
import urllib.request

from kitty.fast_data_types import Screen, wcswidth
from kitty.tab_bar import (
    DrawData,
    ExtraData,
    TabBarData,
    as_rgb,
    draw_tab_with_powerline,
)

# Weather cache configuration (avoids network lag on terminal draws)
WEATHER_CACHE = "/tmp/kitty_weather.cache"
WEATHER_REFRESH_SECONDS = 1800  # Refresh every 30 minutes


def _fetch_weather_async() -> None:
    """Fetches weather in the background without blocking terminal rendering."""
    def _worker():
        try:
            req = urllib.request.Request(
                "https://wttr.in/?format=%c+%t",
                headers={"User-Agent": "curl/8.0"}
            )
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = resp.read().decode("utf-8").strip()
                # Clean up formatting (e.g., '+22°C' -> '22°C')
                data = data.replace("+", "")
                with open(WEATHER_CACHE, "w", encoding="utf-8") as f:
                    f.write(data)
        except Exception:
            pass

    threading.Thread(target=_worker, daemon=True).start()


def get_weather() -> str:
    """Reads cached weather or triggers background update."""
    try:
        if os.path.exists(WEATHER_CACHE):
            mtime = os.path.getmtime(WEATHER_CACHE)
            if datetime.datetime.now().timestamp() - mtime < WEATHER_REFRESH_SECONDS:
                with open(WEATHER_CACHE, "r", encoding="utf-8") as f:
                    return f.read().strip()
            else:
                _fetch_weather_async()
                with open(WEATHER_CACHE, "r", encoding="utf-8") as f:
                    return f.read().strip()
        else:
            _fetch_weather_async()
            return "⛅ --°C"
    except Exception:
        return "⛅ --°C"


def get_battery() -> str:
    """Reads Linux sysfs power supply for battery level and charging state."""
    try:
        base = "/sys/class/power_supply"
        if not os.path.exists(base):
            return ""

        for d in os.listdir(base):
            if d.startswith("BAT"):
                cap_path = os.path.join(base, d, "capacity")
                stat_path = os.path.join(base, d, "status")
                if os.path.exists(cap_path):
                    with open(cap_path, "r") as f:
                        cap = int(f.read().strip())
                    stat = ""
                    if os.path.exists(stat_path):
                        with open(stat_path, "r") as f:
                            stat = f.read().strip().lower()

                    is_charging = "charging" in stat
                    if is_charging:
                        icon = "󰂄"
                    elif cap >= 90:
                        icon = "󰁹"
                    elif cap >= 70:
                        icon = "󰂁"
                    elif cap >= 50:
                        icon = "󰁿"
                    elif cap >= 30:
                        icon = "󰁽"
                    elif cap >= 15:
                        icon = "󰁻"
                    else:
                        icon = "󰁺"
                    return f"{icon} {cap}%"

        # Fallback to AC if no battery found
        ac_path = os.path.join(base, "AC/online")
        if os.path.exists(ac_path):
            with open(ac_path, "r") as f:
                if f.read().strip() == "1":
                    return "󰂄 AC"
    except Exception:
        return ""
    return ""


def get_time() -> str:
    """Formats current 24-hour time with clock icon."""
    return datetime.datetime.now().strftime(" %H:%M")


def _draw_right_status(screen: Screen, draw_data: DrawData) -> None:
    """Draws right-aligned status capsules (Weather, Battery, Clock)."""
    widgets = []

    # 1. Weather Widget (Muted Slate / Gold)
    weather = get_weather()
    if weather:
        widgets.append((f" {weather} ", 0xD4BE98, 0x32302F))

    # 2. Battery Widget (Forest Sage / Dark Text)
    battery = get_battery()
    if battery:
        widgets.append((f" {battery} ", 0x1A1005, 0x89B482))

    # 3. Clock Widget (Warm Amber / Dark Text)
    time_str = get_time()
    widgets.append((f" {time_str} ", 0x1A1005, 0xD4874C))

    if not widgets:
        return

    # Separator glyph matching tab bar style
    sep_symbol = "" if draw_data.powerline_style == "slanted" else ""

    # Calculate total character cells needed for right status
    total_width = 0
    for text, _, _ in widgets:
        total_width += wcswidth(text) + 1  # +1 for separator

    default_bg = as_rgb(int(draw_data.default_bg))
    available_space = screen.columns - screen.cursor.x

    if available_space <= total_width:
        return

    # Fill whitespace gap between left tabs and right status bar
    gap = screen.columns - total_width - screen.cursor.x
    if gap > 0:
        screen.cursor.bg = default_bg
        screen.cursor.fg = default_bg
        screen.draw(" " * gap)

    # Render each status capsule with powerline separator
    prev_bg = default_bg
    for text, fg, bg in widgets:
        bg_rgb = as_rgb(bg)
        fg_rgb = as_rgb(fg)

        # Draw left-pointing separator
        screen.cursor.fg = bg_rgb
        screen.cursor.bg = prev_bg
        screen.draw(sep_symbol)

        # Draw capsule content
        screen.cursor.fg = fg_rgb
        screen.cursor.bg = bg_rgb
        screen.draw(text)

        prev_bg = bg_rgb

    # Reset cursor
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
    end = draw_tab_with_powerline(
        draw_data, screen, tab, before, max_tab_length, index, is_last, extra_data
    )
    if is_last:
        _draw_right_status(screen, draw_data)
    return end
