# likemodas/account/profile_page.py

import reflex as rx
import reflex_local_auth

from likemodas.models import EmploymentRequest
from ..state import AppState
from ..account.layout import account_layout
from ..ui.password_input import password_input

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
                    rx.button("Verificar y Activar", type="submit", color_scheme="violet"),
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

def seccion_solicitudes_empleo() -> rx.Component:
    """Componente para mostrar las solicitudes de empleo recibidas."""
    
    def solicitud_card(req: EmploymentRequest) -> rx.Component:
        """Card individual para una solicitud de empleo."""
        return rx.card(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "Solicitud de empleo recibida de:",
                        size="2", color_scheme="gray"
                    ),
                    rx.hstack( # Usamos hstack para alinear nombre y fecha
                        rx.text(
                            rx.cond(
                                req.requester & req.requester.user,
                                req.requester.user.username,
                                "Vendedor Desconocido"
                            ),
                            weight="bold"
                        ),
                        rx.spacer(),
                        # --- ✨ CORRECCIÓN AQUÍ: Usamos la nueva propiedad formateada ---
                        rx.text(req.created_at_formatted, size="2", color_scheme="gray"),
                    ),
                    align_items="start"
                ),
                rx.spacer(),
                rx.hstack(
                    rx.button("Rechazar", on_click=AppState.responder_solicitud_empleo(req.id, False), color_scheme="red", variant="soft"),
                    rx.button("Aceptar", on_click=AppState.responder_solicitud_empleo(req.id, True), color_scheme="green"),
                )
            )
        )

    return rx.cond(
        AppState.solicitudes_de_empleo_recibidas,
        rx.vstack(
            rx.heading("Solicitudes de Empleo Pendientes", size="6"),
            rx.foreach(AppState.solicitudes_de_empleo_recibidas, solicitud_card),
            spacing="4",
            width="100%"
        )
    )

@reflex_local_auth.require_login
def profile_page_content() -> rx.Component:
    """Página de CLIENTE para gestionar perfil, con estética mejorada y sección 2FA."""
    admin_redirect_view = rx.center(
        rx.vstack(rx.spinner(size="3"), rx.text("Redirigiendo...")),
        min_height="85vh", on_mount=rx.redirect("/admin/profile"),
    )

    security_section = rx.card(
        rx.vstack(
            rx.hstack(rx.icon("shield-check", size=24), rx.heading("Seguridad de la Cuenta", size="6")),
            rx.text("Activa la autenticación de dos factores (2FA) para una capa extra de protección.", color_scheme="gray"),
            rx.divider(),
            rx.cond(
                AppState.profile_info.tfa_enabled,
                rx.hstack(
                    rx.badge("2FA Activada", color_scheme="green", variant="soft", size="2"),
                    rx.alert_dialog.root(
                        rx.alert_dialog.trigger(rx.button("Desactivar", color_scheme="red", variant="soft")),
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
                    align="center", justify="between", width="100%",
                ),
                rx.hstack(
                    rx.badge("2FA Inactiva", color_scheme="orange", variant="soft", size="2"),
                    rx.button("Activar Ahora", on_click=AppState.start_tfa_activation, color_scheme="violet", size="2"),
                    align="center", justify="between", width="100%",
                )
            ),
            spacing="4", width="100%",
        )
    )

    danger_zone = rx.card(
        rx.form(
            rx.vstack(
                rx.hstack(rx.icon("triangle-alert", color_scheme="red", size=24), rx.heading("Zona de Peligro", color_scheme="red", size="6")),
                rx.text("La eliminación de tu cuenta es permanente. Esta acción no se puede deshacer.", color_scheme="gray"),
                rx.divider(border_color="var(--red-a6)"),
                rx.text("Confirma tu contraseña para proceder:", margin_top="1em"),
                password_input(name="password", placeholder="Contraseña actual...", required=True),
                rx.alert_dialog.root(
                    rx.alert_dialog.trigger(rx.button("Eliminar mi Cuenta Permanentemente", color_scheme="red", type="button", width="100%")),
                    rx.alert_dialog.content(
                        rx.alert_dialog.title("¿Estás absolutamente seguro?"),
                        rx.alert_dialog.description("Todos tus datos, compras y comentarios serán eliminados para siempre."),
                        rx.flex(
                            rx.alert_dialog.cancel(rx.button("Cancelar", variant="soft")),
                            rx.alert_dialog.action(rx.button("Sí, entiendo, eliminar mi cuenta", type="submit")),
                            spacing="3", margin_top="1em", justify="end",
                        ),
                    ),
                ),
                align="start", spacing="4",
            ),
            on_submit=AppState.handle_account_deletion,
        ),
        style={"border": "1px solid var(--red-a7)"}
    )
    
    client_profile_view = account_layout(
        rx.vstack(
            rx.heading("Mi Perfil", size="8", width="100%", text_align="center"),
            rx.text("Gestiona tu información personal y de seguridad.", size="4", color_scheme="gray", width="100%", text_align="center"),
            rx.divider(margin_y="1.5em"),
            rx.card(
                rx.vstack(
                    rx.heading("Imagen de Perfil", size="6"),
                    rx.hstack(
                        rx.avatar(src=rx.get_upload_url(AppState.profile_info.avatar_url), fallback=rx.cond(AppState.profile_info.username, AppState.profile_info.username[0].upper(), "?"), size="8"),
                        rx.upload(
                            rx.vstack(rx.icon("upload"), rx.text("Arrastra o haz clic para subir imagen")),
                            id="avatar_upload", border="2px dashed var(--gray-a7)", padding="2.5em",
                            on_drop=AppState.handle_avatar_upload(rx.upload_files("avatar_upload")),
                            flex_grow="1",
                        ),
                        align="center", spacing="5", width="100%",
                    ),
                    spacing="5", width="100%",
                )
            ),
            rx.grid(
                rx.card(rx.form(rx.vstack(rx.heading("Información General", size="6"), rx.text("Nombre de Usuario"), rx.input(name="username", value=AppState.profile_username, on_change=AppState.set_profile_username, required=True), rx.text("Email (no se puede cambiar)"), rx.input(name="email", value=AppState.profile_info.email, is_disabled=True), rx.text("Teléfono"), rx.input(name="phone", value=AppState.profile_phone, on_change=AppState.set_profile_phone), rx.spacer(), rx.button("Guardar Cambios", type="submit", margin_top="1em", color_scheme="violet"), align_items="stretch", spacing="3", height="100%"), on_submit=AppState.handle_profile_update, height="100%"), height="100%"),
                rx.card(rx.form(rx.vstack(rx.heading("Cambiar Contraseña", size="6"), rx.text("Contraseña Actual"), password_input(name="current_password", required=True), rx.text("Nueva Contraseña"), password_input(name="new_password", required=True), rx.text("Confirmar Nueva Contraseña"), password_input(name="confirm_password", required=True), rx.spacer(), rx.button("Actualizar Contraseña", type="submit", margin_top="1em", color_scheme="violet"), align_items="stretch", spacing="3", height="100%"), on_submit=AppState.handle_password_change, height="100%"), height="100%"),
                columns={"initial": "1", "md": "2"}, spacing="5", width="100%",
            ),
            security_section,
            seccion_solicitudes_empleo(),
            danger_zone,
            spacing="5", 
            width="100%", 
            max_width="1200px", 
            align="center",
        )
    )

    return rx.fragment(
        rx.cond(AppState.is_admin, admin_redirect_view, client_profile_view),
        tfa_activation_modal()
    )