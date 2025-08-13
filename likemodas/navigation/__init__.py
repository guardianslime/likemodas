# likemodas/navigation/__init__.py (CORREGIDO)

from . import routes

# Ya no se exporta NavState porque fue fusionado en AppState.
# Los métodos de navegación se llaman directamente desde AppState.
__all__ = [
    "routes",
]
