# likemodas/auth/admin_auth.py (CORREGIDO)

import reflex as rx
from functools import wraps
from ..state import AppState

def require_admin(page):
    """Decorador para proteger páginas que solo los administradores pueden ver."""
    @wraps(page)
    def admin_page(*args, **kwargs):
        error_content = rx.center(
            rx.vstack(
                rx.heading("Acceso Denegado", size="9"),
                rx.text("Esta página es solo para administradores."),
                rx.link(rx.button("Volver al Inicio"), href="/", margin_top="1em"),
                align="center", spacing="4",
            ),
            min_height="85vh"
        )

        return rx.cond(
            AppState.is_hydrated,
            rx.cond(
                AppState.is_admin,
                page(*args, **kwargs),
                error_content
            ),
            rx.center(rx.spinner(), height="100vh")
        )
    return admin_page