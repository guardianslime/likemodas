# full_stack_python/auth/state.py (CORREGIDO Y COMPLETO)

import reflex as rx
import reflex_local_auth
import sqlmodel
from ..models import UserInfo, UserRole 

class SessionState(reflex_local_auth.LocalAuthState):

    @rx.var(cache=True)
    def my_userinfo_id(self) -> str | None: 
        if self.authenticated_user_info is None:
            return None
        return str(self.authenticated_user_info.id)

    @rx.var(cache=True)
    def my_user_id(self) -> str | None: 
        if not self.authenticated_user or self.authenticated_user.id < 0:
            return None
        return str(self.authenticated_user.id)

    @rx.var(cache=True)
    def authenticated_username(self) -> str | None: 
        if not self.authenticated_user or self.authenticated_user.id < 0:
            return None
        return self.authenticated_user.username

    @rx.var(cache=True)
    def authenticated_user_info(self) -> UserInfo | None: 
        if not self.authenticated_user or self.authenticated_user.id < 0:
            return None
        with rx.session() as session:
            result = session.exec(
                sqlmodel.select(UserInfo).where(
                    UserInfo.user_id == self.authenticated_user.id
                )
            ).one_or_none()
            return result

    @rx.var
    def is_admin(self) -> bool:
        return self.authenticated_user_info is not None and self.authenticated_user_info.role == UserRole.ADMIN

    @rx.var
    def is_customer(self) -> bool:
        return self.authenticated_user_info is not None and self.authenticated_user_info.role == UserRole.CUSTOMER
    
    def on_load(self):
        if not self.is_authenticated:
            return reflex_local_auth.LoginState.redir
        print("Autenticado:", self.is_authenticated)
        print("UserInfo:", self.authenticated_user_info)

    def perform_logout(self):
        self.do_logout()
        return rx.redirect("/")


class MyRegisterState(reflex_local_auth.RegistrationState): 
    def handle_registration(self, form_data) -> rx.event.EventSpec | list[rx.event.EventSpec]: # type: ignore 
        username = form_data["username"]
        password = form_data["password"]
        validation_errors = self._validate_fields(
            username, password, form_data["confirm_password"]
        )
        if validation_errors:
            self.new_user_id = -1
            return validation_errors
        self._register_user(username, password) 
        return type(self).successful_registration

    def handle_registration_email(self, form_data):
        registration_event = self.handle_registration(form_data)
        
        if self.new_user_id >= 0:
            with rx.session() as session:
                
                # --- ✨ LÓGICA DE ADMIN ÚNICO AÑADIDA AQUÍ ---
                # Comprueba si el nombre de usuario es el del admin
                is_admin_user = form_data.get("username") == "guardiantlemor01"
                user_role = UserRole.ADMIN if is_admin_user else UserRole.CUSTOMER
                
                session.add(
                    UserInfo(
                        email=form_data["email"],
                        user_id=self.new_user_id,
                        # Asigna el rol correspondiente
                        role=user_role
                    )
                )
                session.commit()
        return registration_event