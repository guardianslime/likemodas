# full_stack_python/auth/admin_auth.py (CORREGIDO Y COMPLETO)

import reflex as rx
import reflex_local_auth
from functools import wraps
from .state import SessionState
from ..models import UserRole
# ✨ AÑADIDO: Importar base_page para un layout consistente en la página de error
from ..ui.base import base_page

def require_admin(page):
    """
    Un decorador para proteger páginas que solo los administradores pueden ver.
    """
    @wraps(page)
    def admin_page(*args, **kwargs):
        return rx.cond(
            SessionState.is_hydrated,
            rx.cond(
                # Se usa la variable computada para más claridad
                SessionState.is_admin,
                page(*args, **kwargs),
                # --- ✨ CORRECCIÓN: Se elimina la llamada a login_form_component ---
                # Ahora se muestra una página de error con el layout base.
                base_page(
                    rx.center(
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
                )
            ),
            rx.center(rx.spinner(), height="100vh")
        )
    return admin_page