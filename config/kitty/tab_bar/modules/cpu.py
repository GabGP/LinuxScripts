# ==============================================================================
#  config/kitty/tab_bar/modules/cpu.py - CPU Load Average & Thermal Reader
# ==============================================================================

import os
from tab_bar.registry import register_widget


@register_widget("cpu", style="inactive")
def get_cpu() -> str:
    """Reads Linux 1-minute load average and hardware CPU thermal sensor."""
    try:
        load_str = ""
        with open("/proc/loadavg", "r", encoding="utf-8") as f:
            load_str = f.read().split()[0]

        temp_c = None
        base = "/sys/class/thermal"
        if os.path.exists(base):
            for d in os.listdir(base):
                if d.startswith("thermal_zone"):
                    tfile = os.path.join(base, d, "type")
                    valfile = os.path.join(base, d, "temp")
                    if os.path.exists(tfile) and os.path.exists(valfile):
                        with open(tfile, "r", encoding="utf-8") as f:
                            sensor_type = f.read().strip()
                        if sensor_type in (
                            "x86_pkg_temp",
                            "coretemp",
                            "cpu-thermal",
                            "k10temp",
                        ):
                            with open(valfile, "r", encoding="utf-8") as f:
                                temp_c = int(f.read().strip()) // 1000
                            break

            # Fallback to thermal_zone0 if specific CPU sensor not identified
            if temp_c is None and os.path.exists("/sys/class/thermal/thermal_zone0/temp"):
                with open("/sys/class/thermal/thermal_zone0/temp", "r", encoding="utf-8") as f:
                    temp_c = int(f.read().strip()) // 1000

        if temp_c is not None:
            return f" {load_str}  {temp_c}°C"
        return f" {load_str}"
    except Exception:
        pass
    return ""
