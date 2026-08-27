# Kitty Modular Tab Bar Extension

A high-performance, modular Python extension for the [Kitty terminal](https://sw.kovidgoyal.net/kitty/) tab bar featuring declarative configuration (`tab_bar.conf`), 197+ command icons with auto-detection, universal mirrored Powerline styles (`angled`, `slanted`, `round`), dynamic theme color inheritance, and zero-polling hardware interrupt timers.

---

## ✨ Features

- **Declarative Configuration (`tab_bar.conf`)**: Centralized key-value file with full comment support (`#`) for configuring title depth, active widgets, clock formats, and custom command icons.
- **197+ Pre-Configured Nerd Font Command Icons**: Pre-mapped glyphs for languages, compilers, package managers, cloud tools, containers, editors (`nvim`, `helix`), and system utilities (`btop`, `yazi`).
- **Smart Auto-Detection & Fallback (`auto_detect_commands yes`)**: Automatically detects running CLI binaries via cached PATH lookup and prefixes ` tool: ...` without manual configuration.
- **Plug-and-Play Dynamic Widget Registry**: Reorder, enable, or disable status modules in one line via `active_widgets` in `tab_bar.conf`.
- **Dynamic Title Formatting & Path Truncation Pipeline**:
  1. *Semantic Cleanup:* Strips shell boilerplate (`admin@fedora:`), normalizes `$HOME` to `~`, and preserves interactive command glyphs (` nvim: …`, `󱘗 cargo: …`, `󰊢 git: …`).
  2. *Dynamic Depth Truncation:* Truncates deep paths to any custom directory level configured via `max_title_depth` in `tab_bar.conf` (e.g. 1, 2, 3, 4, etc.).
  3. *Space Reservation:* Dynamically calculates right status width and caps `max_tab_length` so long titles truncate with `…` without crowding status widgets.
- **Universal Symmetrical Powerline Glyphs**: Fully supports all Kitty `tab_powerline_style` settings (`angled`, `slanted`, `round`), dynamically matching forward separators (`` / `` / ``) on the left to exact inverted transitions (`` / `` / ``) and soft dividers (`` / `╱` / ``) on the right.
- **Right Status Widgets**:
  - ⛅ **Weather**: High-accuracy condition icon + temperature in Celsius (powered by **Open-Meteo** ECMWF/NOAA models).
  - 󰍛 **RAM**: Active memory footprint in GB read directly from `/proc/meminfo`.
  -  **CPU**: 1-minute kernel load average (`/proc/loadavg`) + hardware CPU package thermal sensor.
  - 󰂄 **Battery**: Real-time battery percentage and charging status read directly from Linux sysfs (`/sys/class/power_supply/`).
  -  **Clock**: Clean time (`HH:MM` or custom strftime format).
- **Dynamic Theme Palette**: Automatically inherits background, foreground, active tab, and ANSI accent colors from your current Kitty theme.
- **Normalized Capsule Padding**: Consistent `[ icon value ]` internal spacing across all widgets.
- **Zero Busy-Polling (60 wakeups/hr)**: Aligned one-shot kernel interrupt timer calculates exact fractional milliseconds to the upcoming `:00.000` minute boundary, sleeping the terminal completely when idle.

---

## 📁 Package Architecture

All modules follow the Single Responsibility Principle, with every file kept strictly under 100 lines of code:

```text
tab_bar/
├── tab_bar.conf              # Declarative user settings & 197+ command icons
├── README.md                 # This documentation
├── __init__.py               # Package marker
├── config.py                 # Stdlib parser, settings cache & fallback defaults
├── constants.py              # Paths (.cache/), timing intervals, diagnostic logger
├── title.py                  # Dynamic path truncation & icon-aware command detection
├── widgets.py                # Dynamic widget registry, theme palette extractor, width calc
├── renderer.py               # Mirrored Powerline geometry, space reservation, Kitty draw_tab hook
├── timer.py                  # Minute boundary math & aligned C-timer interrupt scheduler
├── dispatcher.py             # Multi-window compositor dirty flags & event loop wakeups
└── modules/                  # Self-contained status widget providers
    ├── __init__.py           # Widget exports
    ├── battery.py            # Linux sysfs (/sys/class/power_supply/) reader
    ├── clock.py              # Customizable Clock widget (supports strftime patterns)
    ├── cpu.py                # 1-minute load average & thermal sensor reader
    ├── ram.py                # /proc/meminfo memory reader
    └── weather/              # Modular Open-Meteo weather provider package
        ├── __init__.py       # Public get_weather() facade & cache reader
        ├── wmo.py            # WMO weather code constants to emoji mapping
        ├── geo.py            # GeoIP location resolver & coordinate cache
        └── client.py         # Async HTTP fetcher with rate limiting & circuit breakers
```

---

## ⚙️ How It Works

1. **Kitty Loader (`tab_bar.py`)**:
   Kitty evaluates `~/.config/kitty/tab_bar.py` via `tab_bar_style custom`. The entry point clears `sys.modules` for live config hot-reloading (`Ctrl + Shift + F5`), then delegates rendering to `tab_bar.renderer.draw_tab` and timer scheduling to `tab_bar.timer.init_timer`.
2. **Declarative Engine & Settings Cache (`tab_bar/config.py`)**:
   Loads `tab_bar.conf` using Python standard library, building fast $O(1)$ lookup maps for command icons, active widget arrays, and formatting parameters.
3. **Aligned Kernel Timer & Dispatcher (`tab_bar/timer.py` & `tab_bar/dispatcher.py`)**:
   Uses `kitty.fast_data_types.add_timer(..., remaining, False)` to register a native one-shot C timer into the Wayland/GLFW event loop. When the `:00.000` minute mark arrives:
   - Updates the tab bar buffer in memory (`boss.refresh_active_tab_bar()`).
   - Marks the window screen buffer as dirty (`boss.active_window.refresh()`).
   - Marks all OS window frames dirty (`mark_os_window_dirty()`).
   - Wakes the Wayland/GLFW event loop immediately (`wakeup_main_loop()`).
   - Arms the next one-shot timer for the next minute boundary.
4. **Tab Title Formatting & Icon Resolution (`tab_bar/title.py`)**:
   Cleans shell prefix boilerplate, normalizes `$HOME`, maps command glyphs (` nvim: …`), auto-detects unmapped binaries with ``, and dynamically truncates nested directory paths according to `max_title_depth`.
5. **Widget Aggregation & Rendering (`tab_bar/widgets.py` & `tab_bar/renderer.py`)**:
   Extracts current theme colors dynamically (`DrawData`), calculates column spacing, and draws right-aligned mirrored Powerline capsules matching the configured `tab_powerline_style` (`angled`, `slanted`, or `round`).

---

## ⚙️ Configuration (`tab_bar.conf`)

Edit `~/.config/kitty/tab_bar.conf` and press `Ctrl + Shift + F5` to hot-reload:

```conf
# Title settings
max_title_depth         3
auto_detect_commands    yes
default_cmd_icon        

# Active widgets pipeline (in left-to-right display order)
active_widgets          weather ram cpu battery clock

# Options
clock_format            %H:%M
weather_refresh_seconds 1800

# Command Icons
cmd_icon nvim           
cmd_icon cargo          󱘗
cmd_icon git            󰊢
cmd_icon docker         󰡨
```

---

## ➕ Adding a New Status Widget

1. **Create your widget file** in `tab_bar/modules/my_widget.py`:
   ```python
   def get_my_status() -> str:
       return "󰍛 4.2G"
   ```
2. **Export it** in `tab_bar/modules/__init__.py`:
   ```python
   from tab_bar.modules.my_widget import get_my_status
   __all__ = [..., "get_my_status"]
   ```
3. **Register it** in `tab_bar/widgets.py`:
   ```python
   WIDGET_REGISTRY["my_widget"] = (get_my_status, "inactive")
   ```
4. **Enable it** in `tab_bar.conf`:
   ```conf
   active_widgets weather ram cpu my_widget battery clock
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
