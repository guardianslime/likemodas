# ============================================================================
# likemodas/pages/dashboard.py (CORRECCIÓN CRÍTICA APLICADA)
# ============================================================================
import reflex as rx 
from ..ui.components import product_gallery_component
from ..cart.state import CartState

def dashboard_component() -> rx.Component:
    """Componente del dashboard que muestra los productos destacados."""
    return rx.box(
        rx.heading("Bienvenido de regreso", size='2'),
        rx.divider(margin_top='1em', margin_bottom='1em'),
        # ✅ SOLUCIÓN: Se accede directamente a la lista 'posts' y se corta (slice)
        # para evitar el error de compilación con la variable computada 'dashboard_posts'.
        product_gallery_component(posts=CartState.posts[:20]),
        min_height="85vh",
    )