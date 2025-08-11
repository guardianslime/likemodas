# likemodas/admin/users_page.py (CORREGIDO CON rx.chakra)

import reflex as rx
from ..state import AppState
from ..models import UserInfo, UserRole

def user_status_badge(user: UserInfo) -> rx.Component:
    """Devuelve un badge de estado basado en si el usuario está verificado o vetado."""
    return rx.cond(
        user.is_banned,
        rx.chakra.badge("Vetado", color_scheme="red"),
        rx.cond(
            user.is_verified,
            rx.chakra.badge("Verificado", color_scheme="green"),
            rx.chakra.badge("Sin Verificar", color_scheme="orange")
        )
    )

def user_row(user: UserInfo) -> rx.Component:
    """Componente para renderizar una fila de la tabla de usuarios con sintaxis de Chakra UI."""
    return rx.chakra.tr(
        rx.chakra.td(user.user.username),
        rx.chakra.td(user.email),
        rx.chakra.td(rx.chakra.badge(user.role)),
        rx.chakra.td(user_status_badge(user)),
        rx.chakra.td(
            rx.chakra.hstack(
                rx.chakra.button(
                    rx.cond(user.role == UserRole.ADMIN, "Quitar Admin", "Hacer Admin"),
                    on_click=lambda: AppState.toggle_admin_role(user.id),
                    size="sm"
                ),
                rx.cond(
                    user.is_banned,
                    rx.chakra.button("Quitar Veto", on_click=lambda: AppState.unban_user(user.id), color_scheme="green", size="sm"),
                    rx.chakra.button("Vetar (7 días)", on_click=lambda: AppState.ban_user(user.id, 7), color_scheme="red", size="sm"),
                ),
                spacing="2"
            )
        ),
    )

def user_management_page() -> rx.Component:
    """Página principal de gestión de usuarios con tabla compatible."""
    return rx.chakra.container(
        rx.chakra.vstack(
            rx.chakra.heading("Gestión de Usuarios", font_size="2em"),
            rx.chakra.text("Administra los roles y el estado de todos los usuarios registrados."),
            rx.chakra.divider(margin_y="1.5em"),
            rx.chakra.table(
                rx.chakra.thead(
                    rx.chakra.tr(
                        rx.chakra.th("Usuario"),
                        rx.chakra.th("Email"),
                        rx.chakra.th("Rol"),
                        rx.chakra.th("Estado"),
                        rx.chakra.th("Acciones"),
                    )
                ),
                rx.chakra.tbody(
                    rx.foreach(AppState.all_users, user_row)
                ),
                variant="striped",
                width="100%",
            ),
            align_items="stretch",
            width="100%",
        ),
        padding_top="2em",
        max_width="1200px"
    )