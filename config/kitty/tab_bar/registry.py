# ==============================================================================
#  config/kitty/tab_bar/registry.py - Plug-and-Play Widget Registry & Loader
# ==============================================================================

import importlib
import pkgutil
from typing import Callable

# Registry mapping widget name -> (getter_function, style_mode)
# "inactive": uses inactive tab background/foreground palette
# "active": uses active tab accent palette
WIDGET_REGISTRY: dict[str, tuple[Callable[[], str | None], str]] = {}


def register_widget(name: str, style: str = "inactive") -> Callable:
    """Decorator to register a status widget provider function."""
    def decorator(fn: Callable[[], str | None]) -> Callable[[], str | None]:
        WIDGET_REGISTRY[name.strip().lower()] = (fn, style)
        return fn
    return decorator


def discover_and_load_widgets() -> None:
    """Auto-discovers and imports all status modules under tab_bar.modules."""
    try:
        import tab_bar.modules as modules_pkg
        for _, mod_name, _ in pkgutil.iter_modules(modules_pkg.__path__, modules_pkg.__name__ + "."):
            try:
                importlib.import_module(mod_name)
            except Exception:
                pass
    except Exception:
        pass
