# likemodas/auth/forms.py (Función `my_register_form` limpia)

import reflex as rx
import reflex_local_auth
from reflex_local_auth.pages.components import input_100w, MIN_WIDTH
from ..ui.password_input import password_input
from ..state import AppState

def register_error() -> rx.Component:
    """Muestra errores de registro leyendo desde AppState."""
    return rx.cond(
        AppState.error_message != "",
        rx.callout(
            rx.text(
                AppState.error_message,
                white_space="pre-wrap"
            ),
            icon="triangle_alert",
            color_scheme="red",
            role="alert",
            width="100%",
        ),
    )

def my_register_form() -> rx.Component:
    """El formulario de registro, ahora con enlaces a políticas."""
    return rx.form(
        rx.vstack(
            rx.heading("Crear una Cuenta", size="7"),
            register_error(),
            rx.text("Nombre de usuario"),
            input_100w("username"),
            rx.text("Email"),
            input_100w("email", type='email'),
            rx.text("Contraseña"),
            password_input(placeholder="Password", name="password"),
            rx.text("Confirmar Contraseña"),
            password_input(placeholder="Confirm password", name="confirm_password"),
            
            # --- ✨ INICIO: CÓDIGO A AÑADIR ✨ ---
            rx.text(
                "Al hacer clic en 'Crear Cuenta', aceptas nuestros ",
                rx.link("Términos y Condiciones", href="/terms", color_scheme="violet", is_external=False),
                " y confirmas que has leído nuestra ",
                rx.link("Política de Privacidad", href="/privacy", color_scheme="violet", is_external=False),
                ".",
                size="2",
                color_scheme="gray",
                text_align="center",
                margin_y="1em",
            ),
            # --- ✨ FIN ✨ ---
            
            rx.button("Crear Cuenta", width="100%", type="submit", color_scheme="violet"),
            rx.center(
                rx.link("¿Ya tienes cuenta? Inicia sesión", on_click=lambda: rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE), color_scheme="violet"),
                width="100%",
                padding_top="1em" # Añadido para dar más espacio
            ),
            min_width=MIN_WIDTH,
        ),
        on_submit=AppState.handle_registration_email,
        reset_on_submit=True,
    )