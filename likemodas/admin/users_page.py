# likemodas/admin/user_page.py 

import reflex as rx
from ..state import AppState, UserManagementDTO
from ..models import UserRole 
from ..auth.admin_auth import require_admin # Importa el decorador de admin
from ..ui.password_input import password_input # Importa el campo de contraseña

def ban_user_modal() -> rx.Component:
    """Modal para configurar la duración del veto de un usuario."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Vetar Usuario"),
            rx.dialog.description(
                "Selecciona por cuánto tiempo quieres vetar a ",
                rx.text.strong(rx.cond(AppState.user_to_ban, AppState.user_to_ban.username, "")),
                ". El usuario no podrá iniciar sesión durante este período."
            ),
            rx.form(
                rx.vstack(
                    rx.hstack(
                        rx.input(
                            placeholder="Ej: 7",
                            value=AppState.ban_duration_value,
                            on_change=AppState.set_ban_duration_value,
                            type="number",
                        ),
                        rx.select(
                            ["días", "meses", "años"],
                            value=AppState.ban_duration_unit,
                            on_change=AppState.set_ban_duration_unit,
                        ),
                        spacing="3",
                    ),
                    rx.flex(
                        rx.dialog.close(
                            rx.button(
                                "Cancelar", 
                                variant="soft", 
                                color_scheme="gray", 
                                on_click=AppState.close_ban_modal,
                                type="button"
                            )
                        ),
                        rx.button("Confirmar Veto", type="submit", color_scheme="red"),
                        spacing="3",
                        margin_top="1em",
                        justify="end",
                    ),
                    spacing="3",
                    margin_top="1em",
                ),
                on_submit=AppState.confirm_ban,
            ),
        ),
        open=AppState.show_ban_modal,
        on_open_change=AppState.close_ban_modal,
    )

def hard_delete_user_modal() -> rx.Component:
    """
    Modal de confirmación "Zona de Peligro" para la eliminación permanente de un usuario.
    Requiere la contraseña del administrador.
    """
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            # Argumentos posicionales (hijos) PRIMERO
            rx.alert_dialog.title("¿Estásolutamente seguro?"),
            rx.alert_dialog.description(
                "Esta acción es irreversible. Se eliminará permanentemente al usuario: ",
                rx.text.strong(rx.cond(AppState.user_to_delete, AppState.user_to_delete.username, "...")),
                ". Todos sus datos (publicaciones, comentarios, compras) se perderán. Para confirmar, introduce tu contraseña de administrador."
            ),
            # Formulario interno para la contraseña
            rx.form(
                rx.flex(
                    password_input(
                        name="admin_password",
                        placeholder="Tu contraseña de administrador...",
                        required=True,
                        width="100%",
                    ),
                    direction="column",
                    spacing="3",
                    margin_top="1em",
                ),
                rx.flex(
                    rx.alert_dialog.cancel(
                        rx.button("Cancelar", variant="soft", color_scheme="gray", type="button")
                    ),
                    rx.alert_dialog.action(
                        rx.button("Sí, entiendo, eliminar permanentemente", type="submit", color_scheme="red")
                    ),
                    spacing="3",
                    margin_top="1em",
                    justify="end",
                ),
                # Evento de envío del formulario
                on_submit=AppState.confirm_hard_delete_user,
            ),
            # Argumento con nombre (style) AL FINAL
            style={"max_width": "450px"},
        ),
        # Controla la apertura/cierre del modal
        open=AppState.show_delete_user_modal,
        on_open_change=AppState.close_delete_modal,
    )


def user_status_badge(user: UserManagementDTO) -> rx.Component:
    """Devuelve un badge de estado (Vetado, Verificado, etc.)."""
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
    """Componente de tarjeta responsiva para la vista móvil."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.avatar(fallback=rx.cond(user.username, user.username[0].upper(), "?"), size="4"),
                rx.vstack(
                    rx.heading(user.username, size="4", trim="end", no_of_lines=1),
                    rx.text(user.email, size="2", color_scheme="gray", trim="end", no_of_lines=1),
                    align_items="start", spacing="0",
                ),
                rx.spacer(),
                align="center", width="100%",
            ),
            rx.divider(margin_y="0.75em"),
            rx.hstack(rx.text("Rol:", weight="medium", size="2"), rx.spacer(), rx.badge(user.role), align="center", width="100%"),
            rx.hstack(rx.text("Estado:", weight="medium", size="2"), rx.spacer(), user_status_badge(user), align="center", width="100%"),
            rx.divider(margin_y="0.75em"),
            
            # --- SECCIÓN DE ACCIONES MÓVIL (CON BOTÓN ELIMINAR) ---
            rx.flex(
                # Fila 1: Acciones de Rol
                rx.button(rx.cond(user.role == UserRole.ADMIN, "Quitar Admin", "Hacer Admin"), on_click=AppState.toggle_admin_role(user.id), size="1", flex_grow=1),
                rx.button(rx.cond(user.role == UserRole.VENDEDOR, "Quitar Vendedor", "Hacer Vendedor"), on_click=AppState.toggle_vendedor_role(user.id), size="1", color_scheme="violet", flex_grow=1, is_disabled=(user.role == UserRole.ADMIN)),
                rx.cond(user.role == UserRole.VENDEDOR, rx.button("Vigilar", on_click=AppState.start_vigilancia(user.id), color_scheme="gray", variant="outline", size="1", flex_grow=1)),
                
                # Fila 2: Acciones de Estado (Vetar/Quitar Veto)
                rx.cond(
                    user.is_banned,
                    rx.button("Quitar Veto", on_click=AppState.unban_user(user.id), color_scheme="green", size="1", flex_grow=1),
                    rx.button("Vetar", on_click=AppState.open_ban_modal(user), color_scheme="orange", variant="soft", size="1", flex_grow=1),
                ),
                
                # Fila 3: Zona de Peligro (Eliminar)
                rx.button("Eliminar", on_click=AppState.open_delete_modal(user), color_scheme="red", variant="solid", size="1", flex_grow=1),
                
                spacing="2", 
                wrap="wrap", # Permite que los botones se reordenen
                width="100%"
            ),
            
            spacing="3", width="100%",
        )
    )

def desktop_user_row(user: UserManagementDTO) -> rx.Component:
    """Componente para una fila de la tabla de escritorio."""
    return rx.table.row(
        rx.table.cell(user.username),
        rx.table.cell(user.email),
        rx.table.cell(rx.badge(user.role)),
        rx.table.cell(user_status_badge(user)),
        rx.table.cell(
            # --- SECCIÓN DE ACCIONES ESCRITORIO (CON BOTÓN ELIMINAR) ---
            rx.hstack(
                # Acciones de Rol
                rx.button(rx.cond(user.role == UserRole.ADMIN, "Quitar Admin", "Hacer Admin"), on_click=AppState.toggle_admin_role(user.id), size="1"),
                rx.button(rx.cond(user.role == UserRole.VENDEDOR, "Quitar Vendedor", "Hacer Vendedor"), on_click=AppState.toggle_vendedor_role(user.id), size="1", color_scheme="violet", is_disabled=(user.role == UserRole.ADMIN)),
                rx.cond(user.role == UserRole.VENDEDOR, rx.button("Vigilar", on_click=AppState.start_vigilancia(user.id), color_scheme="gray", variant="outline", size="1")),
                
                # Acciones de Estado
                rx.cond(
                    user.is_banned,
                    rx.button("Quitar Veto", on_click=AppState.unban_user(user.id), color_scheme="green", size="1"),
                    rx.button("Vetar", on_click=AppState.open_ban_modal(user), color_scheme="orange", variant="soft", size="1"),
                ),
                
                # Zona de Peligro
                rx.button("Eliminar", on_click=AppState.open_delete_modal(user), color_scheme="red", variant="solid", size="1"),
                
                spacing="2"
            )
        ),
    )

@require_admin # Asegura que solo los admins vean esta página
def user_management_page() -> rx.Component:
    """Página de gestión de usuarios con diseño responsivo y modal de veto."""
    page_content = rx.container(
        rx.vstack(
            rx.heading("Gestión de Usuarios", size="7"),
            rx.text("Administra los roles y el estado de todos los usuarios registrados."),
            
            # Filtros (Búsqueda y Fecha)
            rx.input(placeholder="Buscar por nombre de usuario o email...", value=AppState.search_query_all_users, on_change=AppState.set_search_query_all_users, width="100%", max_width="400px", margin_y="1em"),
            rx.hstack(
                rx.vstack(rx.text("Registrado desde:", size="2"), rx.input(type="date", value=AppState.user_filter_start_date, on_change=AppState.set_user_filter_start_date), align_items="stretch"),
                rx.vstack(rx.text("Registrado hasta:", size="2"), rx.input(type="date", value=AppState.user_filter_end_date, on_change=AppState.set_user_filter_end_date), align_items="stretch"),
                spacing="4", width="100%", max_width="400px", justify="start",
            ),
            rx.divider(margin_y="1.5em"),
            
            # --- LÓGICA RESPONSIVA ---
            # Vista de Tabla (Solo para escritorio)
            rx.box(
                rx.table.root(
                    rx.table.header(rx.table.row(rx.table.column_header_cell("Usuario"), rx.table.column_header_cell("Email"), rx.table.column_header_cell("Rol"), rx.table.column_header_cell("Estado"), rx.table.column_header_cell("Acciones"))),
                    rx.table.body(rx.foreach(AppState.filtered_all_users, desktop_user_row)),
                    variant="surface", width="100%",
                ),
                display=["none", "none", "block"] # Oculto en móvil y tablet
            ),
            
            # Vista de Tarjetas (Solo para móvil)
            rx.box(
                rx.vstack(rx.foreach(AppState.filtered_all_users, mobile_user_card), spacing="4", width="100%"),
                display=["block", "block", "none"] # Visible en móvil y tablet, oculto en escritorio
            ),
            
            align="stretch", width="100%",
        ),
        padding_top="2em", max_width="1400px",
    )

    return rx.fragment(
        page_content,
        ban_user_modal(), # El modal de veto
        hard_delete_user_modal(), # El nuevo modal de eliminación permanente
    )