# ==============================================================================
#  Kitty Custom Tab Bar Extension
# ==============================================================================
#  - Left: Powerline tabs matching kitty.conf style (angled / slanted / round)
#  - Right: Live status widgets (Weather, Battery, Clock)
#  - Colors: Dynamically inherited from Kitty active theme (current-theme.conf)
#  - Timer: Aligned One-Shot Kernel Interrupt Timer (60 wakeups per hour)
# ==============================================================================

import datetime
import os
import threading
import time
import urllib.request

from kitty.fast_data_types import (
    Screen,
    add_timer,
    get_boss,
    get_options,
    mark_os_window_dirty,
    wakeup_main_loop,
    wcswidth,
)
from kitty.tab_bar import (
    DrawData,
    ExtraData,
    TabBarData,
    as_rgb,
    draw_tab_with_powerline,
)
from kitty.utils import color_as_int

# Resolve repository root directory and runtime cache directory
_REAL_FILE = os.path.realpath(__file__)
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_REAL_FILE)))
CACHE_DIR = os.path.join(_REPO_ROOT, ".cache")

try:
    os.makedirs(CACHE_DIR, exist_ok=True)
except Exception:
    CACHE_DIR = "/tmp"

WEATHER_CACHE = os.path.join(CACHE_DIR, "weather.cache")
DIAG_LOG = os.path.join(CACHE_DIR, "tabbar.log")
WEATHER_REFRESH_SECONDS = 1800  # 30 minutes


def _log(msg: str) -> None:
    try:
        with open(DIAG_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {msg}\n")
    except Exception:
        pass


# ------------------------------------------------------------------------------
# 1. Aligned One-Shot Kernel Timer (Zero Busy-Polling / 60 Wakeups Per Hour)
# ------------------------------------------------------------------------------
_timer_registered = False


def _schedule_next_minute_tick() -> None:
    """Calculates exact milliseconds to the next :00 mark and arms a one-shot kernel timer."""
    now = datetime.datetime.now()
    remaining = 60.0 - (now.second + now.microsecond / 1_000_000.0)
    if remaining <= 0.05:
        remaining = 60.0

    _log(f"Scheduled next minute timer in {remaining:.3f}s")
    try:
        if get_boss() is not None:
            # Arm a one-shot kernel timer (repeats=False)
            add_timer(_on_minute_tick, remaining, False)
    except Exception as e:
        _log(f"Failed to arm add_timer: {e}")


def _on_minute_tick(timer_id: int | None) -> None:
    """Executed on exact minute boundary via Linux kernel timer interrupt."""
    _log(f"Kernel timer interrupt fired (timer_id={timer_id})")
    try:
        boss = get_boss()
        if boss:
            # 1. Recompute tab bar in memory
            boss.refresh_active_tab_bar()

            # 2. Mark active window dirty and trigger GPU redraw
            w = boss.active_window
            if w:
                w.refresh()

            # 3. Mark OS window dirty for Wayland/OpenGL compositor
            for os_window_id in boss.os_window_map:
                mark_os_window_dirty(os_window_id)

            wakeup_main_loop()
            _log("Triggered tab bar refresh + OS window dirty + wakeup_main_loop")
    except Exception as e:
        _log(f"Error in _on_minute_tick: {e}")
    finally:
        # Arm the next one-shot interrupt for the upcoming minute
        _schedule_next_minute_tick()


def _ensure_auto_refresh() -> None:
    """Initializes the aligned one-shot interrupt chain on first render."""
    global _timer_registered
    if _timer_registered:
        return
    _timer_registered = True
    _log("Initializing auto-refresh kernel timer chain")
    _schedule_next_minute_tick()


# ------------------------------------------------------------------------------
# 2. Weather & Battery Data Fetchers
# ------------------------------------------------------------------------------
def _fetch_weather_async():
    def _worker():
        try:
            req = urllib.request.Request(
                "https://wttr.in/?format=%c+%t",
                headers={"User-Agent": "curl/8.0"}
            )
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = resp.read().decode("utf-8").strip()
                data = data.replace("+", "")
                with open(WEATHER_CACHE, "w", encoding="utf-8") as f:
                    f.write(data)
        except Exception:
            pass

    threading.Thread(target=_worker, daemon=True).start()


def get_weather() -> str:
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

        ac_path = os.path.join(base, "AC/online")
        if os.path.exists(ac_path):
            with open(ac_path, "r") as f:
                if f.read().strip() == "1":
                    return "󰂄 AC"
    except Exception:
        return ""
    return ""


def get_time() -> str:
    return datetime.datetime.now().strftime(" %H:%M")


# ------------------------------------------------------------------------------
# 3. Right Status Bar Renderer (Theme Inherited & Mirrored Powerline)
# ------------------------------------------------------------------------------
def _draw_right_status(screen: Screen, draw_data: DrawData) -> None:
    try:
        opts = get_options()
    except Exception:
        opts = None

    # Inherit colors directly from Kitty theme palette
    default_bg = as_rgb(int(draw_data.default_bg))
    active_bg = as_rgb(int(draw_data.active_bg))
    active_fg = as_rgb(int(draw_data.active_fg))
    inactive_bg = as_rgb(int(draw_data.inactive_bg))
    inactive_fg = as_rgb(int(draw_data.inactive_fg))

    # Palette accents if available from theme
    color_green = as_rgb(color_as_int(opts.color2)) if opts else active_bg
    color_blue = as_rgb(color_as_int(opts.color4)) if opts else inactive_bg

    def _fmt(text: str) -> str:
        # Normalize double spaces and ensure uniform padding [ icon value ]
        return f" {' '.join(text.split())} "

    # Build status widgets: (text, fg_color, bg_color)
    widgets = []

    # 1. Weather Widget (Theme Blue / Inactive Accent)
    weather = get_weather()
    if weather:
        widgets.append((_fmt(weather), inactive_fg, color_blue))

    # 2. Battery Widget (Theme Green Accent)
    battery = get_battery()
    if battery:
        widgets.append((_fmt(battery), active_fg, color_green))

    # 3. Clock Widget (Theme Active Tab Colors)
    time_str = get_time()
    widgets.append((_fmt(time_str), active_fg, active_bg))

    if not widgets:
        return

    # Mirror the left powerline separator symbol for right-aligned widgets
    # Left: '' (angled) -> Right: ''
    # Left: '' (slanted) -> Right: ''
    # Left: '' (round)   -> Right: ''
    if draw_data.powerline_style == "slanted":
        sep_symbol = ""
    elif draw_data.powerline_style == "round":
        sep_symbol = ""
    else:  # angled (default)
        sep_symbol = ""

    # Calculate total width required on screen
    total_width = 0
    for text, _, _ in widgets:
        total_width += wcswidth(text) + 1  # +1 for powerline separator

    available_space = screen.columns - screen.cursor.x
    if available_space <= total_width:
        return

    # Fill gap between left tabs and right widgets
    gap = screen.columns - total_width - screen.cursor.x
    if gap > 0:
        screen.cursor.bg = default_bg
        screen.cursor.fg = default_bg
        screen.draw(" " * gap)

    # Draw each widget capsule
    prev_bg = default_bg
    for text, fg, bg in widgets:
        # Draw mirrored powerline separator
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


# ------------------------------------------------------------------------------
# 4. Main Entry Point
# ------------------------------------------------------------------------------
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
    # Ensure aligned minute timer is armed
    _ensure_auto_refresh()

    # Draw left tab with Kitty built-in powerline function
    end = draw_tab_with_powerline(
        draw_data, screen, tab, before, max_tab_length, index, is_last, extra_data
    )

    # When the final tab is reached, draw the right status bar
    if is_last:
        _draw_right_status(screen, draw_data)

    return end


# Initialize timer when module is loaded by Kitty
_ensure_auto_refresh()
