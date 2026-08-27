# ==============================================================================
#  config/kitty/tab_bar/modules/weather/__init__.py - Weather Provider Facade
# ==============================================================================

import datetime
import os

from tab_bar.constants import WEATHER_CACHE, WEATHER_REFRESH_SECONDS
from tab_bar.modules.weather.client import fetch_weather_async


def get_weather() -> str:
    """Reads cached Open-Meteo weather or triggers background refresh."""
    try:
        if os.path.exists(WEATHER_CACHE):
            mtime = os.path.getmtime(WEATHER_CACHE)
            if datetime.datetime.now().timestamp() - mtime < WEATHER_REFRESH_SECONDS:
                with open(WEATHER_CACHE, "r", encoding="utf-8") as f:
                    return f.read().strip()
            else:
                fetch_weather_async()
                with open(WEATHER_CACHE, "r", encoding="utf-8") as f:
                    return f.read().strip()
        else:
            fetch_weather_async()
            return "⛅ --°C"
    except Exception:
        return "⛅ --°C"


__all__ = ["get_weather"]
