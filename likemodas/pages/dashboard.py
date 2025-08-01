# ============================================================================
# likemodas/pages/dashboard.py (CORRECCIÓN CRÍTICA APLICADA)
# ============================================================================
import reflex as rx 
# --- ✅ SOLUCIÓN: Se cambia la importación para que sea directa. ---
# En lugar de importar desde '..blog.page', se importa directamente desde
# la ubicación original del componente para evitar problemas de importación circular
# y de resolución de dependencias durante la compilación.
from ..ui.components import product_gallery_component
from ..cart.state import CartState

def dashboard_component() -> rx.Component:
    """Componente del dashboard que muestra los productos destacados."""
    return rx.box(
        rx.heading("Bienvenido de regreso", size='2'),
        rx.divider(margin_top='1em', margin_bottom='1em'),
        # Esta línea ahora funcionará porque la importación es directa y clara.
        product_gallery_component(posts=CartState.dashboard_posts),
        min_height="85vh",
    )