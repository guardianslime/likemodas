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
            # --- AJUSTE DE TAMAÑO ---
            rx.heading("Zona de Peligro", color_scheme="red", size="6"),
            rx.text("Una vez que elimines tu cuenta, no hay vuelta atrás. Por favor, ten la certeza.", color_scheme="gray", size="3"),
            rx.divider(),
            rx.text("Confirma tu contraseña para continuar:", size="4"),
            # --- AJUSTE DE TAMAÑO ---
            password_input(name="password", placeholder="Contraseña actual...", required=True, size="3"),
            rx.alert_dialog.root(
                rx.alert_dialog.trigger(
                    # --- AJUSTE DE TAMAÑO ---
                    rx.button("Eliminar mi Cuenta Permanentemente", color_scheme="red", type="button", size="3")
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
            # --- AJUSTE DE TAMAÑO ---
            spacing="4",
        ),
        on_submit=AppState.handle_account_deletion,
        border="1px solid var(--red-7)",
        border_radius="var(--radius-3)",
        padding="1.5em",
        width="100%",
    )
    
    page_content = rx.center(
        rx.vstack(
            # --- AJUSTE DE TAMAÑO ---
            rx.heading("Mi Perfil", size="8"),
            rx.text("Gestiona tu información personal y de seguridad.", size="4"),
            rx.divider(margin_y="1.5em"),
            
            # --- AJUSTE DE TAMAÑO ---
            rx.heading("Imagen de Perfil", size="6"),
            rx.hstack(
                # --- AJUSTE DE TAMAÑO ---
                rx.avatar(
                    src=rx.get_upload_url(AppState.profile_info.avatar_url), 
                    fallback=rx.cond(AppState.profile_info.username, AppState.profile_info.username[0].upper(), "?"), 
                    size="8"
                ),
                rx.upload(
                    rx.vstack(
                        rx.icon("upload", size=32),
                        rx.text("Haz clic o arrastra una imagen aquí."),
                        spacing="3",
                    ),
                    id="avatar_upload",
                    border="2px dashed #ccc",
                    padding="3em", # --- AJUSTE DE TAMAÑO ---
                    border_radius="var(--radius-3)",
                    on_drop=AppState.handle_avatar_upload(rx.upload_files("avatar_upload")),
                    flex_grow="1",
                ),
                align="center",
                spacing="5",
                width="100%",
            ),

            rx.divider(margin_y="1.5em"),

            rx.form(
                rx.vstack(
                    # --- AJUSTE DE TAMAÑO ---
                    rx.heading("Información General", size="6"),
                    rx.text("Nombre de Usuario", size="4"),
                    rx.input(name="username", value=AppState.profile_username, on_change=AppState.set_profile_username, required=True, size="3"),
                    rx.text("Email (no se puede cambiar)", size="4"),
                    rx.input(name="email", value=AppState.profile_info.email, is_disabled=True, size="3"),
                    rx.text("Teléfono de Contacto", size="4"),
                    rx.input(name="phone", value=AppState.profile_phone, on_change=AppState.set_profile_phone, placeholder="Ej: 3001234567", size="3"),
                    rx.button("Guardar Cambios", type="submit", size="3"),
                    align_items="start",
                    width="100%",
                    # --- AJUSTE DE TAMAÑO ---
                    spacing="4",
                ),
                on_submit=AppState.handle_profile_update,
            ),
            
            rx.divider(margin_y="1.5em"),

            rx.form(
                rx.vstack(
                    # --- AJUSTE DE TAMAÑO ---
                    rx.heading("Cambiar Contraseña", size="6"),
                    rx.text("Contraseña Actual", size="4"),
                    password_input(name="current_password", required=True, size="3"),
                    rx.text("Nueva Contraseña", size="4"),
                    password_input(name="new_password", required=True, size="3"),
                    rx.text("Confirmar Nueva Contraseña", size="4"),
                    password_input(name="confirm_password", required=True, size="3"),
                    rx.button("Actualizar Contraseña", type="submit", size="3"),
                    align_items="start",
                    width="100%",
                    # --- AJUSTE DE TAMAÑO ---
                    spacing="4",
                ),
                on_submit=AppState.handle_password_change,
            ),

            rx.divider(margin_y="2em"),
            danger_zone,

            # --- AJUSTE DE TAMAÑO ---
            spacing="6",
            width="100%",
            max_width="800px",
        )
    )

    return account_layout(page_content)