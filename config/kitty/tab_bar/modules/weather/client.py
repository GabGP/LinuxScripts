# ==============================================================================
#  config/kitty/tab_bar/modules/weather/client.py - Async Open-Meteo Client
# ==============================================================================

import datetime
import json
import threading
import urllib.error
import urllib.request

from tab_bar.constants import WEATHER_CACHE
from tab_bar.modules.weather.geo import get_coordinates
from tab_bar.modules.weather.wmo import get_wmo_icon

_fetch_lock = threading.Lock()
_is_fetching = False
_last_fetch_attempt: float = 0.0
_cooldown_seconds: float = 0.0  # Dynamic backoff on failure / 429


def fetch_weather_async() -> None:
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
            coords = get_coordinates()
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
                icon = get_wmo_icon(code)

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
