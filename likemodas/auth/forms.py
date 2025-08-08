import reflex as rx
import reflex_local_auth
from reflex_local_auth.pages.components import input_100w, MIN_WIDTH
from ..ui.password_input import password_input
from ..state import AppState

# ESTADO PERSONALIZADO PARA EL REGISTRO (COMO LO INDICA LA LIBRERÍA)
class CustomRegistrationState(reflex_local_auth.RegistrationState):
    """
    Estado que maneja el formulario de registro y llama a AppState 
    para la lógica personalizada post-registro.
    """
    def handle_registration_email(self, form_data: dict):
        """
        Valida el formulario y llama a la lógica de registro base.
        Si el registro es exitoso, delega la creación de UserInfo y el envío
        de correo electrónico al AppState principal.
        """
        # Primero, se ejecuta la lógica de registro original de la librería
        super().handle_registration(form_data)
        
        # Si el usuario se creó correctamente (new_user_id ya no es -1)
        if self.success:
            # Llama a un nuevo evento en AppState para manejar nuestras tareas personalizadas
            return AppState.post_registration_tasks(
                self.new_user_id, 
                form_data.get("email"), 
                form_data.get("username")
            )

def register_error() -> rx.Component:
    """Muestra errores de registro."""
    return rx.cond(
        reflex_local_auth.RegistrationState.error_message != "",
        rx.callout(
            rx.text(
                reflex_local_auth.RegistrationState.error_message, 
                white_space="pre-wrap"
            ),
            icon="triangle_alert",
            color_scheme="red",
            role="alert",
            width="100%",
        ),
    )

def my_register_form() -> rx.Component:
    """El formulario de registro, ahora usando el estado correcto."""
    return rx.form(
        rx.vstack(
            rx.heading("Create an account", size="7"),
            register_error(),
            rx.text("Username"),
            input_100w("username"),
            rx.text("Email"),
            input_100w("email", type='email'),
            rx.text("Password"),
            password_input(placeholder="Password", name="password"),
            rx.text("Confirm password"),
            password_input(placeholder="Confirm password", name="confirm_password"),
            rx.button("Sign up", width="100%"),
            rx.center(
                rx.link("Login", on_click=lambda: rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)),
                width="100%",
            ),
            min_width=MIN_WIDTH,
        ),
        # CAMBIO CLAVE: on_submit ahora llama al método en nuestro nuevo estado personalizado.
        on_submit=CustomRegistrationState.handle_registration_email,
    )