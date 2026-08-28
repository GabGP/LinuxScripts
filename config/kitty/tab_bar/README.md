# Kitty Modular Tab Bar Extension

A high-performance, modular Python extension for the [Kitty terminal](https://sw.kovidgoyal.net/kitty/) tab bar featuring declarative configuration (`tab_bar.conf`), 197+ command icons with auto-detection, plug-and-play auto-discovery widget architecture, universal mirrored Powerline styles (`angled`, `slanted`, `round`), dynamic theme color inheritance, and zero-polling hardware interrupt timers.

---

## ✨ Features

- **Declarative Configuration (`tab_bar.conf`)**: Centralized key-value file with full comment support (`#`) for configuring title depth, active widgets, clock formats, weather coordinates, and custom command icons.
- **Plug-and-Play Widget Auto-Discovery**: Add new status modules by dropping a single file in `tab_bar/modules/` with the `@register_widget` decorator without modifying core package files.
- **197+ Pre-Configured Nerd Font Command Icons**: Pre-mapped glyphs for languages, compilers, package managers, cloud tools, containers, editors (`nvim`, `helix`), and system utilities (`btop`, `yazi`). Supports full binary paths (`/usr/bin/nvim`) and elevated wrappers (`sudo`, `doas`).
- **Smart Auto-Detection & Fallback (`auto_detect_commands yes`)**: Automatically detects running CLI binaries via cached PATH lookup and prefixes ` tool: ...` without manual configuration.
- **Dynamic Title Formatting & Path Truncation Pipeline**:
  1. *Semantic Cleanup:* Strips shell boilerplate (`admin@fedora:`), normalizes `$HOME` to `~`, and preserves interactive command glyphs (` nvim: …`, `󱘗 cargo: …`, `󰊢 git: …`).
  2. *Dynamic Depth Truncation:* Truncates deep paths to any custom directory level configured via `max_title_depth` in `tab_bar.conf` (e.g. 1, 2, 3, 4, etc.).
  3. *Space Reservation:* Dynamically calculates right status width and caps `max_tab_length` so long titles truncate with `…` without crowding status widgets.
- **Universal Symmetrical Powerline Glyphs**: Fully supports all Kitty `tab_powerline_style` settings (`angled`, `slanted`, `round`), dynamically matching forward separators (`` / `` / ``) on the left to exact inverted transitions (`` / `` / ``) and soft dividers (`` / `╱` / ``) on the right.
- **Right Status Widgets**:
  - ⛅ **Weather**: High-accuracy condition icon + temperature in Celsius (powered by **Open-Meteo** ECMWF/NOAA models). Supports manual coordinate override (`weather_lat`, `weather_lon`) or automatic HTTPS GeoIP resolution.
  - 󰍛 **RAM**: Active memory footprint in GB read directly from `/proc/meminfo`.
  -  **CPU**: 1-minute kernel load average (`/proc/loadavg`) + hardware CPU package thermal sensor.
  - 󰂄 **Battery**: Real-time battery percentage and charging status read directly from Linux sysfs (`/sys/class/power_supply/`).
  -  **Clock**: Clean time (`HH:MM` or custom strftime format).
- **Frame-Scoped Render Memoization**: Caches telemetry evaluations per render frame to eliminate redundant `/proc` and `/sys` disk I/O when redrawing multi-tab sessions.
- **Dynamic Theme Palette**: Automatically inherits background, foreground, active tab, and ANSI accent colors from your current Kitty theme.
- **Zero Busy-Polling (60 wakeups/hr)**: Aligned one-shot kernel interrupt timer calculates exact fractional milliseconds to the upcoming `:00.000` minute boundary, sleeping the terminal completely when idle.

---

## 📁 Package Architecture

All modules follow the Single Responsibility Principle, with every file kept strictly under 100 lines of code:

```text
config/kitty/
├── kitty.conf                # Main terminal configuration
├── current-theme.conf        # Active theme managed by Kitty theme switcher
├── tab_bar.conf              # Declarative user settings & 197+ command icons
├── tab_bar.py                # Entry point with live reload cache eviction
├── themes/                   # Custom theme preset catalog
│   ├── dimidium.conf
│   └── kokiri_dark.conf
└── tab_bar/                  # Modular Python status bar package (< 100 LoC per file)
    ├── README.md             # This documentation
    ├── __init__.py           # Package marker
    ├── registry.py           # Plug-and-play @register_widget decorator & auto-discovery
    ├── config.py             # Stdlib parser, settings cache & fallback defaults
    ├── constants.py          # Paths (.cache/), timing intervals, auto-rotated logger
    ├── title.py              # Dynamic path truncation & icon-aware command detection
    ├── widgets.py            # Widget pipeline, theme palette extractor, frame memoizer
    ├── renderer.py           # Mirrored Powerline geometry, space reservation, Kitty hook
    ├── timer.py              # Minute boundary math & aligned C-timer interrupt scheduler
    ├── dispatcher.py         # Multi-window compositor dirty flags & event loop wakeups
    └── modules/              # Self-contained status widget providers
        ├── __init__.py       # Provider exports
        ├── battery.py        # Linux sysfs (/sys/class/power_supply/) reader
        ├── clock.py          # Customizable Clock widget (supports strftime patterns)
        ├── cpu.py            # 1-minute load average & thermal sensor reader
        ├── ram.py            # /proc/meminfo memory reader
        └── weather/          # Modular Open-Meteo weather provider package
            ├── __init__.py   # Public get_weather() facade & cache reader
            ├── wmo.py        # WMO weather code constants to emoji mapping
            ├── geo.py        # GeoIP location resolver & coordinate cache
            └── client.py     # Async HTTP fetcher with rate limiting & circuit breakers
```

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

# Optional manual GPS coordinates (e.g. 52.5200, 13.4050 for Berlin, overrides GeoIP)
# weather_lat           52.5200
# weather_lon           13.4050

# Diagnostic Logging (auto-rotated at 512KB to .cache/tab_bar.log)
enable_logging          no

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
   from tab_bar.registry import register_widget

   @register_widget("my_widget", style="inactive")
   def get_my_status() -> str:
       return "󰍛 4.2G"
   ```
2. **Enable it** in `tab_bar.conf`:
   ```conf
   active_widgets weather ram cpu my_widget battery clock
   ```
*The auto-discovery engine loads your module on startup without touching any other files.*

---

## 🔍 Diagnostics & Debugging

To enable diagnostic logging, set `enable_logging yes` in `tab_bar.conf` and hot-reload with `Ctrl + Shift + F5`. Logs are saved to `.cache/tab_bar.log` (gitignored) and automatically rotate at 512 KB:

```bash
tail -f .cache/tab_bar.log
```

Expected log output (1 heartbeat per minute):
```text
[06:00:00.001] Kernel timer interrupt fired (timer_id=2270) for minute 06:00
[06:00:00.003] Triggered tab bar refresh + OS window dirty + wakeup_main_loop
[06:00:00.003] Scheduled next minute timer in 59.997s
```
