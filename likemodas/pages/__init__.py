# likemodas/pages/__init__.py

from .about import about_page
from .dashboard import dashboard_component
from .landing import landing_component
from .pricing import pricing_page
from .protected import protected_page
from . import search_results
# --- 👇 AÑADE ESTA LÍNEA DE IMPORTACIÓN 👇 ---
from . import category_page


__all__ = [ 
    'about_page',
    'dashboard_component',
    'landing_component',
    'pricing_page',
    'protected_page',
    'search_results',
    # --- 👇 Y AÑADE ESTA LÍNEA AQUÍ TAMBIÉN 👇 ---
    'category_page'
]