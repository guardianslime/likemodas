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
from ..data.product_options import LISTA_TIPOS_ROPA, LISTA_TIPOS_ZAPATOS, LISTA_TIPOS_MOCHILAS, LISTA_TIPOS_GENERAL


def validate_password(password: str) -> list[str]:
    """
    Valida que una contraseña cumpla con los requisitos de seguridad.
    Devuelve una lista de errores. Si la lista está vacía, la contraseña es válida.
    """
    errors = []
    if len(password) < 8:
        errors.append("Debe tener al menos 8 caracteres.")
    if not re.search(r"\d", password):
        errors.append("Debe contener al menos un número.")
    if not re.search(r"[A-Z]", password):
        errors.append("Debe contener al menos una letra mayúscula.")
    
    return errors

class SessionState(reflex_local_auth.LocalAuthState):
    new_purchase_notification: bool = False
    min_price: str = ""
    max_price: str = ""
    show_filters: bool = False
    current_category: str = ""

    # --- ✨ NEW STATE VARIABLES FOR FILTERS ---
    filter_color: str = ""
    filter_talla: str = ""
    filter_tipo_prenda: str = ""
    filter_numero_calzado: str = ""
    filter_tipo_zapato: str = ""
    filter_tipo_mochila: str = ""

    # --- ✨ NUEVOS ESTADOS PARA FILTROS GENERALES ---
    filter_tipo_general: str = ""
    filter_material_tela: str = ""
    filter_medida_talla: str = ""
    
    # --- ✨ NUEVOS ESTADOS PARA LA BÚSQUEDA EN FILTROS ---
    search_tipo_prenda: str = ""
    search_tipo_zapato: str = ""
    search_tipo_mochila: str = ""
    search_tipo_general: str = ""

    open_filter_name: str = ""

    # --- ✨ NEW EVENT HANDLERS FOR FILTERS ---
    def set_filter_color(self, value: str): self.filter_color = value
    def set_filter_talla(self, value: str): self.filter_talla = value
    def set_filter_tipo_prenda(self, value: str): self.filter_tipo_prenda = value
    def set_filter_numero_calzado(self, value: str): self.filter_numero_calzado = value
    def set_filter_tipo_zapato(self, value: str): self.filter_tipo_zapato = value
    def set_filter_tipo_mochila(self, value: str): self.filter_tipo_mochila = value

    # --- ✨ NUEVOS EVENT HANDLERS PARA FILTROS GENERALES ---
    def set_filter_tipo_general(self, value: str): self.filter_tipo_general = value
    def set_filter_material_tela(self, value: str): self.filter_material_tela = value
    def set_filter_medida_talla(self, value: str): self.filter_medida_talla = value

    # --- ✨ NUEVOS EVENT HANDLERS PARA BÚSQUEDA EN FILTROS ---
    def set_search_tipo_prenda(self, query: str): self.search_tipo_prenda = query
    def set_search_tipo_zapato(self, query: str): self.search_tipo_zapato = query
    def set_search_tipo_mochila(self, query: str): self.search_tipo_mochila = query
    def set_search_tipo_general(self, query: str): self.search_tipo_general = query

    # --- ✨ NUEVAS PROPIEDADES COMPUTADAS PARA LISTAS FILTRADAS ---
    @rx.var
    def filtered_tipos_ropa(self) -> list[str]:
        if not self.search_tipo_prenda.strip():
            return LISTA_TIPOS_ROPA
        return [tipo for tipo in LISTA_TIPOS_ROPA if self.search_tipo_prenda.lower() in tipo.lower()]

    @rx.var
    def filtered_tipos_zapatos(self) -> list[str]:
        if not self.search_tipo_zapato.strip():
            return LISTA_TIPOS_ZAPATOS
        return [tipo for tipo in LISTA_TIPOS_ZAPATOS if self.search_tipo_zapato.lower() in tipo.lower()]

    @rx.var
    def filtered_tipos_mochilas(self) -> list[str]:
        if not self.search_tipo_mochila.strip():
            return LISTA_TIPOS_MOCHILAS
        return [tipo for tipo in LISTA_TIPOS_MOCHILAS if self.search_tipo_mochila.lower() in tipo.lower()]

    @rx.var
    def filtered_tipos_general(self) -> list[str]:
        if not self.search_tipo_general.strip():
            return LISTA_TIPOS_GENERAL
        return [tipo for tipo in LISTA_TIPOS_GENERAL if self.search_tipo_general.lower() in tipo.lower()]


    def toggle_filters(self):
        """Muestra u oculta el panel de filtros."""
        self.show_filters = not self.show_filters

    @rx.event
    def toggle_filter_dropdown(self, filter_name: str):
        """Abre un filtro o lo cierra si ya estaba abierto."""
        if self.open_filter_name == filter_name:
            self.open_filter_name = ""
        else:
            self.open_filter_name = filter_name

    def set_min_price(self, price: str):
        """Actualiza el valor del precio mínimo."""
        self.min_price = price.strip()

    def set_max_price(self, price: str):
        """Actualiza el valor del precio máximo."""
        self.max_price = price.strip()
    # --- FIN DE LA ADICIÓN ---
    

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
                # 1. Crear el UserInfo
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

                # ✨ --- LÓGICA DE VERIFICACIÓN AÑADIDA --- ✨
                # 2. Crear el token de verificación
                token_str = secrets.token_urlsafe(32)
                expires = datetime.utcnow() + timedelta(hours=24) # El token dura 24 horas
                
                verification_token = VerificationToken(
                    token=token_str,
                    userinfo_id=new_user_info.id,
                    expires_at=expires
                )
                session.add(verification_token)
                session.commit()
                
                # 3. Enviar el correo electrónico
                send_verification_email(
                    recipient_email=new_user_info.email,
                    token=token_str
                )
                # ✨ --- FIN DE LA LÓGICA --- ✨
                
        return registration_event
    
