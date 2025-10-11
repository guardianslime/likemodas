# likemodas/admin/profile_page.py

import reflex as rx
from ..state import AppState
from ..ui.base import base_page
from ..ui.password_input import password_input
# --- ✨ INICIO: AÑADE ESTAS DOS LÍNEAS DE IMPORTACIÓN ✨ ---
from ..account.profile_page import tfa_activation_modal
from ..account.profile_page import seccion_solicitudes_empleo # <--- Importa la sección
# --- ✨ FIN: AÑADE ESTAS DOS LÍNEAS DE IMPORTACIÓN ✨ ---

# ✨ --- NUEVO COMPONENTE PARA LA OPCIÓN DE RENUNCIAR --- ✨
def renounce_seller_section() -> rx.Component:
    """
    Una sección de "Zona de Peligro" específica para que los vendedores
    puedan renunciar a su rol.
    """
    return rx.card(
        rx.vstack(
            rx.hstack(rx.icon("user-minus", color_scheme="orange", size=24), rx.heading("Volver a ser Cliente", color_scheme="orange", size="6")),
            rx.text(
                "Si decides dejar de ser vendedor, perderás acceso al panel de gestión y tus publicaciones se ocultarán. Esta acción es irreversible y solo un administrador podrá concederte el rol de vendedor nuevamente.",
                color_scheme="gray",
            ),
            rx.divider(border_color="var(--orange-a6)"),
            rx.alert_dialog.root(
                rx.alert_dialog.trigger(
                    rx.button("Quiero dejar de ser Vendedor", color_scheme="orange", variant="soft", width="100%", margin_top="1em")
                ),
                rx.alert_dialog.content(
                    rx.alert_dialog.title("¿Estás seguro?"),
                    rx.alert_dialog.description(
                        "Esta acción no se puede deshacer. Para volver a ser vendedor, necesitarás la aprobación de un administrador."
                    ),
                    rx.flex(
                        rx.alert_dialog.cancel(rx.button("Cancelar")),
                        rx.alert_dialog.action(
                            rx.button("Sí, entiendo, continuar", on_click=AppState.renounce_seller_role, color_scheme="red")
                        ),
                        spacing="3", margin_top="1em", justify="end",
                    ),
                ),
            ),
            align="start", spacing="4",
        ),
        style={"border": "1px solid var(--orange-a7)"}
    )

def admin_profile_page_content() -> rx.Component:
    """Página de perfil para administradores con mejoras estéticas y de alineación."""

    security_section = rx.card(
        rx.vstack(
            rx.heading("Seguridad de la Cuenta", size="6"),
            rx.text("Gestiona la autenticación de dos factores (2FA) para proteger tu cuenta."),
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
                    align_items="start", width="100%",
                ),
                rx.vstack(
                    rx.callout.root(rx.callout.icon(rx.icon("shield-alert")), rx.callout.text("2FA no está activa."), color_scheme="orange"),
                    rx.button("Activar 2FA", on_click=AppState.start_tfa_activation, margin_top="1em", color_scheme="violet"),
                    align_items="start", width="100%",
                )
            ),
            spacing="4", width="100%",
        )
    )

    page_content = rx.vstack(
        rx.vstack(
            # ✨ --- INICIO DE LA CORRECCIÓN DEL TÍTULO --- ✨
            rx.heading(
                rx.cond(
                    AppState.is_admin, 
                    "Perfil de Administrador", 
                    "Perfil de Vendedor"
                ), 
                size="8", 
                text_align="center", 
                width="100%"
            ),
            # ✨ --- FIN DE LA CORRECCIÓN DEL TÍTULO --- ✨
            rx.text(
                "Gestiona tu información personal y de seguridad para la plataforma.",
                size="4", color_scheme="gray", text_align="center", width="100%"
            ),
            # --- FIN DE LA CORRECCIÓN 1 ---
            rx.divider(margin_y="1em"),
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
                rx.card(
                    rx.form(
                        rx.vstack(
                            rx.heading("Información General", size="6"),
                            rx.text("Nombre de Usuario"),
                            rx.input(name="username", value=AppState.profile_username, on_change=AppState.set_profile_username, required=True),
                            rx.text("Email (no se puede cambiar)"),
                            rx.input(name="email", value=AppState.profile_info.email, is_disabled=True),
                            rx.text("Teléfono de Contacto"),
                            rx.input(name="phone", value=AppState.profile_phone, on_change=AppState.set_profile_phone),
                            # --- 3. AÑADIR SPACER PARA ALINEAR BOTONES ---
                            rx.spacer(),
                            # --- 2. CAMBIAR COLOR DE BOTONES ---
                            rx.button("Guardar Cambios", type="submit", margin_top="1em", color_scheme="violet"),
                            align_items="stretch", spacing="3", height="100%",
                        ),
                        on_submit=AppState.handle_profile_update, height="100%",
                    ),
                    height="100%",
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
                            # --- 3. AÑADIR SPACER PARA ALINEAR BOTONES ---
                            rx.spacer(),
                            # --- 2. CAMBIAR COLOR DE BOTONES ---
                            rx.button("Actualizar Contraseña", type="submit", margin_top="1em", color_scheme="violet"),
                            align_items="stretch", spacing="3", height="100%",
                        ),
                        on_submit=AppState.handle_password_change, height="100%",
                    ),
                    height="100%",
                ),
                columns={"initial": "1", "lg": "2"}, spacing="5", width="100%",
            ),
            security_section,
            seccion_solicitudes_empleo(),

            # ✨ --- INICIO DE LA CORRECCIÓN --- ✨
            # Esta nueva sección solo se mostrará si el usuario es un Vendedor.
            rx.cond(
                AppState.is_vendedor,
                renounce_seller_section()
            ),
            # ✨ --- FIN DE LA CORRECCIÓN --- ✨
            
            spacing="5", width="100%", max_width="1200px",
        ),
        align="center", width="100%", padding_y="2em"
    )

    return rx.fragment(
        base_page(page_content),
        tfa_activation_modal()
    )