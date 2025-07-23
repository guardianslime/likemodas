# likemodas/pages/__init__.py

from .about import about_page
from .dashboard import dashboard_component
from .landing import landing_component
from .pricing import pricing_page
from .protected import protected_page
from . import search_results
# --- 👇 DESCOMENTA ESTA LÍNEA 👇 ---
from . import category_page
from . import test_page


__all__ = [
    'about_page',
    'dashboard_component',
    'landing_component',
    'pricing_page',
    'protected_page',
    'search_results',
    # --- 👇 Y DESCOMENTA ESTA LÍNEA TAMBIÉN 👇 ---
    'category_page',
    'test_page'
]