# likemodas/auth/admin_auth.py (CORREGIDO)

import reflex as rx
import reflex_local_auth
from functools import wraps
from .state import SessionState

def require_admin(page):
    """
    Un decorador para proteger páginas que solo los administradores pueden ver.
    Ahora no aplica un layout base para evitar anidamiento.
    """
    @wraps(page)
    def admin_page(*args, **kwargs):
        # El contenido de error que se mostrará si el usuario no es admin.
        error_content = rx.center(
            rx.vstack(
                rx.heading("Acceso Denegado", size="9"),
                rx.text("Esta página es solo para administradores."),
                rx.link(
                    rx.button("Volver al Inicio"),
                    href="/",
                    margin_top="1em"
                ),
                align="center",
                spacing="4",
            ),
            min_height="85vh"
        )

        return rx.cond(
            SessionState.is_hydrated,
            rx.cond(
                SessionState.is_admin,
                page(*args, **kwargs),
                # ✅ CORRECCIÓN: Ya no se llama a base_page aquí.
                error_content
            ),
            # Muestra un spinner mientras se hidrata el estado
            rx.center(rx.spinner(), height="100vh")
        )
    return admin_page