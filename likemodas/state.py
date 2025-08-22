from __future__ import annotations
import reflex as rx
import reflex_local_auth
import sqlmodel
import sqlalchemy
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta, timezone
import secrets
import bcrypt
import re
import asyncio
# ✨ 1. AÑADE ESTA LÍNEA DE IMPORTACIÓN AQUÍ ✨
from reflex.config import get_config
# ✨ 1. AÑADE ESTAS LÍNEAS AQUÍ ✨
from urllib.parse import urlparse, parse_qs



from . import navigation
from .models import (
    UserInfo, UserRole, VerificationToken, BlogPostModel, ShippingAddressModel,
    PurchaseModel, PurchaseStatus, PurchaseItemModel, NotificationModel, Category,
    PasswordResetToken, LocalUser, ContactEntryModel, CommentModel 
)
from .services.email_service import send_verification_email, send_password_reset_email
from .utils.formatting import format_to_cop
from .utils.validators import validate_password
from .data.colombia_locations import load_colombia_data
from .data.product_options import (
    MATERIALES_ROPA, MATERIALES_CALZADO, MATERIALES_MOCHILAS, LISTA_TIPOS_ROPA, LISTA_TIPOS_ZAPATOS, LISTA_TIPOS_MOCHILAS, LISTA_TAMANOS_MOCHILAS, LISTA_TIPOS_GENERAL,
    LISTA_COLORES, LISTA_TALLAS_ROPA, LISTA_NUMEROS_CALZADO, LISTA_MATERIALES, LISTA_MEDIDAS_GENERAL
)

class ProductCardData(rx.Base):
    id: int
    title: str
    price: float = 0.0
    price_cop: str = "" 
    image_urls: list[str] = []
    average_rating: float = 0.0
    rating_count: int = 0
    attributes: dict = {}

    class Config:
        orm_mode = True
    
    @property
    def price_cop(self) -> str:
        return format_to_cop(self.price)
    
class ProductDetailData(rx.Base):
    id: int
    title: str
    content: str
    price_cop: str
    image_urls: list[str] = []
    created_at_formatted: str
    average_rating: float = 0.0
    rating_count: int = 0
    seller_name: str = ""
    seller_id: int = 0
    attributes: dict = {}

    class Config:
        orm_mode = True

class AdminPurchaseCardData(rx.Base):
    id: int; customer_name: str; customer_email: str; purchase_date_formatted: str
    status: str; total_price: float; shipping_name: str; shipping_full_address: str
    shipping_phone: str; items_formatted: list[str]
    @property
    def total_price_cop(self) -> str:
        return format_to_cop(self.total_price)
        
class UserPurchaseHistoryCardData(rx.Base):
    id: int; purchase_date_formatted: str; status: str; total_price_cop: str
    shipping_name: str; shipping_address: str; shipping_neighborhood: str
    shipping_city: str; shipping_phone: str; items_formatted: list[str]

class AttributeData(rx.Base):
    key: str
    value: str

class CommentData(rx.Base):
    id: int
    content: str
    rating: int
    author_username: str
    author_initial: str
    created_at_formatted: str
    updates: List["CommentData"] = []

# PEGA LAS CLASES AQUÍ
class InvoiceItemData(rx.Base):
    """Un modelo específico para cada línea de artículo en la factura."""
    name: str
    quantity: int
    price: float

    @property
    def price_cop(self) -> str:
        """Propiedad computada para formatear el precio unitario."""
        return format_to_cop(self.price)

    @property
    def total_cop(self) -> str:
        """Propiedad computada para formatear el precio total del artículo."""
        return format_to_cop(self.price * self.quantity)

class InvoiceData(rx.Base):
    """DTO para contener toda la información necesaria para una factura."""
    id: int
    purchase_date_formatted: str
    status: str
    items: list[InvoiceItemData]
    customer_name: str
    customer_email: str
    shipping_full_address: str
    shipping_phone: str
    subtotal_cop: str
    total_price_cop: str


# --- ESTADO PRINCIPAL DE LA APLICACIÓN ---
class AppState(reflex_local_auth.LocalAuthState):
    """El estado único y monolítico de la aplicación."""

    _product_id_to_load_on_mount: Optional[int] = None # <-- AÑADE ESTA LÍNEA
    success: bool = False
    error_message: str = ""
    
    @rx.var(cache=True)
    def authenticated_user_info(self) -> UserInfo | None:
        if not self.is_authenticated or self.authenticated_user.id < 0:
            return None
        
        # --- ✨ INICIO DE LA CORRECCIÓN ✨ ---
        with rx.session() as session:
            # Usamos .options() con joinedload para cargar el 'user' relacionado
            # en la misma consulta.
            query = (
                sqlmodel.select(UserInfo)
                .options(sqlalchemy.orm.joinedload(UserInfo.user))
                .where(UserInfo.user_id == self.authenticated_user.id)
            )
            return session.exec(query).one_or_none()
        # --- ✨ FIN DE LA CORRECCIÓN ✨ ---

    @rx.var
    def is_admin(self) -> bool:
        return self.authenticated_user_info is not None and self.authenticated_user_info.role == UserRole.ADMIN

    def handle_registration_email(self, form_data: dict):
        self.success = False
        self.error_message = ""
        username = form_data.get("username")
        email = form_data.get("email")
        password = form_data.get("password")
        confirm_password = form_data.get("confirm_password")

        if not all([username, email, password, confirm_password]):
            self.error_message = "Todos los campos son obligatorios."
            return
        if password != confirm_password:
            self.error_message = "Las contraseñas no coinciden."
            return
        password_errors = validate_password(password)
        if password_errors:
            self.error_message = "\n".join(password_errors)
            return

        try:
            with rx.session() as session:
                if session.exec(sqlmodel.select(LocalUser).where(LocalUser.username == username)).first():
                    self.error_message = "El nombre de usuario ya está en uso."
                    return
                if session.exec(sqlmodel.select(UserInfo).where(UserInfo.email == email)).first():
                    self.error_message = "El email ya está registrado."
                    return

                password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
                new_user = LocalUser(username=username, password_hash=password_hash, enabled=True)
                session.add(new_user)
                session.commit()
                session.refresh(new_user)
                
                user_role = UserRole.ADMIN if username == "guardiantlemor01" else UserRole.CUSTOMER
                new_user_info = UserInfo(email=email, user_id=new_user.id, role=user_role)
                session.add(new_user_info)
                session.commit()
                session.refresh(new_user_info)

                token_str = secrets.token_urlsafe(32)
                expires = datetime.now(timezone.utc) + timedelta(hours=24)
                verification_token = VerificationToken(token=token_str, userinfo_id=new_user_info.id, expires_at=expires)
                session.add(verification_token)
                session.commit()
                
                send_verification_email(recipient_email=email, token=token_str)
                self.success = True
        except Exception as e:
            self.error_message = f"Error inesperado: {e}"

    message: str = ""
    @rx.event
    def verify_token(self):
        token = self.router.query_params.get("token", "")
        if not token:
            self.message = "Error: No se proporcionó un token de verificación."
            return
        
        with rx.session() as session:
            db_token = session.exec(sqlmodel.select(VerificationToken).where(VerificationToken.token == token)).one_or_none()
            if db_token and db_token.expires_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
                user_info = session.get(UserInfo, db_token.userinfo_id)
                if user_info:
                    user_info.is_verified = True
                    session.add(user_info)
                    session.delete(db_token)
                    session.commit()
                    yield rx.toast.success("¡Cuenta verificada! Por favor, inicia sesión.")
                    return rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)
            self.message = "El token de verificación es inválido o ha expirado."

    is_success: bool = False
    token: str = ""
    is_token_valid: bool = False

    def handle_forgot_password(self, form_data: dict):
        email = form_data.get("email", "")
        if not email:
            self.message, self.is_success = "Por favor, introduce tu correo electrónico.", False
            return
        with rx.session() as session:
            user_info = session.exec(sqlmodel.select(UserInfo).where(UserInfo.email == email)).one_or_none()
            if user_info:
                token_str = secrets.token_urlsafe(32)
                expires = datetime.now(timezone.utc) + timedelta(hours=1)
                reset_token = PasswordResetToken(token=token_str, user_id=user_info.user_id, expires_at=expires)
                session.add(reset_token)
                session.commit()
                send_password_reset_email(recipient_email=email, token=token_str)
        self.message, self.is_success = "Si una cuenta con ese correo existe, hemos enviado un enlace para restablecer la contraseña.", True

    def on_load_check_token(self):
        self.token = self.router.query_params.get("token", "")
        if not self.token:
            self.message, self.is_token_valid = "Enlace no válido. Falta el token.", False
            return
        with rx.session() as session:
            db_token = session.exec(sqlmodel.select(PasswordResetToken).where(PasswordResetToken.token == self.token)).one_or_none()
            if db_token and db_token.expires_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
                self.is_token_valid = True
            else:
                self.message, self.is_token_valid = "El enlace de reseteo es inválido o ha expirado.", False
                if db_token:
                    session.delete(db_token)
                    session.commit()

    def handle_reset_password(self, form_data: dict):
        password, confirm_password = form_data.get("password", ""), form_data.get("confirm_password", "")
        if not self.is_token_valid: self.message = "Token no válido."; return
        if password != confirm_password: self.message = "Las contraseñas no coinciden."; return
        password_errors = validate_password(password)
        if password_errors: self.message = "\n".join(password_errors); return
        with rx.session() as session:
            db_token = session.exec(sqlmodel.select(PasswordResetToken).where(PasswordResetToken.token == self.token)).one_or_none()
            if not db_token: self.message = "Token inválido."; return
            user = session.get(LocalUser, db_token.user_id)
            if user:
                user.password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
                session.add(user)
                session.delete(db_token)
                session.commit()
                yield rx.toast.success("¡Contraseña actualizada con éxito!")
                return rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)
            
    
    @rx.var
    def get_invoice_data(self, purchase_id: int) -> Optional[InvoiceData]:
        """
        Busca los datos de una compra y los devuelve como un DTO.
        Este método es llamado por otros estados.
        """
        if not self.is_authenticated:
            # No podemos lanzar toasts desde aquí, pero devolvemos None si no hay permisos.
            return None

        with rx.session() as session:
            purchase = session.exec(
                sqlmodel.select(PurchaseModel)
                .options(
                    sqlalchemy.orm.joinedload(PurchaseModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post)
                )
                .where(PurchaseModel.id == purchase_id)
            ).one_or_none()

            if not purchase:
                return None

            # Verificación de permisos
            if not self.is_admin and (not self.authenticated_user_info or self.authenticated_user_info.id != purchase.userinfo_id):
                return None

            invoice_items = [
                InvoiceItemData(
                    name=item.blog_post.title,
                    quantity=item.quantity,
                    price=item.price_at_purchase
                )
                for item in purchase.items if item.blog_post
            ]

            return InvoiceData(
                id=purchase.id,
                purchase_date_formatted=purchase.purchase_date_formatted,
                status=purchase.status.value,
                items=invoice_items,
                customer_name=purchase.shipping_name,
                customer_email=purchase.userinfo.email if purchase.userinfo else "N/A",
                shipping_full_address=f"{purchase.shipping_address}, {purchase.shipping_neighborhood}, {purchase.shipping_city}",
                shipping_phone=purchase.shipping_phone,
                subtotal_cop=format_to_cop(purchase.total_price),
                total_price_cop=purchase.total_price_cop,
            )
            
    # --- ✨ 2. AÑADE ESTAS DOS NUEVAS PROPIEDADES COMPUTADAS ---

    @rx.var
    def available_types(self) -> list[str]:
        """Devuelve la lista de tipos correcta según la categoría seleccionada."""
        if self.category == Category.ROPA.value:
            return LISTA_TIPOS_ROPA
        if self.category == Category.CALZADO.value:
            return LISTA_TIPOS_ZAPATOS
        if self.category == Category.MOCHILAS.value:
            return LISTA_TIPOS_MOCHILAS
        return []

    @rx.var
    def material_label(self) -> str:
        """Devuelve la etiqueta correcta ('Tela' o 'Material') para el formulario."""
        if self.category == Category.ROPA.value:
            return "Tela"
        return "Material"

    @rx.var
    def available_materials(self) -> list[str]:
        """Devuelve la lista de materiales correcta según la categoría seleccionada."""
        if self.category == Category.ROPA.value:
            return MATERIALES_ROPA
        if self.category == Category.CALZADO.value:
            return MATERIALES_CALZADO
        if self.category == Category.MOCHILAS.value:
            return MATERIALES_MOCHILAS
        return [] # Devuelve una lista vacía si no hay categoría
            
    # --- NUEVO: Variables para las características del producto ---
    # --- ✅ 1. MODIFICAR ATRIBUTOS DEL FORMULARIO DE 'str' a 'list[str]' ---
    # ANTES: attr_talla_ropa: str = ""
    attr_tallas_ropa: list[str] = []
    # ANTES: attr_numero_calzado: str = ""
    attr_numeros_calzado: list[str] = []
    # ANTES: attr_tamano_mochila: str = ""
    attr_tamanos_mochila: list[str] = []
    # Mantenemos el color y material como selección única en el formulario de creación para simplicidad
    attr_colores: list[str] = []
    attr_material: str = ""
    # --- ✨ LÍNEAS NUEVAS ---
    # Variable para guardar el tipo seleccionado en el formulario
    attr_tipo: str = ""
    # Variable para la búsqueda dentro del selector de tipo
    search_attr_tipo: str = ""

    # --- NUEVO: Event handlers para actualizar las características ---
    def set_attr_talla_ropa(self, value: str): self.attr_talla_ropa = value
    def set_attr_material(self, value: str): self.attr_material = value
    def set_attr_numero_calzado(self, value: str): self.attr_numero_calzado = value
    def set_attr_tipo(self, value: str):
        """Actualiza el tipo seleccionado en el estado del formulario."""
        self.attr_tipo = value

    def _clear_add_form(self):
        self.title = ""
        self.content = ""
        self.price = ""
        self.category = ""
        self.temp_images = []
        # --- NUEVO: Limpiar los atributos ---
        self.attr_colores = [] # <-- AHORA
        self.attr_talla_ropa = ""
        self.attr_material = ""
        self.attr_numero_calzado = ""
        self.attr_tamano_mochila = ""

    @rx.event
    def submit_and_publish(self, form_data: dict):
        if not self.is_admin: return rx.toast.error("Acción no permitida.")
        if not all([form_data.get("title"), form_data.get("price"), form_data.get("category")]):
            return rx.toast.error("Título, precio y categoría son obligatorios.")
        
        # --- NUEVO: Recopilar los atributos seleccionados ---
        attributes = {}
        category = form_data.get("category")
        if category == Category.ROPA.value:
            if self.attr_tipo: attributes["Tipo"] = self.attr_tipo
            # --- MODIFICAR LÍNEA ---
            if self.attr_colores: attributes["Color"] = self.attr_colores # <-- AHORA
            if self.attr_tallas_ropa: attributes["Talla"] = self.attr_tallas_ropa
            if self.attr_material: attributes["Tela"] = self.attr_material

        elif category == Category.CALZADO.value:
            if self.attr_tipo: attributes["Tipo"] = self.attr_tipo
            # --- MODIFICAR LÍNEA ---
            if self.attr_colores: attributes["Color"] = self.attr_colores # <-- AHORA
            if self.attr_numeros_calzado: attributes["Número"] = self.attr_numeros_calzado
            if self.attr_material: attributes["Material"] = self.attr_material
        
        elif category == Category.MOCHILAS.value:
            if self.attr_tipo: attributes["Tipo"] = self.attr_tipo
            # --- MODIFICAR LÍNEA ---
            if self.attr_colores: attributes["Color"] = self.attr_colores # <-- AHORA
            if self.attr_tamanos_mochila: attributes["Tamaño"] = self.attr_tamanos_mochila
            if self.attr_material: attributes["Material"] = self.attr_material
        
        with rx.session() as session:
            new_post = BlogPostModel(
                userinfo_id=self.authenticated_user_info.id,
                title=form_data["title"],
                content=form_data.get("content", ""),
                price=float(form_data.get("price", 0.0)),
                category=category,
                image_urls=self.temp_images,
                attributes=attributes,  # Se guardan los atributos en el campo JSON
                publish_active=True,
                publish_date=datetime.now(timezone.utc),
            )
            session.add(new_post)
            session.commit()
            session.refresh(new_post)
        self._clear_add_form()
        yield rx.toast.success("Producto publicado.")
        return rx.redirect("/blog")
    
    @rx.var
    def displayed_posts(self) -> list[ProductCardData]:
        """
        Una propiedad computada que devuelve la lista de productos
        filtrada según las selecciones del panel.
        """
        # Empezamos con todos los productos de la categoría actual
        posts_to_filter = self.posts

        # 1. Filtrar por precio
        if self.min_price:
            try:
                min_p = float(self.min_price)
                posts_to_filter = [p for p in posts_to_filter if p.price >= min_p]
            except ValueError:
                pass # Ignorar si el valor no es un número
        if self.max_price:
            try:
                max_p = float(self.max_price)
                posts_to_filter = [p for p in posts_to_filter if p.price <= max_p]
            except ValueError:
                pass

        # 2. Filtrar por color (selección múltiple)
        if self.filter_colors:
            posts_to_filter = [
                p for p in posts_to_filter 
                if p.attributes.get("Color") in self.filter_colors
            ]
            
        # 3. Filtrar por material/tela (selección múltiple)
        if self.filter_materiales_tela:
            posts_to_filter = [
                p for p in posts_to_filter 
                if (p.attributes.get("Material") in self.filter_materiales_tela) or 
                   (p.attributes.get("Tela") in self.filter_materiales_tela)
            ]

        # 4. Filtrar por talla/medida (selección múltiple y complejo)
        if self.filter_tallas:
            posts_to_filter = [
                p for p in posts_to_filter
                # El 'any' comprueba si CUALQUIERA de las tallas del producto
                # está en la lista de tallas que el usuario seleccionó.
                if any(
                    size in self.filter_tallas 
                    for size in p.attributes.get("Talla", [])
                )
            ]

            if self.filter_tipos_general:
                posts_to_filter = [
                    p for p in posts_to_filter
                    if p.attributes.get("Tipo") in self.filter_tipos_general
                ]

        return posts_to_filter
    
    # --- NUEVO: Variables para la BÚSQUEDA en características ---
    search_attr_color: str = ""
    search_attr_talla_ropa: str = ""
    search_attr_material: str = ""
    search_attr_numero_calzado: str = ""
    search_attr_tamano_mochila: str = ""

    # --- NUEVO: Event handlers para la BÚSQUEDA ---
    def set_search_attr_color(self, query: str): self.search_attr_color = query
    def set_search_attr_talla_ropa(self, query: str): self.search_attr_talla_ropa = query
    def set_search_attr_material(self, query: str): self.search_attr_material = query
    def set_search_attr_numero_calzado(self, query: str): self.search_attr_numero_calzado = query
    def set_search_attr_tipo(self, query: str):
        """Actualiza el texto de búsqueda para el selector de tipo."""
        self.search_attr_tipo = query

    # --- NUEVO: Listas filtradas para los buscadores ---
    @rx.var
    def filtered_attr_colores(self) -> list[str]:
        if not self.search_attr_color.strip(): return LISTA_COLORES
        return [o for o in LISTA_COLORES if self.search_attr_color.lower() in o.lower()]

    @rx.var
    def filtered_attr_tallas_ropa(self) -> list[str]:
        if not self.search_attr_talla_ropa.strip(): return LISTA_TALLAS_ROPA
        return [o for o in LISTA_TALLAS_ROPA if self.search_attr_talla_ropa.lower() in o.lower()]

    @rx.var
    def filtered_attr_materiales(self) -> list[str]:
        """
        Filtra la lista de materiales DISPONIBLES según el texto de búsqueda.
        """
        # ANTES: if not self.search_attr_material.strip(): return LISTA_MATERIALES
        # AHORA: Usa la nueva propiedad dinámica 'available_materials'
        if not self.search_attr_material.strip():
            return self.available_materials

        # ANTES: return [o for o in LISTA_MATERIALES if self.search_attr_material.lower() in o.lower()]
        # AHORA: También usa 'available_materials' como fuente
        return [
            o for o in self.available_materials 
            if self.search_attr_material.lower() in o.lower()
        ]

    @rx.var
    def filtered_attr_numeros_calzado(self) -> list[str]:
        if not self.search_attr_numero_calzado.strip(): return LISTA_NUMEROS_CALZADO
        return [o for o in LISTA_NUMEROS_CALZADO if self.search_attr_numero_calzado.lower() in o.lower()]

    @rx.var
    def filtered_attr_tipos(self) -> list[str]:
        """Filtra la lista de tipos disponibles según el texto de búsqueda en el formulario."""
        if not self.search_attr_tipo.strip():
            return self.available_types
        return [
            o for o in self.available_types 
            if self.search_attr_tipo.lower() in o.lower()
        ]

    min_price: str = ""
    max_price: str = ""
    show_filters: bool = False
    current_category: str = ""
    open_filter_name: str = ""
    # ANTES: filter_color: str = ""
    filter_colors: list[str] = []
    # ANTES: filter_talla: str = ""
    filter_tallas: list[str] = []
    # ANTES: filter_tipo_prenda: str = ""
    filter_tipos_prenda: list[str] = []
    # ... (Haz lo mismo para todos los filtros que quieres que sean múltiples)
    filter_tipos_zapato: list[str] = []
    filter_numeros_calzado: list[str] = []
    filter_tipos_mochila: list[str] = []
    filter_materiales_tela: list[str] = []
    filter_tipos_general: list[str] = [] # <-- ✨ AÑADE ESTA LÍNEA

    # --- ✅ 3. NUEVOS EVENT HANDLERS GENÉRICOS ---
    def add_attribute_value(self, attribute_name: str, value: str):
        """Añade un valor a una lista de atributos en el formulario de creación."""
        current_list = getattr(self, attribute_name)
        if value not in current_list:
            current_list.append(value)
            setattr(self, attribute_name, current_list)

    def remove_attribute_value(self, attribute_name: str, value: str):
        """Elimina un valor de una lista de atributos en el formulario."""
        current_list = getattr(self, attribute_name)
        if value in current_list:
            current_list.remove(value)
            setattr(self, attribute_name, current_list)

    def add_filter_value(self, filter_name: str, value: str):
        """Añade un valor a una lista de filtros, con un límite de 5."""
        current_list = getattr(self, filter_name)
        if value not in current_list:
            if len(current_list) >= 5:
                # Notifica al usuario que no puede agregar más.
                return rx.toast.info("Puedes seleccionar un máximo de 5 filtros por característica.")
            current_list.append(value)
            setattr(self, filter_name, current_list)

    def remove_filter_value(self, filter_name: str, value: str):
        """Elimina un valor de una lista de filtros."""
        current_list = getattr(self, filter_name)
        if value in current_list:
            current_list.remove(value)
            setattr(self, filter_name, current_list)

    def toggle_filters(self): self.show_filters = not self.show_filters
    def clear_all_filters(self):
        self.min_price = ""
        self.max_price = ""
        self.filter_color = ""
        self.filter_talla = ""
        self.filter_tipo_prenda = ""
        self.filter_tipo_zapato = ""
        self.filter_tipo_mochila = ""
        self.filter_tipo_general = ""
        self.filter_material_tela = ""
        self.filter_medida_talla = ""

    def toggle_filter_dropdown(self, name: str): self.open_filter_name = "" if self.open_filter_name == name else name
    def clear_filter(self, filter_name: str): setattr(self, filter_name, "")
    def set_min_price(self, price: str): self.min_price = price
    def set_max_price(self, price: str): self.max_price = price
    def set_filter_color(self, color: str): self.filter_color = color
    def set_filter_talla(self, talla: str): self.filter_talla = talla
    def set_filter_tipo_prenda(self, prenda: str): self.filter_tipo_prenda = prenda
    def set_filter_tipo_zapato(self, zapato: str): self.filter_tipo_zapato = zapato
    def set_filter_numero_calzado(self, numero: str): self.filter_numero_calzado = numero
    def set_filter_tipo_mochila(self, mochila: str): self.filter_tipo_mochila = mochila
    def set_filter_tipo_general(self, general: str): self.filter_tipo_general = general
    def set_filter_material_tela(self, material: str): self.filter_material_tela = material
    def set_filter_medida_talla(self, medida: str): self.filter_medida_talla = medida
    def set_attr_tamano_mochila(self, value: str): self.attr_tamano_mochila = value
    def set_search_attr_tamano_mochila(self, query: str): self.search_attr_tamano_mochila = query


    search_tipo_prenda: str = ""
    search_tipo_zapato: str = ""
    search_tipo_mochila: str = ""
    search_tipo_general: str = ""
    search_color: str = ""
    search_talla: str = ""
    search_numero_calzado: str = ""
    search_material_tela: str = ""
    search_medida_talla: str = ""
    search_tipo_general: str = "" # <-- ✨ AÑADE ESTA LÍNEA

    def set_search_tipo_prenda(self, query: str): self.search_tipo_prenda = query
    def set_search_tipo_zapato(self, query: str): self.search_tipo_zapato = query
    def set_search_tipo_mochila(self, query: str): self.search_tipo_mochila = query
    def set_search_tipo_general(self, query: str): self.search_tipo_general = query
    def set_search_color(self, query: str): self.search_color = query
    def set_search_talla(self, query: str): self.search_talla = query
    def set_search_numero_calzado(self, query: str): self.search_numero_calzado = query
    def set_search_material_tela(self, query: str): self.search_material_tela = query
    def set_search_medida_talla(self, query: str): self.search_medida_talla = query
    def set_search_tipo_general(self, query: str): self.search_tipo_general = query # <-- ✨ AÑADE ESTA LÍNEA

    @rx.var
    def filtered_tipos_general(self) -> list[str]: # <-- ✨ AÑADE ESTA FUNCIÓN COMPLETA
        if not self.search_tipo_general.strip(): return LISTA_TIPOS_GENERAL
        return [o for o in LISTA_TIPOS_GENERAL if self.search_tipo_general.lower() in o.lower()]

    @rx.var
    def filtered_tipos_ropa(self) -> list[str]:
        if not self.search_tipo_prenda.strip(): return LISTA_TIPOS_ROPA
        return [o for o in LISTA_TIPOS_ROPA if self.search_tipo_prenda.lower() in o.lower()]
    @rx.var
    def filtered_tipos_zapatos(self) -> list[str]:
        if not self.search_tipo_zapato.strip(): return LISTA_TIPOS_ZAPATOS
        return [o for o in LISTA_TIPOS_ZAPATOS if self.search_tipo_zapato.lower() in o.lower()]
    @rx.var
    def filtered_tipos_mochilas(self) -> list[str]:
        if not self.search_tipo_mochila.strip(): return LISTA_TIPOS_MOCHILAS
        return [o for o in LISTA_TIPOS_MOCHILAS if self.search_tipo_mochila.lower() in o.lower()]
    @rx.var
    def filtered_colores(self) -> list[str]:
        if not self.search_color.strip(): return LISTA_COLORES
        return [o for o in LISTA_COLORES if self.search_color.lower() in o.lower()]
    @rx.var
    def filtered_tallas_ropa(self) -> list[str]:
        if not self.search_talla.strip(): return LISTA_TALLAS_ROPA
        return [o for o in LISTA_TALLAS_ROPA if self.search_talla.lower() in o.lower()]
    @rx.var
    def filtered_numeros_calzado(self) -> list[str]:
        if not self.search_numero_calzado.strip(): return LISTA_NUMEROS_CALZADO
        return [o for o in LISTA_NUMEROS_CALZADO if self.search_numero_calzado.lower() in o.lower()]
    @rx.var
    def filtered_materiales(self) -> list[str]:
        if not self.search_material_tela.strip(): return LISTA_MATERIALES
        return [o for o in LISTA_MATERIALES if self.search_material_tela.lower() in o.lower()]
    @rx.var
    def filtered_tipos_general(self) -> list[str]:
        if not self.search_tipo_general.strip(): return LISTA_TIPOS_GENERAL
        return [o for o in LISTA_TIPOS_GENERAL if self.search_tipo_general.lower() in o.lower()]
    @rx.var
    def filtered_medidas_general(self) -> list[str]:
        if not self.search_medida_talla.strip(): return LISTA_MEDIDAS_GENERAL
        return [o for o in LISTA_MEDIDAS_GENERAL if self.search_medida_talla.lower() in o.lower()]
    @rx.var
    def filtered_attr_tamanos_mochila(self) -> list[str]:
        if not self.search_attr_tamano_mochila.strip(): return LISTA_TAMANOS_MOCHILAS
        return [o for o in LISTA_TAMANOS_MOCHILAS if self.search_attr_tamano_mochila.lower() in o.lower()]
    

    posts: list[ProductCardData] = []
    is_loading: bool = True

    @rx.event
    def on_load(self):
        """
        Carga los productos. Si hay un parámetro de categoría en la URL,
        actualiza el estado y filtra los resultados.
        """
        self.is_loading = True
        yield

        category = None
        full_url = self.router.url

        if full_url and "?" in full_url:
            parsed_url = urlparse(full_url)
            query_params = parse_qs(parsed_url.query)
            
            category_list = query_params.get("category")
            if category_list:
                category = category_list[0]
                
        # --- ✨ LA LÍNEA CLAVE QUE FALTA ---
        # Aquí actualizamos el estado con la categoría de la URL.
        # Si no hay categoría, se establece como "todos".
        self.current_category = category if category else "todos"

        with rx.session() as session:
            query = sqlmodel.select(BlogPostModel).where(BlogPostModel.publish_active == True)
            
            if self.current_category and self.current_category != "todos":
                query = query.where(BlogPostModel.category == self.current_category)
            
            results = session.exec(query.order_by(BlogPostModel.created_at.desc())).all()

            # --- INICIO DE LA CORRECCIÓN CLAVE ---
            # Reemplaza la línea "self.posts = [ProductCardData.from_orm(p) for p in results]"
            # con este bucle manual:
            
            temp_posts = []
            for p in results:
                temp_posts.append(
                    ProductCardData(
                        id=p.id,
                        title=p.title,
                        price=p.price,
                        # Llamamos a la propiedad del MODELO y guardamos el resultado
                        price_cop=p.price_cop, 
                        image_urls=p.image_urls,
                        average_rating=p.average_rating,
                        rating_count=p.rating_count,
                        attributes=p.attributes,
                    )
                )
            self.posts = temp_posts
            # --- FIN DE LA CORRECCIÓN CLAVE ---
        
        self.is_loading = False
    
    show_detail_modal: bool = False
    # ✨ CORRECCIÓN CRÍTICA: La variable del modal ahora usa el DTO, no el modelo ORM.
    product_in_modal: Optional[ProductDetailData] = None
    current_image_index: int = 0
    is_editing_post: bool = False
    post_to_edit: Optional[BlogPostModel] = None
    post_title: str = ""
    post_content: str = ""
    price_str: str = ""

    # ✨ NUEVAS VARIABLE PARA GESTIONAR IMÁGENES EN EDICIÓN
    post_images_in_form: list[str] = []

    @rx.var
    def current_image_url(self) -> str:
        if self.product_in_modal and self.product_in_modal.image_urls:
            if not self.product_in_modal.image_urls: return ""
            safe_index = self.current_image_index % len(self.product_in_modal.image_urls)
            return self.product_in_modal.image_urls[safe_index]
        return ""

    def next_image(self):
        if self.product_in_modal and self.product_in_modal.image_urls:
            self.current_image_index = (self.current_image_index + 1) % len(self.product_in_modal.image_urls)

    def prev_image(self):
        if self.product_in_modal and self.product_in_modal.image_urls:
            self.current_image_index = (self.current_image_index - 1 + len(self.product_in_modal.image_urls)) % len(self.product_in_modal.image_urls)

    def set_post_title(self, title: str): self.post_title = title
    def set_post_content(self, content: str): self.post_content = content
    def set_price(self, price: str): self.price_str = price

    @rx.event
    def start_editing_post(self, post_id: int):
        if not self.is_admin:
            return rx.toast.error("Acción no permitida.")
        with rx.session() as session:
            db_post = session.get(BlogPostModel, post_id)
            if db_post and (db_post.userinfo_id == self.authenticated_user_info.id or self.is_admin):
                self.post_to_edit = db_post
                self.post_title = db_post.title
                self.post_content = db_post.content
                self.price_str = str(db_post.price or 0.0)
                # ✨ CARGAMOS LAS IMÁGENES EXISTENTES EN NUESTRA ÚNICA LISTA
                self.post_images_in_form = db_post.image_urls.copy() if db_post.image_urls else []
                self.is_editing_post = True
            else:
                yield rx.toast.error("No se encontró la publicación o no tienes permisos.")

    @rx.event
    def cancel_editing_post(self, open_state: bool):
        if not open_state:
            self.is_editing_post = False
            self.post_to_edit = None
            self.post_title = ""
            self.post_content = ""
            self.price_str = ""
            # ✨ LIMPIAMOS LA LISTA ÚNICA
            self.post_images_in_form = []

    @rx.event
    def save_edited_post(self, form_data: dict):
        if not self.is_admin or not self.post_to_edit:
            return rx.toast.error("No se pudo guardar la publicación.")
        
        with rx.session() as session:
            post_to_update = session.get(BlogPostModel, self.post_to_edit.id)
            if post_to_update:
                post_to_update.title = form_data.get("title", post_to_update.title)
                post_to_update.content = form_data.get("content", post_to_update.content)
                try:
                    price_val = form_data.get("price", post_to_update.price)
                    post_to_update.price = float(price_val) if price_val else 0.0
                except (ValueError, TypeError):
                    return rx.toast.error("El precio debe ser un número válido.")

                # ✨ LÓGICA SIMPLIFICADA: Guardamos el estado actual de la lista de imágenes
                post_to_update.image_urls = self.post_images_in_form
                
                session.add(post_to_update)
                session.commit()
                yield self.cancel_editing_post(False)
                # Recargamos ambas vistas de admin para que los cambios se vean en todos lados
                yield self.load_all_my_posts()
                yield self.on_load_admin_store()
                yield rx.toast.success("Publicación actualizada correctamente.")

    # --- Lógica de subida de imágenes (CORREGIDA CON MANEJADORES SEPARADOS) ---
    temp_images: list[str] = [] # Para el formulario de 'añadir'

    @rx.event
    async def handle_add_upload(self, files: list[rx.UploadFile]):
        """Manejador de subida solo para el formulario de AÑADIR publicación."""
        for file in files:
            upload_data = await file.read()
            unique_filename = f"{secrets.token_hex(8)}-{file.name}"
            outfile = rx.get_upload_dir() / unique_filename
            outfile.write_bytes(upload_data)
            self.temp_images.append(unique_filename)

    @rx.event
    def remove_temp_image(self, filename: str):
        """Elimina una imagen de la lista temporal del formulario de AÑADIR."""
        if filename in self.temp_images:
            self.temp_images.remove(filename)

    @rx.event
    async def handle_edit_upload(self, files: list[rx.UploadFile]):
        """Manejador de subida solo para el formulario de EDITAR publicación."""
        for file in files:
            upload_data = await file.read()
            unique_filename = f"{secrets.token_hex(8)}-{file.name}"
            outfile = rx.get_upload_dir() / unique_filename
            outfile.write_bytes(upload_data)
            self.post_images_in_form.append(unique_filename)

    @rx.event
    def remove_edited_image(self, filename: str):
        """Elimina una imagen de la lista del formulario de EDITAR."""
        if filename in self.post_images_in_form:
            self.post_images_in_form.remove(filename)


    def _clear_add_form(self):
        self.title = ""
        self.content = ""
        self.price = ""
        self.category = ""
        self.temp_images = []

    cart: Dict[int, int] = {}
    
    @rx.var
    def cart_items_count(self) -> int: return sum(self.cart.values())
    @rx.var
    def cart_total(self) -> float: return sum(p.price * q for p, q in self.cart_details if p and p.price)
    @rx.var
    def cart_total_cop(self) -> str: return format_to_cop(self.cart_total)
    
    @rx.var
    def cart_details(self) -> List[Tuple[Optional[BlogPostModel], int]]:
        if not self.cart: return []
        with rx.session() as session:
            post_ids = list(self.cart.keys())
            if not post_ids: return []
            results = session.exec(sqlmodel.select(BlogPostModel).where(BlogPostModel.id.in_(post_ids))).all()
            post_map = {p.id: p for p in results}
            return [(post_map.get(pid), self.cart[pid]) for pid in post_ids]

    @rx.event
    def add_to_cart(self, post_id: int):
        if not self.is_authenticated:
            return rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)
        self.cart[post_id] = self.cart.get(post_id, 0) + 1
        self.show_detail_modal = False
        self.product_in_modal = None
        return rx.toast.success("Producto añadido al carrito.")
        
    @rx.event
    def remove_from_cart(self, post_id: int):
        if post_id in self.cart:
            self.cart[post_id] -= 1
            if self.cart[post_id] <= 0:
                del self.cart[post_id]

    title: str = ""
    content: str = ""
    price: str = "" 
    category: str = ""
    temp_images: list[str] = []

    @rx.var
    def categories(self) -> list[str]: return [c.value for c in Category]
    def set_title(self, value: str): self.title = value
    def set_content(self, value: str): self.content = value
    def set_price_from_input(self, value: str): self.price = value
    def set_category(self, value: str): self.category = value

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        uploaded_filenames = []
        for file in files:
            upload_data = await file.read()
            outfile = rx.get_upload_dir() / file.name
            outfile.write_bytes(upload_data)
            uploaded_filenames.append(file.name)
        self.temp_images.extend(uploaded_filenames)

    @rx.event
    def remove_image(self, filename: str): self.temp_images.remove(filename)
    def _clear_add_form(self): self.title = ""; self.content = ""; self.price = ""; self.category = ""; self.temp_images = []

    @rx.event
    def submit_and_publish(self, form_data: dict):
        """
        Valida, recopila todos los atributos (incluyendo selecciones múltiples)
        y guarda el nuevo producto en la base de datos.
        """
        if not self.is_admin:
            return rx.toast.error("Acción no permitida.")
        
        if not all([form_data.get("title"), form_data.get("price"), form_data.get("category")]):
            return rx.toast.error("Título, precio y categoría son obligatorios.")
        
        # --- 1. Recopilación dinámica de atributos ---
        # Inicializamos un diccionario vacío para guardar las características.
        attributes = {}
        category = form_data.get("category")

        if category == Category.ROPA.value:
            if self.attr_color:
                attributes["Color"] = self.attr_color
            # Comprobamos la lista de tallas. Si no está vacía, la guardamos.
            if self.attr_tallas_ropa:
                attributes["Talla"] = self.attr_tallas_ropa
            if self.attr_material:
                # Usamos la etiqueta "Tela" específicamente para la categoría Ropa.
                attributes["Tela"] = self.attr_material

        elif category == Category.CALZADO.value:
            if self.attr_color:
                attributes["Color"] = self.attr_color
            # Comprobamos la lista de números. Si no está vacía, la guardamos.
            if self.attr_numeros_calzado:
                attributes["Número"] = self.attr_numeros_calzado
            if self.attr_material:
                attributes["Material"] = self.attr_material
        
        elif category == Category.MOCHILAS.value:
            if self.attr_color:
                attributes["Color"] = self.attr_color
            # Comprobamos la lista de tamaños. Si no está vacía, la guardamos.
            if self.attr_tamanos_mochila:
                attributes["Tamaño"] = self.attr_tamanos_mochila
            if self.attr_material:
                attributes["Material"] = self.attr_material
        
        with rx.session() as session:
            new_post = BlogPostModel(
                userinfo_id=self.authenticated_user_info.id,
                title=form_data["title"],
                content=form_data.get("content", ""),
                price=float(form_data.get("price", 0.0)),
                category=category,
                image_urls=self.temp_images,
                
                # --- 2. Guardar el diccionario de atributos en la BD ---
                # El campo 'attributes' de tu modelo es de tipo JSON y puede
                # guardar perfectamente nuestro diccionario.
                attributes=attributes,
                
                publish_active=True,
                publish_date=datetime.now(timezone.utc),
            )
            session.add(new_post)
            session.commit()
            session.refresh(new_post)
            
        # Limpiamos el formulario, incluyendo las nuevas listas de atributos.
        self._clear_add_form()
        yield rx.toast.success("Producto publicado exitosamente.")
        return rx.redirect("/blog")
        
    @rx.var
    def my_admin_posts(self) -> list[BlogPostModel]:
        if not self.authenticated_user_info:
            return []
        with rx.session() as session:
            return session.exec(sqlmodel.select(BlogPostModel).where(BlogPostModel.userinfo_id == self.authenticated_user_info.id).order_by(BlogPostModel.created_at.desc())).all()

    @rx.event
    def delete_post(self, post_id: int):
        if not self.authenticated_user_info:
            return rx.toast.error("Acción no permitida.")
        with rx.session() as session:
            post_to_delete = session.get(BlogPostModel, post_id)
            if post_to_delete and post_to_delete.userinfo_id == self.authenticated_user_info.id:
                session.delete(post_to_delete)
                session.commit()
                yield rx.toast.success("Publicación eliminada.")
            else:
                yield rx.toast.error("No tienes permiso para eliminar esta publicación.")

    @rx.event
    def toggle_publish_status(self, post_id: int):
        if not self.authenticated_user_info:
            return rx.toast.error("Acción no permitida.")
        with rx.session() as session:
            post_to_update = session.get(BlogPostModel, post_id)
            if post_to_update and post_to_update.userinfo_id == self.authenticated_user_info.id:
                post_to_update.publish_active = not post_to_update.publish_active
                session.add(post_to_update)
                session.commit()
                yield rx.toast.info(f"Estado de publicación cambiado.")
                
    addresses: List[ShippingAddressModel] = []
    show_form: bool = False
    city: str = ""
    neighborhood: str = ""
    search_city: str = ""
    search_neighborhood: str = ""
    default_shipping_address: Optional[ShippingAddressModel] = None

    @rx.event
    def handle_checkout(self):
        if not self.is_authenticated or not self.default_shipping_address:
            return rx.toast.error("Por favor, selecciona una dirección predeterminada.")
        if not self.authenticated_user_info:
            return rx.toast.error("Error de usuario. Vuelve a iniciar sesión.")
        
        with rx.session() as session:
            new_purchase = PurchaseModel(
                userinfo_id=self.authenticated_user_info.id,
                total_price=self.cart_total, 
                status=PurchaseStatus.PENDING,
                shipping_name=self.default_shipping_address.name, 
                shipping_city=self.default_shipping_address.city,
                shipping_neighborhood=self.default_shipping_address.neighborhood, 
                shipping_address=self.default_shipping_address.address,
                shipping_phone=self.default_shipping_address.phone
            )
            session.add(new_purchase)
            session.commit()
            session.refresh(new_purchase)
            
            post_map = {p.id: p for p in session.exec(sqlmodel.select(BlogPostModel).where(BlogPostModel.id.in_(list(self.cart.keys())))).all()}
            for post_id, quantity in self.cart.items():
                if post_id in post_map: 
                    session.add(PurchaseItemModel(
                        purchase_id=new_purchase.id,
                        blog_post_id=post_map[post_id].id,
                        quantity=quantity,
                        price_at_purchase=post_map[post_id].price
                    ))
            session.commit()
            
        self.cart.clear()
        self.default_shipping_address = None
        yield self.notify_admin_of_new_purchase()
        yield rx.toast.success("¡Gracias por tu compra! Tu orden está pendiente de confirmación.")
        return rx.redirect("/my-purchases")

    def toggle_form(self):
        # --- ✨ CORRECCIÓN 1 AQUÍ ---
        # Usamos 'not' para la negación lógica en lugar de '~' (que es bit a bit).
        self.show_form = not self.show_form
    def set_city(self, city: str): self.city = city; self.neighborhood = ""
    def set_neighborhood(self, hood: str): self.neighborhood = hood
    def set_search_city(self, query: str): self.search_city = query
    def set_search_neighborhood(self, query: str): self.search_neighborhood = query
    
    @rx.var
    def cities(self) -> List[str]:
        data = load_colombia_data()
        if not self.search_city.strip(): return sorted(list(data.keys()))
        return [c for c in data if self.search_city.lower() in c.lower()]

    @rx.var
    def neighborhoods(self) -> List[str]:
        if not self.city: return []
        data = load_colombia_data()
        all_hoods = data.get(self.city, [])
        if not self.search_neighborhood.strip(): return all_hoods
        return [n for n in all_hoods if self.search_neighborhood.lower() in n.lower()]

    @rx.event
    def load_addresses(self):
        if self.authenticated_user_info:
            with rx.session() as session:
                self.addresses = session.exec(sqlmodel.select(ShippingAddressModel).where(ShippingAddressModel.userinfo_id == self.authenticated_user_info.id).order_by(ShippingAddressModel.is_default.desc())).all()

    @rx.event
    def add_new_address(self, form_data: dict):
        if not all([form_data.get("name"), form_data.get("phone"), self.city, form_data.get("address")]):
            return rx.toast.error("Por favor, completa todos los campos requeridos.")
        with rx.session() as session:
            is_first_address = len(self.addresses) == 0
            new_addr = ShippingAddressModel(
                userinfo_id=self.authenticated_user_info.id, name=form_data["name"],
                phone=form_data["phone"], city=self.city, neighborhood=self.neighborhood,
                address=form_data["address"], is_default=is_first_address
            )
            session.add(new_addr)
            session.commit()
        self.show_form = False
        yield self.load_addresses()
        return rx.toast.success("Nueva dirección guardada.")

    @rx.event
    def load_default_shipping_info(self):
        if self.authenticated_user_info:
            with rx.session() as session:
                self.default_shipping_address = session.exec(
                    sqlmodel.select(ShippingAddressModel).where(
                        ShippingAddressModel.userinfo_id == self.authenticated_user_info.id,
                        ShippingAddressModel.is_default == True
                    )
                ).one_or_none()

    @rx.event
    def delete_address(self, address_id: int):
        if not self.authenticated_user_info: return
        with rx.session() as session:
            address_to_delete = session.get(ShippingAddressModel, address_id)
            if address_to_delete and address_to_delete.userinfo_id == self.authenticated_user_info.id:
                session.delete(address_to_delete)
                session.commit()
                yield self.load_addresses()

    @rx.event
    def set_as_default(self, address_id: int):
        if not self.authenticated_user_info: return
        with rx.session() as session:
            current_default = session.exec(sqlmodel.select(ShippingAddressModel).where(ShippingAddressModel.userinfo_id == self.authenticated_user_info.id, ShippingAddressModel.is_default == True)).one_or_none()
            if current_default:
                current_default.is_default = False
                session.add(current_default)
            new_default = session.get(ShippingAddressModel, address_id)
            if new_default and new_default.userinfo_id == self.authenticated_user_info.id:
                new_default.is_default = True
                session.add(new_default)
                session.commit()
                yield self.load_addresses()
    
    search_term: str = ""
    search_results: List[ProductCardData] = []
    def set_search_term(self, term: str): self.search_term = term

    @rx.event
    def perform_search(self):
        if not self.search_term.strip(): return
        with rx.session() as session:
            results = session.exec(sqlmodel.select(BlogPostModel).where(BlogPostModel.title.ilike(f"%{self.search_term.strip()}%"), BlogPostModel.publish_active == True)).all()
            self.search_results = [ProductCardData.from_orm(p) for p in results]
        return rx.redirect("/search-results")
        
    pending_purchases: List[AdminPurchaseCardData] = []
    confirmed_purchases: List[AdminPurchaseCardData] = []
    new_purchase_notification: bool = False
    all_users: List[UserInfo] = []
    admin_store_posts: list[ProductCardData] = []
    show_admin_sidebar: bool = False

    def set_new_purchase_notification(self, value: bool):
        self.new_purchase_notification = value

    @rx.event
    def notify_admin_of_new_purchase(self):
        self.new_purchase_notification = True

    @rx.event
    def load_pending_purchases(self):
        if not self.is_admin: return
        with rx.session() as session:
            purchases = session.exec(sqlmodel.select(PurchaseModel).options(sqlalchemy.orm.joinedload(PurchaseModel.userinfo).joinedload(UserInfo.user), sqlalchemy.orm.joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post)).where(PurchaseModel.status == PurchaseStatus.PENDING).order_by(PurchaseModel.purchase_date.asc())).unique().all()
            self.pending_purchases = [
                AdminPurchaseCardData(
                    id=p.id, customer_name=p.userinfo.user.username, customer_email=p.userinfo.email,
                    purchase_date_formatted=p.purchase_date_formatted, status=p.status.value, total_price=p.total_price,
                    shipping_name=p.shipping_name, shipping_full_address=f"{p.shipping_address}, {p.shipping_neighborhood}, {p.shipping_city}",
                    shipping_phone=p.shipping_phone, items_formatted=p.items_formatted
                ) for p in purchases
            ]
            yield self.set_new_purchase_notification(len(self.pending_purchases) > 0)

    @rx.event
    def confirm_payment(self, purchase_id: int):
        if not self.is_admin:
            return rx.toast.error("Acción no permitida.")
        with rx.session() as session:
            purchase = session.get(PurchaseModel, purchase_id)
            if purchase and purchase.status == PurchaseStatus.PENDING:
                purchase.status = PurchaseStatus.CONFIRMED
                purchase.confirmed_at = datetime.now(timezone.utc)
                notification = NotificationModel(
                    userinfo_id=purchase.userinfo_id,
                    message=f"¡Tu compra #{purchase.id} ha sido confirmada!",
                    url="/my-purchases"
                )
                session.add(purchase)
                session.add(notification)
                session.commit()
                yield rx.toast.success(f"Compra #{purchase_id} confirmada.")
                
                # Esta es la línea corregida
                yield AppState.load_pending_purchases
            else:
                yield rx.toast.error("La compra no se encontró o ya fue confirmada.")

    search_query_admin_history: str = ""

    def set_search_query_admin_history(self, query: str):
        self.search_query_admin_history = query

    @rx.var
    def filtered_admin_purchases(self) -> list[AdminPurchaseCardData]:
        if not self.search_query_admin_history.strip():
            return self.confirmed_purchases
        q = self.search_query_admin_history.lower()
        return [
            p for p in self.confirmed_purchases
            if q in f"#{p.id}" or q in p.customer_name.lower() or q in p.customer_email.lower()
        ]

    @rx.event
    def load_confirmed_purchases(self):
        if not self.is_admin:
            self.confirmed_purchases = []
            return
        with rx.session() as session:
            results = session.exec(
                sqlmodel.select(PurchaseModel)
                .options(
                    sqlalchemy.orm.joinedload(PurchaseModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post)
                )
                .where(PurchaseModel.status != PurchaseStatus.PENDING)
                .order_by(PurchaseModel.purchase_date.desc())
            ).unique().all()
            self.confirmed_purchases = [
                AdminPurchaseCardData(
                    id=p.id,
                    customer_name=p.userinfo.user.username,
                    customer_email=p.userinfo.email,
                    purchase_date_formatted=p.purchase_date_formatted,
                    status=p.status.value,
                    total_price=p.total_price,
                    shipping_name=p.shipping_name,
                    shipping_full_address=f"{p.shipping_address}, {p.shipping_neighborhood}, {p.shipping_city}",
                    shipping_phone=p.shipping_phone,
                    items_formatted=p.items_formatted
                ) for p in results
            ]

    user_purchases: List[UserPurchaseHistoryCardData] = []
    search_query_user_history: str = ""
    
    def set_search_query_user_history(self, query: str):
        self.search_query_user_history = query

    @rx.var
    def filtered_user_purchases(self) -> list[UserPurchaseHistoryCardData]:
        if not self.search_query_user_history.strip():
            return self.user_purchases
        q = self.search_query_user_history.lower()
        return [
            p for p in self.user_purchases 
            if q in f"#{p.id}" or any(q in item.lower() for item in p.items_formatted)
        ]

    @rx.event
    def load_purchases(self):
        if not self.authenticated_user_info:
            self.user_purchases = []
            return
        with rx.session() as session:
            results = session.exec(
                sqlmodel.select(PurchaseModel)
                .options(
                    sqlalchemy.orm.joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post)
                )
                .where(PurchaseModel.userinfo_id == self.authenticated_user_info.id)
                .order_by(PurchaseModel.purchase_date.desc())
            ).unique().all()
            self.user_purchases = [
                UserPurchaseHistoryCardData(
                    id=p.id, purchase_date_formatted=p.purchase_date_formatted,
                    status=p.status.value, total_price_cop=p.total_price_cop,
                    shipping_name=p.shipping_name, shipping_address=p.shipping_address,
                    shipping_neighborhood=p.shipping_neighborhood, shipping_city=p.shipping_city,
                    shipping_phone=p.shipping_phone, items_formatted=p.items_formatted
                ) for p in results
            ]

    notifications: List[NotificationModel] = []
    
    @rx.var
    def unread_count(self) -> int:
        return sum(1 for n in self.notifications if not n.is_read)
    
    @rx.event
    def load_notifications(self):
        if not self.authenticated_user_info:
            self.notifications = []
            return
        with rx.session() as session:
            self.notifications = session.exec(
                sqlmodel.select(NotificationModel)
                .where(NotificationModel.userinfo_id == self.authenticated_user_info.id)
                .order_by(sqlmodel.col(NotificationModel.created_at).desc())
            ).all()
    
    @rx.event
    def mark_all_as_read(self):
        if not self.authenticated_user_info:
            return
        unread_ids = [n.id for n in self.notifications if not n.is_read]
        if not unread_ids:
            return
        with rx.session() as session:
            stmt = sqlmodel.update(NotificationModel).where(NotificationModel.id.in_(unread_ids)).values(is_read=True)
            session.exec(stmt)
            session.commit()
        yield self.load_notifications()

    form_data: dict = {}
    did_submit_contact: bool = False
    contact_entries: list[ContactEntryModel] = []
    search_query_contact: str = ""
    
    def set_search_query_contact(self, query: str):
        self.search_query_contact = query

    @rx.var
    def filtered_entries(self) -> list[ContactEntryModel]:
        if not self.search_query_contact.strip():
            return self.contact_entries
        q = self.search_query_contact.lower()
        return [
            e for e in self.contact_entries 
            if q in f"{e.first_name} {e.last_name} {e.email} {e.message}".lower()
        ]
    
    async def handle_contact_submit(self, form_data: dict):
        self.form_data = form_data
        with rx.session() as session:
            user_info = self.authenticated_user_info
            entry = ContactEntryModel(
                first_name=form_data.get("first_name"),
                last_name=form_data.get("last_name"),
                email=form_data.get("email"),
                message=form_data.get("message"),
                userinfo_id=user_info.id if user_info else None
            )
            session.add(entry)
            session.commit()
        self.did_submit_contact = True
        yield
        await asyncio.sleep(4)
        self.did_submit_contact = False
        yield

    def load_entries(self):
        with rx.session() as session:
            self.contact_entries = session.exec(sqlmodel.select(ContactEntryModel).order_by(ContactEntryModel.id.desc())).all()
    
    @rx.event
    def load_all_users(self):
        if not self.is_admin:
            self.all_users = []
            return rx.redirect("/")
        
        with rx.session() as session:
            self.all_users = session.exec(
                sqlmodel.select(UserInfo).options(
                    sqlalchemy.orm.joinedload(UserInfo.user)
                )
            ).all()

    @rx.event
    def toggle_admin_role(self, userinfo_id: int):
        if not self.is_admin:
            return rx.toast.error("No tienes permisos.")
            
        with rx.session() as session:
            user_info = session.get(UserInfo, userinfo_id)
            if user_info:
                if user_info.id == self.authenticated_user_info.id:
                    return rx.toast.warning("No puedes cambiar tu propio rol.")
                
                if user_info.role == UserRole.ADMIN:
                    user_info.role = UserRole.CUSTOMER
                else:
                    user_info.role = UserRole.ADMIN
                session.add(user_info)
                session.commit()
        return self.load_all_users()

    @rx.event
    def ban_user(self, userinfo_id: int, days: int = 7):
        if not self.is_admin:
            return rx.toast.error("No tienes permisos.")
        
        with rx.session() as session:
            user_info = session.get(UserInfo, userinfo_id)
            if user_info:
                if user_info.id == self.authenticated_user_info.id:
                    return rx.toast.warning("No puedes vetarte a ti mismo.")

                user_info.is_banned = True
                user_info.ban_expires_at = datetime.now(timezone.utc) + timedelta(days=days)
                session.add(user_info)
                session.commit()
        return self.load_all_users()

    @rx.event
    def unban_user(self, userinfo_id: int):
        if not self.is_admin:
            return rx.toast.error("No tienes permisos.")

        with rx.session() as session:
            user_info = session.get(UserInfo, userinfo_id)
            if user_info:
                user_info.is_banned = False
                user_info.ban_expires_at = None
                session.add(user_info)
                session.commit()
        return self.load_all_users()
    
    admin_store_posts: list[ProductCardData] = []

    @rx.event
    def on_load_admin_store(self):
        if not self.is_admin:
            return rx.redirect("/")

        with rx.session() as session:
            results = session.exec(
                sqlmodel.select(BlogPostModel)
                .options(sqlalchemy.orm.joinedload(BlogPostModel.comments))
                # --- INICIO DE LA MODIFICACIÓN ---
                # Filtramos para que solo muestre los posts del usuario logueado
                .where(BlogPostModel.userinfo_id == self.authenticated_user_info.id)
                # --- FIN DE LA MODIFICACIÓN ---
                .order_by(BlogPostModel.created_at.desc())
            ).unique().all()
            
            self.admin_store_posts = [
                ProductCardData.from_orm(p) for p in results
            ]

    show_admin_sidebar: bool = False

    def toggle_admin_sidebar(self):
        self.show_admin_sidebar = not self.show_admin_sidebar

    @rx.event
    def on_load_main_page(self):
        """
        Carga los productos y, si hay un parámetro ?product=ID en la URL,
        usa un manejador secundario para abrir el modal de forma segura.
        """
        if self.is_admin:
            return rx.redirect("/admin/store")

        yield AppState.on_load

        full_url = self.router.url
        product_id = None

        if full_url and "?" in full_url:
            parsed_url = urlparse(full_url)
            query_params = parse_qs(parsed_url.query)
            product_id_list = query_params.get("product")
            if product_id_list:
                product_id = product_id_list[0]

        if product_id is not None:
            # Guardamos el ID en el estado
            self._product_id_to_load_on_mount = int(product_id)
            # Llamamos al nuevo manejador SIN argumentos
            yield self.trigger_modal_from_load # <--- Llamada corregida

    # --- ✨ LÓGICA PARA OPINIONES Y VALORACIONES ---

    # Almacena los comentarios del producto que está en el modal
    product_comments: list[CommentData] = []
    
    # Almacena la opinión del usuario actual para el producto actual (si existe)
    my_review_for_product: Optional[CommentData] = None

    # Estado del formulario de opinión
    review_rating: int = 0
    review_content: str = ""
    show_review_form: bool = False # <--- AÑADE ESTA LÍNEA
    review_limit_reached: bool = False # <-- ✨ AÑADE ESTA LÍNEA

    @rx.var
    def can_review_product(self) -> bool:
        """
        Determina si el usuario actual puede dejar una opinión.
        Debe estar autenticado y haber comprado el producto.
        """
        if not self.is_authenticated or not self.product_in_modal:
            return False
        with rx.session() as session:
            # Comprueba si existe una compra confirmada por este usuario para este producto
            purchase_item = session.exec(
                sqlmodel.select(PurchaseItemModel)
                .join(PurchaseModel)
                .where(
                    PurchaseModel.userinfo_id == self.authenticated_user_info.id,
                    PurchaseItemModel.blog_post_id == self.product_in_modal.id,
                    PurchaseModel.status.in_([PurchaseStatus.CONFIRMED, PurchaseStatus.SHIPPED])
                )
            ).first()
            return purchase_item is not None
        
    # --- ✨ AÑADE ESTA FUNCIÓN DENTRO DE AppState ✨ ---
    @rx.var
    def product_attributes_list(self) -> list[AttributeData]:
        """
        Convierte el diccionario de atributos en una lista de DTOs,
        asegurando que el valor sea siempre un string.
        """
        if self.product_in_modal and self.product_in_modal.attributes:
            processed_attributes = []
            for k, v in self.product_in_modal.attributes.items():
                # Convertimos la lista a un string aquí, en el backend
                if isinstance(v, list):
                    value_str = ", ".join(v)
                else:
                    value_str = str(v)
                processed_attributes.append(AttributeData(key=k, value=value_str))
            return processed_attributes
        return []

    def _find_unclaimed_purchase(self, session: sqlmodel.Session) -> Optional[PurchaseItemModel]:
        """
        Encuentra un item de compra del usuario para el producto actual que aún no tenga 
        un comentario original asociado.
        """
        if not self.authenticated_user_info or not self.product_in_modal:
            return None
        
        # 1. Obtener todas las compras confirmadas de este producto por el usuario.
        purchase_items = session.exec(
            sqlmodel.select(PurchaseItemModel)
            .join(PurchaseModel)
            .where(
                PurchaseModel.userinfo_id == self.authenticated_user_info.id,
                PurchaseItemModel.blog_post_id == self.product_in_modal.id,
                PurchaseModel.status.in_([PurchaseStatus.CONFIRMED, PurchaseStatus.SHIPPED])
            )
        ).all()

        # 2. Obtener los IDs de las compras que ya tienen un comentario ORIGINAL asociado.
        claimed_purchase_ids = set(
            session.exec(
                sqlmodel.select(CommentModel.purchase_item_id)
                .where(
                    CommentModel.userinfo_id == self.authenticated_user_info.id,
                    CommentModel.blog_post_id == self.product_in_modal.id,
                    CommentModel.parent_comment_id == None, # Solo hilos de comentarios originales
                    CommentModel.purchase_item_id != None
                )
            ).all()
        )

        # 3. Devolver la primera compra que aún no ha sido "reclamada" por un comentario.
        for item in purchase_items:
            if item.id not in claimed_purchase_ids:
                return item
        
        return None

    def set_review_rating(self, rating: int):
        """Actualiza la valoración en el estado del formulario."""
        self.review_rating = rating
    
    # --- ✨ INICIO DE LA MODIFICACIÓN 1 ✨ ---
    # Diccionario para rastrear qué comentarios están expandidos.
    # La clave será el ID del comentario, el valor será True (expandido) o False (colapsado).
    expanded_comments: dict[int, bool] = {}

    def toggle_comment_updates(self, comment_id: int):
        """Expande o colapsa el historial de un comentario específico."""
        # Obtiene el estado actual (si no existe, es False) y lo invierte.
        self.expanded_comments[comment_id] = not self.expanded_comments.get(comment_id, False)
    # --- ✨ FIN DE LA MODIFICACIÓN 1 ✨ ---

    # ✅ ASEGÚRATE DE QUE LA FUNCIÓN ESTÉ INDENTADA A ESTE NIVEL
    @rx.event
    def submit_review(self, form_data: dict):
        """
        Gestiona el envío de una nueva opinión o la actualización de una existente,
        aplicando el límite de 2 actualizaciones por compra.
        """
        if not self.is_authenticated or not self.product_in_modal:
            return rx.toast.error("Debes iniciar sesión para opinar.")
        if self.review_rating == 0:
            return rx.toast.error("Debes seleccionar una valoración.")

        content = form_data.get("review_content", "")
        with rx.session() as session:
            user_info = self.authenticated_user_info
            if not user_info or not user_info.user:
                return rx.toast.error("No se pudo identificar al usuario.")

            if self.my_review_for_product:
                # --- LÓGICA DE ACTUALIZACIÓN ---
                # Usamos el ID del DTO para obtener el objeto "vivo" de la BD
                original_comment = session.get(CommentModel, self.my_review_for_product.id)

                # --- ✨ MEJORA DE ROBUSTEZ AÑADIDA ✨ ---
                # Verificamos que el comentario realmente exista antes de continuar.
                if not original_comment:
                    return rx.toast.error("El comentario que intentas actualizar ya no existe.")

                # Buscamos el comentario raíz (el original sin padre)
                while original_comment.parent:
                    original_comment = original_comment.parent
                
                # Verificamos el límite de 2 actualizaciones
                if len(original_comment.updates) >= 2:
                    return rx.toast.error("Ya has alcanzado el límite de 2 actualizaciones para esta compra.")

                new_update = CommentModel(
                    userinfo_id=user_info.id,
                    blog_post_id=self.product_in_modal.id,
                    rating=self.review_rating,
                    content=content,
                    author_username=user_info.user.username,
                    author_initial=user_info.user.username[0].upper(),
                    parent_comment_id=original_comment.id,
                    # La actualización hereda el vínculo de la compra original.
                    purchase_item_id=original_comment.purchase_item_id 
                )
                session.add(new_update)
                yield rx.toast.success("¡Opinión actualizada!")
            else:
                # --- LÓGICA DE NUEVO COMENTARIO ---
                # Buscamos una compra "sin reclamar" para este producto.
                unclaimed_purchase_item = self._find_unclaimed_purchase(session)
                if not unclaimed_purchase_item:
                    return rx.toast.error("Debes comprar este producto para poder dejar una opinión.")

                new_review = CommentModel(
                    userinfo_id=user_info.id,
                    blog_post_id=self.product_in_modal.id,
                    rating=self.review_rating,
                    content=content,
                    author_username=user_info.user.username,
                    author_initial=user_info.user.username[0].upper(),
                    # Vinculamos este nuevo comentario a la compra que lo desbloqueó.
                    purchase_item_id=unclaimed_purchase_item.id
                )
                session.add(new_review)
                yield rx.toast.success("¡Gracias por tu opinión!")
            
            session.commit()
        yield AppState.open_product_detail_modal(self.product_in_modal.id)

    # --- AÑADE ESTA NUEVA FUNCIÓN PRIVADA DENTRO DE AppState ---
    def _find_unclaimed_purchase(self, session: sqlmodel.Session) -> Optional[PurchaseItemModel]:
        """Encuentra un item de compra del usuario para el producto actual que aún no tenga un comentario asociado."""
        if not self.authenticated_user_info or not self.product_in_modal:
            return None
        
        # 1. Obtener todas las compras confirmadas de este producto por el usuario
        purchase_items = session.exec(
            sqlmodel.select(PurchaseItemModel)
            .join(PurchaseModel)
            .where(
                PurchaseModel.userinfo_id == self.authenticated_user_info.id,
                PurchaseItemModel.blog_post_id == self.product_in_modal.id,
                PurchaseModel.status.in_([PurchaseStatus.CONFIRMED, PurchaseStatus.SHIPPED])
            )
        ).all()

        # 2. Obtener los IDs de las compras que ya tienen un comentario
        claimed_purchase_ids = {
            c.purchase_item_id for c in self.product_comments if c.purchase_item_id
        }

        # 3. Devolver la primera compra que aún no ha sido "reclamada" por un comentario
        for item in purchase_items:
            if item.id not in claimed_purchase_ids:
                return item
        return None

    # --- AÑADIR: Variables para publicaciones guardadas ---
    saved_post_ids: set[int] = set()
    saved_posts_gallery: list[ProductCardData] = []

    @rx.var
    def is_current_post_saved(self) -> bool:
        """Comprueba si el producto en el modal está guardado por el usuario actual."""
        if not self.product_in_modal or not self.is_authenticated:
            return False
        return self.product_in_modal.id in self.saved_post_ids

    @rx.event
    def load_saved_post_ids(self):
        """Carga los IDs de las publicaciones guardadas por el usuario actual."""
        if not self.authenticated_user_info:
            self.saved_post_ids = set()
            return
        
        with rx.session() as session:
            # Recargamos el user_info para acceder a la nueva relación 'saved_posts'
            user_info = session.get(UserInfo, self.authenticated_user_info.id)
            if user_info:
                self.saved_post_ids = {post.id for post in user_info.saved_posts}

    @rx.event
    def toggle_save_post(self):
        """Guarda o elimina una publicación de la lista de guardados del usuario."""
        if not self.authenticated_user_info or not self.product_in_modal:
            return rx.toast.error("Debes iniciar sesión para guardar publicaciones.")

        post_id = self.product_in_modal.id
        with rx.session() as session:
            user_info = session.get(UserInfo, self.authenticated_user_info.id)
            post_to_toggle = session.get(BlogPostModel, post_id)

            if not user_info or not post_to_toggle:
                return rx.toast.error("Error al procesar la solicitud.")

            if post_id in self.saved_post_ids:
                # Si ya está guardado, lo eliminamos
                user_info.saved_posts.remove(post_to_toggle)
                self.saved_post_ids.remove(post_id)
                yield rx.toast.info("Publicación eliminada de tus guardados.")
            else:
                # Si no está guardado, lo añadimos
                user_info.saved_posts.append(post_to_toggle)
                self.saved_post_ids.add(post_id)
                yield rx.toast.success("¡Publicación guardada!")
            
            session.add(user_info)
            session.commit()

    @rx.event
    def trigger_modal_from_load(self):
        """Abre el modal usando el ID guardado en el estado."""
        if self._product_id_to_load_on_mount is not None:
            # Usamos yield from para ejecutar el otro manejador de eventos
            yield from self.open_product_detail_modal(self._product_id_to_load_on_mount)
            # Limpiamos la variable para que no se vuelva a ejecutar
            self._product_id_to_load_on_mount = None

    # --- AÑADE ESTA FUNCIÓN DE AYUDA DENTRO DE LA CLASE AppState ---
    def _convert_comment_to_dto(self, comment_model: CommentModel) -> CommentData:
        """Convierte recursivamente un CommentModel de la BD a un DTO CommentData."""
        return CommentData(
            id=comment_model.id,
            content=comment_model.content,
            rating=comment_model.rating,
            author_username=comment_model.author_username,
            author_initial=comment_model.author_initial,
            created_at_formatted=comment_model.created_at_formatted,
            updates=[self._convert_comment_to_dto(update) for update in sorted(comment_model.updates, key=lambda u: u.created_at)]
        )

    @rx.event
    def open_product_detail_modal(self, post_id: int):
        # --- 1. Limpieza de estado (añade el reseteo de la nueva variable) ---
        self.product_in_modal = None
        self.show_detail_modal = True
        self.current_image_index = 0
        self.product_comments = []
        self.my_review_for_product = None
        self.review_rating = 0
        self.review_content = ""
        self.show_review_form = False
        self.review_limit_reached = False # <-- ✨ AÑADE ESTA LÍNEA

        with rx.session() as session:
            # ... (el resto del código de carga de datos no cambia) ...
            db_post = session.exec(
            sqlmodel.select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.comments).joinedload(CommentModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(BlogPostModel.comments).joinedload(CommentModel.updates).joinedload(CommentModel.userinfo).joinedload(UserInfo.user)
                ).where(BlogPostModel.id == post_id)
            ).unique().one_or_none()

            if db_post and db_post.publish_active:
                # ... (la creación del product_dto y la carga de comentarios no cambia) ...
                product_dto = ProductDetailData.from_orm(db_post)
                if db_post.userinfo and db_post.userinfo.user:
                    product_dto.seller_name = db_post.userinfo.user.username
                    product_dto.seller_id = db_post.userinfo.id
                self.product_in_modal = product_dto
                
                all_comment_dtos = [self._convert_comment_to_dto(c) for c in db_post.comments]
                original_comment_dtos = [dto for dto in all_comment_dtos if dto.id not in {update.id for parent in all_comment_dtos for update in parent.updates}]
                self.product_comments = sorted(original_comment_dtos, key=lambda c: c.id, reverse=True)

                # --- ✨ INICIO DE LA LÓGICA CORREGIDA ✨ ---
                if self.is_authenticated:
                    user_info = self.authenticated_user_info

                    purchase_count = session.exec(
                        sqlmodel.select(sqlmodel.func.count(PurchaseItemModel.id))
                        .join(PurchaseModel)
                        .where(
                            PurchaseModel.userinfo_id == user_info.id,
                            PurchaseItemModel.blog_post_id == post_id,
                            PurchaseModel.status.in_([PurchaseStatus.CONFIRMED, PurchaseStatus.SHIPPED])
                        )
                    ).one()

                    if purchase_count > 0:
                        user_original_comment = next(
                            (c for c in db_post.comments if c.userinfo_id == user_info.id and c.parent_comment_id is None),
                            None
                        )

                        if not user_original_comment:
                            self.show_review_form = True
                        else:
                            # Se cambió la lógica aquí para ser más precisa.
                            # Asumimos 1 actualización por compra. Si compra 2 veces, tiene 2 actualizaciones.
                            total_allowed_updates = purchase_count 
                            current_updates_count = len(user_original_comment.updates)

                            if current_updates_count < total_allowed_updates:
                                self.show_review_form = True
                                latest_entry_in_thread = sorted(
                                    [user_original_comment] + user_original_comment.updates,
                                    key=lambda c: c.created_at,
                                    reverse=True
                                )[0]
                                self.my_review_for_product = self._convert_comment_to_dto(latest_entry_in_thread)
                                self.review_rating = latest_entry_in_thread.rating
                                self.review_content = latest_entry_in_thread.content
                            else:
                                # Si no le quedan créditos, marcamos el límite como alcanzado
                                self.review_limit_reached = True # <-- ✨ ESTA ES LA LÓGICA NUEVA
                # --- ✨ FIN DE LA LÓGICA CORREGIDA ✨ ---
            else:
                self.show_detail_modal = False
                yield rx.toast.error("Producto no encontrado o no disponible.")
                return

        yield AppState.load_saved_post_ids

    
    # --- AÑADIR: Evento para cargar la página de guardados ---
    @rx.event
    def on_load_saved_posts_page(self):
        """Carga la galería de publicaciones guardadas por el usuario."""
        if not self.authenticated_user_info:
            self.saved_posts_gallery = []
            return rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)
        
        with rx.session() as session:
            user_info = session.get(UserInfo, self.authenticated_user_info.id)
            if user_info:
                # Creamos los DTOs para la galería
                temp_posts = []
                # Accedemos a los posts a través de la relación y los ordenamos
                sorted_posts = sorted(user_info.saved_posts, key=lambda p: p.created_at, reverse=True)
                for p in sorted_posts:
                    product_dto = ProductCardData.from_orm(p)
                    product_dto.price_cop = p.price_cop
                    temp_posts.append(product_dto)
                self.saved_posts_gallery = temp_posts

    # Este método también se simplifica
    @rx.event
    def close_product_detail_modal(self, open_state: bool):
        if not open_state:
            self.show_detail_modal = False
            self.product_in_modal = None
            # ✨ ELIMINADO: Ya no necesitamos redirigir a "/", la URL base no cambia
    
    # ✨ NUEVA PROPIEDAD COMPUTADA
    @rx.var
    def base_app_url(self) -> str:
        """
        Devuelve la URL PÚBLICA de la aplicación para construir enlaces.
        Usa 'deploy_url' de la configuración.
        """
        # Usamos deploy_url para los enlaces que ven los usuarios,
        # no api_url que es para la conexión interna.
        return get_config().deploy_url
    
    # --- AÑADIR: Variables para la página del vendedor ---
    seller_page_info: Optional[UserInfo] = None
    seller_page_posts: list[ProductCardData] = []

    @rx.event
    def on_load_seller_page(self):
        """Carga la información del vendedor analizando la URL completa."""
        self.is_loading = True
        self.seller_page_info = None
        self.seller_page_posts = []
        yield

        seller_id_str = "0"
        try:
            # 1. Obtenemos la URL completa, ej: "/vendedor?id=42"
            full_url = self.router.url
            if full_url and "?" in full_url:
                # 2. Analizamos la URL para aislar los parámetros de consulta
                parsed_url = urlparse(full_url)
                query_dict = parse_qs(parsed_url.query)
                
                # 3. Extraemos el valor de "id" de forma segura
                # parse_qs devuelve una lista, ej: {'id': ['42']}
                id_list = query_dict.get("id")
                if id_list:
                    seller_id_str = id_list[0]
        except Exception:
            pass # Si algo falla, usamos el valor por defecto

        try:
            seller_id_int = int(seller_id_str)
        except (ValueError, TypeError):
            seller_id_int = 0

        # El resto de la lógica para cargar los datos es la misma y funcionará correctamente
        if seller_id_int > 0:
            with rx.session() as session:
                seller_info = session.exec(
                    sqlmodel.select(UserInfo).options(sqlalchemy.orm.joinedload(UserInfo.user))
                    .where(UserInfo.id == seller_id_int)
                ).one_or_none()
                self.seller_page_info = seller_info

                if seller_info:
                    posts = session.exec(
                        sqlmodel.select(BlogPostModel)
                        .where(
                            BlogPostModel.userinfo_id == seller_id_int,
                            BlogPostModel.publish_active == True
                        )
                        .order_by(BlogPostModel.created_at.desc())
                    ).all()
                    
                    temp_posts = []
                    for p in posts:
                        product_dto = ProductCardData.from_orm(p)
                        product_dto.price_cop = p.price_cop
                        temp_posts.append(product_dto)
                        
                    self.seller_page_posts = temp_posts

        self.is_loading = False