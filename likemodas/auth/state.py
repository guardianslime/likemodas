# likemodas/auth/state.py (CORREGIDO Y COMPLETO)

import re
import reflex as rx
import reflex_local_auth
import sqlmodel
from ..models import UserInfo, UserRole, VerificationToken
from ..services.email_service import send_verification_email
from datetime import datetime, timedelta
from ..utils.validators import validate_password
import secrets


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

    # --- ✨ NUEVAS VARIABLES PARA BÚSQUEDA EN FILTROS ---
    # Para filtros generales
    tipo_general_search: str = ""
    material_tela_search: str = ""
    medida_talla_search: str = ""
    color_search: str = ""
    
    # Para filtros específicos de Ropa
    tipo_prenda_search: str = ""
    talla_search: str = ""
    
    # Para filtros específicos de Calzado
    tipo_zapato_search: str = ""
    numero_calzado_search: str = ""
    
    # Para filtros específicos de Mochilas
    tipo_mochila_search: str = ""
    
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

    def _filter_options(self, options: list[dict], search_term: str) -> list[dict]:
        """Función auxiliar para filtrar opciones de un selector."""
        if not search_term.strip():
            return options
        # Verificamos que las opciones sean diccionarios antes de filtrar
        valid_options = [opt for opt in options if isinstance(opt, dict) and "label" in opt]
        return [
            opt for opt in valid_options
            if search_term.lower() in str(opt["label"]).lower()
        ]

    @rx.var
    def filtered_general_types(self) -> list[dict]:
        from ..cart.state import CartState
        return self._filter_options(CartState.general_available_materials, self.tipo_general_search)

    @rx.var
    def filtered_general_materials(self) -> list[dict]:
        from ..cart.state import CartState
        return self._filter_options(CartState.general_available_materials, self.material_tela_search)

    @rx.var
    def filtered_general_sizes(self) -> list[dict]:
        from ..cart.state import CartState
        return self._filter_options(CartState.general_available_sizes, self.medida_talla_search)
    
    @rx.var
    def filtered_general_colors(self) -> list[dict]:
        from ..cart.state import CartState
        return self._filter_options(CartState.general_available_colors, self.color_search)

    # --- Filtros Específicos ---
    @rx.var
    def filtered_available_colors(self) -> list[dict]:
        from ..pages.category_page import CategoryPageState
        return self._filter_options(CategoryPageState.available_colors, self.color_search)

    @rx.var
    def filtered_available_tallas(self) -> list[dict]:
        from ..pages.category_page import CategoryPageState
        return self._filter_options(CategoryPageState.available_tallas, self.talla_search)

    @rx.var
    def filtered_available_numeros(self) -> list[dict]:
        from ..pages.category_page import CategoryPageState
        return self._filter_options(CategoryPageState.available_numeros, self.numero_calzado_search)
        

    def toggle_filters(self):
        """Muestra u oculta el panel de filtros."""
        self.show_filters = not self.show_filters

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
    
