# -----------------------------------------------------------------------------
# likemodas/navigation/__init__.py
# -----------------------------------------------------------------------------
from . import routes
from .state import NavState
# ✨ CAMBIO: Se importa y exporta el nuevo nombre del estado.

__all__ = [
    "routes",
    "NavState",
]