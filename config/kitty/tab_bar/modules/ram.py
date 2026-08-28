# ==============================================================================
#  config/kitty/tab_bar/modules/ram.py - RAM Memory Telemetry Reader
# ==============================================================================


from tab_bar.registry import register_widget


@register_widget("ram", style="inactive")
def get_ram() -> str:
    """Reads Linux /proc/meminfo for memory usage in Gigabytes."""
    try:
        total, avail = 0, 0
        with open("/proc/meminfo", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    total = int(line.split()[1])
                elif line.startswith("MemAvailable:"):
                    avail = int(line.split()[1])

        if total > 0:
            used_gb = (total - avail) / 1048576  # 1024 * 1024 kB = 1 GB
            return f"󰍛 {used_gb:.1f}G"
    except Exception:
        pass
    return ""
