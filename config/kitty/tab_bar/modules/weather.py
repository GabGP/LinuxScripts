# ==============================================================================
#  config/kitty/tab_bar/modules/weather.py - Asynchronous Cached Weather Provider
# ==============================================================================

import datetime
import os
import threading
import urllib.request

from tab_bar.constants import WEATHER_CACHE, WEATHER_REFRESH_SECONDS


def _fetch_weather_async() -> None:
    """Fetches weather from wttr.in asynchronously to prevent terminal lag."""
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
    """Reads cached weather or triggers background refresh."""
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
