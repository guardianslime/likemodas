import reflex as rx
import reflex_local_auth
from ..state import AppState
from ..account.layout import account_layout
from ..ui.password_input import password_input

# El modal de TFA se mantiene aquí porque otras partes del código lo importan desde este archivo.
def tfa_activation_modal() -> rx.Component:
    """Modal para mostrar el QR y confirmar la activación de 2FA."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Activar Autenticación de Dos Factores"),
            rx.dialog.description("Escanea este código QR con tu aplicación de autenticación."),
            rx.center(
                rx.cond(
                    AppState.tfa_qr_code_data_uri,
                    rx.image(src=AppState.tfa_qr_code_data_uri, width="256px", height="256px"),
                    rx.spinner()
                ),
                margin_y="1.5em",
            ),
            rx.form(
                rx.vstack(
                    rx.text("Introduce el código de 6 dígitos para confirmar."),
                    rx.input(name="tfa_code", placeholder="123456", required=True, max_length=6),
                    rx.button("Verificar y Activar", type="submit"),
                    spacing="3",
                ),
                on_submit=AppState.verify_and_enable_tfa,
            ),
            rx.flex(
                rx.dialog.close(rx.button("Cancelar", variant="soft", color_scheme="gray")),
                justify="end", margin_top="1em",
            ),
        ),
        open=AppState.show_tfa_activation_modal,
        on_open_change=AppState.set_show_tfa_activation_modal,
    )

@reflex_local_auth.require_login
def profile_page_content() -> rx.Component:
    """Página para que el CLIENTE gestione su perfil. Redirige a los admins."""

    # --- Lógica de redirección para administradores ---
    admin_redirect_view = rx.center(
        rx.vstack(
            rx.spinner(size="3"),
            rx.text("Redirigiendo al perfil de administrador..."),
            spacing="4"
        ),
        min_height="85vh",
        on_mount=rx.redirect("/admin/profile"), # Redirige al cargar la página
    )

    # --- Contenido original y completo de la página de perfil para CLIENTES ---
    client_profile_view = rx.fragment(
        tfa_activation_modal(), # El modal de 2FA
        account_layout(
            rx.center(
                rx.vstack(
                    rx.heading("Mi Perfil", size="8"),
                    rx.text("Gestiona tu información personal y de seguridad.", size="4", color_scheme="gray"),
                    rx.divider(margin_y="1.5em"),
                    
                    rx.heading("Imagen de Perfil", size="6"),
                    rx.hstack(
                        rx.avatar(
                            src=rx.get_upload_url(AppState.profile_info.avatar_url),
                            fallback=rx.cond(AppState.profile_info.username, AppState.profile_info.username[0].upper(), "?"),
                            size="8"
                        ),
                        rx.upload(
                            rx.vstack(rx.icon("upload"), rx.text("Arrastra o haz clic para subir imagen")),
                            id="avatar_upload",
                            border="2px dashed var(--gray-a7)",
                            padding="3em",
                            border_radius="var(--radius-3)",
                            on_drop=AppState.handle_avatar_upload(rx.upload_files("avatar_upload")),
                            flex_grow="1",
                        ),
                        align="center", spacing="5", width="100%",
                    ),
                    rx.divider(margin_y="1.5em"),
                    rx.grid(
                        rx.card(
                            rx.form(
                                rx.vstack(
                                    rx.heading("Información General", size="6"),
                                    rx.text("Nombre de Usuario"),
                                    rx.input(name="username", value=AppState.profile_username, on_change=AppState.set_profile_username, required=True),
                                    rx.text("Email (no se puede cambiar)"),
                                    rx.input(name="email", value=AppState.profile_info.email, is_disabled=True),
                                    rx.text("Teléfono"),
                                    rx.input(name="phone", value=AppState.profile_phone, on_change=AppState.set_profile_phone),
                                    rx.button("Guardar Cambios", type="submit", margin_top="1em"),
                                    align_items="stretch", spacing="3",
                                ),
                                on_submit=AppState.handle_profile_update,
                            )
                        ),
                        rx.card(
                            rx.form(
                                rx.vstack(
                                    rx.heading("Cambiar Contraseña", size="6"),
                                    rx.text("Contraseña Actual"),
                                    password_input(name="current_password", required=True),
                                    rx.text("Nueva Contraseña"),
                                    password_input(name="new_password", required=True),
                                    rx.text("Confirmar Nueva Contraseña"),
                                    password_input(name="confirm_password", required=True),
                                    rx.button("Actualizar Contraseña", type="submit", margin_top="1em"),
                                    align_items="stretch", spacing="3",
                                ),
                                on_submit=AppState.handle_password_change,
                            )
                        ),
                        columns={"initial": "1", "md": "2"}, spacing="5", width="100%",
                    ),
                    rx.divider(margin_y="2em"),
                    rx.card(
                        rx.form(
                            rx.vstack(
                                rx.heading("Zona de Peligro", color_scheme="red", size="6"),
                                rx.text("Una vez que elimines tu cuenta, no hay vuelta atrás. Por favor, ten la certeza."),
                                rx.text("Confirma tu contraseña para continuar:", margin_top="1em"),
                                password_input(name="password", placeholder="Contraseña actual...", required=True),
                                rx.alert_dialog.root(
                                    rx.alert_dialog.trigger(rx.button("Eliminar mi Cuenta Permanentemente", color_scheme="red", type="button")),
                                    rx.alert_dialog.content(
                                        rx.alert_dialog.title("¿Estás absolutamente seguro?"),
                                        rx.alert_dialog.description("Esta acción es irreversible y eliminará todos tus datos."),
                                        rx.flex(
                                            rx.alert_dialog.cancel(rx.button("Cancelar", variant="soft")),
                                            rx.alert_dialog.action(rx.button("Sí, eliminar mi cuenta", type="submit")),
                                            spacing="3", margin_top="1em", justify="end",
                                        ),
                                    ),
                                ),
                                align_items="start", spacing="4",
                            ),
                            on_submit=AppState.handle_account_deletion,
                        ),
                        style={"border": "1px solid var(--red-a7)"}
                    ),
                    spacing="6", width="100%", max_width="1200px",
                ),
            )
        )
    )

    # Condición principal: si es admin, redirige; si no, muestra el perfil de cliente.
    return rx.cond(
        AppState.is_admin,
        admin_redirect_view,
        client_profile_view
    )