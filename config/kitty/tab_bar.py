# ==============================================================================
#  Kitty Custom Tab Bar Extension (Main Entry Point)
# ==============================================================================
#  - Left: Powerline tabs matching kitty.conf style (angled / slanted / round)
#  - Right: Live status widgets (Weather, Battery, Clock)
#  - Timer: Aligned One-Shot Kernel Interrupt Timer (60 wakeups per hour)
#  - Architecture: Modular package under ~/.config/kitty/tab_bar/
# ==============================================================================

import os
import sys

# Ensure tab_bar package directory is in sys.path (supports direct and symlink loads)
_CURRENT_DIR = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
if _CURRENT_DIR not in sys.path:
    sys.path.insert(0, _CURRENT_DIR)

from tab_bar.renderer import draw_tab  # noqa: F401 (Loaded by Kitty)
from tab_bar.timer import init_timer

# Initialize the aligned kernel timer chain when module is loaded by Kitty
init_timer()
