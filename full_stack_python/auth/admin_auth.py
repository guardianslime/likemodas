# full_stack_python/auth/admin_auth.py

import reflex as rx
import reflex_local_auth
from functools import wraps
from .state import SessionState
from ..models import UserRole

def require_admin(page):
    """
    Un decorador para proteger páginas que solo los administradores pueden ver.
    """
    @wraps(page)
    def admin_page(*args, **kwargs):
        return rx.cond(
            SessionState.is_hydrated,
            rx.cond(
                (SessionState.is_authenticated) & (SessionState.authenticated_user_info.role == UserRole.ADMIN),
                page(*args, **kwargs),
                reflex_local_auth.pages.components.login_form_component(
                    rx.center(
                        rx.vstack(
                            rx.heading("Acceso Denegado"),
                            rx.text("Esta página es solo para administradores."),
                            rx.link("Volver al inicio", href="/"),
                        )
                    )
                )
            ),
            rx.center(rx.spinner())
        )
    return admin_page