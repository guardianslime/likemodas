# full_stack_python/auth/state.py

import reflex as rx
import reflex_local_auth
from sqlmodel import select
from typing import Optional

from ..models import UserInfo

class SessionState(reflex_local_auth.LocalAuthState):
    """La clase de estado de la sesión para la aplicación."""

    my_userinfo: Optional[UserInfo] = None
    my_userinfo_id: Optional[int] = None

    @rx.var
    def authenticated_username(self) -> str | None:
        """Devuelve el nombre de usuario de la sesión autenticada."""
        if self.authenticated_user:
            return self.authenticated_user.username
        return None

    @rx.var
    def authenticated_user_info(self) -> UserInfo | None:
        """Devuelve la información del usuario de la sesión autenticada."""
        if self.is_authenticated and self.my_userinfo:
            return self.my_userinfo
        return None
    
    def on_load(self):
        """
        Carga la información del usuario (UserInfo) si hay una sesión autenticada.
        Este evento debe ser llamado en las páginas que requieren datos del usuario.
        """
        if not self.is_authenticated or not self.user_id:
            return
        
        # Evita recargar los datos si ya los tenemos
        if self.my_userinfo is not None and self.my_userinfo.user_id == self.user_id:
            return

        with rx.session() as session:
            result = session.exec(
                select(UserInfo).where(UserInfo.user_id == self.user_id)
            ).one_or_none()
            if result:
                self.my_userinfo = result
                self.my_userinfo_id = result.id
            else:
                self.my_userinfo = None
                self.my_userinfo_id = None