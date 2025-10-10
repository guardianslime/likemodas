# En: likemodas/admin/users_page.py

import reflex as rx
from ..state import AppState, UserManagementDTO
from ..models import UserRole 

def user_status_badge(user: UserManagementDTO) -> rx.Component:
    """Devuelve un badge de estado basado en si el usuario está verificado o vetado."""
    return rx.cond(
        user.is_banned,
        rx.badge("Vetado", color_scheme="red", variant="solid"),
        rx.cond(
            user.is_verified,
            rx.badge("Verificado", color_scheme="green", variant="soft"),
            rx.badge("Sin Verificar", color_scheme="orange", variant="soft")
        )
    )

def mobile_user_card(user: UserManagementDTO) -> rx.Component:
    """Componente de tarjeta para mostrar un usuario en la vista móvil."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                # ✨ --- INICIO DE LA CORRECCIÓN --- ✨
                rx.avatar(
                    # Se reemplaza el if/else de Python por rx.cond
                    fallback=rx.cond(
                        user.username,
                        user.username[0].upper(),
                        "?"
                    ), 
                    size="4"
                ),
                # ✨ --- FIN DE LA CORRECCIÓN --- ✨
                rx.vstack(
                    rx.heading(user.username, size="4", trim="end", no_of_lines=1),
                    rx.text(user.email, size="2", color_scheme="gray", trim="end", no_of_lines=1),
                    align_items="start", spacing="0",
                ),
                rx.spacer(),
                align="center", width="100%",
            ),
            rx.divider(margin_y="0.75em"),
            rx.hstack(
                rx.text("Rol:", weight="medium", size="2"),
                rx.spacer(),
                # ✨ CORRECCIÓN AQUÍ: Se elimina .value ✨
                rx.badge(user.role),
                align="center", width="100%",
            ),
            rx.hstack(
                rx.text("Estado:", weight="medium", size="2"),
                rx.spacer(),
                user_status_badge(user),
                align="center", width="100%",
            ),
            rx.divider(margin_y="0.75em"),
            rx.flex(
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
                    rx.button("Vigilar", on_click=AppState.start_vigilancia(user.id), color_scheme="gray", variant="outline", size="1")
                ),
                rx.cond(
                    user.is_banned,
                    rx.button("Quitar Veto", on_click=AppState.unban_user(user.id), color_scheme="green", size="1"),
                    rx.button("Vetar (7 días)", on_click=AppState.ban_user(user.id, 7), color_scheme="red", size="1"),
                ),
                spacing="2", wrap="wrap",
            ),
            spacing="3", width="100%",
        )
    )

def desktop_user_row(user: UserManagementDTO) -> rx.Component:
    """Componente para renderizar una fila de la tabla de usuarios."""
    return rx.table.row(
        rx.table.cell(user.username),
        rx.table.cell(user.email),
        # ✨ CORRECCIÓN AQUÍ: Se elimina .value ✨
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
                    rx.button("Vigilar", on_click=AppState.start_vigilancia(user.id), color_scheme="gray", variant="outline", size="1")
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
    """Página de gestión de usuarios con diseño responsivo."""
    desktop_view = rx.box(
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
                rx.foreach(AppState.filtered_all_users, desktop_user_row)
            ),
            variant="surface",
            width="100%",
        ),
        display=["none", "none", "block"] # Oculto en móvil y tablet
    )

    mobile_view = rx.box(
        rx.vstack(
            rx.foreach(AppState.filtered_all_users, mobile_user_card),
            spacing="4",
            width="100%",
        ),
        display=["block", "block", "none"] # Visible solo en móvil y tablet
    )

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
            
            rx.hstack(
                rx.vstack(
                    rx.text("Registrado desde:", size="2"),
                    rx.input(type="date", value=AppState.user_filter_start_date, on_change=AppState.set_user_filter_start_date),
                    align_items="stretch"
                ),
                rx.vstack(
                    rx.text("Registrado hasta:", size="2"),
                    rx.input(type="date", value=AppState.user_filter_end_date, on_change=AppState.set_user_filter_end_date),
                    align_items="stretch"
                ),
                spacing="4",
                width="100%",
                max_width="400px",
                justify="start",
            ),
            
            rx.divider(margin_y="1.5em"),
            
            rx.fragment(
                desktop_view,
                mobile_view,
            ),
            
            align="stretch",
            width="100%",
        ),
        padding_top="2em",
        max_width="1400px",
    )