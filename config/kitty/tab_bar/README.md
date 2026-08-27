# Kitty Modular Tab Bar Extension

A high-performance, modular Python extension for the [Kitty terminal](https://sw.kovidgoyal.net/kitty/) tab bar featuring mirrored Powerline capsules, dynamic theme color inheritance, and zero-polling hardware interrupt timers.

---

## ✨ Features

- **Left Tabs**: Native Powerline angled/slanted tabs driven by `tab_powerline_style` in `kitty.conf`.
- **3-Level Path Truncation**: Automatically trims left tab titles to at most 3 directory levels (`…/kitty/tab_bar/modules`), strips shell boilerplate (`admin@fedora:`), normalizes `$HOME` to `~`, and preserves interactive command prefixes (`nvim: …`, `cargo: …`, `git: …`).
- **Right Status Widgets**:
  - ⛅ **Weather**: High-accuracy condition icon + temperature in Celsius (powered by **Open-Meteo** ECMWF/NOAA models).
  - 󰍛 **RAM**: Active memory footprint in GB read directly from `/proc/meminfo`.
  -  **CPU**: 1-minute kernel load average (`/proc/loadavg`) + hardware CPU package thermal sensor.
  - 󰂄 **Battery**: Real-time battery percentage and charging status read directly from Linux sysfs (`/sys/class/power_supply/`).
  -  **Clock**: Clean 24-hour time (`HH:MM`).
- **Dynamic Theme Palette**: Automatically inherits background, foreground, active tab, and ANSI accent colors from your current Kitty theme.
- **Symmetrical Mirrored Glyphs**: Matches forward Powerline separators (`` / ``) on the left to exact inverted separators (`` / ``) on the right.
- **Normalized Capsule Padding**: Consistent `[ icon value ]` internal spacing across all widgets.
- **Zero Busy-Polling (60 wakeups/hr)**: Aligned one-shot kernel interrupt timer calculates exact fractional milliseconds to the upcoming `:00.000` minute boundary, sleeping the terminal completely when idle.

---

## 📁 Package Architecture

```text
tab_bar/
├── README.md             # This documentation
├── __init__.py           # Package marker
├── constants.py          # Paths (.cache/), timing intervals, diagnostic logger
├── timer.py              # Kernel interrupt scheduler, stale timer purger, frame dispatcher
├── renderer.py           # Mirrored Powerline geometry, palette extractor, capsule drawer
└── modules/              # Self-contained status widget providers
    ├── __init__.py       # Widget exports
    ├── battery.py        # Linux sysfs (/sys/class/power_supply/) reader
    ├── clock.py          # 24h Clock widget
    ├── cpu.py            # 1-minute load average & thermal reader
    ├── ram.py            # /proc/meminfo memory reader
    └── weather.py        # Asynchronous Open-Meteo weather provider
```

---

## ⚙️ How It Works

1. **Kitty Loader (`tab_bar.py`)**:
   Kitty evaluates `~/.config/kitty/tab_bar.py` via `tab_bar_style custom`. The entry point clears `sys.modules` for hot reloading and delegates rendering to `tab_bar.renderer.draw_tab` and timer scheduling to `tab_bar.timer.init_timer`.
2. **Aligned Kernel Timer (`tab_bar/timer.py`)**:
   Uses `kitty.fast_data_types.add_timer(..., remaining, False)` to register a native one-shot C timer into the Wayland/GLFW event loop. When the `:00.000` minute mark arrives:
   - Updates the tab bar buffer in memory (`boss.refresh_active_tab_bar()`).
   - Marks the window screen buffer as dirty (`boss.active_window.refresh()`).
   - Marks the OS window frame dirty (`mark_os_window_dirty()`).
   - Wakes the Wayland/GLFW event loop immediately (`wakeup_main_loop()`).
   - Arms the next one-shot timer for the next minute boundary.
3. **Widget Rendering (`tab_bar/renderer.py`)**:
   Calculates terminal columns via `screen.columns` and `wcswidth`, drawing right-aligned mirrored Powerline capsules with crisp bold formatting.

---

## ➕ Adding a New Widget

Adding a new status widget is simple:

1. **Create your widget file** in `tab_bar/modules/my_widget.py`:
   ```python
   def get_status() -> str:
       return "󰍛 4.2G"
   ```
2. **Export it** in `tab_bar/modules/__init__.py`:
   ```python
   from tab_bar.modules.my_widget import get_status
   __all__ = [..., "get_status"]
   ```
3. **Add to the render list** in `tab_bar/renderer.py`:
   ```python
   my_data = get_status()
   if my_data:
       widgets.append((_fmt(my_data), fg_color, bg_color))
   ```

---

## 🔍 Diagnostics & Debugging

Diagnostic logs are saved to `.cache/tabbar.log` (gitignored). To observe live kernel interrupt events in real time:

```bash
tail -f .cache/tabbar.log
```

Expected log output (1 heartbeat per minute):
```text
[06:00:00.001] Kernel timer interrupt fired (timer_id=2270) for minute 06:00
[06:00:00.003] Triggered tab bar refresh + OS window dirty + wakeup_main_loop
[06:00:00.003] Scheduled next minute timer in 59.997s
```
