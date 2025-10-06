# likemodas/auth/admin_auth.py (CORREGIDO)

import reflex as rx
from functools import wraps
from ..state import AppState

def require_admin(page):
    """
    Decorador estricto que protege páginas que SOLO los administradores pueden ver,
    como la página de Gestión de Usuarios.
    """
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

def require_panel_access(page):
    """
    [NUEVO Y CORREGIDO] Decorador para proteger páginas del panel de control.
    Permite el acceso a usuarios que sean Administradores O Vendedores.
    """
    @wraps(page)
    def protected_page(*args, **kwargs):
        error_content = rx.center(
            rx.vstack(
                rx.heading("Acceso Denegado", size="9"),
                rx.text("No tienes permiso para acceder a esta página."),
                rx.link(rx.button("Volver al Inicio"), href="/", margin_top="1em"),
                align="center", spacing="4",
            ),
            min_height="85vh"
        )

        return rx.cond(
            AppState.is_hydrated,
            # --- ¡LÓGICA CLAVE CORREGIDA! ---
            # Se comprueba si el usuario es admin O vendedor.
            rx.cond(
                AppState.is_admin | AppState.is_vendedor,
                page(*args, **kwargs),
                error_content
            ),
            rx.center(rx.spinner(), height="100vh")
        )
    return protected_page