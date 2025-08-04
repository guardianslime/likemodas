# likemodas/auth/state.py

import re
import reflex as rx
import reflex_local_auth
import sqlmodel
from ..models import UserInfo, UserRole, VerificationToken
from ..services.email_service import send_verification_email
from datetime import datetime, timedelta
from ..utils.validators import validate_password
import secrets
from ..data.product_options import (
    LISTA_TIPOS_ROPA, LISTA_TIPOS_ZAPATOS, LISTA_TIPOS_MOCHILAS, LISTA_TIPOS_GENERAL,
    LISTA_COLORES, LISTA_TALLAS_ROPA, LISTA_NUMEROS_CALZADO, LISTA_MATERIALES, LISTA_MEDIDAS_GENERAL
)

class SessionState(reflex_local_auth.LocalAuthState):
    """
    El estado base para la sesión, autenticación y datos globales compartidos.
    Todos los demás estados de la aplicación heredarán de este.
    """
    # Notificación global para el admin
    new_purchase_notification: bool = False

    # Estados de los filtros
    min_price: str = ""
    max_price: str = ""
    show_filters: bool = False
    current_category: str = ""
    filter_color: str = ""
    filter_talla: str = ""
    filter_tipo_prenda: str = ""
    filter_numero_calzado: str = ""
    filter_tipo_zapato: str = ""
    filter_tipo_mochila: str = ""
    filter_tipo_general: str = ""
    filter_material_tela: str = ""
    filter_medida_talla: str = ""
    
    search_tipo_prenda: str = ""
    search_tipo_zapato: str = ""
    search_tipo_mochila: str = ""
    search_tipo_general: str = ""
    search_color: str = ""
    search_talla: str = ""
    search_numero_calzado: str = ""
    search_material_tela: str = ""
    search_medida_talla: str = ""

    open_filter_name: str = ""

    @rx.event
    def notify_admin_of_new_purchase(self):
        """
        Evento central que activa la notificación de nueva compra para el admin.
        Al estar en el estado base, cualquier sub-estado puede llamarlo.
        """
        self.new_purchase_notification = True

    @rx.var(cache=True)
    def my_userinfo_id(self) -> str | None: 
        if self.authenticated_user_info is None:
            return None
        return str(self.authenticated_user_info.id)

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

class MyRegisterState(reflex_local_auth.RegistrationState): 
    def handle_registration_email(self, form_data):
        registration_event = self.handle_registration(form_data)
        
        if self.new_user_id >= 0:
            with rx.session() as session:
                is_admin_user = form_data.get("username") == "guardiantlemor01"
                user_role = UserRole.ADMIN if is_admin_user else UserRole.CUSTOMER
                
                new_user_info = UserInfo(
                    email=form_data["email"],
                    user_id=self.new_user_id,
                    role=user_role
                )
                session.add(new_user_info)
                session.commit()
                session.refresh(new_user_info)

                token_str = secrets.token_urlsafe(32)
                expires = datetime.utcnow() + timedelta(hours=24)
                
                verification_token = VerificationToken(
                    token=token_str,
                    userinfo_id=new_user_info.id,
                    expires_at=expires
                )
                session.add(verification_token)
                session.commit()
                
                send_verification_email(
                    recipient_email=new_user_info.email,
                    token=token_str
                )
        return registration_event