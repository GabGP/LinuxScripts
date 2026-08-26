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


_fetch_lock = threading.Lock()
_is_fetching = False
_last_fetch_attempt: float = 0.0
_cooldown_seconds: float = 0.0  # Dynamic backoff on failure / 429


def _get_coordinates() -> tuple[float, float] | None:
    """Retrieves cached GPS coordinates or resolves them via GeoIP lookup."""
    try:
        if os.path.exists(GEO_CACHE):
            with open(GEO_CACHE, "r", encoding="utf-8") as f:
                parts = f.read().strip().split(",")
                if len(parts) == 2:
                    return float(parts[0]), float(parts[1])

        # Resolve location via GeoIP (cached permanently in GEO_CACHE)
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
    """Fetches weather data asynchronously with rate-limiting & backoff guardrails."""
    global _is_fetching, _last_fetch_attempt, _cooldown_seconds

    now = datetime.datetime.now().timestamp()
    # Guardrail 1: Rate limit protection & minimum cooldown
    if _is_fetching or (now - _last_fetch_attempt < max(60.0, _cooldown_seconds)):
        return

    # Guardrail 2: Thread stampede lock
    with _fetch_lock:
        if _is_fetching:
            return
        _is_fetching = True
        _last_fetch_attempt = now

    def _worker():
        global _is_fetching, _cooldown_seconds
        try:
            coords = _get_coordinates()
            if not coords:
                _cooldown_seconds = 300.0  # Back off 5 min if geo lookup fails
                return
            lat, lon = coords

            url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code"
            )
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "curl/8.0 (Kitty TabBar Widget)"}
            )
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                current = data.get("current", {})
                temp = round(current.get("temperature_2m", 0))
                code = current.get("weather_code", 0)
                icon = WMO_ICONS.get(code, "⛅")

                with open(WEATHER_CACHE, "w", encoding="utf-8") as f:
                    f.write(f"{icon} {temp}°C")

                # Reset cooldown on successful fetch
                _cooldown_seconds = 0.0
        except urllib.error.HTTPError as e:
            # Guardrail 3: HTTP 429 / Error Circuit Breaker
            if e.code == 429:
                _cooldown_seconds = 3600.0  # 1 hour backoff on 429 Too Many Requests
            else:
                _cooldown_seconds = 300.0   # 5 min backoff on other HTTP errors
        except Exception:
            # Guardrail 4: Offline / Network Timeout Backoff (prevents hammering network)
            _cooldown_seconds = 300.0
        finally:
            _is_fetching = False

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
