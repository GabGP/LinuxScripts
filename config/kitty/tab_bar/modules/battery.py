# ==============================================================================
#  config/kitty/tab_bar/modules/battery.py - Battery & AC Power Supply Reader
# ==============================================================================

import os


def get_battery() -> str:
    """Reads Linux sysfs power supply for capacity and charging status."""
    try:
        base = "/sys/class/power_supply"
        if not os.path.exists(base):
            return ""

        for d in os.listdir(base):
            if d.startswith("BAT"):
                cap_path = os.path.join(base, d, "capacity")
                stat_path = os.path.join(base, d, "status")
                if os.path.exists(cap_path):
                    with open(cap_path, "r", encoding="utf-8") as f:
                        cap = int(f.read().strip())
                    stat = ""
                    if os.path.exists(stat_path):
                        with open(stat_path, "r", encoding="utf-8") as f:
                            stat = f.read().strip().lower()

                    is_charging = "charging" in stat
                    if is_charging:
                        icon = "󰂄"
                    elif cap >= 90:
                        icon = "󰁹"
                    elif cap >= 70:
                        icon = "󰂁"
                    elif cap >= 50:
                        icon = "󰁿"
                    elif cap >= 30:
                        icon = "󰁽"
                    elif cap >= 15:
                        icon = "󰁻"
                    else:
                        icon = "󰁺"
                    return f"{icon} {cap}%"

        # Fallback to AC status if no BAT directory found
        ac_path = os.path.join(base, "AC/online")
        if os.path.exists(ac_path):
            with open(ac_path, "r", encoding="utf-8") as f:
                if f.read().strip() == "1":
                    return "󰂄 AC"
    except Exception:
        return ""
    return ""
