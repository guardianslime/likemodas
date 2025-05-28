import reflex as rx
import reflex_local_auth

import sqlmodel

from .models import UserInfo


class SessionState(reflex_local_auth.LocalAuthState):
    @rx.var(cache=True)
    def authenticated_user_info(self) -> UserInfo | None:
        # Si no hay usuario autenticado, devuelve None.
        if self.authenticated_user.id < 0:
            return None
        with rx.session() as session:
            # Esta consulta debería traer la información de UserInfo
            # si el ID del usuario autenticado coincide con un user_id en UserInfo.
            return session.exec(
                sqlmodel.select(UserInfo).where(
                    UserInfo.user_id == self.authenticated_user.id
                ),
            ).one_or_none()
            
    @rx.event
    def on_load(self):
        # Esta es la lógica que protege la ruta.
        # Si el usuario no está autenticado, redirige a la página de login.
        if not self.is_authenticated:
            return reflex_local_auth.LoginState.redir
        
        # Estas impresiones se ejecutarán SOLO si el usuario está autenticado
        # y ha accedido a una página que tiene un on_load configurado con SessionState.on_load
        # o que usa @reflex_local_auth.require_login (que internamente llama a on_load de LocalAuthState).
        print(f"Usuario autenticado: {self.is_authenticated}")
        
        # Intenta acceder y imprimir la información de UserInfo aquí.
        # authenticated_user_info es un rx.var, Reflex lo resolverá cuando se acceda.
        if self.authenticated_user_info:
            print(f"Información de usuario (UserInfo): Email: {self.authenticated_user_info.email}")
            # Puedes imprimir otros campos si los agregaste a UserInfo, por ejemplo:
            # print(f"User Info Created At: {self.authenticated_user_info.created_at}")
        else:
            print("Información de usuario (UserInfo) no disponible para el usuario autenticado.")
        

class MyRegisterState(reflex_local_auth.RegistrationState):
    def handle_registration(self, form_data
    ) -> rx.event.EventSpec | list[rx.event.EventSpec]: # type: ignore
        username = form_data["username"]
        password = form_data["password"]
        validation_errors = self._validate_fields(
            username, password, form_data["confirm_password"]
        )
        if validation_errors:
            self.new_user_id = -1
            return validation_errors
        self._register_user(username, password)
        return self.new_user_id
        

    def handle_registration_email(self, form_data):
        new_user_id = self.handle_registration(form_data)
        if isinstance(new_user_id, int) and new_user_id >= 0:
            with rx.session() as session:
                user_info = UserInfo( # Crear la instancia de UserInfo
                    email=form_data["email"],
                    user_id=self.new_user_id,
                )
                session.add(user_info)
                session.commit()
                # Opcional pero recomendado: refrescar el objeto para asegurar que se carguen los datos de DB
                session.refresh(user_info)
                print(f"UserInfo guardado en la DB: Email: {user_info.email}, User ID: {user_info.user_id}")
        return type(self).successful_registration