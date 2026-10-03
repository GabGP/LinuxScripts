# ==============================================================================
#  config/kitty/tab_bar/modules/weather/geo.py - GeoIP Location Resolver
# ==============================================================================

import json
import os
import urllib.request

from tab_bar.config import CONFIG
from tab_bar.constants import GEO_CACHE


def get_coordinates() -> tuple[float, float] | None:
    """Retrieves configured GPS coordinates, cached coordinates, or resolves via GeoIP."""
    # 1. Manual coordinate override from tab_bar.conf
    if CONFIG.weather_lat is not None and CONFIG.weather_lon is not None:
        return CONFIG.weather_lat, CONFIG.weather_lon

    # 2. Disk cache lookup
    try:
        if os.path.exists(GEO_CACHE):
            with open(GEO_CACHE, "r", encoding="utf-8") as f:
                parts = f.read().strip().split(",")
                if len(parts) == 2:
                    return float(parts[0]), float(parts[1])

        # 3. Dynamic GeoIP resolution via HTTPS
        urls = ["https://ip-api.com/json/", "http://ip-api.com/json/"]
        for url in urls:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
                with urllib.request.urlopen(req, timeout=3.0) as resp:
                    geo = json.loads(resp.read().decode("utf-8"))
                    lat, lon = float(geo["lat"]), float(geo["lon"])
                    with open(GEO_CACHE, "w", encoding="utf-8") as f:
                        f.write(f"{lat},{lon}")
                    return lat, lon
            except Exception:
                continue
    except Exception:
        pass

    return None
