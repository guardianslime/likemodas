# likemodas/account/profile_page.py (versión modificada)
import reflex as rx
from ..state import AppState
from ..account.layout import account_layout
from ..ui.password_input import password_input

def tfa_activation_modal() -> rx.Component:
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

def profile_page_content() -> rx.Component:
    danger_zone = rx.form(
        rx.vstack(
            rx.heading("Zona de Peligro", color_scheme="red", size="6"),
            rx.text("La eliminación de tu cuenta es permanente."),
            rx.divider(),
            rx.text("Confirma tu contraseña:"),
            password_input(name="password", required=True),
            rx.alert_dialog.root(
                rx.alert_dialog.trigger(rx.button("Eliminar mi Cuenta", color_scheme="red")),
                rx.alert_dialog.content(
                    rx.alert_dialog.title("¿Estás seguro?"),
                    rx.alert_dialog.description("Esta acción es irreversible."),
                    rx.flex(
                        rx.alert_dialog.cancel(rx.button("Cancelar")),
                        rx.alert_dialog.action(rx.button("Sí, eliminar", type="submit")),
                        spacing="3", margin_top="1em", justify="end",
                    ),
                ),
            ),
            align_items="start", spacing="4",
        ),
        on_submit=AppState.handle_account_deletion,
        border="1px solid var(--red-7)", border_radius="var(--radius-3)", padding="1.5em",
    )
    
    security_section = rx.vstack(
        rx.heading("Seguridad de la Cuenta", size="6"),
        rx.text("Gestiona la autenticación de dos factores (2FA)."),
        rx.divider(),
        rx.cond(
            AppState.profile_info.tfa_enabled,
            rx.vstack(
                rx.callout.root(rx.callout.icon(rx.icon("shield-check")), rx.callout.text("2FA está activa."), color_scheme="green"),
                rx.alert_dialog.root(
                    rx.alert_dialog.trigger(rx.button("Desactivar 2FA", color_scheme="red", variant="soft", margin_top="1em")),
                    rx.alert_dialog.content(
                        rx.alert_dialog.title("¿Desactivar 2FA?"),
                        rx.alert_dialog.description("Introduce tu contraseña para confirmar."),
                        rx.form(
                            rx.vstack(
                                password_input(name="password", required=True),
                                rx.flex(
                                    rx.alert_dialog.cancel(rx.button("Cancelar")),
                                    rx.alert_dialog.action(rx.button("Sí, desactivar", type="submit")),
                                    spacing="3", margin_top="1em", justify="end",
                                ),
                            ),
                            on_submit=AppState.disable_tfa,
                        ),
                    ),
                ),
                align_items="start",
            ),
            rx.vstack(
                rx.callout.root(rx.callout.icon(rx.icon("shield-alert")), rx.callout.text("2FA no está activa."), color_scheme="orange"),
                rx.button("Activar 2FA", on_click=AppState.start_tfa_activation, margin_top="1em"),
                align_items="start",
            )
        ),
        spacing="4", border="1px solid var(--gray-a7)", border_radius="var(--radius-3)", padding="1.5em",
    )

    page_content = rx.center(
        rx.vstack(
            rx.heading("Mi Perfil", size="8"),
            rx.text("Gestiona tu información personal y de seguridad."),
            rx.divider(margin_y="1.5em"),
            rx.heading("Imagen de Perfil", size="6"),
            rx.hstack(
                rx.avatar(src=rx.get_upload_url(AppState.profile_info.avatar_url), fallback=rx.cond(AppState.profile_info.username, AppState.profile_info.username[0].upper(), "?"), size="8"),
                rx.upload(
                    rx.vstack(rx.icon("upload"), rx.text("Arrastra una imagen aquí.")),
                    id="avatar_upload", border="2px dashed #ccc", padding="3em",
                    on_drop=AppState.handle_avatar_upload(rx.upload_files("avatar_upload")),
                ),
                align="center", spacing="5",
            ),
            rx.divider(margin_y="1.5em"),
            rx.grid(
                rx.form(
                    rx.vstack(
                        rx.heading("Información General", size="6"),
                        rx.text("Nombre de Usuario"),
                        rx.input(name="username", value=AppState.profile_username, on_change=AppState.set_profile_username, required=True),
                        rx.text("Email (no se puede cambiar)"),
                        rx.input(name="email", value=AppState.profile_info.email, is_disabled=True),
                        rx.text("Teléfono"),
                        rx.input(name="phone", value=AppState.profile_phone, on_change=AppState.set_profile_phone),
                        rx.button("Guardar Cambios", type="submit"),
                        align_items="start", spacing="4",
                    ),
                    on_submit=AppState.handle_profile_update,
                ),
                rx.form(
                    rx.vstack(
                        rx.heading("Cambiar Contraseña", size="6"),
                        rx.text("Contraseña Actual"),
                        password_input(name="current_password", required=True),
                        rx.text("Nueva Contraseña"),
                        password_input(name="new_password", required=True),
                        rx.text("Confirmar Nueva Contraseña"),
                        password_input(name="confirm_password", required=True),
                        rx.button("Actualizar Contraseña", type="submit"),
                        align_items="start", spacing="4",
                    ),
                    on_submit=AppState.handle_password_change,
                ),
                columns={"initial": "1", "md": "2"}, spacing="6",
            ),
            rx.divider(margin_y="2em"),
            security_section,
            rx.divider(margin_y="2em"),
            danger_zone,
            spacing="6", max_width="1200px",
        ),
        padding_x="1em",
    )

    return rx.fragment(
        account_layout(page_content),
        tfa_activation_modal()
    )