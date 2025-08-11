# likemodas/admin/users_page.py (CORRECCIÓN FINAL CON rx.el.*)

import reflex as rx
from ..state import AppState
from ..models import UserInfo, UserRole

def user_status_badge(user: UserInfo) -> rx.Component:
    """Devuelve un badge de estado basado en si el usuario está verificado o vetado."""
    return rx.cond(
        user.is_banned,
        rx.badge("Vetado", color_scheme="red"),
        rx.cond(
            user.is_verified,
            rx.badge("Verificado", color_scheme="green"),
            rx.badge("Sin Verificar", color_scheme="orange")
        )
    )

def user_row(user: UserInfo) -> rx.Component:
    """Componente para renderizar una fila de la tabla de usuarios con sintaxis rx.el.*."""
    return rx.el.tr(
        rx.el.td(user.user.username),
        rx.el.td(user.email),
        rx.el.td(rx.badge(user.role)),
        rx.el.td(user_status_badge(user)),
        rx.el.td(
            rx.hstack(
                rx.button(
                    rx.cond(user.role == UserRole.ADMIN, "Quitar Admin", "Hacer Admin"),
                    on_click=lambda: AppState.toggle_admin_role(user.id),
                    size="sm"
                ),
                rx.cond(
                    user.is_banned,
                    rx.button("Quitar Veto", on_click=lambda: AppState.unban_user(user.id), color_scheme="green", size="sm"),
                    rx.button("Vetar (7 días)", on_click=lambda: AppState.ban_user(user.id, 7), color_scheme="red", size="sm"),
                ),
                spacing="2"
            )
        ),
    )

def user_management_page() -> rx.Component:
    """Página principal de gestión de usuarios con tabla compatible."""
    return rx.container(
        rx.vstack(
            rx.heading("Gestión de Usuarios", font_size="2em"),
            rx.text("Administra los roles y el estado de todos los usuarios registrados."),
            rx.divider(margin_y="1.5em"),
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th("Usuario"),
                        rx.el.th("Email"),
                        rx.el.th("Rol"),
                        rx.el.th("Estado"),
                        rx.el.th("Acciones"),
                    )
                ),
                rx.el.tbody(
                    rx.foreach(AppState.all_users, user_row)
                ),
                width="100%",
            ),
            align_items="stretch",
            width="100%",
        ),
        padding_top="2em",
        max_width="1200px"
    )