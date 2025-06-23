# -----------------------------------------------------------------
# full_stack_python/auth/state.py (VERSIÓN CORREGIDA)
# -----------------------------------------------------------------
from typing import Optional
import reflex as rx
import reflex_local_auth
import sqlmodel

from ..models import UserInfo

class SessionState(reflex_local_auth.LocalAuthState):
    """
    Estado de la sesión del usuario.
    
    Este estado sigue el patrón recomendado:
    1. Carga datos de la BD en un evento (on_load).
    2. Almacena los datos en una variable de estado simple (self.user_info).
    3. Usa @rx.var para leer de esa variable de estado, sin acceder a la BD.
    """
    
    # Variable de estado para guardar la información del perfil del usuario.
    user_info: Optional[UserInfo] = None

    @rx.var
    def authenticated_user_info(self) -> Optional[UserInfo]:
        """Devuelve la información del perfil del usuario autenticado. Es rápido y seguro."""
        return self.user_info

    @rx.var
    def authenticated_username(self) -> Optional[str]:
        """Devuelve el nombre de usuario si está autenticado."""
        if self.is_authenticated:
            return self.authenticated_user.username
        return None

    def on_load(self):
        """
        Verifica la autenticación y carga los datos del perfil del usuario si es necesario.
        Se debe llamar en el `on_load` de las páginas protegidas.
        """
        if not self.is_authenticated:
            return rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)
        
        # Si estamos autenticados pero no hemos cargado el perfil, lo hacemos ahora.
        if self.user_info is None and self.authenticated_user.id >= 0:
            try:
                with rx.session() as session:
                    result = session.exec(
                        sqlmodel.select(UserInfo).where(
                            UserInfo.user_id == self.authenticated_user.id
                        )
                    ).one_or_none()
                    self.user_info = result
            except Exception as e:
                print(f"Error al cargar el perfil de usuario (UserInfo): {e}")

    def perform_logout(self):
        """Cierra la sesión y limpia el estado."""
        self.user_info = None  # Limpia la información del perfil
        self.do_logout()
        return rx.redirect("/")

class MyRegisterState(reflex_local_auth.RegistrationState):
    """Maneja el registro de un nuevo usuario y su perfil."""

    def handle_registration_email(self, form_data: dict):
        """
        Maneja el envío del formulario, valida, crea el usuario base
        y luego crea el perfil de usuario (UserInfo).
        """
        username = form_data.get("username")
        password = form_data.get("password")
        
        # Valida los campos del formulario
        validation_errors = self._validate_fields(
            username, password, form_data.get("confirm_password")
        )
        if validation_errors:
            return validation_errors
        
        # Registra el usuario en la tabla `LocalUser`
        if not self._register_user(username, password):
            # self.error_message ya lo establece _register_user en caso de fallo
            return 
        
        # Si el usuario se creó correctamente, crea el perfil en `UserInfo`
        if self.new_user_id >= 0:
            try:
                with rx.session() as session:
                    session.add(
                        UserInfo(
                            email=form_data.get("email", ""),
                            user_id=self.new_user_id,
                        )
                    )
                    session.commit()
                # Si todo sale bien, procede al flujo de registro exitoso
                return type(self).successful_registration
            except Exception as e:
                # Si falla la creación del perfil, debemos manejarlo
                print(f"Error crítico: No se pudo crear el UserInfo para el nuevo usuario. Error: {e}")
                self.error_message = "Error al crear el perfil de usuario. Contacte al soporte."
                # Opcional: Podrías querer eliminar el LocalUser recién creado para mantener la consistencia.
                return