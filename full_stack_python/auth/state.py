# =================================================================
# ARCHIVO 2: full_stack_python/auth/state.py (Corregido)
# =================================================================
from typing import Optional
import reflex as rx
import reflex_local_auth
import sqlmodel

# ¡CORRECCIÓN! Se usan importaciones absolutas.
from full_stack_python.models import UserInfo

class SessionState(reflex_local_auth.LocalAuthState):
    """Estado de la sesión del usuario."""
    
    user_info: Optional[UserInfo] = None

    @rx.var
    def authenticated_user_info(self) -> Optional[UserInfo]:
        """Devuelve la información del perfil del usuario autenticado."""
        return self.user_info

    @rx.var
    def authenticated_username(self) -> Optional[str]:
        """Devuelve el nombre de usuario si está autenticado."""
        if self.is_authenticated:
            return self.authenticated_user.username
        return None

    def on_load(self):
        """Verifica la autenticación y carga los datos del perfil del usuario."""
        if not self.is_authenticated:
            return rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)
        
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
        self.user_info = None
        self.do_logout()
        return rx.redirect("/")

class MyRegisterState(reflex_local_auth.RegistrationState):
    """Maneja el registro de un nuevo usuario y su perfil."""

    def handle_registration_email(self, form_data: dict):
        """Maneja el registro del usuario y su perfil asociado."""
        username = form_data.get("username")
        password = form_data.get("password")
        
        validation_errors = self._validate_fields(
            username, password, form_data.get("confirm_password")
        )
        if validation_errors:
            return validation_errors
        
        if not self._register_user(username, password):
            return 
        
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
                return type(self).successful_registration
            except Exception as e:
                print(f"Error crítico: No se pudo crear el UserInfo. Error: {e}")
                self.error_message = "Error al crear el perfil de usuario."
                return

