# likemodas/account/__init__.py (CORREGIDO)

from . import page
from . import shipping_info
from .layout import account_layout
from .sidebar import account_sidebar
from . import display_settings_page # <-- AÑADE ESTA LÍNEA

# Se eliminan las exportaciones de los estados antiguos.
__all__ = [
    "page", 
    "shipping_info", 
    "account_layout", 
    "account_sidebar",
    "display_settings_page", # <-- AÑADE ESTA LÍNEA
]