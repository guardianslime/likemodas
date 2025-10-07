# likemodas/admin/users_page.py (NUEVO ARCHIVO)

import reflex as rx
from ..state import AppState, UserManagementDTO # Importa el nuevo DTO
from ..models import UserRole 

def user_status_badge(user: UserManagementDTO) -> rx.Component: # <-- Usa el DTO
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

def user_row(user: UserManagementDTO) -> rx.Component: # <-- Usa el DTO
    """Componente para renderizar una fila de la tabla de usuarios."""
    return rx.table.row(
        rx.table.cell(user.username), # Acceso directo
        rx.table.cell(user.email),
        rx.table.cell(rx.badge(user.role)),
        rx.table.cell(user_status_badge(user)),
        rx.table.cell(
            rx.hstack(
                rx.button(
                    rx.cond(user.role == UserRole.ADMIN, "Quitar Admin", "Hacer Admin"),
                    on_click=AppState.toggle_admin_role(user.id),
                    size="1"
                ),
                rx.button(
                    rx.cond(user.role == UserRole.VENDEDOR, "Quitar Vendedor", "Hacer Vendedor"),
                    on_click=AppState.toggle_vendedor_role(user.id),
                    size="1",
                    color_scheme="violet",
                    is_disabled=(user.role == UserRole.ADMIN)
                ),
                rx.cond(
                    user.role == UserRole.VENDEDOR,
                    rx.button(
                        "Vigilar", 
                        on_click=AppState.start_vigilancia(user.id), 
                        color_scheme="gray", 
                        variant="outline", 
                        size="1"
                    )
                ),
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
    """Página principal de gestión de usuarios con búsqueda."""
    return rx.container(
        rx.vstack(
            rx.heading("Gestión de Usuarios", size="7"),
            rx.text("Administra los roles y el estado de todos los usuarios registrados."),
            
            rx.input(
                placeholder="Buscar por nombre de usuario o email...",
                value=AppState.search_query_all_users,
                on_change=AppState.set_search_query_all_users,
                width="100%",
                max_width="400px",
                margin_y="1em"
            ),
            
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
                    rx.foreach(AppState.filtered_all_users, user_row)
                ),
                variant="surface",
                width="100%",
            ),
            align="stretch",
            width="100%",
        ),
        padding_top="2em",
    )