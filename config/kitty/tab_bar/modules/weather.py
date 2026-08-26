# ==============================================================================
#  config/kitty/tab_bar/modules/weather.py - Open-Meteo Weather Provider
# ==============================================================================

import datetime
import json
import os
import threading
import urllib.request

from tab_bar.constants import GEO_CACHE, WEATHER_CACHE, WEATHER_REFRESH_SECONDS

# WMO Weather interpretation codes (WW)
# https://open-meteo.com/en/docs
WMO_ICONS: dict[int, str] = {
    0: "☀️",          # Clear sky
    1: "🌤️", 2: "⛅",  # Mainly clear, partly cloudy
    3: "☁️",          # Overcast
    45: "🌫️", 48: "🌫️", # Fog, depositing rime fog
    51: "🌦️", 53: "🌦️", 55: "🌦️",  # Drizzle: Light, moderate, dense
    56: "🌨️", 57: "🌨️",            # Freezing Drizzle
    61: "🌧️", 63: "🌧️", 65: "🌧️",  # Rain: Slight, moderate, heavy
    66: "🌨️", 67: "🌨️",            # Freezing Rain
    71: "❄️", 73: "❄️", 75: "❄️", 77: "❄️",  # Snow fall & snow grains
    80: "🌧️", 81: "🌧️", 82: "🌧️",  # Rain showers: Slight, moderate, violent
    85: "🌨️", 86: "🌨️",            # Snow showers
    95: "⛈️", 96: "⛈️", 99: "⛈️",  # Thunderstorm
}


def _get_coordinates() -> tuple[float, float] | None:
    """Retrieves cached GPS coordinates or resolves them via GeoIP lookup."""
    try:
        if os.path.exists(GEO_CACHE):
            with open(GEO_CACHE, "r", encoding="utf-8") as f:
                parts = f.read().strip().split(",")
                if len(parts) == 2:
                    return float(parts[0]), float(parts[1])

        # Resolve location via GeoIP
        req = urllib.request.Request(
            "http://ip-api.com/json/",
            headers={"User-Agent": "curl/8.0"}
        )
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            geo = json.loads(resp.read().decode("utf-8"))
            lat, lon = float(geo["lat"]), float(geo["lon"])
            with open(GEO_CACHE, "w", encoding="utf-8") as f:
                f.write(f"{lat},{lon}")
            return lat, lon
    except Exception:
        return None


def _fetch_weather_async() -> None:
    """Fetches high-accuracy weather data asynchronously from Open-Meteo."""
    def _worker():
        try:
            coords = _get_coordinates()
            if not coords:
                return
            lat, lon = coords

            url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code"
            )
            req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                current = data.get("current", {})
                temp = round(current.get("temperature_2m", 0))
                code = current.get("weather_code", 0)
                icon = WMO_ICONS.get(code, "⛅")

                with open(WEATHER_CACHE, "w", encoding="utf-8") as f:
                    f.write(f"{icon} {temp}°C")
        except Exception:
            pass

    threading.Thread(target=_worker, daemon=True).start()


def get_weather() -> str:
    """Reads cached Open-Meteo weather or triggers background refresh."""
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
