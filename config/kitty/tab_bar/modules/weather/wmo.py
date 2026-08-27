# ==============================================================================
#  config/kitty/tab_bar/modules/weather/wmo.py - WMO Weather Code Mappings
# ==============================================================================

# WMO Weather interpretation codes (WW)
# https://open-meteo.com/en/docs
WMO_ICONS: dict[int, str] = {
    0: "☀️",           # Clear sky
    1: "🌤️", 2: "⛅",   # Mainly clear, partly cloudy
    3: "☁️",           # Overcast
    45: "🌫️", 48: "🌫️",  # Fog, depositing rime fog
    51: "🌦️", 53: "🌦️", 55: "🌦️",  # Drizzle: Light, moderate, dense
    56: "🌨️", 57: "🌨️",             # Freezing Drizzle
    61: "🌧️", 63: "🌧️", 65: "🌧️",   # Rain: Slight, moderate, heavy
    66: "🌨️", 67: "🌨️",             # Freezing Rain
    71: "❄️", 73: "❄️", 75: "❄️", 77: "❄️",  # Snow fall & snow grains
    80: "🌧️", 81: "🌧️", 82: "🌧️",   # Rain showers: Slight, moderate, violent
    85: "🌨️", 86: "🌨️",             # Snow showers
    95: "⛈️", 96: "⛈️", 99: "⛈️",   # Thunderstorm
}


def get_wmo_icon(code: int) -> str:
    """Returns the matching emoji icon for a WMO weather interpretation code."""
    return WMO_ICONS.get(code, "⛅")
