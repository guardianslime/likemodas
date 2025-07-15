# full_stack_python/navigation/__init__.py (CÓDIGO CORREGIDO)

from . import routes
from .state import NavState
# ✨ CAMBIO: Se importa y exporta el nuevo nombre del estado.
from .device import NavDeviceState

__all__ = [
    "routes",
    "NavState",
    "NavDeviceState",
]