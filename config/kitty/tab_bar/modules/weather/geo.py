# ==============================================================================
#  config/kitty/tab_bar/modules/weather/geo.py - GeoIP Location Resolver
# ==============================================================================

import json
import os
import urllib.request

from tab_bar.constants import GEO_CACHE


def get_coordinates() -> tuple[float, float] | None:
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
