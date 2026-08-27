# ==============================================================================
#  config/kitty/tab_bar/dispatcher.py - Compositor & Event Loop Dispatcher
# ==============================================================================

from kitty.fast_data_types import get_boss, mark_os_window_dirty, wakeup_main_loop
from tab_bar.constants import log_diag


def dispatch_tab_refresh() -> None:
    """Dispatches dirty redraw signals to Kitty's Wayland/GLFW window compositor."""
    boss = get_boss()
    if boss is None:
        return

    try:
        # 1. Recompute tab bar in memory
        boss.refresh_active_tab_bar()

        # 2. Mark active window dirty and trigger GPU redraw
        w = boss.active_window
        if w:
            w.refresh()

        # 3. Mark OS window dirty for Wayland/OpenGL compositor
        for os_window_id in boss.os_window_map:
            mark_os_window_dirty(os_window_id)

        # 4. Wake main event loop
        wakeup_main_loop()
        log_diag("Triggered tab bar refresh + OS window dirty + wakeup_main_loop")
    except Exception as e:
        log_diag(f"Error in dispatch_tab_refresh: {e}")
