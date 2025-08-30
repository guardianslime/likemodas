# likemodas/state.py (Bloque de imports corregido)

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
import math
from collections import defaultdict
from reflex.config import get_config
from urllib.parse import urlparse, parse_qs

from likemodas.data.geography_data import LISTA_DE_BARRIOS
from .logic.shipping_calculator import calculate_dynamic_shipping

from . import navigation
from .models import (
    UserInfo, UserRole, VerificationToken, BlogPostModel, ShippingAddressModel,
    PurchaseModel, PurchaseStatus, PurchaseItemModel, NotificationModel, Category,
    PasswordResetToken, LocalUser, ContactEntryModel, CommentModel,
    SupportTicketModel, SupportMessageModel, TicketStatus, format_utc_to_local
)
from .services.email_service import send_verification_email, send_password_reset_email
from .utils.formatting import format_to_cop
from .utils.validators import validate_password
from .data.colombia_locations import load_colombia_data
from .data.product_options import (
    MATERIALES_ROPA, MATERIALES_CALZADO, MATERIALES_MOCHILAS, LISTA_TIPOS_ROPA, LISTA_TIPOS_ZAPATOS, LISTA_TIPOS_MOCHILAS, LISTA_TAMANOS_MOCHILAS, LISTA_TIPOS_GENERAL,
    LISTA_COLORES, LISTA_TALLAS_ROPA, LISTA_NUMEROS_CALZADO, LISTA_MATERIALES, LISTA_MEDIDAS_GENERAL
)

def _get_shipping_display_text(shipping_cost: Optional[float]) -> str:
    """Genera el texto de envío basado en el costo."""
    if shipping_cost == 0.0:
        return "Envío Gratis"
    if shipping_cost is not None and shipping_cost > 0:
        return f"Envío: {format_to_cop(shipping_cost)}"
    return "Envío a convenir"

# --- ✨ INICIO DE LA CORRECCIÓN: NUEVOS DTOs ---

class UserInfoDTO(rx.Base):
    """DTO simple y serializable para la información del usuario en sesión."""
    id: int
    user_id: int
    username: str
    email: str
    role: str

class NotificationDTO(rx.Base):
    """DTO para las notificaciones."""
    id: int
    message: str
    is_read: bool
    url: Optional[str]
    created_at_formatted: str

class ContactEntryDTO(rx.Base):
    """DTO para las entradas de contacto."""
    id: int
    first_name: str
    last_name: Optional[str]
    email: Optional[str]
    message: str
    created_at_formatted: str
    userinfo_id: Optional[int]


# --- ✨ FIN DE LA CORRECCIÓN ---

class ProductCardData(rx.Base):
    id: int
    title: str
    price: float = 0.0
    price_cop: str = ""
    variants: list[dict] = []
    attributes: dict = {}
    shipping_cost: Optional[float] = None
    is_moda_completa_eligible: bool = False
    shipping_display_text: str = ""
    is_imported: bool = False
    userinfo_id: int
    average_rating: float = 0.0
    rating_count: int = 0

    class Config:
        orm_mode = True

    @property
    def full_stars(self) -> list[int]:
        return list(range(math.floor(self.average_rating)))

    @property
    def has_half_star(self) -> bool:
        return (self.average_rating - math.floor(self.average_rating)) >= 0.5

    @property
    def empty_stars(self) -> list[int]:
        return list(range(5 - math.ceil(self.average_rating)))

class ProductDetailData(rx.Base):
    id: int
    title: str
    content: str
    price_cop: str
    variants: list[dict] = []
    created_at_formatted: str
    average_rating: float = 0.0
    rating_count: int = 0
    seller_name: str = ""
    seller_id: int = 0
    attributes: dict = {}
    shipping_cost: Optional[float] = None
    is_moda_completa_eligible: bool = False
    shipping_display_text: str = ""
    is_imported: bool = False

    class Config:
        orm_mode = True

    @property
    def full_stars(self) -> list[int]:
        return list(range(math.floor(self.average_rating)))

    @property
    def has_half_star(self) -> bool:
        return (self.average_rating - math.floor(self.average_rating)) >= 0.5

    @property
    def empty_stars(self) -> list[int]:
        return list(range(5 - math.ceil(self.average_rating)))

class AdminPurchaseCardData(rx.Base):
    id: int; customer_name: str; customer_email: str; purchase_date_formatted: str
    status: str; total_price: float; shipping_name: str; shipping_full_address: str
    shipping_phone: str; items_formatted: list[str]
    payment_method: str
    # --- ✨ AÑADE ESTA LÍNEA ✨ ---
    confirmed_at: Optional[datetime] = None

    @property
    def total_price_cop(self) -> str:
        return format_to_cop(self.total_price)
    
class PurchaseItemCardData(rx.Base):
    """DTO para mostrar la miniatura de un artículo en el historial de compras."""
    id: int
    title: str
    image_url: str
    price_at_purchase: float
    price_at_purchase_cop: str
    quantity: int

    @property # <-- ✨ ESTA ES LA CORRECCIÓN
    def subtotal_cop(self) -> str:
        """Calcula y formatea el subtotal para esta línea de artículo."""
        return format_to_cop(self.price_at_purchase * self.quantity)
    
class UserPurchaseHistoryCardData(rx.Base):
    """DTO actualizado para el historial de compras del usuario."""
    id: int
    userinfo_id: int  # --- AÑADE ESTA LÍNEA ---
    purchase_date_formatted: str
    status: str
    total_price_cop: str
    shipping_applied_cop: str
    shipping_name: str
    shipping_address: str
    shipping_neighborhood: str
    shipping_city: str
    shipping_phone: str
    items: list[PurchaseItemCardData]

class AdminPostRowData(rx.Base):
    """DTO para una fila en la tabla de publicaciones del admin."""
    id: int
    title: str
    price_cop: str
    publish_active: bool
    main_image_url: str = ""

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

class InvoiceItemData(rx.Base):
    """Un modelo específico para cada línea de artículo en la factura."""
    name: str
    quantity: int
    price_cop: str
    subtotal_cop: str
    iva_cop: str
    total_con_iva_cop: str

    @property
    def price_cop(self) -> str:
        return format_to_cop(self.price)

    @property
    def total_cop(self) -> str:
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
    shipping_applied_cop: str # <-- ✨ 1. AÑADE ESTE CAMPO
    iva_cop: str
    total_price_cop: str

class SupportMessageData(rx.Base):
    author_id: int
    author_username: str
    content: str
    created_at_formatted: str

class SupportTicketAdminData(rx.Base):
    """DTO para mostrar un resumen del ticket en la lista del admin."""
    ticket_id: int
    purchase_id: int
    buyer_name: str
    subject: str
    status: str
    created_at_formatted: str

class SellerInfoData(rx.Base):
    """DTO para mostrar la información pública de un vendedor."""
    id: int
    username: str

class SupportTicketData(rx.Base):
    """DTO para mostrar la información de un ticket en la vista de chat."""
    id: int
    purchase_id: int
    buyer_id: int
    seller_id: int
    subject: str
    status: str

    # --- ✨ INICIO DE LA CORRECCIÓN ✨ ---
    # Se añade esta configuración para permitir el uso de .from_orm()
    class Config:
        orm_mode = True
    # --- ✨ FIN DE LA CORRECCIÓN ✨ ---

# --- ✨ INICIO DE LA MODIFICACIÓN ✨ ---
class AttributeGroupDTO(rx.Base):
    """DTO para agrupar un atributo y sus posibles valores."""
    key: str        # ej: "Talla"
    options: list[str] # RENOMBRADO de 'values' a 'options'
# --- ✨ FIN DE LA MODIFICACIÓN ✨ ---

class CartItemData(rx.Base):
    """DTO para el carrito, ahora incluye detalles de la variante."""
    cart_key: str  # e.g., "15-2" (product_id-variant_index)
    product_id: int
    variant_index: int
    title: str
    price: float
    price_cop: str
    image_url: str
    quantity: int
    variant_details: dict # e.g., {"Talla": "S", "Color": "Azul"}

    @property
    def subtotal(self) -> float:
        return self.price * self.quantity

    @property
    def subtotal_cop(self) -> str:
        return format_to_cop(self.subtotal)
    
class ModalSelectorDTO(rx.Base):
    """Representa el estado completo de un selector en el modal."""
    key: str           # ej: "Talla"
    options: list[str]   # ej: ["S", "M"] (solo las opciones válidas)
    current_value: str # ej: "S"

class VariantFormData(rx.Base):
    """DTO para manejar los datos de una variante en el formulario."""
    attributes: dict[str, str]
    stock: int = 10  # Stock por defecto
    image_url: str = ""

# --- AÑADE ESTA NUEVA CLASE DTO AQUÍ ---
class UniqueVariantItem(rx.Base):
    """Un DTO para que rx.foreach entienda la estructura de las variantes únicas."""
    variant: dict  # El diccionario de la variante en sí
    index: int     # El índice original en la lista completa de variantes

# --- ESTADO PRINCIPAL DE LA APLICACIÓN ---
class AppState(reflex_local_auth.LocalAuthState):
    """El estado único y monolítico de la aplicación."""

    # --- 👇 INICIO DE LA CORRECCIÓN 👇 ---
    # Se define como una variable de estado normal, no como una propiedad computada.
    # Esto asegura que esté disponible durante la compilación para las migraciones.
    # --- ✨ INICIO DE LA CORRECCIÓN: VARIABLES DE ESTADO MODIFICADAS ---
    _notifications: List[NotificationDTO] = []
    contact_entries: list[ContactEntryDTO] = []
    # --- ✨ FIN DE LA CORRECCIÓN ---
    lista_de_barrios_popayan: list[str] = LISTA_DE_BARRIOS
    # --- FIN DE LA CORRECCIÓN ---

    # --- Variables de Perfil del Vendedor ---
    seller_profile_barrio: str = ""
    seller_profile_address: str = ""
    
    _product_id_to_load_on_mount: Optional[int] = None
    success: bool = False
    error_message: str = ""


    
    # --- ✨ INICIO DE LA CORRECCIÓN: PROPIEDADES COMPUTADAS REFACTORIZADAS ---
    @rx.var(cache=True)
    def authenticated_user_info(self) -> UserInfoDTO | None:
        if not self.is_authenticated or self.authenticated_user.id < 0:
            return None
        with rx.session() as session:
            query = (
                sqlmodel.select(UserInfo)
                .options(sqlalchemy.orm.joinedload(UserInfo.user))
                .where(UserInfo.user_id == self.authenticated_user.id)
            )
            user_info_db = session.exec(query).one_or_none()
            if user_info_db and user_info_db.user:
                return UserInfoDTO(
                    id=user_info_db.id,
                    user_id=user_info_db.user_id,
                    username=user_info_db.user.username,
                    email=user_info_db.email,
                    role=user_info_db.role.value
                )
            return None

    @rx.var
    def is_admin(self) -> bool:
        return self.authenticated_user_info is not None and self.authenticated_user_info.role == UserRole.ADMIN.value

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
        token = ""
        try:
            full_url = self.router.url
            if "?" in full_url:
                query_string = full_url.split("?")[1]
                params = dict(param.split("=") for param in query_string.split("&"))
                token = params.get("token", "")
        except Exception:
            pass

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
        # --- ✨ INICIO DE LA CORRECCIÓN ✨ ---
        # Reemplazamos el método obsoleto self.router.page.params
        token = ""
        try:
            full_url = self.router.url
            if "?" in full_url:
                query_string = full_url.split("?")[1]
                params = dict(param.split("=") for param in query_string.split("&"))
                token = params.get("token", "")
        except Exception:
            pass  # Falla silenciosamente si la URL está mal formada

        self.token = token
        # --- ✨ FIN DE LA CORRECCIÓN ✨ ---
        
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
            
    
    @rx.event
    def get_invoice_data(self, purchase_id: int) -> Optional[InvoiceData]:
        if not self.is_authenticated:
            return None

        with rx.session() as session:
            # ... (la consulta a la base de datos no cambia) ...
            purchase = session.exec(
                sqlmodel.select(PurchaseModel)
                .options(
                    sqlalchemy.orm.joinedload(PurchaseModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post)
                )
                .where(PurchaseModel.id == purchase_id)
            ).unique().one_or_none()

            if not purchase:
                return None

            if not self.is_admin and (not self.authenticated_user_info or self.authenticated_user_info.id != purchase.userinfo_id):
                return None

            # --- ✨ 2. LÓGICA DE CÁLCULO ACTUALIZADA ✨ ---
            IVA_RATE = 0.19
            grand_total = purchase.total_price
            shipping_cost = purchase.shipping_applied or 0.0
            
            # El subtotal de los productos es el total menos el envío.
            # --- ✨ LÓGICA DE CÁLCULO DE FACTURA TOTALMENTE NUEVA Y CONSISTENTE ✨ ---
            subtotal_base_products = sum(item.blog_post.base_price * item.quantity for item in purchase.items if item.blog_post)
            shipping_cost = purchase.shipping_applied or 0.0
            iva_amount = subtotal_base_products * 0.19
            grand_total = purchase.total_price # Este es el valor final guardado, que debe ser la suma de las partes.

            invoice_items = []
            for item in purchase.items:
                if item.blog_post:
                    item_base_subtotal = item.blog_post.base_price * item.quantity
                    item_iva = item_base_subtotal * 0.19
                    item_total_con_iva = item_base_subtotal + item_iva
                    invoice_items.append(
                        InvoiceItemData(
                            name=item.blog_post.title,
                            quantity=item.quantity,
                            price_cop=format_to_cop(item.blog_post.base_price), # <-- Usamos precio base unitario
                            subtotal_cop=format_to_cop(item_base_subtotal), # <-- Usamos subtotal base
                            iva_cop=format_to_cop(item_iva),
                            total_con_iva_cop=format_to_cop(item_total_con_iva)
                        )
                    )

            return InvoiceData(
                id=purchase.id,
                purchase_date_formatted=purchase.purchase_date_formatted,
                status=purchase.status.value,
                items=invoice_items,
                customer_name=purchase.shipping_name,
                customer_email=purchase.userinfo.email if purchase.userinfo else "N/A",
                shipping_full_address=f"{purchase.shipping_address}, {purchase.shipping_neighborhood}, {purchase.shipping_city}",
                shipping_phone=purchase.shipping_phone,
                subtotal_cop=format_to_cop(subtotal_base_products),
                shipping_applied_cop=format_to_cop(shipping_cost),
                iva_cop=format_to_cop(iva_amount),
                total_price_cop=format_to_cop(grand_total),
            )
            
    @rx.var
    def available_types(self) -> list[str]:
        if self.category == Category.ROPA.value:
            return LISTA_TIPOS_ROPA
        if self.category == Category.CALZADO.value:
            return LISTA_TIPOS_ZAPATOS
        if self.category == Category.MOCHILAS.value:
            return LISTA_TIPOS_MOCHILAS
        return []

    @rx.var
    def material_label(self) -> str:
        if self.category == Category.ROPA.value:
            return "Tela"
        return "Material"

    @rx.var
    def available_materials(self) -> list[str]:
        if self.category == Category.ROPA.value:
            return MATERIALES_ROPA
        if self.category == Category.CALZADO.value:
            return MATERIALES_CALZADO
        if self.category == Category.MOCHILAS.value:
            return MATERIALES_MOCHILAS
        return []
            
    attr_tallas_ropa: list[str] = []
    attr_numeros_calzado: list[str] = []
    attr_tamanos_mochila: list[str] = []
    # --- CAMBIO CLAVE 1: De lista a string ---
    # Ya no permitimos múltiples colores, solo uno a la vez.
    attr_colores: str = "" # Antes era una lista: attr_colores: list[str] = []
    attr_material: str = ""
    attr_tipo: str = ""
    search_attr_tipo: str = ""

    # --- AÑADE ESTE NUEVO SETTER ---
    def set_attr_colores(self, value: str): self.attr_colores = value
    def set_attr_talla_ropa(self, value: str): self.attr_talla_ropa = value
    def set_attr_material(self, value: str): self.attr_material = value
    def set_attr_numero_calzado(self, value: str): self.attr_numero_calzado = value
    def set_attr_tipo(self, value: str):
        self.attr_tipo = value

    SELECTABLE_ATTRIBUTES = ["Talla", "Número", "Tamaño"]

    def select_variant_for_editing(self, index: int):
        """
        Selecciona una imagen. Carga sus atributos guardados en el formulario.
        La nueva propiedad `current_generated_variants` se actualizará automáticamente.
        """
        self.selected_variant_index = index
        
        # Limpia los campos del formulario antes de cargar los nuevos
        self.attr_colores = "" # Limpiar el color
        self.attr_tallas_ropa = []
        self.attr_numeros_calzado = []
        self.attr_tamanos_mochila = []

        # Carga los atributos guardados para esta imagen, si existen
        if 0 <= index < len(self.new_variants):
            variant_attrs = self.new_variants[index].get("attributes", {})
            # Ahora asignamos un string, no una lista. Asumimos el primer color si hay varios guardados por error.
            self.attr_colores = variant_attrs.get("Color", [""])[0] if isinstance(variant_attrs.get("Color"), list) else variant_attrs.get("Color", "")
            if self.category == Category.ROPA.value:
                self.attr_tallas_ropa = variant_attrs.get("Talla", [])
            elif self.category == Category.CALZADO.value:
                self.attr_numeros_calzado = variant_attrs.get("Número", [])
            elif self.category == Category.MOCHILAS.value:
                self.attr_tamanos_mochila = variant_attrs.get("Tamaño", [])

    def save_variant_attributes(self):
        """Guarda los atributos actuales del formulario en la variante seleccionada."""
        if self.selected_variant_index < 0:
            return rx.toast.error("Primero selecciona una imagen para asignarle atributos.")

        attributes = {}
        if self.category == Category.ROPA.value:
            if self.attr_colores: attributes["Color"] = self.attr_colores
            if self.attr_tallas_ropa: attributes["Talla"] = self.attr_tallas_ropa
        elif self.category == Category.CALZADO.value:
            if self.attr_colores: attributes["Color"] = self.attr_colores
            if self.attr_numeros_calzado: attributes["Número"] = self.attr_numeros_calzado
        elif self.category == Category.MOCHILAS.value:
            if self.attr_colores: attributes["Color"] = self.attr_colores
            if self.attr_tamanos_mochila: attributes["Tamaño"] = self.attr_tamanos_mochila

        self.new_variants[self.selected_variant_index]["attributes"] = attributes
        return rx.toast.success(f"Atributos guardados para la imagen #{self.selected_variant_index + 1}")

    def _set_default_attributes_from_variant(self, variant: dict):
        """Función auxiliar para establecer la selección por defecto en el modal."""
        new_selections = {}
        attributes = variant.get("attributes", {})
        for key, value in attributes.items():
            # Si el atributo tiene una lista de opciones (ej: Color), toma la primera
            if isinstance(value, list) and value:
                new_selections[key] = value[0]
            # Si es un solo valor (ej: Talla), lo toma directamente
            elif isinstance(value, str):
                new_selections[key] = value
        # Actualiza el estado que controla los selectores en el modal
        self.modal_selected_attributes = new_selections

    # Nuevas variables para el formulario de variantes
    # --- ✨ INICIO DE LA CORRECCIÓN ✨ ---
    # Se añaden las variables que faltaban para el formulario de AÑADIR posts.
    new_variants: list[dict] = []
    selected_variant_index: int = -1 # -1 significa que no hay ninguna seleccionada
    variant_form_data: list[VariantFormData] = []
    # --- AÑADE ESTA LÍNEA AQUÍ ---
    generated_variants_map: dict[int, list[VariantFormData]] = {}
    # --- FIN DE LA CORRECCIÓN ---

    # --- NUEVA PROPIEDAD COMPUTADA ---

    
    @rx.var
    def current_variant_display_attributes(self) -> dict[str, str]:
        """Prepara los atributos de la variante actual que son de SOLO LECTURA."""
        variant = self.current_modal_variant
        if not variant: return {}
        
        display_attrs = {}
        attributes = variant.get("attributes", {})
        for key, value in attributes.items():
            if key not in self.SELECTABLE_ATTRIBUTES:
                display_attrs[key] = ", ".join(value) if isinstance(value, list) else value
        return display_attrs

    # Método para generar las combinaciones de variantes
    def generate_variants(self):
        """
        Genera variantes y las asocia con la imagen actualmente seleccionada.
        También guarda los atributos en la variante principal para persistencia.
        """
        if self.selected_variant_index < 0:
            return rx.toast.error("Por favor, selecciona una imagen primero.")

        # 1. Recopila los atributos del formulario
        color = self.attr_colores
        sizes, size_key = [], ""
        if self.category == Category.ROPA.value:
            sizes, size_key = self.attr_tallas_ropa, "Talla"
        elif self.category == Category.CALZADO.value:
            sizes, size_key = self.attr_numeros_calzado, "Número"
        elif self.category == Category.MOCHILAS.value:
            sizes, size_key = self.attr_tamanos_mochila, "Tamaño"

        if not color or not sizes: # Se valida el string de color
            return rx.toast.error("Debes seleccionar un color y al menos una talla/tamaño/número.")

       # Guarda los atributos en la imagen (Color ahora es un string)
        current_attributes = {"Color": color, size_key: sizes}
        self.new_variants[self.selected_variant_index]["attributes"] = current_attributes

        # Genera las combinaciones
        generated_variants = []
        for size in sizes: # El bucle de colores ya no es necesario
            generated_variants.append(
                VariantFormData(attributes={"Color": color, size_key: size})
            )
        
        self.generated_variants_map[self.selected_variant_index] = generated_variants
        return rx.toast.info(f"{len(generated_variants)} variantes generadas para la imagen #{self.selected_variant_index + 1}.")


    # --- FUNCIONES DE STOCK MODIFICADAS ---
    def _update_variant_stock(self, group_index: int, item_index: int, new_stock: int):
        if group_index in self.generated_variants_map and 0 <= item_index < len(self.generated_variants_map[group_index]):
            self.generated_variants_map[group_index][item_index].stock = max(0, new_stock)

    def set_variant_stock(self, group_index: int, item_index: int, stock_str: str):
        try:
            self._update_variant_stock(group_index, item_index, int(stock_str))
        except (ValueError, TypeError):
            pass

    def increment_variant_stock(self, group_index: int, item_index: int):
        if group_index in self.generated_variants_map and 0 <= item_index < len(self.generated_variants_map[group_index]):
            current_stock = self.generated_variants_map[group_index][item_index].stock
            self._update_variant_stock(group_index, item_index, current_stock + 1)
            
    def decrement_variant_stock(self, group_index: int, item_index: int):
        if group_index in self.generated_variants_map and 0 <= item_index < len(self.generated_variants_map[group_index]):
            current_stock = self.generated_variants_map[group_index][item_index].stock
            self._update_variant_stock(group_index, item_index, current_stock - 1)

    def assign_image_to_variant(self, group_index: int, item_index: int, image_url: str):
        if group_index in self.generated_variants_map and 0 <= item_index < len(self.generated_variants_map[group_index]):
            self.generated_variants_map[group_index][item_index].image_url = image_url
    


    # --- 👇 AÑADE ESTA NUEVA FUNCIÓN AQUÍ 👇 ---
    @rx.var
    def uploaded_image_urls(self) -> list[str]:
        """
        Devuelve una lista de solo las URLs de las imágenes subidas en el formulario.
        Esta es la forma correcta de transformar datos para la UI.
        """
        if not self.new_variants:
            return []
        # Retorna solo las URLs que no están vacías
        return [
            v.get("image_url", "") 
            for v in self.new_variants 
            if v.get("image_url")
        ]

    @rx.event
    def submit_and_publish(self, form_data: dict):
        """
        Crea y publica un nuevo producto, guardando las variantes con su stock individual.
        """
        if not self.is_admin or not self.authenticated_user_info:
            return rx.toast.error("Acción no permitida.")
        if not all([form_data.get("title"), form_data.get("price"), form_data.get("category")]):
            return rx.toast.error("Título, precio y categoría son obligatorios.")
        
        if not self.generated_variants_map:
            return rx.toast.error("Debes generar y configurar las variantes para al menos una imagen.")

        try:
            shipping_cost = float(self.shipping_cost_str) if self.shipping_cost_str else None
            limit = None
            if self.combines_shipping and self.shipping_combination_limit_str:
                limit = int(self.shipping_combination_limit_str)
            if self.combines_shipping and (limit is None or limit <= 0):
                return rx.toast.error("El límite para envío combinado debe ser un número mayor a 0.")
        except ValueError:
            return rx.toast.error("Los costos y límites deben ser números válidos.")

        # --- Lógica para aplanar las variantes del map a una sola lista para la BD ---
        all_variants_for_db = []
        for index, generated_list in self.generated_variants_map.items():
            # Obtiene la URL de la imagen principal para este grupo de variantes
            main_image_url_for_group = self.new_variants[index].get("image_url", "")
            
            for variant_data in generated_list:
                all_variants_for_db.append({
                    "attributes": variant_data.attributes,
                    "stock": variant_data.stock,
                    # Usa la imagen asignada a la variante, o la imagen principal del grupo como fallback
                    "image_url": variant_data.image_url or main_image_url_for_group
                })

        if not all_variants_for_db:
             return rx.toast.error("No se encontraron variantes configuradas para guardar.")

        with rx.session() as session:
            new_post = BlogPostModel(
                userinfo_id=self.authenticated_user_info.id,
                title=form_data["title"],
                content=form_data.get("content", ""),
                price=float(form_data.get("price", 0.0)),
                price_includes_iva=self.price_includes_iva,
                category=form_data.get("category"),
                variants=all_variants_for_db,
                publish_active=True,
                publish_date=datetime.now(timezone.utc),
                shipping_cost=shipping_cost,
                is_moda_completa_eligible=self.is_moda_completa,
                combines_shipping=self.combines_shipping,
                shipping_combination_limit=limit,
                is_imported=self.is_imported,
            )
            session.add(new_post)
            session.commit()
            session.refresh(new_post)

        self._clear_add_form()
        yield rx.toast.success("Producto publicado exitosamente.")
        return rx.redirect("/blog")
    
    @rx.var
    def displayed_posts(self) -> list[ProductCardData]:
        posts_to_filter = self.posts

        if self.min_price:
            try:
                min_p = float(self.min_price)
                posts_to_filter = [p for p in posts_to_filter if p.price >= min_p]
            except ValueError:
                pass
        if self.max_price:
            try:
                max_p = float(self.max_price)
                posts_to_filter = [p for p in posts_to_filter if p.price <= max_p]
            except ValueError:
                pass

        if self.filter_colors:
            posts_to_filter = [
                p for p in posts_to_filter 
                if p.attributes.get("Color") in self.filter_colors
            ]
            
        if self.filter_materiales_tela:
            posts_to_filter = [
                p for p in posts_to_filter 
                if (p.attributes.get("Material") in self.filter_materiales_tela) or 
                (p.attributes.get("Tela") in self.filter_materiales_tela)
            ]

        if self.filter_tallas:
            posts_to_filter = [
                p for p in posts_to_filter
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

        if self.filter_free_shipping:
            posts_to_filter = [
                p for p in posts_to_filter 
                if p.shipping_cost == 0.0
            ]

        # --- 👇 LÓGICA DEL FILTRO CORREGIDA AQUÍ 👇 ---
        if self.filter_complete_fashion:
            posts_to_filter = [
                p for p in posts_to_filter 
                if p.is_moda_completa_eligible
            ]
        # --- FIN DE LA CORRECCIÓN ---

        return posts_to_filter
    
    search_attr_color: str = ""
    search_attr_talla_ropa: str = ""
    search_attr_material: str = ""
    search_attr_numero_calzado: str = ""
    search_attr_tamano_mochila: str = ""

    def set_search_attr_color(self, query: str): self.search_attr_color = query
    def set_search_attr_talla_ropa(self, query: str): self.search_attr_talla_ropa = query
    def set_search_attr_material(self, query: str): self.search_attr_material = query
    def set_search_attr_numero_calzado(self, query: str): self.search_attr_numero_calzado = query
    def set_search_attr_tipo(self, query: str):
        self.search_attr_tipo = query

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
        if not self.search_attr_material.strip():
            return self.available_materials
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
    filter_colors: list[str] = []
    filter_tallas: list[str] = []
    filter_tipos_prenda: list[str] = []
    filter_tipos_zapato: list[str] = []
    filter_numeros_calzado: list[str] = []
    filter_tipos_mochila: list[str] = []
    filter_materiales_tela: list[str] = []
    filter_tipos_general: list[str] = []

    def add_variant_attribute(self, key: str, value: str):
        """
        Añade un valor de atributo (ej: "S") a la lista de un atributo específico (ej: "Talla")
        de la variante actualmente seleccionada.
        """
        if self.selected_variant_index < 0 or self.selected_variant_index >= len(self.new_variants):
            return

        variant = self.new_variants[self.selected_variant_index]
        if "attributes" not in variant:
            variant["attributes"] = {}
        
        if key not in variant["attributes"]:
            variant["attributes"][key] = []

        # Evita duplicados
        if value not in variant["attributes"][key]:
            variant["attributes"][key].append(value)
            # Actualiza también el "buffer" de la UI para que se refresque visualmente
            if key == "Talla": self.attr_tallas_ropa = variant["attributes"][key]
            elif key == "Número": self.attr_numeros_calzado = variant["attributes"][key]
            elif key == "Tamaño": self.attr_tamanos_mochila = variant["attributes"][key]


    def remove_variant_attribute(self, key: str, value: str):
        """
        Elimina un valor de atributo de la lista de un atributo específico
        de la variante actualmente seleccionada.
        """
        if self.selected_variant_index < 0 or self.selected_variant_index >= len(self.new_variants):
            return

        variant = self.new_variants[self.selected_variant_index]
        if "attributes" in variant and key in variant["attributes"]:
            if value in variant["attributes"][key]:
                variant["attributes"][key].remove(value)
                # Actualiza también el "buffer" de la UI para que se refresque visualmente
                if key == "Talla": self.attr_tallas_ropa = variant["attributes"][key]
                elif key == "Número": self.attr_numeros_calzado = variant["attributes"][key]
                elif key == "Tamaño": self.attr_tamanos_mochila = variant["attributes"][key]

    def add_filter_value(self, filter_name: str, value: str):
        current_list = getattr(self, filter_name)
        if value not in current_list:
            if len(current_list) >= 5:
                return rx.toast.info("Puedes seleccionar un máximo de 5 filtros por característica.")
            current_list.append(value)
            setattr(self, filter_name, current_list)

    def remove_filter_value(self, filter_name: str, value: str):
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
    search_tipo_general: str = ""

    def set_search_tipo_prenda(self, query: str): self.search_tipo_prenda = query
    def set_search_tipo_zapato(self, query: str): self.search_tipo_zapato = query
    def set_search_tipo_mochila(self, query: str): self.search_tipo_mochila = query
    def set_search_tipo_general(self, query: str): self.search_tipo_general = query
    def set_search_color(self, query: str): self.search_color = query
    def set_search_talla(self, query: str): self.search_talla = query
    def set_search_numero_calzado(self, query: str): self.search_numero_calzado = query
    def set_search_material_tela(self, query: str): self.search_material_tela = query
    def set_search_medida_talla(self, query: str): self.search_medida_talla = query
    def set_search_tipo_general(self, query: str): self.search_tipo_general = query

    @rx.var
    def filtered_tipos_general(self) -> list[str]:
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
    
    _raw_posts: list[ProductCardData] = []
    posts: list[ProductCardData] = []
    is_loading: bool = True



    @rx.event
    def on_load(self):
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
            
            self.current_category = category if category else "todos"

        with rx.session() as session:
            query = sqlmodel.select(BlogPostModel).where(BlogPostModel.publish_active == True)
            
            if self.current_category and self.current_category != "todos":
                query = query.where(BlogPostModel.category == self.current_category)

            results = session.exec(query.order_by(BlogPostModel.created_at.desc())).all()
            
            temp_posts = []
            for p in results:
                temp_posts.append(
                    ProductCardData(
                        id=p.id,
                        userinfo_id=p.userinfo_id,
                        title=p.title,
                        price=p.price,
                        price_cop=p.price_cop,
                        # --- ✨ INICIO DE LA CORRECCIÓN ✨ ---
                        # Se reemplaza 'image_urls=p.image_urls' por 'variants=p.variants'
                        variants=p.variants or [],
                        # --- ✨ FIN DE LA CORRECCIÓN ✨ ---
                        average_rating=p.average_rating,
                        rating_count=p.rating_count,
                        shipping_cost=p.shipping_cost,
                        is_moda_completa_eligible=p.is_moda_completa_eligible,
                        shipping_display_text=_get_shipping_display_text(p.shipping_cost),
                        is_imported=p.is_imported,
                    )
                )
            self.posts = temp_posts
        
        self.is_loading = False
    

    show_detail_modal: bool = False
    product_in_modal: Optional[ProductDetailData] = None
    current_image_index: int = 0
    is_editing_post: bool = False
    post_to_edit_id: Optional[int] = None 
    post_title: str = ""
    post_content: str = ""
    price_str: str = ""
    price_includes_iva: bool = True
    post_images_in_form: list[str] = []

    

    
    # --- ✨ FIN DE LA CORRECCIÓN ✨ ---

    def next_image(self):
        if self.product_in_modal and self.product_in_modal.image_urls:
            self.current_image_index = (self.current_image_index + 1) % len(self.product_in_modal.image_urls)

    def prev_image(self):
        if self.product_in_modal and self.product_in_modal.image_urls:
            self.current_image_index = (self.current_image_index - 1 + len(self.product_in_modal.image_urls)) % len(self.product_in_modal.image_urls)

    def set_post_title(self, title: str): self.post_title = title
    def set_post_content(self, content: str): self.post_content = content
    def set_price(self, price: str): self.price_str = price

    def set_price_includes_iva(self, value: bool):
        self.price_includes_iva = value

    # --- AÑADE ESTAS LÍNEAS ---
    is_imported: bool = False

    def set_is_imported(self, value: bool):
        self.is_imported = value
    # --- FIN ---

    @rx.event
    def start_editing_post(self, post_id: int):
        if not self.is_admin:
            return rx.toast.error("Acción no permitida.")
        with rx.session() as session:
            db_post = session.get(BlogPostModel, post_id)
            if db_post and (db_post.userinfo_id == self.authenticated_user_info.id or self.is_admin):
                # --- 👇 LÍNEAS CORREGIDAS 👇 ---
                # Guardamos solo el ID
                self.post_to_edit_id = db_post.id
                # El resto de los campos se llenan como antes
                self.post_title = db_post.title
                self.post_content = db_post.content
                self.price_str = str(db_post.price or 0.0)
                # Obtenemos las imágenes de los variants
                self.post_images_in_form = [v.get("image_url", "") for v in (db_post.variants or [])]
                self.is_editing_post = True
            else:
                yield rx.toast.error("No se encontró la publicación o no tienes permisos.")

    @rx.event
    def cancel_editing_post(self, open_state: bool):
        if not open_state:
            self.is_editing_post = False
            # --- 👇 LÍNEA CORREGIDA 👇 ---
            self.post_to_edit_id = None
            self.post_title = ""
            self.post_content = ""
            self.price_str = ""
            self.post_images_in_form = []

    @rx.event
    def save_edited_post(self, form_data: dict):
        # 1. Se comprueba 'post_to_edit_id' en lugar de 'post_to_edit'
        if not self.is_admin or self.post_to_edit_id is None:
            return rx.toast.error("No se pudo guardar la publicación.")
        
        with rx.session() as session:
            # 2. Se carga el post desde la base de datos usando el ID
            post_to_update = session.get(BlogPostModel, self.post_to_edit_id)
            if post_to_update:
                post_to_update.title = form_data.get("title", post_to_update.title)
                post_to_update.content = form_data.get("content", post_to_update.content)
                try:
                    price_val = form_data.get("price", post_to_update.price)
                    post_to_update.price = float(price_val) if price_val else 0.0
                except (ValueError, TypeError):
                    return rx.toast.error("El precio debe ser un número válido.")

                # --- 3. Lógica para actualizar 'variants' preservando atributos ---
                
                # Mapea las URLs originales a sus atributos para no perderlos
                existing_variants_map = {
                    v.get("image_url"): v.get("attributes", {}) 
                    for v in (post_to_update.variants or [])
                }
                
                new_variants_list = []
                for image_url in self.post_images_in_form:
                    # Si la imagen ya existía, se conservan sus atributos.
                    # Si es nueva, se le asignan atributos vacíos.
                    new_variants_list.append({
                        "image_url": image_url,
                        "attributes": existing_variants_map.get(image_url, {})
                    })
                
                post_to_update.variants = new_variants_list
                
                session.add(post_to_update)
                session.commit()
                
                # El resto de la lógica para cerrar el modal y notificar es correcta
                yield AppState.cancel_editing_post(False)
                yield AppState.on_load_admin_store
                yield rx.toast.success("Publicación actualizada correctamente.")
                # --- ✨ FIN DE LA CORRECCIÓN ✨ ---

    temp_images: list[str] = []

    async def handle_add_upload(self, files: list[rx.UploadFile]):
        """Modificado para crear placeholders y auto-seleccionar la primera imagen."""
        for file in files:
            upload_data = await file.read()
            unique_filename = f"{secrets.token_hex(8)}-{file.name}"
            outfile = rx.get_upload_dir() / unique_filename
            outfile.write_bytes(upload_data)
            self.new_variants.append({
                "image_url": unique_filename,
                "attributes": {}
            })
        
        # 1. CORRECCIÓN: Si es la primera imagen, la seleccionamos automáticamente.
        if self.selected_variant_index == -1 and len(self.new_variants) > 0:
            self.selected_variant_index = 0

    @rx.event
    def remove_temp_image(self, filename: str):
        if filename in self.temp_images:
            self.temp_images.remove(filename)

    @rx.event
    async def handle_edit_upload(self, files: list[rx.UploadFile]):
        for file in files:
            upload_data = await file.read()
            unique_filename = f"{secrets.token_hex(8)}-{file.name}"
            outfile = rx.get_upload_dir() / unique_filename
            outfile.write_bytes(upload_data)
            self.post_images_in_form.append(unique_filename)

    @rx.event
    def remove_edited_image(self, filename: str):
        if filename in self.post_images_in_form:
            self.post_images_in_form.remove(filename)



    @rx.var
    def current_modal_variant(self) -> Optional[dict]:
        """Devuelve la variante seleccionada actualmente en el modal."""
        if self.product_in_modal and self.product_in_modal.variants:
            if 0 <= self.modal_selected_variant_index < len(self.product_in_modal.variants):
                return self.product_in_modal.variants[self.modal_selected_variant_index]
        return None

    @rx.var
    def current_modal_image_filename(self) -> str:
        """
        Devuelve SOLO el nombre del archivo de la variante seleccionada.
        Esto es un string simple y seguro para el backend.
        """
        variant = self.current_modal_variant
        return variant.get("image_url", "") if variant else ""

    @rx.var
    def current_modal_attributes_list(self) -> list[AttributeData]:
        """Devuelve los atributos de la variante seleccionada como una lista para la UI."""
        variant = self.current_modal_variant
        if not variant or not variant.get("attributes"):
            return []

        processed = []
        for k, v in variant["attributes"].items():
            value_str = ", ".join(v) if isinstance(v, list) else str(v)
            processed.append(AttributeData(key=k, value=value_str))
        return processed
    
    @rx.var
    def unique_modal_variants(self) -> list[UniqueVariantItem]: # <-- Cambia el tipo de retorno
        """
        Devuelve una lista de DTOs con URLs de imagen únicas para las miniaturas del modal.
        """
        if not self.product_in_modal or not self.product_in_modal.variants:
            return []
        
        unique_items = []
        seen_images = set()
        for i, variant in enumerate(self.product_in_modal.variants):
            image_url = variant.get("image_url")
            if image_url and image_url not in seen_images:
                seen_images.add(image_url)
                # En lugar de un dict, creamos una instancia del nuevo DTO
                unique_items.append(UniqueVariantItem(variant=variant, index=i))
        return unique_items

    cart: Dict[int, int] = {}

    modal_selected_attributes: dict = {}
    
    @rx.var
    def cart_items_count(self) -> int: return sum(self.cart.values())
    # @rx.var
    # def cart_total(self) -> float: return sum(p.price * q for p, q in self.cart_details if p and p.price)
    #@rx.var
    # def cart_total_cop(self) -> str: return format_to_cop(self.cart_total)
    
    @rx.var(cache=True)
    def authenticated_user_info(self) -> UserInfo | None:
        if not self.is_authenticated or self.authenticated_user.id < 0:
            return None
        with rx.session() as session:
            query = (
                sqlmodel.select(UserInfo)
                .options(sqlalchemy.orm.joinedload(UserInfo.user))
                .where(UserInfo.user_id == self.authenticated_user.id)
            )
            return session.exec(query).one_or_none()

    @rx.var
    def is_admin(self) -> bool:
        return self.authenticated_user_info is not None and self.authenticated_user_info.role == UserRole.ADMIN
        
    @rx.event
    def on_load_seller_profile(self):
        """Carga los datos del perfil del vendedor al entrar a la página de edición."""
        if self.is_admin and self.authenticated_user_info:
            self.seller_profile_barrio = self.authenticated_user_info.seller_barrio or ""
            self.seller_profile_address = self.authenticated_user_info.seller_address or ""

    def set_seller_profile_barrio(self, barrio: str):
        """Actualiza el barrio seleccionado en el formulario de perfil."""
        self.seller_profile_barrio = barrio

    def set_seller_profile_address(self, address: str):
        self.seller_profile_address = address

    @rx.event
    def save_seller_profile(self, form_data: dict):
        """Guarda la información de ubicación del vendedor en la base de datos."""
        if not self.is_admin or not self.authenticated_user_info:
            return rx.toast.error("Acción no permitida.")

        address = form_data.get("seller_address", "")
        if not self.seller_profile_barrio or not address:
            return rx.toast.error("Debes seleccionar un barrio y escribir una dirección.")

        with rx.session() as session:
            user_info_to_update = session.get(UserInfo, self.authenticated_user_info.id)
            if user_info_to_update:
                user_info_to_update.seller_barrio = self.seller_profile_barrio
                user_info_to_update.seller_address = address
                session.add(user_info_to_update)
                session.commit()
                return rx.toast.success("¡Ubicación de origen guardada!")
            
    # --- ✨ 1. AÑADE LAS NUEVAS VARIABLES DE ESTADO ✨ ---
    payment_method: str = "online" # Valor por defecto para el carrito
    # --- ✨ AÑADE ESTA LÍNEA AQUÍ ✨ ---
    active_purchases: List[AdminPurchaseCardData] = []
    admin_delivery_time: Dict[int, Dict[str, str]] = {}

    # --- ✨ 2. AÑADE LOS SETTERS ✨ ---
    def set_payment_method(self, method: str):
        self.payment_method = method

    def set_admin_delivery_time(self, purchase_id: int, unit: str, value: str):
        if purchase_id not in self.admin_delivery_time:
            self.admin_delivery_time[purchase_id] = {"days": "0", "hours": "0", "minutes": "0"}
        self.admin_delivery_time[purchase_id][unit] = value
    
    # --- ✨ PASO 3: REEMPLAZAR LA PROPIEDAD cart_summary ✨ ---
    @rx.var
    def cart_summary(self) -> dict:
        """
        Calcula el resumen del carrito usando el precio base para consistencia.
        """
        if not self.cart:
            return {"subtotal": 0, "shipping_cost": 0, "grand_total": 0, "free_shipping_achieved": False, "iva": 0}

        with rx.session() as session:
            cart_items_details = self.cart_details
            if not cart_items_details:
                return {"subtotal": 0, "shipping_cost": 0, "grand_total": 0, "free_shipping_achieved": False, "iva": 0}

            # --- ✨ INICIO DE LA CORRECCIÓN ✨ ---
            # Usamos 'item.product_id' en lugar de 'item.id'
            post_ids = [item.product_id for item in cart_items_details]
            # --- ✨ FIN DE LA CORRECCIÓN ✨ ---

            db_posts = session.exec(sqlmodel.select(BlogPostModel).where(BlogPostModel.id.in_(post_ids))).all()
            post_map = {p.id: p for p in db_posts}

            subtotal_base = sum(post_map.get(item.product_id).base_price * item.quantity for item in cart_items_details if post_map.get(item.product_id))
            iva = subtotal_base * 0.19
            subtotal_con_iva = subtotal_base + iva
            free_shipping_achieved = subtotal_con_iva >= 200000
            
            final_shipping_cost = 0.0
            if not free_shipping_achieved and self.default_shipping_address:
                buyer_barrio = self.default_shipping_address.neighborhood
                seller_groups = defaultdict(list)
                for item in cart_items_details:
                    db_post = post_map.get(item.product_id)
                    if db_post:
                        for _ in range(item.quantity):
                            seller_groups[db_post.userinfo_id].append(db_post)

                seller_ids = list(seller_groups.keys())
                sellers_info = session.exec(sqlmodel.select(UserInfo).where(UserInfo.id.in_(seller_ids))).all()
                seller_barrio_map = {info.id: info.seller_barrio for info in sellers_info}

                for seller_id, items_from_seller in seller_groups.items():
                    combinable_items = [p for p in items_from_seller if p.combines_shipping]
                    individual_items = [p for p in items_from_seller if not p.combines_shipping]
                    seller_barrio = seller_barrio_map.get(seller_id)
                    for individual_item in individual_items:
                        cost = calculate_dynamic_shipping(
                            base_cost=individual_item.shipping_cost or 0.0,
                            seller_barrio=seller_barrio,
                            buyer_barrio=buyer_barrio
                        )
                        final_shipping_cost += cost
                    if combinable_items:
                        valid_limits = [p.shipping_combination_limit for p in combinable_items if p.shipping_combination_limit and p.shipping_combination_limit > 0] or [1]
                        limit = min(valid_limits)
                        num_fees = math.ceil(len(combinable_items) / limit)
                        highest_base_cost = max((p.shipping_cost or 0.0 for p in combinable_items), default=0.0)
                        group_shipping_fee = calculate_dynamic_shipping(
                            base_cost=highest_base_cost,
                            seller_barrio=seller_barrio,
                            buyer_barrio=buyer_barrio
                        )
                        final_shipping_cost += (group_shipping_fee * num_fees)
            
            grand_total = subtotal_con_iva + final_shipping_cost
            
            return {
                "subtotal": subtotal_base,
                "shipping_cost": final_shipping_cost,
                "iva": iva,
                "grand_total": grand_total,
                "free_shipping_achieved": free_shipping_achieved,
            }
    # --- ✨ FIN DEL PASO 3 ✨ ---
        
    # --- 👇 AÑADE ESTAS TRES NUEVAS PROPIEDADES 👇 ---
    @rx.var
    def subtotal_cop(self) -> str:
        """Devuelve el subtotal del carrito ya formateado."""
        return format_to_cop(self.cart_summary["subtotal"])

    @rx.var
    def shipping_cost_cop(self) -> str:
        """Devuelve el costo de envío del carrito ya formateado."""
        return format_to_cop(self.cart_summary["shipping_cost"])

    @rx.var
    def grand_total_cop(self) -> str:
        """Devuelve el total general del carrito ya formateado."""
        return format_to_cop(self.cart_summary["grand_total"])

    @rx.var
    def cart_details(self) -> List[CartItemData]:
        """
        Reconstruye los detalles del carrito leyendo la clave única que
        contiene la selección específica del usuario.
        """
        if not self.cart: return []
        with rx.session() as session:
            product_ids = list(set([int(key.split('-')[0]) for key in self.cart.keys()]))
            if not product_ids: return []

            results = session.exec(sqlmodel.select(BlogPostModel).where(BlogPostModel.id.in_(product_ids))).all()
            post_map = {p.id: p for p in results}
            
            cart_items_data = []
            for cart_key, quantity in self.cart.items():
                parts = cart_key.split('-')
                product_id = int(parts[0])
                variant_index = int(parts[1])
                
                post = post_map.get(product_id)
                if post and post.variants and 0 <= variant_index < len(post.variants):
                    variant = post.variants[variant_index]
                    
                    # Reconstruye la selección del usuario desde la clave del carrito
                    selection_details = {}
                    if len(parts) > 2:
                        selection_parts = parts[2:]
                        for part in selection_parts:
                            if ':' in part:
                                key, value = part.split(':', 1)
                                selection_details[key] = value

                    # Combina los atributos de solo lectura (Color) con la selección del usuario (Talla)
                    variant_display_details = {}
                    for key, value in variant.get("attributes", {}).items():
                        if key not in self.SELECTABLE_ATTRIBUTES:
                            variant_display_details[key] = ", ".join(value) if isinstance(value, list) else value
                    
                    # La selección final que se mostrará
                    final_details_to_display = {**variant_display_details, **selection_details}

                    cart_items_data.append(
                        CartItemData(
                            cart_key=cart_key, product_id=product_id, variant_index=variant_index,
                            title=post.title, price=post.price, price_cop=post.price_cop,
                            image_url=variant.get("image_url", ""), quantity=quantity,
                            variant_details=final_details_to_display
                        )
                    )
            return cart_items_data
    
    modal_selected_variant_index: int = 0

     # --- ✨ NUEVO EVENT HANDLER para actualizar la selección en el modal ✨ ---
    def set_modal_selected_attribute(self, key: str, value: str):
        """
        Actualiza la selección de un atributo y resetea los atributos dependientes.
        """
        self.modal_selected_attributes[key] = value

        # Reinicia las selecciones de los atributos que vienen después
        all_keys = sorted(list(
            {k for variant in self.product_in_modal.variants for k in variant.get("attributes", {})}
        ))
        
        key_index = all_keys.index(key)
        for next_key in all_keys[key_index + 1:]:
            if next_key in self.modal_selected_attributes:
                del self.modal_selected_attributes[next_key]

    @rx.var
    def modal_attribute_selectors(self) -> list[ModalSelectorDTO]:
        if not self.product_in_modal: return []
        
        all_variants = self.product_in_modal.variants
        current_selection = self.modal_selected_attributes
        
        # 1. Obtenemos todas las claves de atributos presentes en las variantes
        all_keys_in_variants = sorted(list(
            {key for v in all_variants for key in v.get("attributes", {})}
        ))
        
        # 2. Filtramos para quedarnos SOLO con las que son seleccionables
        selectable_keys = [key for key in all_keys_in_variants if key in self.SELECTABLE_ATTRIBUTES]

        selectors = []
        # Ahora el bucle solo se ejecutará para "Talla", "Número", o "Tamaño"
        for i, key in enumerate(selectable_keys):
            # ... el resto de la lógica de la función no necesita cambios ...
            filtered_variants = all_variants
            for prev_key in selectable_keys[:i]:
                if prev_key in current_selection:
                    filtered_variants = [
                        v for v in filtered_variants 
                        if v.get("attributes", {}).get(prev_key) == current_selection[prev_key] # [cite: 885, 886]
                    ]
            
            valid_options = {
                v.get("attributes", {}).get(key)
                for v in filtered_variants
                if v.get("stock", 0) > 0 and v.get("attributes", {}).get(key) # [cite: 887]
            }
            
            if valid_options:
                selectors.append(
                    ModalSelectorDTO(
                        key=key,
                        options=sorted(list(valid_options)),
                        current_value=current_selection.get(key, "") # [cite: 888, 889]
                    )
                )
        return selectors

    @rx.event
    def add_to_cart(self, product_id: int):
        """
        Añade una variante específica de un producto al carrito, validando la selección y el stock.
        """
        if not self.is_authenticated:
            return rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)
        if not self.product_in_modal or product_id != self.product_in_modal.id:
            return rx.toast.error("Error al identificar el producto.")

        # --- ✨ INICIO DE LA LÓGICA DE STOCK CORREGIDA ✨ ---

        # 1. Validar que se hayan seleccionado todos los atributos requeridos (Talla, Número, etc.)
        required_keys = {selector.key for selector in self.modal_attribute_selectors}
        if not all(key in self.modal_selected_attributes for key in required_keys):
            missing_keys = required_keys - set(self.modal_selected_attributes.keys())
            return rx.toast.error(f"Por favor, selecciona: {', '.join(missing_keys)}")

        # 2. Encontrar la variante exacta que coincide con la selección del usuario
        variant_to_add = None
        for variant in self.product_in_modal.variants:
            variant_attrs = variant.get("attributes", {})
            
            # Compara los atributos de solo lectura (como Color) y los seleccionables (como Talla)
            current_variant_attrs_for_comparison = self.product_in_modal.variants[self.modal_selected_variant_index].get("attributes", {})
            
            is_match = True
            # Comprobar atributos de solo lectura (los de la variante visual)
            for key, value in current_variant_attrs_for_comparison.items():
                if key not in self.SELECTABLE_ATTRIBUTES and variant_attrs.get(key) != value:
                    is_match = False
                    break
            if not is_match: continue

            # Comprobar atributos seleccionables (los del estado `modal_selected_attributes`)
            for key, value in self.modal_selected_attributes.items():
                if variant_attrs.get(key) != value:
                    is_match = False
                    break
            
            if is_match:
                variant_to_add = variant
                break
        
        if not variant_to_add:
            return rx.toast.error("La combinación de producto seleccionada no está disponible.")

        # 3. Construir la clave única para el carrito
        selection_items = sorted(self.modal_selected_attributes.items())
        selection_key_part = "-".join([f"{k}:{v}" for k, v in selection_items])
        
        # El índice de la variante visual (thumbnail) sigue siendo parte de la clave para la imagen
        cart_key = f"{product_id}-{self.modal_selected_variant_index}-{selection_key_part}"
        
        # 4. Verificar el stock de la variante encontrada
        stock_disponible = variant_to_add.get("stock", 0)
        cantidad_en_carrito = self.cart.get(cart_key, 0)
        
        if cantidad_en_carrito + 1 > stock_disponible:
            return rx.toast.error("¡Lo sentimos! No hay suficiente stock para esta combinación.")
        
        # 5. Si hay stock, añadir al carrito
        self.cart[cart_key] = cantidad_en_carrito + 1
        
        # --- ✨ FIN DE LA LÓGICA DE STOCK CORREGIDA ✨ ---
        
        self.show_detail_modal = False
        return rx.toast.success("Producto añadido al carrito.")

    @rx.event
    def remove_from_cart(self, cart_key: str):
        """Elimina un artículo del carrito usando su clave única."""
        if cart_key in self.cart:
            self.cart[cart_key] -= 1
            if self.cart[cart_key] <= 0:
                del self.cart[cart_key]

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
    def set_category(self, value: str):
        """
        Establece la categoría del producto y reinicia todos los estados
        relacionados con los atributos para evitar la contaminación de datos.
        """
        # 1. Establecer la nueva categoría
        self.category = value

        # 2. Limpiar todas las listas y valores de atributos del formulario
        self.attr_colores = ""
        self.attr_tallas_ropa = []
        self.attr_numeros_calzado = []
        self.attr_tamanos_mochila = []
        self.attr_material = ""
        self.attr_tipo = ""

        # 3. Limpiar las variantes ya generadas, ya que ahora son inválidas
        self.generated_variants_map = {}
        
        # 4. Limpiar los atributos guardados en las imágenes subidas
        for variant in self.new_variants:
            if "attributes" in variant:
                variant["attributes"] = {}
                
        # 5. Reiniciar la selección de la imagen a la primera (si hay alguna)
        if self.new_variants:
            self.selected_variant_index = 0
        else:
            self.selected_variant_index = -1

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
    
    def _clear_add_form(self):
        self.title = ""
        self.content = ""
        self.price = ""
        self.category = ""
        self.temp_images = []
        self.new_variants = []
        self.selected_variant_index = -1
        self.attr_colores = "" # Reiniciar a una cadena vacía, no una lista.
        self.attr_tallas_ropa = []
        self.attr_numeros_calzado = []
        self.attr_tamanos_mochila = []
        self.attr_material = ""
        self.attr_tipo = ""
        self.shipping_cost_str = ""
        self.is_moda_completa = True
        self.is_imported = False
        self.combines_shipping = False
        self.shipping_combination_limit_str = "3"
        
        # --- 👇 LÍNEA IMPORTANTE A AÑADIR/VERIFICAR 👇 ---
        self.variant_form_data = [] # Asegúrate de que esta línea esté aquí
        self.generated_variants_map = {} # Asegúrate de limpiar el map

    # --- 👇 AÑADE ESTAS VARIABLES PARA EL FORMULARIO 👇 ---
    shipping_cost_str: str = ""
    #free_shipping_threshold_str: str = ""
    # --- 👇 AÑADE ESTA LÍNEA 👇 ---
    is_moda_completa: bool = True # Activo por defecto

    # --- 👇 AÑADE ESTE NUEVO MÉTODO 👇 ---
    def set_is_moda_completa(self, value: bool):
        self.is_moda_completa = value

    # --- 👇 AÑADE ESTAS VARIABLES PARA LOS FILTROS 👇 ---
    filter_free_shipping: bool = False
    filter_complete_fashion: bool = False
        
    @rx.var
    def my_admin_posts(self) -> list[AdminPostRowData]: # <-- Cambia el tipo de retorno
        if not self.authenticated_user_info:
            return []
        with rx.session() as session:
            posts_from_db = session.exec(
                sqlmodel.select(BlogPostModel)
                .where(BlogPostModel.userinfo_id == self.authenticated_user_info.id)
                .order_by(BlogPostModel.created_at.desc())
            ).all()

            # --- INICIO DE LA CORRECCIÓN ---
            # Convertir los modelos de la BD al DTO simple
            admin_posts = []
            for p in posts_from_db:
                main_image = p.variants[0].get("image_url", "") if p.variants else ""
                admin_posts.append(
                    AdminPostRowData(
                        id=p.id,
                        title=p.title,
                        price_cop=p.price_cop,
                        publish_active=p.publish_active,
                        main_image_url=main_image,
                    )
                )
            return admin_posts
            # --- FIN DE LA CORRECCIÓN ---

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
        """
        Procesa la compra:
        1. Bloquea los productos en la BD para evitar sobreventas.
        2. Verifica el stock de cada variante específica.
        3. Si hay stock, deduce la cantidad y crea el registro de compra.
        4. Si un producto se queda sin stock, lo desactiva automáticamente.
        """
        if not self.is_authenticated or not self.default_shipping_address:
            return rx.toast.error("Por favor, inicia sesión y selecciona una dirección predeterminada.")
        if not self.authenticated_user_info:
            return rx.toast.error("Error de sesión. Vuelve a iniciar sesión.")
        if not self.cart:
            return rx.toast.info("Tu carrito está vacío.")

        summary = self.cart_summary

        with rx.session() as session:
            product_ids = list(set([int(key.split('-')[0]) for key in self.cart.keys()]))
            
            # Bloquea las filas de los productos en la BD para una transacción segura
            posts_to_update = session.exec(
                sqlmodel.select(BlogPostModel)
                .where(BlogPostModel.id.in_(product_ids))
                .with_for_update()
            ).all()
            post_map = {p.id: p for p in posts_to_update}

            # --- FASE 1: Verificación de Stock ---
            for cart_key, quantity_in_cart in self.cart.items():
                parts = cart_key.split('-')
                prod_id = int(parts[0])
                selection_parts = parts[2:]
                selection_attrs = dict(part.split(':', 1) for part in selection_parts if ':' in part)

                post = post_map.get(prod_id)
                if not post:
                    return rx.toast.error(f"El producto con ID {prod_id} ya no está disponible. Compra cancelada.")

                variant_found = False
                for variant in post.variants:
                    if variant.get("attributes") == selection_attrs:
                        if variant.get("stock", 0) < quantity_in_cart:
                            attr_str = ', '.join(selection_attrs.values())
                            return rx.toast.error(f"Stock insuficiente para '{post.title} ({attr_str})'. Tu compra ha sido cancelada.")
                        variant_found = True
                        break
                
                if not variant_found:
                    return rx.toast.error(f"La variante seleccionada para '{post.title}' ya no existe. Compra cancelada.")

            # --- FASE 2: Creación de Compra y Deducción de Stock ---
            new_purchase = PurchaseModel(
                userinfo_id=self.authenticated_user_info.id,
                total_price=summary["grand_total"],
                shipping_applied=summary["shipping_cost"],
                status=PurchaseStatus.PENDING_CONFIRMATION,
                payment_method=self.payment_method,
                shipping_name=self.default_shipping_address.name,
                shipping_city=self.default_shipping_address.city,
                shipping_neighborhood=self.default_shipping_address.neighborhood,
                shipping_address=self.default_shipping_address.address,
                shipping_phone=self.default_shipping_address.phone
            )
            session.add(new_purchase)
            session.commit()
            session.refresh(new_purchase)
            
            for cart_key, quantity_in_cart in self.cart.items():
                parts = cart_key.split('-')
                prod_id = int(parts[0])
                selection_parts = parts[2:]
                selection_attrs = dict(part.split(':', 1) for part in selection_parts if ':' in part)
                
                post = post_map.get(prod_id)
                
                # Deducir el stock de la variante correcta
                for variant in post.variants:
                    if variant.get("attributes") == selection_attrs:
                        variant["stock"] -= quantity_in_cart
                        break
                
                # Marcar el post para ser actualizado en la sesión
                session.add(post)

                # Crear el registro del artículo comprado
                session.add(PurchaseItemModel(
                    purchase_id=new_purchase.id,
                    blog_post_id=post.id,
                    quantity=quantity_in_cart,
                    price_at_purchase=post.price,
                    selected_variant=selection_attrs # Guarda la variante exacta
                ))

            # --- FASE 3: Verificación de Desactivación Automática ---
            for post in post_map.values():
                total_stock = sum(v.get("stock", 0) for v in post.variants)
                if total_stock <= 0:
                    post.publish_active = False
                    session.add(post)

            session.commit()

        self.cart.clear()
        self.default_shipping_address = None
        yield AppState.notify_admin_of_new_purchase
        yield rx.toast.success("¡Gracias por tu compra! Tu orden está pendiente de confirmación.")
        return rx.redirect("/my-purchases")

    def toggle_form(self):
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
        """
        Devuelve la lista de barrios para el selector de dirección.
        CORREGIDO: Ahora usa la lista completa de barrios de Popayán.
        """
        # --- INICIO DE LA CORRECCIÓN ---
        # Antes usaba un archivo incorrecto. Ahora usamos la lista completa.
        from .data.geography_data import LISTA_DE_BARRIOS

        if self.city != "Popayán":
             # Mantenemos la lógica anterior por si se añaden otras ciudades
            data = load_colombia_data()
            all_hoods = data.get(self.city, [])
        else:
            # Si la ciudad es Popayán, usamos nuestra lista maestra.
            all_hoods = LISTA_DE_BARRIOS
        # --- FIN DE LA CORRECCIÓN ---

        if not self.search_neighborhood.strip():
            return sorted(all_hoods)
        return sorted([
            n for n in all_hoods if self.search_neighborhood.lower() in n.lower()
        ])

    @rx.event
    def recalculate_all_shipping_costs(self):
        """
        Toma la lista de productos cruda y recalcula el costo de envío para cada uno
        basado en la dirección actual del comprador.
        """
        if not self._raw_posts:
            self.posts = []
            return

        if not self.default_shipping_address:
            # Si no hay dirección, los costos vuelven a ser los base.
            self.posts = self._raw_posts
            return

        buyer_barrio = self.default_shipping_address.neighborhood
        
        with rx.session() as session:
            seller_ids = {p.userinfo_id for p in self._raw_posts}
            sellers_info = session.exec(
                sqlmodel.select(UserInfo).where(UserInfo.id.in_(list(seller_ids)))
            ).all()
            seller_barrio_map = {info.id: info.seller_barrio for info in sellers_info}

            recalculated_posts = []
            for post in self._raw_posts:
                seller_barrio = seller_barrio_map.get(post.userinfo_id)
                
                final_shipping_cost = calculate_dynamic_shipping(
                    base_cost=post.shipping_cost or 0.0,
                    seller_barrio=seller_barrio,
                    buyer_barrio=buyer_barrio
                )

                # Creamos una copia del post para no modificar el original
                updated_post = post.copy()
                updated_post.shipping_display_text = f"Envío: {format_to_cop(final_shipping_cost)}" if final_shipping_cost > 0 else "Envío a convenir"
                
                recalculated_posts.append(updated_post)

        self.posts = recalculated_posts

    @rx.event
    async def load_main_page_data(self):
        """
        Orquestador principal: carga la dirección y LUEGO los productos y recalcula.
        """
        self.is_loading = True
        yield
        yield AppState.load_default_shipping_info

        with rx.session() as session:
            results = session.exec(sqlmodel.select(BlogPostModel).where(BlogPostModel.publish_active == True).order_by(BlogPostModel.created_at.desc())).all()
            
            temp_posts = []
            for p in results:
                temp_posts.append(
                    ProductCardData(
                        id=p.id, 
                        userinfo_id=p.userinfo_id, 
                        title=p.title, 
                        price=p.price,
                        price_cop=p.price_cop,
                        # --- 👇 LÍNEA CORREGIDA 👇 ---
                        variants=p.variants or [],
                        attributes={},
                        average_rating=p.average_rating,
                        rating_count=p.rating_count,
                        shipping_cost=p.shipping_cost,
                        is_moda_completa_eligible=p.is_moda_completa_eligible,
                        shipping_display_text=_get_shipping_display_text(p.shipping_cost),
                        is_imported=p.is_imported
                    )
                )
            self._raw_posts = temp_posts
        
        yield AppState.recalculate_all_shipping_costs
        self.is_loading = False

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
            # La lógica para crear y guardar la dirección no cambia
            is_first_address = len(self.addresses) == 0
            new_addr = ShippingAddressModel(
                userinfo_id=self.authenticated_user_info.id, name=form_data["name"],
                phone=form_data["phone"], city=self.city, neighborhood=self.neighborhood,
                address=form_data["address"], is_default=is_first_address
            )
            session.add(new_addr)
            session.commit()

        self.show_form = False

        # --- ✨ INICIO DE LA CORRECCIÓN ✨ ---
        # En lugar de llamar a las funciones con `()`, entregamos la referencia al evento.
        yield AppState.load_addresses
        yield AppState.load_default_shipping_info
        yield AppState.recalculate_all_shipping_costs
        # --- ✨ FIN DE LA CORRECCIÓN ✨ ---

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
        
        # --- ✨ INICIO DE LA CORRECCIÓN ✨ ---
        # En lugar de llamar a las funciones con `()`, entregamos la referencia al evento.
        yield AppState.load_addresses
        yield AppState.load_default_shipping_info
        yield AppState.recalculate_all_shipping_costs
        # --- ✨ FIN DE LA CORRECCIÓN ✨ ---

    @rx.event
    def set_as_default(self, address_id: int):
        """
        MODIFICADO: Ahora dispara el recálculo después de cambiar la dirección.
        """
        if not self.authenticated_user_info: return
        with rx.session() as session:
            # ... (la lógica para cambiar la dirección en la BD se mantiene igual) ...
            current_default = session.exec(sqlmodel.select(ShippingAddressModel).where(ShippingAddressModel.userinfo_id == self.authenticated_user_info.id, ShippingAddressModel.is_default == True)).one_or_none()
            if current_default:
                current_default.is_default = False
                session.add(current_default)
            new_default = session.get(ShippingAddressModel, address_id)
            if new_default and new_default.userinfo_id == self.authenticated_user_info.id:
                new_default.is_default = True
                session.add(new_default)
                session.commit()
        
        # ✨ CORRECCIÓN AQUÍ
        yield AppState.load_addresses
        yield AppState.load_default_shipping_info
        yield AppState.recalculate_all_shipping_costs
    
    # --- ✨ 4. AÑADE LAS NUEVAS FUNCIONES DE LÓGICA DE ENTREGA ✨ ---
    
    @rx.event
    def user_confirm_delivery(self, purchase_id: int):
        """El usuario confirma que ha recibido el pedido."""
        if not self.authenticated_user_info:
            return

        with rx.session() as session:
            purchase = session.get(PurchaseModel, purchase_id)
            if purchase and purchase.userinfo_id == self.authenticated_user_info.id and purchase.status == PurchaseStatus.SHIPPED:
                purchase.status = PurchaseStatus.DELIVERED
                purchase.user_confirmed_delivery_at = datetime.now(timezone.utc)
                session.add(purchase)
                
                # Notifica al usuario que ya puede calificar el producto
                notification = NotificationModel(
                    userinfo_id=purchase.userinfo_id,
                    message=f"¡Gracias por confirmar! Ya puedes calificar los productos de tu compra #{purchase.id}.",
                    url="/my-purchases"
                )
                session.add(notification)
                session.commit()
                yield AppState.load_purchases

    @rx.event
    def check_for_auto_confirmations(self):
        """Revisa y auto-confirma entregas antiguas."""
        if not self.authenticated_user_info:
            return
        
        with rx.session() as session:
            five_days_ago = datetime.now(timezone.utc) - timedelta(days=5)
            
            overdue_purchases = session.exec(
                sqlmodel.select(PurchaseModel).where(
                    PurchaseModel.userinfo_id == self.authenticated_user_info.id,
                    PurchaseModel.status == PurchaseStatus.SHIPPED,
                    PurchaseModel.delivery_confirmation_sent_at != None,
                    PurchaseModel.delivery_confirmation_sent_at < five_days_ago,
                    PurchaseModel.user_confirmed_delivery_at == None,
                )
            ).all()

            if not overdue_purchases:
                return

            for purchase in overdue_purchases:
                purchase.status = PurchaseStatus.DELIVERED
                session.add(purchase)
            
            session.commit()
            # ✨ CORRECCIÓN AQUÍ
            yield AppState.load_purchases

    search_term: str = ""
    search_results: List[ProductCardData] = []
    def set_search_term(self, term: str): self.search_term = term

    @rx.event
    def perform_search(self):
        if not self.search_term.strip(): return
        with rx.session() as session:
            results = session.exec(
                sqlmodel.select(BlogPostModel)
                .where(
                    BlogPostModel.title.ilike(f"%{self.search_term.strip()}%"), 
                    BlogPostModel.publish_active == True
                )
            ).all()
            
            temp_results = []
            for p in results:
                temp_results.append(
                    ProductCardData(
                        id=p.id,
                        userinfo_id=p.userinfo_id,
                        title=p.title,
                        price=p.price,
                        price_cop=p.price_cop,
                        # --- ✨ CORRECCIÓN AQUÍ ✨ ---
                        variants=p.variants or [],
                        average_rating=p.average_rating,
                        rating_count=p.rating_count,
                        shipping_cost=p.shipping_cost,
                        is_moda_completa_eligible=p.is_moda_completa_eligible,
                        shipping_display_text=_get_shipping_display_text(p.shipping_cost),
                        is_imported=p.is_imported
                    )
                )
            self.search_results = temp_results
            
        return rx.redirect("/search-results")
        

    pending_purchases: List[AdminPurchaseCardData] = []
    purchase_history: List[AdminPurchaseCardData] = []
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
    def load_purchase_history(self):
        """Carga el historial de compras finalizadas (Entregadas)."""
        if not self.is_admin:
            self.purchase_history = []
            return
        with rx.session() as session:
            results = session.exec(
                sqlmodel.select(PurchaseModel)
                .options(
                    sqlalchemy.orm.joinedload(PurchaseModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post)
                )
                .where(PurchaseModel.status == PurchaseStatus.DELIVERED)
                .order_by(PurchaseModel.purchase_date.desc())
            ).unique().all()
            
            # El nombre de esta variable estaba incorrecto, lo corregí a self.purchase_history
            self.purchase_history = [
                AdminPurchaseCardData(
                    id=p.id, customer_name=p.userinfo.user.username, customer_email=p.userinfo.email,
                    purchase_date_formatted=p.purchase_date_formatted, status=p.status.value, total_price=p.total_price,
                    # --- ✨ LÍNEA AÑADIDA PARA CORREGIR EL ERROR ✨ ---
                    payment_method=p.payment_method,
                    shipping_name=p.shipping_name, shipping_full_address=f"{p.shipping_address}, {p.shipping_neighborhood}, {p.shipping_city}",
                    shipping_phone=p.shipping_phone, items_formatted=p.items_formatted
                ) for p in results
            ]
        
        self.set_new_purchase_notification(
            any(p.status == "pending_confirmation" for p in self.active_purchases)
        )
            
    @rx.event
    def load_active_purchases(self):
        """Carga las compras que requieren acción del admin."""
        if not self.is_admin: return
        with rx.session() as session:
            purchases = session.exec(
                sqlmodel.select(PurchaseModel)
                .options(
                    sqlalchemy.orm.joinedload(PurchaseModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post)
                )
                # --- ✨ INICIO DE LA CORRECCIÓN ✨ ---
                # Se elimina el estado 'DELIVERED' de esta consulta.
                # Ahora solo se mostrarán las órdenes que están pendientes o en tránsito.
                .where(PurchaseModel.status.in_([
                    PurchaseStatus.PENDING_CONFIRMATION,
                    PurchaseStatus.CONFIRMED,
                    PurchaseStatus.SHIPPED,
                ]))
                # --- ✨ FIN DE LA CORRECCIÓN ✨ ---
                .order_by(PurchaseModel.purchase_date.asc())
            ).unique().all()
            
            self.active_purchases = [
                AdminPurchaseCardData(
                    id=p.id, customer_name=p.userinfo.user.username, customer_email=p.userinfo.email,
                    purchase_date_formatted=p.purchase_date_formatted, status=p.status.value, total_price=p.total_price,
                    payment_method=p.payment_method,
                    confirmed_at=p.confirmed_at,
                    shipping_name=p.shipping_name, shipping_full_address=f"{p.shipping_address}, {p.shipping_neighborhood}, {p.shipping_city}",
                    shipping_phone=p.shipping_phone, items_formatted=p.items_formatted
                ) for p in purchases
            ]
            self.set_new_purchase_notification(
                any(p.status == PurchaseStatus.PENDING_CONFIRMATION.value for p in self.active_purchases)
            )

    # ✨ NUEVA FUNCIÓN solo para notificar el envío
    @rx.event
    def ship_confirmed_online_order(self, purchase_id: int):
        if not self.is_admin: 
            return rx.toast.error("Acción no permitida.")
        
        time_data = self.admin_delivery_time.get(purchase_id, {})
        try:
            days = int(time_data.get("days", "0") or "0")
            hours = int(time_data.get("hours", "0") or "0")
            minutes = int(time_data.get("minutes", "0") or "0")
            total_delta = timedelta(days=days, hours=hours, minutes=minutes)
            if total_delta.total_seconds() <= 0:
                return rx.toast.error("El tiempo de entrega debe ser mayor a cero.")
        except (ValueError, TypeError):
            return rx.toast.error("Por favor, introduce números válidos para el tiempo de entrega.")

        with rx.session() as session:
            purchase = session.get(PurchaseModel, purchase_id)
            if purchase and purchase.status == PurchaseStatus.CONFIRMED:
                purchase.status = PurchaseStatus.SHIPPED
                purchase.estimated_delivery_date = datetime.now(timezone.utc) + total_delta
                purchase.delivery_confirmation_sent_at = datetime.now(timezone.utc)
                session.add(purchase)

                # --- ✨ LÓGICA DE MENSAJE MEJORADA ✨ ---
                time_parts = []
                if days > 0: time_parts.append(f"{days} día(s)")
                if hours > 0: time_parts.append(f"{hours} hora(s)")
                if minutes > 0: time_parts.append(f"{minutes} minuto(s)")
                
                time_str = ", ".join(time_parts) if time_parts else "pronto"
                mensaje = f"¡Tu compra #{purchase.id} está en camino! Llegará en aprox. {time_str}."
                # --- ✨ FIN DE LA LÓGICA MEJORADA ✨ ---

                notification = NotificationModel(
                    userinfo_id=purchase.userinfo_id,
                    message=mensaje,
                    url="/my-purchases"
                )
                session.add(notification)
                session.commit()
                
                yield rx.toast.success("Notificación de envío enviada.")
                yield AppState.load_active_purchases
            else:
                yield rx.toast.error("La compra debe estar 'confirmada' para poder notificar el envío.")

    @rx.event
    def ship_pending_cod_order(self, purchase_id: int):
        if not self.is_admin: 
            return rx.toast.error("Acción no permitida.")
        
        time_data = self.admin_delivery_time.get(purchase_id, {})
        try:
            days = int(time_data.get("days", "0") or "0")
            hours = int(time_data.get("hours", "0") or "0")
            minutes = int(time_data.get("minutes", "0") or "0")
            total_delta = timedelta(days=days, hours=hours, minutes=minutes)
            if total_delta.total_seconds() <= 0:
                return rx.toast.error("El tiempo de entrega debe ser mayor a cero.")
        except (ValueError, TypeError):
            return rx.toast.error("Por favor, introduce números válidos para el tiempo de entrega.")

        with rx.session() as session:
            purchase = session.get(PurchaseModel, purchase_id)
            if purchase and purchase.status == PurchaseStatus.PENDING_CONFIRMATION and purchase.payment_method == "Contra Entrega":
                purchase.status = PurchaseStatus.SHIPPED
                purchase.estimated_delivery_date = datetime.now(timezone.utc) + total_delta
                purchase.delivery_confirmation_sent_at = datetime.now(timezone.utc)
                session.add(purchase)

                # --- ✨ LÓGICA DE MENSAJE MEJORADA ✨ ---
                time_parts = []
                if days > 0: time_parts.append(f"{days} día(s)")
                if hours > 0: time_parts.append(f"{hours} hora(s)")
                if minutes > 0: time_parts.append(f"{minutes} minuto(s)")
                
                time_str = ", ".join(time_parts) if time_parts else "pronto"
                mensaje = f"¡Tu compra #{purchase.id} está en camino! Llegará en aprox. {time_str}."
                # --- ✨ FIN DE LA LÓGICA MEJORADA ✨ ---

                notification = NotificationModel(
                    userinfo_id=purchase.userinfo_id,
                    message=mensaje,
                    url="/my-purchases"
                )

                session.add(notification)
                session.commit()
                yield rx.toast.success("Pedido contra entrega en camino y notificado.")
                yield AppState.load_active_purchases
            else:
                yield rx.toast.error("Esta acción no es válida para este pedido.")
    
    @rx.event
    def confirm_online_payment(self, purchase_id: int):
        """
        Confirma un pago online. Cambia el estado de PENDING a CONFIRMED.
        Este es el primer paso para los pagos online.
        """
        if not self.is_admin:
            return rx.toast.error("Acción no permitida.")

        with rx.session() as session:
            purchase = session.get(PurchaseModel, purchase_id)
            if purchase and purchase.status == PurchaseStatus.PENDING and purchase.payment_method == "Online":
                purchase.status = PurchaseStatus.CONFIRMED
                purchase.confirmed_at = datetime.now(timezone.utc)
                session.add(purchase)

                # Notificar al cliente que su pago fue confirmado
                notification = NotificationModel(
                    userinfo_id=purchase.userinfo_id,
                    message=f"¡Tu pago para la compra #{purchase.id} ha sido confirmado! Pronto prepararemos tu envío.",
                    url="/my-purchases"
                )
                session.add(notification)
                session.commit()
                yield rx.toast.success(f"Pago de la compra #{purchase_id} confirmado.")
                yield AppState.load_active_purchases
            else:
                yield rx.toast.error("Esta acción no es válida para este tipo de compra o estado.")

    @rx.event
    def confirm_cod_payment_received(self, purchase_id: int):
        """
        Permite al admin registrar que el pago Contra Entrega fue recibido.
        Esto NO cambia el estado de la entrega, solo registra la fecha de confirmación del pago.
        """
        if not self.is_admin:
            return rx.toast.error("Acción no permitida.")
        
        with rx.session() as session:
            purchase = session.get(PurchaseModel, purchase_id)
            
            # La condición correcta: la orden debe ser 'Contra Entrega' y ya debe haber sido 'Enviada'.
            if purchase and purchase.payment_method == "Contra Entrega" and purchase.status == PurchaseStatus.SHIPPED:
                # 1. Se registra únicamente la fecha en que se confirmó el pago.
                purchase.confirmed_at = datetime.now(timezone.utc)
                session.add(purchase)
                session.commit()
                
                # 2. Se notifica al admin y se recarga la vista para que vea el cambio.
                yield rx.toast.success(f"Pago de la compra #{purchase_id} registrado.")
                yield AppState.load_active_purchases
            else:
                # Si la orden no cumple las condiciones, se muestra un error.
                yield rx.toast.error("Esta acción no es válida para este pedido o su estado actual.")

    search_query_admin_history: str = ""

    def set_search_query_admin_history(self, query: str):
        self.search_query_admin_history = query

    @rx.var
    def filtered_admin_purchases(self) -> list[AdminPurchaseCardData]:
        if not self.search_query_admin_history.strip():
            # Usa el nuevo nombre de la variable
            return self.purchase_history
        q = self.search_query_admin_history.lower()
        return [
            # Usa el nuevo nombre de la variable
            p for p in self.purchase_history
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

    # --- ✨ INICIO DE LA CORRECCIÓN DEL ERROR DE COMPILACIÓN ✨ ---
    @rx.var
    def filtered_user_purchases(self) -> list[UserPurchaseHistoryCardData]:
        """Filtra las compras del usuario."""
        if not self.search_query_user_history.strip():
            return self.user_purchases
        q = self.search_query_user_history.lower()
        # Restauramos esta lógica más eficiente, ya que no era la causa del error.
        return [
            p for p in self.user_purchases
            if q in f"#{p.id}" or any(q in item.title.lower() for item in p.items)
        ]
    # --- ✨ FIN DE LA CORRECCIÓN ✨ ---
    
    # --- ✨ INICIO DE LA SOLUCIÓN DEFINITIVA: NUEVA PROPIEDAD COMPUTADA ✨ ---
    @rx.var
    def purchase_items_map(self) -> dict[int, list[PurchaseItemCardData]]:
        """
        Crea un diccionario que mapea el ID de una compra a su lista de artículos.
        Esto evita el acceso anidado (purchase.items) que causa el error de compilación.
        """
        return {p.id: p.items for p in self.user_purchases}
    # --- ✨ FIN DE LA SOLUCIÓN DEFINITIVA ✨ ---

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
            
            temp_purchases = []
            for p in results:
                purchase_items_data = []
                if p.items:
                    for item in p.items:
                        if item.blog_post:
                            # --- ✨ INICIO DE LA CORRECCIÓN ✨ ---
                            # Se obtiene la imagen de la primera variante del producto
                            main_image = ""
                            if item.blog_post.variants:
                                main_image = item.blog_post.variants[0].get("image_url", "")
                            # --- ✨ FIN DE LA CORRECCIÓN ✨ ---
                            
                            purchase_items_data.append(
                                PurchaseItemCardData(
                                    id=item.blog_post.id,
                                    title=item.blog_post.title,
                                    image_url=main_image, # Se usa la nueva variable
                                    price_at_purchase=item.price_at_purchase,
                                    price_at_purchase_cop=format_to_cop(item.price_at_purchase),
                                    quantity=item.quantity
                                )
                            )
                
                temp_purchases.append(
                    UserPurchaseHistoryCardData(
                        id=p.id,
                        userinfo_id=p.userinfo_id,
                        purchase_date_formatted=p.purchase_date_formatted,
                        status=p.status.value,
                        total_price_cop=p.total_price_cop,
                        shipping_applied_cop=format_to_cop(p.shipping_applied),
                        shipping_name=p.shipping_name,
                        shipping_address=p.shipping_address,
                        shipping_neighborhood=p.shipping_neighborhood,
                        shipping_city=p.shipping_city,
                        shipping_phone=p.shipping_phone,
                        items=purchase_items_data
                    )
                )
            self.user_purchases = temp_purchases
    
    @rx.var
    def notification_list(self) -> list[NotificationDTO]:
        return getattr(self, "_notifications", [])

    @rx.var
    def unread_count(self) -> int:
        """
        Calcula de forma segura el número de notificaciones no leídas.
        """
        # --- INICIO DE LA CORRECCIÓN ---
        # Usamos getattr aquí también para acceder a la lista de forma segura
        notifications_list = getattr(self, "_notifications", [])
        return sum(1 for n in notifications_list if not n.is_read)
    
    @rx.event
    def load_notifications(self):
        if not self.authenticated_user_info:
            self._notifications = []
            return
        with rx.session() as session:
            notifications_db = session.exec(
                sqlmodel.select(NotificationModel)
                .where(NotificationModel.userinfo_id == self.authenticated_user_info.id)
                .order_by(sqlmodel.col(NotificationModel.created_at).desc())
            ).all()
            # Convertir a DTO
            self._notifications = [
                NotificationDTO(
                    id=n.id,
                    message=n.message,
                    is_read=n.is_read,
                    url=n.url,
                    created_at_formatted=n.created_at_formatted
                ) for n in notifications_db
            ]
    
    @rx.event
    def mark_all_as_read(self):
        if not self.authenticated_user_info:
            return
        unread_ids = [n.id for n in self._notifications if not n.is_read] # <-- Usar el nuevo nombre
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
    def filtered_entries(self) -> list[ContactEntryDTO]:
        if not self.search_query_contact.strip():
            return self.contact_entries
        q = self.search_query_contact.lower()
        return [
            e for e in self.contact_entries 
            if q in f"{e.first_name} {e.last_name} {e.email} {e.message}".lower()
        ]
    
    # --- ✨ AÑADE ESTAS VARIABLES PARA EL FORMULARIO DE PRODUCTO ✨ ---
    combines_shipping: bool = False
    shipping_combination_limit_str: str = "3" # Valor por defecto

    # --- ✨ AÑADE ESTOS SETTERS ✨ ---
    def set_combines_shipping(self, value: bool):
        self.combines_shipping = value
    
    def set_shipping_combination_limit_str(self, value: str):
        self.shipping_combination_limit_str = value

    def set_shipping_cost_str(self, cost: str):
        self.shipping_cost_str = cost

    def set_free_shipping_threshold_str(self, threshold: str):
        self.free_shipping_threshold_str = threshold
    
    def set_filter_free_shipping(self, value: bool):
        self.filter_free_shipping = value

    def set_filter_complete_fashion(self, value: bool):
        self.filter_complete_fashion = value

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
        # ✨ CORRECCIÓN AQUÍ
        yield AppState.load_all_users

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
        yield AppState.load_all_users

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
        yield AppState.load_all_users
    
    admin_store_posts: list[ProductCardData] = []

    @rx.event
    def on_load_admin_store(self):
        if not self.is_admin:
            return rx.redirect("/")

        with rx.session() as session:
            results = session.exec(
                sqlmodel.select(BlogPostModel)
                .where(BlogPostModel.userinfo_id == self.authenticated_user_info.id)
                .order_by(BlogPostModel.created_at.desc())
            ).unique().all()
            
            temp_posts = []
            for p in results:
                temp_posts.append(
                    ProductCardData(
                        id=p.id,
                        userinfo_id=p.userinfo_id,
                        title=p.title,
                        price=p.price,
                        price_cop=p.price_cop,
                        # --- 👇 LÍNEA CORREGIDA 👇 ---
                        variants=p.variants or [],
                        attributes={},
                        average_rating=p.average_rating,
                        rating_count=p.rating_count,
                        shipping_cost=p.shipping_cost,
                        is_moda_completa_eligible=p.is_moda_completa_eligible,
                        shipping_display_text=_get_shipping_display_text(p.shipping_cost),
                        is_imported=p.is_imported
                    )
                )
            self.admin_store_posts = temp_posts

    show_admin_sidebar: bool = False

    def toggle_admin_sidebar(self):
        self.show_admin_sidebar = not self.show_admin_sidebar

    @rx.event
    def on_load_main_page(self):
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
            self._product_id_to_load_on_mount = int(product_id)
            yield self.trigger_modal_from_load

    product_comments: list[CommentData] = []
    my_review_for_product: Optional[CommentData] = None
    review_rating: int = 0
    review_content: str = ""
    show_review_form: bool = False
    review_limit_reached: bool = False

    @rx.var
    def can_review_product(self) -> bool:
        if not self.is_authenticated or not self.product_in_modal:
            return False
        with rx.session() as session:
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
        
    @rx.var
    def product_attributes_list(self) -> list[AttributeData]:
        if self.product_in_modal and self.product_in_modal.attributes:
            processed_attributes = []
            for k, v in self.product_in_modal.attributes.items():
                if isinstance(v, list):
                    value_str = ", ".join(v)
                else:
                    value_str = str(v)
                processed_attributes.append(AttributeData(key=k, value=value_str))
            return processed_attributes
        return []

    def _find_unclaimed_purchase(self, session: sqlmodel.Session) -> Optional[PurchaseItemModel]:
        if not self.authenticated_user_info or not self.product_in_modal:
            return None
        
        purchase_items = session.exec(
            sqlmodel.select(PurchaseItemModel)
            .join(PurchaseModel)
            .where(
                PurchaseModel.userinfo_id == self.authenticated_user_info.id,
                PurchaseItemModel.blog_post_id == self.product_in_modal.id,
                # --- ✨ INICIO DE LA CORRECCIÓN ✨ ---
                # La condición aquí también se cambia para requerir "DELIVERED"
                PurchaseModel.status == PurchaseStatus.DELIVERED
                # --- ✨ FIN DE LA CORRECCIÓN ✨ ---
            )
        ).all()

        claimed_purchase_ids = set(
            session.exec(
                sqlmodel.select(CommentModel.purchase_item_id)
                .where(
                    CommentModel.userinfo_id == self.authenticated_user_info.id,
                    CommentModel.blog_post_id == self.product_in_modal.id,
                    CommentModel.parent_comment_id == None,
                    CommentModel.purchase_item_id != None
                )
            ).all()
        )

        for item in purchase_items:
            if item.id not in claimed_purchase_ids:
                return item
        
        return None

    def set_review_rating(self, rating: int):
        self.review_rating = rating
    
    expanded_comments: dict[int, bool] = {}

    def toggle_comment_updates(self, comment_id: int):
        self.expanded_comments[comment_id] = not self.expanded_comments.get(comment_id, False)

    @rx.event
    def submit_review(self, form_data: dict):
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
                original_comment = session.get(CommentModel, self.my_review_for_product.id)

                if not original_comment:
                    return rx.toast.error("El comentario que intentas actualizar ya no existe.")

                while original_comment.parent:
                    original_comment = original_comment.parent
                
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
                    purchase_item_id=original_comment.purchase_item_id 
                )
                session.add(new_update)
                yield rx.toast.success("¡Opinión actualizada!")
            else:
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
                    purchase_item_id=unclaimed_purchase_item.id
                )
                session.add(new_review)
                yield rx.toast.success("¡Gracias por tu opinión!")
            
            session.commit()
        yield AppState.open_product_detail_modal(self.product_in_modal.id)


    saved_post_ids: set[int] = set()
    saved_posts_gallery: list[ProductCardData] = []

    @rx.var
    def is_current_post_saved(self) -> bool:
        if not self.product_in_modal or not self.is_authenticated:
            return False
        return self.product_in_modal.id in self.saved_post_ids

    @rx.event
    def load_saved_post_ids(self):
        if not self.authenticated_user_info:
            self.saved_post_ids = set()
            return
        
        with rx.session() as session:
            user_info = session.get(UserInfo, self.authenticated_user_info.id)
            if user_info:
                self.saved_post_ids = {post.id for post in user_info.saved_posts}

    @rx.event
    def toggle_save_post(self):
        if not self.authenticated_user_info or not self.product_in_modal:
            return rx.toast.error("Debes iniciar sesión para guardar publicaciones.")

        post_id = self.product_in_modal.id
        with rx.session() as session:
            user_info = session.get(UserInfo, self.authenticated_user_info.id)
            post_to_toggle = session.get(BlogPostModel, post_id)

            if not user_info or not post_to_toggle:
                return rx.toast.error("Error al procesar la solicitud.")

            if post_id in self.saved_post_ids:
                user_info.saved_posts.remove(post_to_toggle)
                self.saved_post_ids.remove(post_id)
                yield rx.toast.info("Publicación eliminada de tus guardados.")
            else:
                user_info.saved_posts.append(post_to_toggle)
                self.saved_post_ids.add(post_id)
                yield rx.toast.success("¡Publicación guardada!")
            
            session.add(user_info)
            session.commit()

    @rx.event
    def on_load_saved_posts_page(self):
        self.is_loading = True
        yield
        
        if not self.authenticated_user_info:
            self.saved_posts_gallery = []
            self.is_loading = False
            return rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)
        
        with rx.session() as session:
            user_info = session.get(UserInfo, self.authenticated_user_info.id)
            if user_info:
                temp_posts = []
                user_with_posts = session.exec(
                    sqlmodel.select(UserInfo).options(sqlalchemy.orm.selectinload(UserInfo.saved_posts))
                    .where(UserInfo.id == self.authenticated_user_info.id)
                ).one()
                
                sorted_posts = sorted(user_with_posts.saved_posts, key=lambda p: p.created_at, reverse=True)
                for p in sorted_posts:
                    temp_posts.append(
                        ProductCardData(
                            id=p.id,
                            userinfo_id=p.userinfo_id,
                            title=p.title,
                            price=p.price,
                            price_cop=p.price_cop,
                            # --- 👇 LÍNEA CORREGIDA 👇 ---
                            variants=p.variants or [],
                            attributes={},
                            average_rating=p.average_rating,
                            rating_count=p.rating_count,
                            shipping_cost=p.shipping_cost,
                            is_moda_completa_eligible=p.is_moda_completa_eligible,
                            shipping_display_text=_get_shipping_display_text(p.shipping_cost),
                            is_imported=p.is_imported
                        )
                    )
                self.saved_posts_gallery = temp_posts
        
        self.is_loading = False


    @rx.event
    def trigger_modal_from_load(self):
        if self._product_id_to_load_on_mount is not None:
            yield from self.open_product_detail_modal(self._product_id_to_load_on_mount)
            self._product_id_to_load_on_mount = None

    def _convert_comment_to_dto(self, comment_model: CommentModel) -> CommentData:
        return CommentData(
            id=comment_model.id,
            content=comment_model.content,
            rating=comment_model.rating,
            author_username=comment_model.author_username,
            author_initial=comment_model.author_initial,
            created_at_formatted=comment_model.created_at_formatted,
            updates=[self._convert_comment_to_dto(update) for update in sorted(comment_model.updates, key=lambda u: u.created_at)]
        )

    # --- NUEVOS MANEJADORES PARA EL MODAL ---
    def set_modal_variant_index(self, index: int):
        """
        Cambia la variante en el modal y actualiza las selecciones de atributos
        para que coincidan con la nueva variante seleccionada.
        """
        self.modal_selected_variant_index = index
        if self.product_in_modal and 0 <= index < len(self.product_in_modal.variants):
            selected_variant = self.product_in_modal.variants[index]
            self._set_default_attributes_from_variant(selected_variant)

    @rx.event
    def open_product_detail_modal(self, post_id: int):
        # Reseteo inicial de todas las variables del modal
        self.product_in_modal = None
        self.show_detail_modal = True
        self.modal_selected_attributes = {}
        self.modal_selected_variant_index = 0
        self.product_comments = []
        self.my_review_for_product = None
        self.review_rating = 0
        self.review_content = ""
        self.show_review_form = False
        self.review_limit_reached = False

        with rx.session() as session:
            db_post = session.exec(
                sqlmodel.select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.comments).joinedload(CommentModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(BlogPostModel.comments).joinedload(CommentModel.updates),
                    sqlalchemy.orm.joinedload(BlogPostModel.userinfo).joinedload(UserInfo.user)
                ).where(BlogPostModel.id == post_id)
            ).unique().one_or_none()

            if not db_post or not db_post.publish_active:
                self.show_detail_modal = False
                yield rx.toast.error("Producto no encontrado o no disponible.")
                return

            # Lógica de envío y datos del vendedor (sin cambios)
            buyer_barrio = self.default_shipping_address.neighborhood if self.default_shipping_address else None
            seller_barrio = db_post.userinfo.seller_barrio if db_post.userinfo else None
            final_shipping_cost = calculate_dynamic_shipping(base_cost=db_post.shipping_cost or 0.0, seller_barrio=seller_barrio, buyer_barrio=buyer_barrio)
            shipping_text = f"Envío: {format_to_cop(final_shipping_cost)}" if final_shipping_cost > 0 else "Envío a convenir"
            seller_name = db_post.userinfo.user.username if db_post.userinfo and db_post.userinfo.user else "N/A"
            seller_id = db_post.userinfo.id if db_post.userinfo else 0
            
            # --- ✨ INICIO DE LA CORRECCIÓN ✨ ---
            # Construimos el DTO manualmente en lugar de usar from_orm con 'update'
            self.product_in_modal = ProductDetailData(
                id=db_post.id,
                title=db_post.title,
                content=db_post.content,
                price_cop=db_post.price_cop,
                variants=db_post.variants or [],
                created_at_formatted=db_post.created_at_formatted,
                average_rating=db_post.average_rating,
                rating_count=db_post.rating_count,
                shipping_cost=db_post.shipping_cost,
                is_moda_completa_eligible=db_post.is_moda_completa_eligible,
                is_imported=db_post.is_imported,
                # Añadimos los campos calculados
                shipping_display_text=shipping_text,
                seller_name=seller_name,
                seller_id=seller_id
            )
            # --- ✨ FIN DE LA CORRECCIÓN ✨ ---
            
            if self.product_in_modal.variants:
                self._set_default_attributes_from_variant(self.product_in_modal.variants[0])

            # El resto de la función (carga de comentarios y lógica de opinión) no cambia
            all_comment_dtos = [self._convert_comment_to_dto(c) for c in db_post.comments]
            original_comment_dtos = [dto for dto in all_comment_dtos if dto.id not in {update.id for parent in all_comment_dtos for update in parent.updates}]
            self.product_comments = sorted(original_comment_dtos, key=lambda c: c.id, reverse=True)

            if self.is_authenticated:
                user_info_id = self.authenticated_user_info.id
                purchase_count = session.exec(
                    sqlmodel.select(sqlmodel.func.count(PurchaseItemModel.id))
                    .join(PurchaseModel)
                    .where(
                        PurchaseModel.userinfo_id == user_info_id,
                        PurchaseItemModel.blog_post_id == post_id,
                        PurchaseModel.status == PurchaseStatus.DELIVERED
                    )
                ).one()

                if purchase_count > 0:
                    user_original_comment = next((c for c in db_post.comments if c.userinfo_id == user_info_id and c.parent_comment_id is None), None)
                    if not user_original_comment:
                        self.show_review_form = True
                    else:
                        current_updates_count = len(user_original_comment.updates)
                        if current_updates_count < purchase_count:
                            self.show_review_form = True
                            latest_entry = sorted([user_original_comment] + user_original_comment.updates, key=lambda c: c.created_at, reverse=True)[0]
                            self.my_review_for_product = self._convert_comment_to_dto(latest_entry)
                            self.review_rating = latest_entry.rating
                            self.review_content = latest_entry.content
                        else:
                            self.review_limit_reached = True

        yield AppState.load_saved_post_ids

    
    @rx.event
    def close_product_detail_modal(self, open_state: bool):
        if not open_state:
            self.show_detail_modal = False
            self.product_in_modal = None
    
    @rx.var
    def base_app_url(self) -> str:
        return get_config().deploy_url
    
    # --- 👇 LÍNEA MODIFICADA 👇 ---
    seller_page_info: Optional[SellerInfoData] = None
    seller_page_posts: list[ProductCardData] = []

    @rx.event
    def on_load_seller_page(self):
        self.is_loading = True
        self.seller_page_info = None
        self.seller_page_posts = []
        yield
        
        seller_id_str = "0"
        try:
            full_url = self.router.url
            if full_url and "?" in full_url:
                parsed_url = urlparse(full_url)
                query_dict = parse_qs(parsed_url.query)
                id_list = query_dict.get("id")
                if id_list:
                    seller_id_str = id_list[0]
        except Exception:
            pass

        try:
            seller_id_int = int(seller_id_str)
        except (ValueError, TypeError):
            seller_id_int = 0

        if seller_id_int > 0:
            with rx.session() as session:
                seller_info_db = session.exec(
                    sqlmodel.select(UserInfo).options(sqlalchemy.orm.joinedload(UserInfo.user))
                    .where(UserInfo.id == seller_id_int)
                ).one_or_none()
                
                # --- 👇 BLOQUE CORREGIDO 👇 ---
                if seller_info_db and seller_info_db.user:
                    # En lugar de guardar el objeto complejo, creamos un DTO simple
                    self.seller_page_info = SellerInfoData(
                        id=seller_info_db.id,
                        username=seller_info_db.user.username
                    )

                    # La carga de los posts del vendedor no cambia
                    posts = session.exec(
                        sqlmodel.select(BlogPostModel)
                        .where(
                            BlogPostModel.userinfo_id == seller_id_int,
                            BlogPostModel.publish_active == True
                        )
                        .order_by(BlogPostModel.created_at.desc())
                    ).all()
                    
                    # ... (el resto del bucle para crear temp_posts no cambia)
                    temp_posts = []
                    for p in posts:
                        temp_posts.append(
                            ProductCardData(
                                # ... todos los campos como los teníamos antes
                                id=p.id,
                                userinfo_id=p.userinfo_id,
                                title=p.title,
                                price=p.price,
                                price_cop=p.price_cop,
                                variants=p.variants or [],
                                attributes={},
                                average_rating=p.average_rating,
                                rating_count=p.rating_count,
                                shipping_cost=p.shipping_cost,
                                is_moda_completa_eligible=p.is_moda_completa_eligible,
                                shipping_display_text=_get_shipping_display_text(p.shipping_cost),
                                is_imported=p.is_imported
                            )
                        )
                    self.seller_page_posts = temp_posts

        self.is_loading = False


    current_ticket_purchase: Optional[UserPurchaseHistoryCardData] = None
    current_ticket: Optional[SupportTicketData] = None
    ticket_messages: list[SupportMessageData] = []
    new_message_content: str = ""
    all_support_tickets: list[SupportTicketAdminData] = []
    search_query_tickets: str = ""

# 3. --- Añadir los nuevos setters y event handlers a AppState ---
    def set_new_message_content(self, content: str):
        self.new_message_content = content

    @rx.event
    def go_to_return_page(self, purchase_id: int):
        """Navega a la página de devoluciones y prepara el estado."""
        self.current_ticket = None
        self.current_ticket_purchase = None
        self.ticket_messages = []
        return rx.redirect(f"/returns?purchase_id={purchase_id}")

    @rx.event
    def on_load_return_page(self):
        """
        Se ejecuta al cargar la página /returns y autoriza al comprador o al vendedor,
        manejando el caso donde el ticket aún no ha sido creado.
        """
        self.is_loading = True
        self.current_ticket = None
        self.current_ticket_purchase = None
        self.ticket_messages = []
        yield

        if not self.authenticated_user_info:
            self.is_loading = False
            return rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)

        purchase_id_str = "0"
        try:
            full_url = self.router.url
            if "?" in full_url:
                query_params = parse_qs(full_url.split("?")[1])
                purchase_id_str = query_params.get("purchase_id", ["0"])[0]
        except Exception:
            pass

        try:
            purchase_id = int(purchase_id_str)
        except ValueError:
            self.is_loading = False
            return rx.toast.error("ID de compra no válido.")

        with rx.session() as session:
            purchase_db = session.get(PurchaseModel, purchase_id)
            if not purchase_db:
                self.is_loading = False
                return rx.toast.error("Compra no encontrada.")

            ticket = session.exec(
                sqlmodel.select(SupportTicketModel).where(SupportTicketModel.purchase_id == purchase_id)
            ).one_or_none()

            is_buyer = purchase_db.userinfo_id == self.authenticated_user_info.id
            is_seller = ticket and ticket.seller_id == self.authenticated_user_info.id
            
            if not is_buyer and not is_seller:
                self.is_loading = False
                return rx.toast.error("No tienes autorización para ver esta solicitud.")

            # --- ✨ INICIO DE LA CORRECCIÓN ✨ ---
            # Primero, preparamos la lista de artículos DTO, como antes.
            purchase_items_data = []
            for item in purchase_db.items:
                if item.blog_post:
                    main_image = item.blog_post.variants[0].get("image_url", "") if item.blog_post.variants else ""
                    purchase_items_data.append(
                        PurchaseItemCardData(
                            id=item.blog_post.id, title=item.blog_post.title, image_url=main_image,
                            price_at_purchase=item.price_at_purchase,
                            price_at_purchase_cop=format_to_cop(item.price_at_purchase),
                            quantity=item.quantity
                        )
                    )
            
            # Ahora, construimos el DTO principal manualmente, campo por campo.
            self.current_ticket_purchase = UserPurchaseHistoryCardData(
                id=purchase_db.id,
                userinfo_id=purchase_db.userinfo_id,
                purchase_date_formatted=purchase_db.purchase_date_formatted,
                status=purchase_db.status.value,
                total_price_cop=purchase_db.total_price_cop,
                shipping_applied_cop=format_to_cop(purchase_db.shipping_applied),
                shipping_name=purchase_db.shipping_name,
                shipping_address=purchase_db.shipping_address,
                shipping_neighborhood=purchase_db.shipping_neighborhood,
                shipping_city=purchase_db.shipping_city,
                shipping_phone=purchase_db.shipping_phone,
                items=purchase_items_data  # Usamos la lista que acabamos de crear
            )
            # --- ✨ FIN DE LA CORRECCIÓN ✨ ---

            if ticket:
                self.current_ticket = SupportTicketData.from_orm(ticket)
                messages = session.exec(
                    sqlmodel.select(SupportMessageModel)
                    .options(sqlalchemy.orm.joinedload(SupportMessageModel.author).joinedload(UserInfo.user))
                    .where(SupportMessageModel.ticket_id == ticket.id)
                    .order_by(SupportMessageModel.created_at.asc())
                ).all()
                
                self.ticket_messages = [
                    SupportMessageData(
                        author_id=m.author_id,
                        author_username=m.author.user.username if m.author and m.author.user else "Usuario",
                        content=m.content,
                        created_at_formatted=m.created_at_formatted,
                    ) for m in messages
                ]
        self.is_loading = False
        # --- ✨ FIN DE LA LÓGICA CORREGIDA ✨ ---

    @rx.event
    def create_support_ticket(self, reason: str):
        """Crea un nuevo ticket de soporte y el mensaje inicial."""
        if not self.authenticated_user_info or not self.current_ticket_purchase:
            return rx.toast.error("Error de sesión. Intenta de nuevo.")

        with rx.session() as session:
            purchase = session.get(PurchaseModel, self.current_ticket_purchase.id)
            if not purchase:
                return rx.toast.error("La compra asociada no existe.")

            # Encontrar el vendedor (dueño del primer producto)
            first_item = purchase.items[0] if purchase.items else None
            if not first_item or not first_item.blog_post:
                return rx.toast.error("No se pueden encontrar los productos de la compra.")
            
            seller_id = first_item.blog_post.userinfo_id

            # Crear el ticket
            new_ticket = SupportTicketModel(
                purchase_id=purchase.id,
                buyer_id=self.authenticated_user_info.id,
                seller_id=seller_id,
                subject=reason,
            )
            session.add(new_ticket)
            session.commit()
            session.refresh(new_ticket)

            # Crear el mensaje inicial
            initial_message_content = (
                f"Solicitud iniciada por el comprador.\n"
                f"Motivo: {reason}\n"
                f"--- Detalles de la Compra ---\n"
                f"ID: #{purchase.id}\n"
                f"Fecha: {purchase.purchase_date_formatted}\n"
                f"Total: {purchase.total_price_cop}"
            )
            initial_message = SupportMessageModel(
                ticket_id=new_ticket.id,
                author_id=self.authenticated_user_info.id,
                content=initial_message_content,
            )
            session.add(initial_message)

            # Notificar al vendedor
            notification = NotificationModel(
                userinfo_id=seller_id,
                message=f"Nueva solicitud de devolución/cambio para la compra #{purchase.id}.",
                url=f"/returns?purchase_id={purchase.id}",
            )
            session.add(notification)
            session.commit()

        yield rx.toast.success("Tu solicitud ha sido enviada al vendedor.")
        yield AppState.on_load_return_page # Recargar la página para mostrar el chat

    @rx.event
    def post_support_message(self, form_data: dict):
        """Añade un nuevo mensaje al chat de soporte."""
        content = form_data.get("message_content")
        if not content or not self.is_authenticated or not self.current_ticket:
            return

        with rx.session() as session:
            new_message = SupportMessageModel(
                ticket_id=self.current_ticket.id,
                author_id=self.authenticated_user_info.id,
                content=content,
            )
            session.add(new_message)
            
            # Determinar a quién notificar
            recipient_id = (
                self.current_ticket.seller_id
                if self.authenticated_user_info.id == self.current_ticket.buyer_id
                else self.current_ticket.buyer_id
            )
            notification = NotificationModel(
                userinfo_id=recipient_id,
                message=f"Nuevo mensaje en tu solicitud para la compra #{self.current_ticket.purchase_id}.",
                url=f"/returns?purchase_id={self.current_ticket.purchase_id}",
            )
            session.add(notification)
            session.commit()
        
        # --- CORRECCIÓN ---
        # Limpiamos explícitamente la variable de estado después de enviar.
        self.new_message_content = ""

        yield AppState.on_load_return_page # Recargar para mostrar el nuevo mensaje

    def set_search_query_tickets(self, query: str):
        """Actualiza el término de búsqueda para los tickets."""
        self.search_query_tickets = query

    @rx.var
    def filtered_support_tickets(self) -> list[SupportTicketAdminData]:
        """Filtra la lista de tickets de soporte para el admin."""
        if not self.search_query_tickets.strip():
            return self.all_support_tickets
        
        query = self.search_query_tickets.lower()
        return [
            ticket for ticket in self.all_support_tickets
            if query in f"#{ticket.purchase_id}" or 
               query in ticket.buyer_name.lower() or
               query in ticket.subject.lower()
        ]

    @rx.event
    def on_load_admin_tickets_page(self):
        """Carga todos los tickets de soporte donde el usuario actual es el vendedor."""
        if not self.is_admin:
            return rx.redirect("/")

        with rx.session() as session:
            tickets = session.exec(
                sqlmodel.select(SupportTicketModel)
                .options(sqlalchemy.orm.joinedload(SupportTicketModel.buyer).joinedload(UserInfo.user))
                .where(SupportTicketModel.seller_id == self.authenticated_user_info.id)
                .order_by(SupportTicketModel.created_at.desc())
            ).all()

            self.all_support_tickets = [
                SupportTicketAdminData(
                    ticket_id=t.id,
                    purchase_id=t.purchase_id,
                    buyer_name=t.buyer.user.username,
                    subject=t.subject,
                    status=t.status.value,
                    created_at_formatted=format_utc_to_local(t.created_at)
                ) for t in tickets if t.buyer and t.buyer.user
            ]

    @rx.event
    def close_ticket(self, ticket_id: int):
        """Permite al comprador o al vendedor cerrar un ticket."""
        if not self.authenticated_user_info:
            return rx.toast.error("Debes iniciar sesión.")

        with rx.session() as session:
            ticket = session.get(SupportTicketModel, ticket_id)
            if not ticket:
                return rx.toast.error("La solicitud no fue encontrada.")

            # Verificar permisos
            if self.authenticated_user_info.id not in [ticket.buyer_id, ticket.seller_id]:
                return rx.toast.error("No tienes permiso para modificar esta solicitud.")

            ticket.status = TicketStatus.CLOSED
            
            # Añadir mensaje de sistema al chat
            system_message = SupportMessageModel(
                ticket_id=ticket.id,
                author_id=self.authenticated_user_info.id,
                content=f"--- Solicitud cerrada por {self.authenticated_user_info.user.username} ---"
            )
            session.add(ticket)
            session.add(system_message)
            session.commit()
        
        yield rx.toast.success("La solicitud ha sido cerrada.")
        yield AppState.on_load_return_page # Recargar la página del chat