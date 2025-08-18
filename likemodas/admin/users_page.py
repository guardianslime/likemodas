# likemodas/admin/users_page.py (NUEVO ARCHIVO)

import reflex as rx
from ..state import AppState
from ..models import UserInfo, UserRole

def user_status_badge(user: UserInfo) -> rx.Component:
    """Devuelve un badge de estado basado en si el usuario está verificado o vetado."""
    # El veto tiene prioridad sobre el estado de verificación
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
    """Componente para renderizar una fila de la tabla de usuarios."""
    return rx.table.row(
        rx.table.cell(user.user.username),
        rx.table.cell(user.email),
        rx.table.cell(rx.badge(user.role)),
        rx.table.cell(user_status_badge(user)),
        rx.table.cell(
            rx.hstack(
                # Botón para cambiar el rol
                rx.button(
                    rx.cond(user.role == UserRole.ADMIN, "Quitar Admin", "Hacer Admin"),
                    on_click=AppState.toggle_admin_role(user.id),  # Correcto
                    size="1"
                ),
                # Botón para vetar/quitar veto
                rx.cond(
                    user.is_banned,
                    rx.button("Quitar Veto", on_click=AppState.unban_user(user.id), color_scheme="green", size="1"),
                    rx.button("Vetar (7 días)", on_click=AppState.ban_user(user.id, 7), color_scheme="red", size="1"),
                ),
                spacing="2"
            )
        ),
    )

def user_management_page() -> rx.Component:
    """Página principal de gestión de usuarios."""
    return rx.container(
        rx.vstack(
            rx.heading("Gestión de Usuarios", size="7"),
            rx.text("Administra los roles y el estado de todos los usuarios registrados."),
            rx.divider(margin_y="1.5em"),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Usuario"),
                        rx.table.column_header_cell("Email"),
                        rx.table.column_header_cell("Rol"),
                        rx.table.column_header_cell("Estado"),
                        rx.table.column_header_cell("Acciones"),
                    )
                ),
                rx.table.body(
                    rx.foreach(AppState.all_users, user_row)
                ),
                variant="surface",
                width="100%",
            ),
            align="stretch",
            width="100%",
        ),
        padding_top="2em",
    )