# ==============================================================================
#  config/kitty/tab_bar/timer.py - Aligned One-Shot Kernel Interrupt Timer
# ==============================================================================

import datetime

from kitty.fast_data_types import add_timer, get_boss, remove_timer
from tab_bar.constants import log_diag
from tab_bar.dispatcher import dispatch_tab_refresh


def _purge_stale_timers(keep_id: int | None = None) -> None:
    """Explicitly cancels all zombie timer IDs from previous config reloads."""
    boss = get_boss()
    if boss is None:
        return

    max_id = (keep_id + 500) if keep_id is not None else 5000
    for tid in range(1, max_id):
        if tid != keep_id:
            try:
                remove_timer(tid)
            except Exception:
                pass


def _schedule_next_minute_tick() -> None:
    """Calculates exact milliseconds to the next :00 mark and arms a single one-shot kernel timer."""
    boss = get_boss()
    if boss is None:
        return

    now = datetime.datetime.now()
    remaining = 60.0 - (now.second + now.microsecond / 1_000_000.0)
    if remaining <= 0.05:
        remaining = 60.0

    log_diag(f"Scheduled next minute timer in {remaining:.3f}s")
    try:
        new_timer = add_timer(_on_minute_tick, remaining, False)
        boss._custom_tabbar_timer_id = new_timer
        _purge_stale_timers(keep_id=new_timer)
    except Exception as e:
        log_diag(f"Failed to arm add_timer: {e}")


def _on_minute_tick(timer_id: int | None) -> None:
    """Executed on exact minute boundary via Linux kernel timer interrupt."""
    boss = get_boss()
    if boss is None:
        return

    now = datetime.datetime.now()
    current_minute = now.hour * 60 + now.minute

    last_minute = getattr(boss, "_custom_tabbar_last_tick_minute", -1)
    active_id = getattr(boss, "_custom_tabbar_timer_id", None)

    # Deduplication guard: kill duplicate or stale timers
    if last_minute == current_minute or (active_id is not None and active_id != timer_id):
        log_diag(f"Pruned duplicate/stale timer (id={timer_id}) for minute {current_minute}")
        if timer_id is not None:
            try:
                remove_timer(timer_id)
            except Exception:
                pass
        return

    boss._custom_tabbar_last_tick_minute = current_minute
    log_diag(f"Kernel timer interrupt fired (timer_id={timer_id}) for minute {now.strftime('%H:%M')}")

    # Dispatch compositor and tab bar refresh
    dispatch_tab_refresh()

    # Arm strictly ONE single next timer for the upcoming minute
    _schedule_next_minute_tick()


def init_timer() -> None:
    """Initializes the aligned one-shot interrupt chain."""
    log_diag("Initializing auto-refresh kernel timer chain")
    _schedule_next_minute_tick()
