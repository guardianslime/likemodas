# likemodas/account/profile_page.py

import reflex as rx
import reflex_local_auth
from ..state import AppState
from ..account.layout import account_layout
from ..ui.password_input import password_input

def profile_page_content() -> rx.Component:
    """Página para que el usuario gestione su información de perfil."""
    
    danger_zone = rx.form(
        rx.vstack(
            rx.heading("Zona de Peligro", color_scheme="red", size="5"),
            rx.text("Una vez que elimines tu cuenta, no hay vuelta atrás. Por favor, ten la certeza.", color_scheme="gray"),
            rx.divider(),
            rx.text("Confirma tu contraseña para continuar:", size="3"),
            password_input(name="password", placeholder="Contraseña actual...", required=True),
            rx.alert_dialog.root(
                rx.alert_dialog.trigger(
                    rx.button("Eliminar mi Cuenta Permanentemente", color_scheme="red", type="button")
                ),
                rx.alert_dialog.content(
                    rx.alert_dialog.title("¿Estás absolutamente seguro?"),
                    rx.alert_dialog.description(
                        "Esta acción es irreversible y eliminará todos tus datos, incluyendo historial de compras y comentarios."
                    ),
                    rx.flex(
                        rx.alert_dialog.cancel(rx.button("Cancelar", variant="soft", color_scheme="gray")),
                        rx.alert_dialog.action(rx.button("Sí, eliminar mi cuenta", type="submit")),
                        spacing="3", margin_top="1em", justify="end",
                    ),
                ),
            ),
            align_items="start",
            width="100%",
            spacing="3",
        ),
        on_submit=AppState.handle_account_deletion,
        border="1px solid var(--red-7)",
        border_radius="var(--radius-3)",
        padding="1.5em",
        width="100%",
    )
    
    # --- ✨ CORRECCIÓN DE DISEÑO: Se envuelve el contenido en un rx.center ✨ ---
    page_content = rx.center(
        rx.vstack(
            rx.heading("Mi Perfil", size="7"),
            rx.text("Gestiona tu información personal y de seguridad."),
            rx.divider(margin_y="1.5em"),
            
            rx.heading("Imagen de Perfil", size="5"),
            rx.hstack(
                # --- ✨ CORRECCIÓN DE ERROR: Se aplica rx.get_upload_url aquí ✨ ---
                rx.avatar(
                    src=rx.get_upload_url(AppState.profile_info.avatar_url), 
                    fallback=rx.cond(AppState.profile_info.username, AppState.profile_info.username[0].upper(), "?"), 
                    size="6"
                ),
                rx.upload(
                    rx.text("Haz clic o arrastra una imagen aquí."),
                    id="avatar_upload",
                    border="1px solid #ccc",
                    padding="2em",
                    border_radius="var(--radius-3)",
                    on_drop=AppState.handle_avatar_upload(rx.upload_files("avatar_upload")),
                ),
                align="center",
                spacing="5",
                width="100%",
            ),

            rx.divider(margin_y="1.5em"),

            rx.form(
                rx.vstack(
                    rx.heading("Información General", size="5"),
                    rx.text("Nombre de Usuario"),
                    rx.input(name="username", value=AppState.profile_username, on_change=AppState.set_profile_username, required=True),
                    rx.text("Email (no se puede cambiar)"),
                    rx.input(name="email", value=AppState.profile_info.email, is_disabled=True),
                    rx.text("Teléfono de Contacto"),
                    rx.input(name="phone", value=AppState.profile_phone, on_change=AppState.set_profile_phone, placeholder="Ej: 3001234567"),
                    rx.button("Guardar Cambios", type="submit"),
                    align_items="start",
                    width="100%",
                    spacing="3",
                ),
                on_submit=AppState.handle_profile_update,
            ),
            
            rx.divider(margin_y="1.5em"),

            rx.form(
                rx.vstack(
                    rx.heading("Cambiar Contraseña", size="5"),
                    rx.text("Contraseña Actual"),
                    password_input(name="current_password", required=True),
                    rx.text("Nueva Contraseña"),
                    password_input(name="new_password", required=True),
                    rx.text("Confirmar Nueva Contraseña"),
                    password_input(name="confirm_password", required=True),
                    rx.button("Actualizar Contraseña", type="submit"),
                    align_items="start",
                    width="100%",
                    spacing="3",
                ),
                on_submit=AppState.handle_password_change,
            ),

            rx.divider(margin_y="2em"),
            danger_zone,

            spacing="5",
            width="100%",
            # --- ✨ CORRECCIÓN DE DISEÑO: Ancho máximo ajustado ✨ ---
            max_width="800px",
        ),
        width="100%",
    )

    return account_layout(page_content)