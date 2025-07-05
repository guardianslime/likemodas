# full_stack_python/auth/state.py

import reflex as rx
import reflex_local_auth
import sqlmodel
from ..models import UserInfo

# La línea 'from ..auth.state import SessionState' se ha eliminado porque es una auto-importación incorrecta.

class SessionState(reflex_local_auth.LocalAuthState):
    """Estado de la sesión que maneja la información del usuario autenticado."""

    @rx.var(cache=True)
    def my_userinfo_id(self) -> str | None:
        if self.authenticated_user_info is None:
            return None
        return str(self.authenticated_user_info.id)

    @rx.var(cache=True)
    def my_user_id(self) -> str | None:
        if self.authenticated_user.id < 0:
            return None
        return str(self.authenticated_user.id)

    @rx.var(cache=True)
    def authenticated_username(self) -> str | None:
        if self.authenticated_user.id < 0:
            return None
        return self.authenticated_user.username

    @rx.var(cache=True)
    def authenticated_user_info(self) -> UserInfo | None:
        if self.authenticated_user.id < 0:
            return None
        with rx.session() as session:
            result = session.exec(
                sqlmodel.select(UserInfo).where(
                    UserInfo.user_id == self.authenticated_user.id
                ),
            ).one_or_none()
            return result
    
    def perform_logout(self):
        self.do_logout()
        return rx.redirect("/")

class MyRegisterState(reflex_local_auth.RegistrationState):
    """Estado para manejar el registro de nuevos usuarios."""
    def handle_registration_email(self, form_data: dict):
        # El método _validate_fields ya está en la clase base
        validation_errors = self._validate_fields(
            form_data["username"], form_data["password"], form_data["confirm_password"]
        )
        if validation_errors:
            return validation_errors
            
        # El método _register_user ya está en la clase base y devuelve el ID
        new_user_id = self._register_user(form_data["username"], form_data["password"])
        
        if isinstance(new_user_id, int) and new_user_id >= 0:
            with rx.session() as session:
                session.add(
                    UserInfo(
                        email=form_data["email"],
                        user_id=new_user_id,
                    )
                )
                session.commit()
        return self.successful_registration