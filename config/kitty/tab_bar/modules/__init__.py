# ==============================================================================
#  config/kitty/tab_bar/modules/__init__.py - Widget Provider Exports
# ==============================================================================

from tab_bar.modules.battery import get_battery
from tab_bar.modules.clock import get_time
from tab_bar.modules.cpu import get_cpu
from tab_bar.modules.ram import get_ram
from tab_bar.modules.weather import get_weather

__all__ = ["get_battery", "get_clock", "get_cpu", "get_ram", "get_time", "get_weather"]
