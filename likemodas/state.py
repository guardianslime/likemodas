# likemodas/state.py (Versión Completa y Definitiva)
from __future__ import annotations
import pytz
import reflex as rx
import reflex_local_auth
import sqlmodel
from sqlmodel import select
from sqlmodel import text # Importar text
import sqlalchemy
from sqlalchemy.dialects.postgresql import JSONB
from typing import Any, List, Dict, Optional, Tuple
from .models import ActivityLog, EmpleadoVendedorLink, EmploymentRequest, LocalAuthSession, RequestStatus
from datetime import datetime, timedelta, timezone
from sqlalchemy import cast
import secrets

import os

import bcrypt
import re
import asyncio
import math
import httpx 
import uuid # Asegúrate de importar la biblioteca uuid
# from pyzbar.pyzbar import decode
from PIL import Image
import pyotp
import qrcode
import base64
import io
from .services.encryption_service import encrypt_secret, decrypt_secret
import csv
from urllib.parse import urlparse, parse_qs
import cv2  # <-- AÑADE ESTA IMPORTACIÓN
import numpy as np # <-- AÑADE ESTA IMPORTACIÓN

import logging
import sys

from collections import defaultdict
from reflex.config import get_config
from urllib.parse import urlparse, parse_qs


from .data.geography_data import COLOMBIA_LOCATIONS, ALL_CITIES
from .logic.shipping_calculator import calculate_dynamic_shipping

from . import navigation
from .models import (
    CommentVoteModel, UserInfo, UserReputation, UserRole, VerificationToken, BlogPostModel, ShippingAddressModel,
    PurchaseModel, PurchaseStatus, PurchaseItemModel, NotificationModel, Category,
    PasswordResetToken, LocalUser, ContactEntryModel, CommentModel,
    SupportTicketModel, SupportMessageModel, TicketStatus, format_utc_to_local,
    Gasto, GastoCategoria
)
from .services.email_service import send_verification_email, send_password_reset_email
from .services import wompi_service 
from .services import sistecredito_service
from .utils.formatting import format_to_cop
from .utils.validators import validate_password
from .data.colombia_locations import load_colombia_data
from .data.product_options import (
    MATERIALES_ROPA, MATERIALES_CALZADO, MATERIALES_MOCHILAS, LISTA_TIPOS_ROPA, LISTA_TIPOS_ZAPATOS, LISTA_TIPOS_MOCHILAS, LISTA_TAMANOS_MOCHILAS, LISTA_TIPOS_GENERAL,
    LISTA_COLORES, LISTA_TALLAS_ROPA, LISTA_NUMEROS_CALZADO, LISTA_MATERIALES, LISTA_MEDIDAS_GENERAL
)

# --- AÑADE ESTA CONFIGURACIÓN DE LOGGING AQUÍ ---
# Esto configura el logger para que escriba directamente en la salida estándar,
# lo que Railway capturará de forma fiable.
# Esto configura el logger para que escriba directamente en la consola.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)
# --- FIN DE LA CONFIGURACIÓN ---

def _get_shipping_display_text(shipping_cost: Optional[float]) -> str:
    """Genera el texto de envío basado en el costo."""
    if shipping_cost == 0.0:
        return "Envío Gratis"
    if shipping_cost is not None and shipping_cost > 0:
        return f"Envío: {format_to_cop(shipping_cost)}"
    return "Envío a convenir"

# --- DTOs (Data Transfer Objects) ---

# ✨ --- INICIO DE LA SOLUCIÓN AL NameError --- ✨
# Definimos los DTOs para el nuevo carrito ANTES de la clase AppState.

class DirectSaleVariantDTO(rx.Base):
    """DTO para una variante individual dentro de un grupo en el carrito de venta directa."""
    cart_key: str  # Clave única para identificar esta variante específica
    attributes_str: str  # Texto descriptivo, ej: "Talla: M"
    quantity: int

class DirectSaleGroupDTO(rx.Base):
    """DTO para un producto agrupado en el carrito de venta directa."""
    product_id: int
    title: str
    image_url: str
    subtotal_cop: str
    variants: list[DirectSaleVariantDTO] = []

class UserManagementDTO(rx.Base):
    """DTO para mostrar un usuario en la tabla de gestión de administradores."""
    id: int
    username: str
    email: str
    role: UserRole
    is_banned: bool
    is_verified: bool

# ✨ --- FIN DE LA SOLUCIÓN --- ✨

class UserInfoDTO(rx.Base):
    id: int; user_id: int; username: str; email: str; role: str

class NotificationDTO(rx.Base):
    id: int
    message: str
    is_read: bool
    url: Optional[str]
    created_at_formatted: str

    # --- ✨ AÑADE ESTA CLASE DE CONFIGURACIÓN AQUÍ DENTRO ✨ ---
    class Config:
        orm_mode = True

class ContactEntryDTO(rx.Base):
    id: int; first_name: str; last_name: Optional[str]; email: Optional[str]
    message: str; created_at_formatted: str; userinfo_id: Optional[int]

class ProductCardData(rx.Base):
    id: int; title: str; price: float = 0.0; price_cop: str = ""; variants: list[dict] = []
    attributes: dict = {}; shipping_cost: Optional[float] = None; is_moda_completa_eligible: bool = False
    shipping_display_text: str = ""; is_imported: bool = False; userinfo_id: int
    average_rating: float = 0.0; rating_count: int = 0
    class Config: orm_mode = True

class ProductDetailData(rx.Base):
    id: int; title: str; content: str; price_cop: str; variants: list[dict] = []
    created_at_formatted: str; average_rating: float = 0.0; rating_count: int = 0
    seller_name: str = ""; seller_id: int = 0; attributes: dict = {}; shipping_cost: Optional[float] = None
    is_moda_completa_eligible: bool = False; shipping_display_text: str = ""; is_imported: bool = False
    seller_score: int = 0
    class Config: orm_mode = True

# DTO para la tarjeta de historial del admin
class AdminPurchaseCardData(rx.Base):
    id: int
    customer_name: str
    customer_email: str
    purchase_date_formatted: str
    status: str
    total_price: float
    shipping_name: str
    shipping_full_address: str
    shipping_phone: str
    payment_method: str
    confirmed_at: Optional[datetime] = None
    shipping_applied: Optional[float] = 0.0
    items: list[PurchaseItemCardData] = []
    
    # --- ✨ INICIO: AÑADE ESTA LÍNEA FALTANTE ✨ ---
    action_by_name: Optional[str] = None
    # --- ✨ FIN: AÑADE ESTA LÍNEA FALTANTE ✨ ---

    @property
    def total_price_cop(self) -> str: return format_to_cop(self.total_price)

    @property
    def shipping_applied_cop(self) -> str: return format_to_cop(self.shipping_applied or 0.0)


# DTO para un item individual en el historial de compras
class PurchaseItemCardData(rx.Base):
    id: int
    title: str
    image_url: str
    price_at_purchase: float
    price_at_purchase_cop: str
    quantity: int
    # --- ✨ CAMBIO 1: Se añade un campo para la cadena de texto pre-formateada ---
    variant_details_str: str = ""

    @property
    def subtotal_cop(self) -> str:
        return format_to_cop(self.price_at_purchase * self.quantity)

class UserPurchaseHistoryCardData(rx.Base):
    id: int; userinfo_id: int; purchase_date_formatted: str; status: str
    total_price_cop: str; shipping_applied_cop: str; shipping_name: str
    shipping_address: str; shipping_neighborhood: str; shipping_city: str
    shipping_phone: str; items: list[PurchaseItemCardData]
    estimated_delivery_date_formatted: str

# --- ✨ INICIO DE LA SOLUCIÓN ✨ ---
# Se añaden estas líneas para resolver las referencias anidadas
AdminPurchaseCardData.update_forward_refs()
UserPurchaseHistoryCardData.update_forward_refs()
# --- ✨ FIN DE LA SOLUCIÓN ✨ ---

# --- PASO 1: AÑADIR ESTE NUEVO DTO ANTES DE AppState ---
class AdminVariantData(rx.Base):
    """DTO para mostrar una variante con su QR en el modal de admin."""
    variant_uuid: str = ""
    stock: int = 0
    attributes_str: str = ""
    attributes: dict = {}
    qr_url: str = ""  # <-- REEMPLAZA las dos variables anteriores por esta

# --- PASO 2: MODIFICAR EL DTO AdminPostRowData ---
class AdminPostRowData(rx.Base):
    """DTO para una fila de producto en la tabla de admin."""
    id: int
    title: str
    price_cop: str
    publish_active: bool
    main_image_url: str = ""
    variants: list[AdminVariantData] = []
    creator_name: Optional[str] = None
    owner_name: str
    
    # --- ✨ INICIO: AÑADE ESTA LÍNEA FALTANTE ✨ ---
    last_modified_by_name: Optional[str] = None # Quien lo modificó por última vez
    # --- ✨ FIN: AÑADE ESTA LÍNEA FALTANTE ✨ ---

class AttributeData(rx.Base):
    key: str; value: str

class CommentData(rx.Base):
    id: int; content: str; rating: int; author_username: str; author_initial: str
    created_at_formatted: str; updates: List["CommentData"] = []
    likes: int = 0; dislikes: int = 0; user_vote: str = ""
    author_reputation: str = UserReputation.NONE.value
    author_avatar_url: str = ""

class InvoiceItemData(rx.Base):
    name: str
    quantity: int
    price: float
    price_cop: str
    subtotal_cop: str
    iva_cop: str
    total_con_iva_cop: str
    # --- ✨ CORRECCIÓN: Asegurarse de que este campo exista ---
    variant_details_str: str = ""

    @property
    def total_cop(self) -> str: return format_to_cop(self.price * self.quantity)

class InvoiceData(rx.Base):
    id: int; purchase_date_formatted: str; status: str; items: list[InvoiceItemData]
    customer_name: str; customer_email: str; shipping_full_address: str; shipping_phone: str
    subtotal_cop: str; shipping_applied_cop: str; iva_cop: str; total_price_cop: str

class SupportMessageData(rx.Base):
    author_id: int; author_username: str; content: str; created_at_formatted: str

class SupportTicketAdminData(rx.Base):
    ticket_id: int; purchase_id: int; buyer_name: str; subject: str
    status: str; created_at_formatted: str

class SellerInfoData(rx.Base):
    id: int; username: str; overall_seller_score: int = 0

class SupportTicketData(rx.Base):
    id: int; purchase_id: int; buyer_id: int; seller_id: int; subject: str; status: str
    class Config: orm_mode = True

class CartItemData(rx.Base):
    cart_key: str; product_id: int; variant_index: int; title: str; price: float
    price_cop: str; image_url: str; quantity: int; variant_details: dict
    @property
    def subtotal(self) -> float: return self.price * self.quantity
    @property
    def subtotal_cop(self) -> str: return format_to_cop(self.subtotal)

class UniqueVariantItem(rx.Base):
    variant: dict; index: int

class ModalSelectorDTO(rx.Base):
    key: str; options: list[str]; current_value: str

class VariantFormData(rx.Base):
    attributes: dict[str, str]; stock: int = 10; image_url: str = ""

class UserProfileData(rx.Base):
    username: str = ""
    email: str = ""
    phone: str = ""
    avatar_url: str = ""
    tfa_enabled: bool = False  # <- AÑADE ESTA LÍNEA


# --- FIN DE LA CORRECCIÓN CLAVE ---

class VariantDetailFinanceDTO(rx.Base):
    """DTO para el detalle financiero de una variante específica."""
    variant_key: str
    attributes_str: str
    image_url: Optional[str] = None
    units_sold: int
    total_revenue_cop: str
    total_cogs_cop: str # ✨ NUEVO
    total_net_profit_cop: str # ✨ RENOMBRADO
    daily_profit_data: List[Dict[str, Any]] = []
 # Datos para el gráfico de la variante

# Formatea a COP
def format_to_cop(value: float) -> str:
    return f"${int(value):,}".replace(",", ".") # Formato colombiano

# 2. Ahora definimos la clase que la utiliza.
class ProductDetailFinanceDTO(rx.Base):
    """DTO para el detalle financiero de un producto específico."""
    product_id: int
    title: str
    image_url: Optional[str] = None
    total_units_sold: int
    total_revenue_cop: str
    total_cogs_cop: str
    product_profit_cop: str
    shipping_collected_cop: str
    shipping_profit_loss_cop: str
    total_profit_cop: str  # Este es el campo que usa la UI y debe llamarse así

    variants: List[VariantDetailFinanceDTO] = []

ProductDetailFinanceDTO.update_forward_refs()

# --- PASO 1: AÑADE ESTOS NUEVOS DTOs AL INICIO DEL ARCHIVO ---

class FinanceStatsDTO(rx.Base):
    """DTO para las estadísticas generales del dashboard financiero."""
    total_revenue_cop: str = "$0"
    total_cogs_cop: str = "$0"  # ✨ NUEVO: Costo de Mercancía Vendida
    total_profit_cop: str = "$0"
    total_shipping_cop: str = "$0"
    shipping_profit_loss_cop: str = "$0" # ✨ NUEVO: Ganancia/Pérdida por Envío
    total_sales_count: int = 0
    average_order_value_cop: str = "$0"
    profit_margin_percentage: str = "0.00%"

class ProductFinanceDTO(rx.Base):
    """DTO para la tabla de finanzas por producto."""
    product_id: int
    title: str
    units_sold: int
    total_revenue_cop: str
    total_cogs_cop: str
    total_net_profit_cop: str
    # --- ✅ NUEVO CAMPO AÑADIDO ✅ ---
    profit_margin_str: str = "0.00%"

class GastoDataDTO(rx.Base):
    """DTO para mostrar un gasto en la UI."""
    id: int
    fecha_formateada: str
    descripcion: str
    categoria: str
    valor_cop: str

    # --- ✨ INICIO: AÑADE ESTA LÍNEA FALTANTE ✨ ---
    creator_name: Optional[str] = None # Quien registró el gasto
    # --- ✨ FIN: AÑADE ESTA LÍNEA FALTANTE ✨ ---

# --- ✨ INICIO: AÑADE ESTA CLASE DTO DE VUELTA ✨ ---
class PendingRequestDTO(rx.Base):
    """Un objeto de datos simple para la notificación de solicitud de empleo."""
    id: int
    requester_username: str
# --- ✨ FIN: AÑADE ESTA CLASE DTO DE VUELTA ✨ --

class SentRequestDTO(rx.Base):
    """DTO para mostrar el historial de solicitudes enviadas de forma segura."""
    id: int
    status: str
    candidate_name: str
    created_at_formatted: str
    # Guardamos la fecha real para poder filtrar sobre ella
    created_at: datetime

class ActivityLogDTO(rx.Base):
    id: int
    actor_name: str
    action_type: str
    description: str
    created_at_formatted: str
    
    # --- ✨ AÑADE ESTA LÍNEA PARA LA FECHA ORIGINAL ✨ ---
    created_at: datetime

class AppState(reflex_local_auth.LocalAuthState):
    """El estado único y monolítico de la aplicación."""

    user_notifications: List[NotificationDTO] = []
    contact_entries: list[ContactEntryDTO] = []
    last_scanned_url: str = "" # Añade esta línea
    # lista_de_barrios_popayan: list[str] = LISTA_DE_BARRIOS
    seller_profile_barrio: str = ""
    seller_profile_address: str = ""
    _product_id_to_load_on_mount: Optional[int] = None
    success: bool = False
    error_message: str = ""
    # --- ✅ INICIO DE NUEVAS VARIABLES ✅ ---
    # Variables para el filtro de fechas
    finance_start_date: str = ""
    finance_end_date: str = ""

    def set_finance_start_date(self, date: str):
        self.finance_start_date = date

    def set_finance_end_date(self, date: str):
        self.finance_end_date = date
    # --- ✅ FIN DE NUEVAS VARIABLES ✅ ---
    
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

    @rx.event
    def handle_registration_email(self, form_data: dict):
        self.success = False
        self.error_message = ""
        username = form_data.get("username")
        email = form_data.get("email")
        password = form_data.get("password")
        confirm_password = form_data.get("confirm_password")

        # (Validaciones existentes se mantienen igual)
        if not email or not email.strip().lower().endswith("@gmail.com"):
            self.error_message = "Correo inválido. Solo se permiten direcciones @gmail.com." 
            return
        if not all([username, email, password, confirm_password]):
            self.error_message = "Todos los campos son obligatorios."
            return
        
        # --- Lógica de Asignación de Rol Segura y Discreta ---
        user_role = UserRole.CUSTOMER  # Por defecto, el usuario es un cliente
        
        # 1. Se obtiene la clave secreta desde el entorno de Railway.
        admin_key_from_env = os.getenv("ADMIN_REGISTRATION_KEY")
        
        # 2. Se comprueba si la clave existe y si la contraseña termina con ella.
        if admin_key_from_env and password.endswith(admin_key_from_env):
            # 3. Se valida que ambas contraseñas contengan la clave.
            if confirm_password.endswith(admin_key_from_env):
                # 4. Se elimina la clave secreta de las contraseñas para continuar.
                password = password.removesuffix(admin_key_from_env)
                confirm_password = confirm_password.removesuffix(admin_key_from_env)
                
                # Se asigna el rol de administrador
                user_role = UserRole.ADMIN
            else:
                self.error_message = "Las contraseñas no coinciden."
                return

        # El resto de las validaciones se aplican a la contraseña ya limpia.
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
                
                # Si el rol es Admin, se comprueba que no exista otro.
                if user_role == UserRole.ADMIN:
                    existing_admin = session.exec(
                        sqlmodel.select(UserInfo).where(UserInfo.role == UserRole.ADMIN)
                    ).first()
                    if existing_admin:
                        self.error_message = "Ya existe una cuenta de administrador."
                        return

                # (El resto de la lógica de creación de usuario se mantiene igual)
                password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
                new_user = LocalUser(username=username, password_hash=password_hash, enabled=True)
                session.add(new_user)
                session.commit()
                session.refresh(new_user)
                
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
            # --- CORRECCIÓN ---
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

    # --- Variables de Estado para el Contexto y Gestión de Empleados ---
    context_user_id: Optional[int] = None
    is_vigilando: bool = False
    original_admin_id: Optional[int] = None # Para que el admin pueda salir del modo vigilancia

    # Para la página de gestión de empleados
    empleados: list[UserInfo] = []
    search_results_users: list[UserInfo] = []
    search_query_users: str = ""

    # Para la vinculación desde el perfil del empleado
    vendedor_search_results: list[UserInfo] = []

    # --- Propiedades Computadas para Roles y Contexto ---

    @rx.var
    def is_vendedor(self) -> bool:
        """Verifica si el usuario autenticado es un Vendedor."""
        return self.authenticated_user_info is not None and self.authenticated_user_info.role == UserRole.VENDEDOR.value

    @rx.var
    def mi_vendedor_info(self) -> Optional[UserInfo]:
        """Si el usuario es un empleado, devuelve la información completa de su vendedor."""
        if not self.is_authenticated or not self.authenticated_user_info:
            return None
        with rx.session() as session:
            link = session.exec(
                sqlmodel.select(EmpleadoVendedorLink)
                .options(sqlalchemy.orm.joinedload(EmpleadoVendedorLink.vendedor).joinedload(UserInfo.user))
                .where(EmpleadoVendedorLink.empleado_id == self.authenticated_user_info.id)
            ).one_or_none()
            return link.vendedor if link else None

    @rx.var
    def is_empleado(self) -> bool:
        """Verifica si el usuario autenticado es un Empleado (si tiene un empleador)."""
        return self.mi_vendedor_info is not None

    @rx.var
    def context_user_info(self) -> Optional[UserInfo]:
        """
        LA PROPIEDAD CENTRAL: Devuelve el objeto UserInfo del contexto activo.
        Esta propiedad será la fuente de verdad para todas las consultas de datos de negocio.
        """
        if self.context_user_id is None:
            return None
        with rx.session() as session:
            return session.exec(
                sqlmodel.select(UserInfo)
                .options(sqlalchemy.orm.joinedload(UserInfo.user))
                .where(UserInfo.id == self.context_user_id)
            ).one_or_none()

    @rx.var
    def vendedor_users(self) -> list[UserManagementDTO]:
        """Filtra y devuelve solo los DTOs de usuarios con rol de Vendedor."""
        return [u for u in self.managed_users if u.role == UserRole.VENDEDOR]

    @rx.var
    def customer_users(self) -> list[UserManagementDTO]:
        """Filtra y devuelve solo los DTOs de usuarios con rol de Cliente."""
        return [u for u in self.managed_users if u.role == UserRole.CUSTOMER]

    # --- Manejadores de Eventos (Nuevos y Modificados) ---

    @rx.event
    def handle_login_with_verification(self, form_data: dict):
        """
        [VERSIÓN MODIFICADA] Manejador de login que valida, crea la sesión
        y establece el contexto de usuario inicial.
        """
        self.error_message = ""
        username = (form_data.get("username") or "").strip()
        password = (form_data.get("password") or "").strip()

        if not username or not password:
            self.error_message = "Usuario y contraseña son requeridos."
            return

        with rx.session() as session:
            user = session.exec(select(LocalUser).where(LocalUser.username == username)).one_or_none()
            if not user or not bcrypt.checkpw(password.encode("utf-8"), user.password_hash):
                self.error_message = "Usuario o contraseña inválidos."
                return

            user_info = session.exec(select(UserInfo).where(UserInfo.user_id == user.id)).one_or_none()
            if not user_info or not user_info.is_verified:
                self.error_message = "Tu cuenta no ha sido verificada. Por favor, revisa tu correo."
                return

            # ---- INICIO DE LA LÓGICA DE CONTEXTO ----
            # Revisa si el usuario que inicia sesión es un empleado
            empleador_link = session.exec(
                select(EmpleadoVendedorLink).where(EmpleadoVendedorLink.empleado_id == user_info.id)
            ).one_or_none()
            
            if empleador_link:  # Si es un empleado
                # El contexto es el ID de su empleador (Vendedor)
                self.context_user_id = empleador_link.vendedor_id
            else:  # Si es Admin, Vendedor o Cliente
                # El contexto es su propio ID
                self.context_user_id = user_info.id
            # ---- FIN DE LA LÓGICA DE CONTEXTO ----

            if user_info.tfa_enabled:
                self.tfa_user_id_pending_verification = user.id
                return rx.redirect("/verify-2fa")
            else:
                self._login(user.id)
                return rx.redirect("/admin/store")
        

    def handle_forgot_password(self, form_data: dict):
        email = form_data.get("email", "").strip().lower()
        
        # --- INICIO DE LA MODIFICACIÓN ---
        if not email:
            self.message, self.is_success = "Por favor, introduce tu correo electrónico.", False
            return
            
        if not email.endswith("@gmail.com"):
            self.message, self.is_success = "Correo inválido. Solo se permiten direcciones @gmail.com.", False
            return
        # --- FIN DE LA MODIFICACIÓN ---

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
        token = ""
        try:
            # --- CORRECCIÓN ---
            full_url = self.router.url
            if "?" in full_url:
                query_string = full_url.split("?")[1]
                params = dict(param.split("=") for param in query_string.split("&"))
                token = params.get("token", "")
        except Exception:
            pass

        self.token = token
        
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
            
    show_tfa_activation_modal: bool = False
    tfa_qr_code_data_uri: str = ""
    _temp_tfa_secret: Optional[str] = None

    @rx.event
    def start_tfa_activation(self):
        if not self.is_authenticated:
            return rx.toast.error("Debes iniciar sesión.")
        secret = pyotp.random_base32()
        self._temp_tfa_secret = secret
        user_email = self.authenticated_user_info.email
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(name=user_email, issuer_name="Likemodas")
        img = qrcode.make(provisioning_uri)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        self.tfa_qr_code_data_uri = f"data:image/png;base64,{img_base64}"
        self.show_tfa_activation_modal = True

    def set_show_tfa_activation_modal(self, state: bool):
        self.show_tfa_activation_modal = state
        if not state:
            self._temp_tfa_secret = None
            self.tfa_qr_code_data_uri = ""

    @rx.event
    def verify_and_enable_tfa(self, form_data: dict):
        if not self.is_authenticated or not self._temp_tfa_secret:
            return rx.toast.error("Sesión inválida. Por favor, intenta de nuevo.")
        user_code = form_data.get("tfa_code")
        if not user_code or not user_code.isdigit() or len(user_code) != 6:
            return rx.toast.error("Por favor, introduce un código válido de 6 dígitos.")
        totp = pyotp.TOTP(self._temp_tfa_secret)
        if totp.verify(user_code):
            with rx.session() as session:
                user_info = session.get(UserInfo, self.authenticated_user_info.id)
                if user_info:
                    user_info.tfa_secret = encrypt_secret(self._temp_tfa_secret)
                    user_info.tfa_enabled = True
                    session.add(user_info)
                    session.commit()
                    self.set_show_tfa_activation_modal(False)
                    yield self.on_load_profile_page()
                    yield rx.toast.success("¡Autenticación de dos factores activada exitosamente!")
                else:
                    yield rx.toast.error("No se pudo encontrar el perfil del usuario.")
        else:
            yield rx.toast.error("El código de verificación es incorrecto.")

    tfa_user_id_pending_verification: Optional[int] = None

    @rx.event
    def verify_tfa_login(self, form_data: dict):
        if self.tfa_user_id_pending_verification is None:
            return rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)
        user_code = form_data.get("tfa_code")
        if not user_code or not user_code.isdigit() or len(user_code) != 6:
            return rx.toast.error("Código inválido.")
        with rx.session() as session:
            user_info = session.exec(select(UserInfo).where(UserInfo.user_id == self.tfa_user_id_pending_verification)).one_or_none()
            if not user_info or not user_info.tfa_secret:
                return rx.toast.error("Error de configuración de 2FA.")
            decrypted_secret = decrypt_secret(user_info.tfa_secret)
            if not decrypted_secret:
                return rx.toast.error("Error de seguridad: no se pudo descifrar el secreto.")
            totp = pyotp.TOTP(decrypted_secret)
            if totp.verify(user_code):
                user_id_to_login = self.tfa_user_id_pending_verification
                self.tfa_user_id_pending_verification = None
                self._login(user_id_to_login)
                return rx.redirect("/admin/store")
            else:
                return rx.toast.error("El código de verificación es incorrecto.")

    @rx.event
    def disable_tfa(self, form_data: dict):
        if not self.is_authenticated:
            return rx.toast.error("Debes iniciar sesión.")
        password = form_data.get("password")
        if not password:
            return rx.toast.error("Se requiere tu contraseña para desactivar 2FA.")
        with rx.session() as session:
            local_user = session.get(LocalUser, self.authenticated_user.id)
            if local_user and bcrypt.checkpw(password.encode("utf-8"), local_user.password_hash):
                user_info = session.get(UserInfo, self.authenticated_user_info.id)
                if user_info:
                    user_info.tfa_enabled = False
                    user_info.tfa_secret = None
                    session.add(user_info)
                    session.commit()
                    yield self.on_load_profile_page()
                    yield rx.toast.success("Autenticación de dos factores desactivada.")
            else:
                yield rx.toast.error("La contraseña es incorrecta.")
            

     # --- INICIO: NUEVAS VARIABLES PARA VENTA DIRECTA ---

    # Un carrito separado para las ventas directas del admin.
    # La clave es el identificador único del item (ej: "product_id-variant_index-Color:Rojo-Talla:M")
    # El valor es la cantidad.
    direct_sale_cart: dict[str, int] = {}

    # Almacena el ID del UserInfo del comprador seleccionado para la venta.
    direct_sale_buyer_id: Optional[int] = None

    # --- INICIO: NUEVAS VARIABLES PARA SIDEBAR DE VENTA ---
    show_direct_sale_sidebar: bool = False

    # Término de búsqueda para encontrar al comprador en la lista.
    search_query_all_buyers: str = ""

    # --- INICIO: NUEVO EVENT HANDLER ---
    def toggle_direct_sale_sidebar(self):
        """Muestra u oculta el sidebar de venta directa."""
        self.show_direct_sale_sidebar = not self.show_direct_sale_sidebar
    # --- FIN: NUEVO EVENT HANDLER ---

    @rx.var
    def direct_sale_cart_details(self) -> List[CartItemData]:
        """
        Calcula y devuelve los detalles de los items en el carrito de venta directa.
        Reutilizamos el DTO `CartItemData` que ya tienes.
        """
        # Esta lógica es muy similar a tu `cart_details` existente,
        # pero opera sobre `self.direct_sale_cart`.
        if not self.direct_sale_cart:
            return []
        with rx.session() as session:
            # Extraer IDs de producto y construir un mapa para eficiencia
            product_ids = list(set([int(key.split('-')[0]) for key in self.direct_sale_cart.keys()]))
            if not product_ids:
                return []
            results = session.exec(sqlmodel.select(BlogPostModel).where(BlogPostModel.id.in_(product_ids))).all()
            post_map = {p.id: p for p in results}
            
            cart_items_data = []
            for cart_key, quantity in self.direct_sale_cart.items():
                parts = cart_key.split('-')
                product_id = int(parts[0])
                variant_index = int(parts[1])
                post = post_map.get(product_id)
                
                if post and post.variants and 0 <= variant_index < len(post.variants):
                    variant = post.variants[variant_index]
                    selection_details = {part.split(':', 1)[0]: part.split(':', 1)[1] for part in parts[2:] if ':' in part}
                    
                    cart_items_data.append(
                        CartItemData(
                            cart_key=cart_key, product_id=product_id, variant_index=variant_index,
                            title=post.title, price=post.price, price_cop=post.price_cop,
                            image_url=variant.get("image_url", ""), quantity=quantity,
                            variant_details=selection_details
                        )
                    )
            return cart_items_data
        
    @rx.var
    def buyer_options_for_select(self) -> list[tuple[str, str]]:
        """
        [CORRECCIÓN DEFINITIVA] Prepara y filtra la lista de DTOs para el selector de comprador.
        """
        options = []
        source_users = self.managed_users # Usa la nueva lista de DTOs

        if self.search_query_all_buyers.strip():
            q = self.search_query_all_buyers.lower()
            source_users = [
                u for u in self.managed_users
                if (q in u.username.lower() or q in u.email.lower())
            ]
            
        for user in source_users:
            label = f"{user.username} ({user.email})"
            value = str(user.id)
            options.append((label, value))
                
        return options
    
    # --- INICIO: NUEVOS EVENT HANDLERS PARA VENTA DIRECTA ---

    def set_search_query_all_buyers(self, query: str):
        """Actualiza el término de búsqueda para los compradores."""
        self.search_query_all_buyers = query

    def set_direct_sale_buyer(self, user_info_id: str):
        """Establece el comprador seleccionado para la venta."""
        try:
            self.direct_sale_buyer_id = int(user_info_id)
        except (ValueError, TypeError):
            self.direct_sale_buyer_id = None

    @rx.event
    def add_to_direct_sale_cart(self, product_id: int):
        """
        Añade un producto al carrito de venta directa del administrador.

        Esta función valida que se hayan seleccionado todas las opciones
        necesarias (como talla o número), encuentra la variante de producto exacta
        que coincide con la selección, verifica su stock específico y, si hay
        disponibilidad, la añade al `direct_sale_cart`.
        """
        # 1. Validaciones iniciales de permisos y estado del modal
        if not self.is_admin:
            return rx.toast.error("Acción no permitida.")
        if not self.product_in_modal or not self.current_modal_variant:
            return rx.toast.error("Error al identificar el producto.")

        # 2. Validar que se hayan seleccionado todos los atributos requeridos
        required_keys = {selector.key for selector in self.modal_attribute_selectors}
        if not all(key in self.modal_selected_attributes for key in required_keys):
            missing = required_keys - set(self.modal_selected_attributes.keys())
            return rx.toast.error(f"Por favor, selecciona: {', '.join(missing)}")

        # 3. Encontrar la variante exacta que coincide con la selección completa
        variant_to_add = None
        # Atributos fijos de la imagen (ej: Color)
        base_attributes = self.current_variant_display_attributes
        # Atributos seleccionables (ej: Talla)
        selected_attributes = self.modal_selected_attributes
        
        # Combinamos ambos para tener la descripción completa de la variante
        full_selection = {**base_attributes, **selected_attributes}
        
        for variant in self.product_in_modal.variants:
            # Comparamos si los atributos de la variante en la BD son idénticos a la selección
            if variant.get("attributes") == full_selection:
                variant_to_add = variant
                break
        
        if not variant_to_add:
            return rx.toast.error("La combinación seleccionada no está disponible o no existe.")

        # 4. Construir la clave única para el carrito de venta directa
        # Esto asegura que "Camisa Roja Talla M" y "Camisa Roja Talla L" sean items distintos.
        selection_key_part = "-".join(sorted([f"{k}:{v}" for k, v in full_selection.items()]))
        cart_key = f"{product_id}-{self.modal_selected_variant_index}-{selection_key_part}"
        
        # 5. Verificar el stock específico de la variante encontrada
        available_stock = variant_to_add.get("stock", 0)
        quantity_in_cart = self.direct_sale_cart.get(cart_key, 0)
        
        if quantity_in_cart + 1 > available_stock:
            return rx.toast.error("¡Lo sentimos! No hay suficiente stock para esta combinación.")
        
        # 6. Si hay stock, añadir al carrito de venta directa
        self.direct_sale_cart[cart_key] = quantity_in_cart + 1
        
        # 7. Cerrar el modal y notificar al vendedor
        self.show_detail_modal = False
        return rx.toast.success("Producto añadido a la venta.")


    @rx.event
    def remove_from_direct_sale_cart(self, cart_key: str):
        """Reduce o elimina un item del carrito de venta directa."""
        if cart_key in self.direct_sale_cart:
            self.direct_sale_cart[cart_key] -= 1
            if self.direct_sale_cart[cart_key] <= 0:
                del self.direct_sale_cart[cart_key]

    @rx.event
    def handle_direct_sale_checkout(self):
        """
        Procesa y finaliza una venta directa, manejando tanto a compradores 
        registrados como anónimos. Si no se selecciona un comprador, la venta 
        se registra a nombre del propio vendedor como una venta de "mostrador".
        """
        # 1. Validaciones iniciales de permisos y estado del carrito
        if not self.is_admin or not self.authenticated_user_info:
            return rx.toast.error("No tienes permisos para realizar esta acción.")
        if not self.direct_sale_cart:
            return rx.toast.error("El carrito de venta está vacío.")

        with rx.session() as session:
            # 2. Determinar el comprador
            # Si no se ha seleccionado un comprador (`direct_sale_buyer_id` es None),
            # la venta se asocia al propio vendedor (venta anónima/invitado).
            buyer_id = self.direct_sale_buyer_id if self.direct_sale_buyer_id is not None else self.authenticated_user_info.id
            buyer_info = session.get(UserInfo, buyer_id)

            if not buyer_info or not buyer_info.user:
                return rx.toast.error("El comprador seleccionado no es válido.")

            # 3. Calcular totales y preparar la orden
            # Para ventas directas, el envío es 0 y el subtotal es el total.
            subtotal = sum(item.subtotal for item in self.direct_sale_cart_details)
            items_to_create = []

            # 4. Verificar stock y preparar los items para la base de datos
            for item in self.direct_sale_cart_details:
                post = session.get(BlogPostModel, item.product_id)
                if not post:
                    return rx.toast.error(f"El producto '{item.title}' ya no existe. Venta cancelada.")

                variant_updated = False
                for variant in post.variants:
                    # Encuentra la variante exacta que coincide con la selección
                    if variant.get("attributes") == item.variant_details:
                        if variant.get("stock", 0) < item.quantity:
                            return rx.toast.error(f"Stock insuficiente para '{item.title}'. Venta cancelada.")
                        
                        # Descuenta el stock
                        variant["stock"] -= item.quantity
                        variant_updated = True
                        break
                
                if not variant_updated:
                    return rx.toast.error(f"La variante de '{item.title}' no fue encontrada. Venta cancelada.")
                
                session.add(post)  # Marca el post para ser actualizado con el nuevo stock
                items_to_create.append(
                    PurchaseItemModel(
                        blog_post_id=item.product_id,
                        quantity=item.quantity,
                        price_at_purchase=item.price,
                        selected_variant=item.variant_details,
                    )
                )

            # 5. Crear el registro de la compra (PurchaseModel)
            now = datetime.now(timezone.utc)
            new_purchase = PurchaseModel(
                userinfo_id=buyer_info.id,
                total_price=subtotal,
                status=PurchaseStatus.DELIVERED,  # Se considera entregada inmediatamente
                payment_method="Venta Directa",
                confirmed_at=now,
                purchase_date=now,
                user_confirmed_delivery_at=now,
                shipping_applied=0,
                # Si es una venta anónima, se usa un texto genérico.
                shipping_name=buyer_info.user.username if self.direct_sale_buyer_id is not None else "Cliente Venta Directa",
                is_direct_sale=True,  # Marca esta compra como una venta directa
            )
            session.add(new_purchase)
            session.commit()
            session.refresh(new_purchase)

            # 6. Vincular los items creados con la compra recién guardada
            for purchase_item in items_to_create:
                purchase_item.purchase_id = new_purchase.id
                session.add(purchase_item)
            
            session.commit()

        # 7. Limpiar el estado de la UI y notificar el éxito
        self.direct_sale_cart.clear()
        self.direct_sale_buyer_id = None
        self.show_direct_sale_sidebar = False  # Oculta el sidebar
        
        yield rx.toast.success(f"Venta #{new_purchase.id} confirmada exitosamente.")
        yield AppState.load_purchase_history  # Actualiza el historial de ventas del vendedor

    
    @rx.var
    def direct_sale_grouped_cart(self) -> list[DirectSaleGroupDTO]:
        """
        [VERSIÓN CORREGIDA]
        Transforma el carrito plano `direct_sale_cart` en una estructura
        agrupada por producto Y POR IMAGEN, para diferenciar los colores.
        """
        if not self.direct_sale_cart_details:
            return []

        # Usaremos una tupla (product_id, image_url) como clave única para cada grupo
        grouped_products = defaultdict(lambda: {
            "product_id": 0, "title": "", "image_url": "", "subtotal": 0.0, "variants": []
        })

        for item in self.direct_sale_cart_details:
            # --- ✨ CAMBIO CLAVE: La nueva clave de agrupación --- ✨
            group_key = (item.product_id, item.image_url)
            # --- ✨ FIN DEL CAMBIO CLAVE --- ✨
            
            group = grouped_products[group_key]

            if not group["title"]:  # Si es la primera vez que vemos este grupo (producto + color)
                group["product_id"] = item.product_id
                group["title"] = item.title
                group["image_url"] = item.image_url
            
            group["subtotal"] += item.subtotal
            
            variant_attrs_str = ", ".join(
                f"{k}: {v}" for k, v in item.variant_details.items() if k != "Color"
            )
            if not variant_attrs_str:
                variant_attrs_str = "Variante única"

            group["variants"].append(
                DirectSaleVariantDTO(
                    cart_key=item.cart_key,
                    attributes_str=variant_attrs_str,
                    quantity=item.quantity
                )
            )
        
        # Convertir el diccionario a la lista final de DTOs
        final_list = []
        for key, data in grouped_products.items():
            final_list.append(
                DirectSaleGroupDTO(
                    product_id=data["product_id"],
                    title=data["title"],
                    image_url=data["image_url"],
                    subtotal_cop=format_to_cop(data["subtotal"]),
                    variants=sorted(data["variants"], key=lambda v: v.attributes_str)
                )
            )
        return sorted(final_list, key=lambda g: g.title)


    @rx.event
    def increase_direct_sale_cart_quantity(self, cart_key: str):
        """
        Aumenta la cantidad de una variante específica en el carrito de venta directa,
        verificando el stock disponible.
        """
        if cart_key not in self.direct_sale_cart:
            return

        # Lógica para extraer datos de la clave y verificar stock (muy similar a `increase_cart_quantity`)
        parts = cart_key.split('-')
        product_id = int(parts[0])
        selection_attrs = dict(part.split(':', 1) for part in parts[2:] if ':' in part)

        with rx.session() as session:
            post = session.get(BlogPostModel, product_id)
            if not post: return rx.toast.error("El producto ya no existe.")

            variant_to_check = next((v for v in post.variants if v.get("attributes") == selection_attrs), None)
            
            if not variant_to_check: return rx.toast.error("La variante ya no existe.")

            stock_disponible = variant_to_check.get("stock", 0)
            if self.direct_sale_cart[cart_key] + 1 > stock_disponible:
                return rx.toast.error("No hay más stock para esta variante.")

            self.direct_sale_cart[cart_key] += 1

    # --- FIN: NUEVOS EVENT HANDLERS ---
    
    # --- ✨ MÉTODO MODIFICADO: `get_invoice_data` ✨ ---
    @rx.event
    def get_invoice_data(self, purchase_id: int) -> Optional[InvoiceData]:
        if not self.is_authenticated:
            return None

        with rx.session() as session:
            purchase = session.exec(
                sqlmodel.select(PurchaseModel)
                .options(
                    sqlalchemy.orm.joinedload(PurchaseModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post)
                )
                .where(PurchaseModel.id == purchase_id)
            ).unique().one_or_none()

            if not purchase: return None
            if not self.is_admin and (not self.authenticated_user_info or self.authenticated_user_info.id != purchase.userinfo_id):
                return None

            subtotal_base_products = sum(item.blog_post.base_price * item.quantity for item in purchase.items if item.blog_post)
            shipping_cost = purchase.shipping_applied or 0.0
            iva_amount = subtotal_base_products * 0.19
            
            invoice_items = []
            for item in purchase.items:
                if item.blog_post:
                    item_base_subtotal = item.blog_post.base_price * item.quantity
                    item_iva = item_base_subtotal * 0.19
                    item_total_con_iva = item_base_subtotal + item_iva

                    # --- LÓGICA AÑADIDA: Formatear detalles de la variante para la factura ---
                    variant_str = ", ".join([f"{k}: {v}" for k,v in item.selected_variant.items()])

                    invoice_items.append(
                        InvoiceItemData(
                            name=item.blog_post.title,
                            quantity=item.quantity,
                            price=item.blog_post.base_price,
                            price_cop=format_to_cop(item.blog_post.base_price),
                            subtotal_cop=format_to_cop(item_base_subtotal),
                            iva_cop=format_to_cop(item_iva),
                            total_con_iva_cop=format_to_cop(item_total_con_iva),
                            # Se pasa la cadena formateada al DTO
                            variant_details_str=variant_str
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
                total_price_cop=format_to_cop(purchase.total_price),
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

    # --- 👇 AÑADE ESTAS LÍNEAS NUEVAS --- 👇
    temp_talla: str = ""
    temp_numero: str = ""
    temp_tamano: str = ""

    def set_temp_talla(self, talla: str):
        self.temp_talla = talla
    
    def set_temp_numero(self, numero: str):
        self.temp_numero = numero
        
    def set_temp_tamano(self, tamano: str):
        self.temp_tamano = tamano
    # --- FIN DE LAS LÍNEAS NUEVAS ---

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
    
    def set_search_query_users(self, query: str):
        self.search_query_users = query

    # --- AÑADE ESTA NUEVA VARIABLE DE ESTADO ---
    solicitudes_de_empleo_enviadas: list[EmploymentRequest] = []

    @rx.var
    def filtered_solicitudes_enviadas(self) -> list[EmploymentRequest]:
        """Filtra el historial de solicitudes enviadas por nombre de candidato."""
        if not self.search_query_sent_requests.strip():
            return self.solicitudes_de_empleo_enviadas

        query = self.search_query_sent_requests.lower()
        return [
            req for req in self.solicitudes_de_empleo_enviadas
            if req.candidate and req.candidate.user and query in req.candidate.user.username.lower()
        ]
    
    # Almacenará los datos crudos de la BD
    _solicitudes_de_empleo_enviadas: list[EmploymentRequest] = []

    # Variables para los filtros del historial
    search_query_sent_requests: str = ""
    request_history_start_date: str = ""
    request_history_end_date: str = ""

    def set_search_query_sent_requests(self, query: str):
        self.search_query_sent_requests = query

    def set_request_history_start_date(self, date: str):
        self.request_history_start_date = date

    def set_request_history_end_date(self, date: str):
        self.request_history_end_date = date

    # --- REEMPLAZA LA FUNCIÓN `load_empleados` ---
    @rx.event
    def load_empleados(self):
        """Carga empleados, historial de solicitudes y el nuevo historial de actividad."""
        if not (self.is_vendedor or self.is_admin or self.is_empleado):
            return

        user_id_to_check = self.context_user_id if self.is_vigilando else (self.authenticated_user_info.id if self.authenticated_user_info else None)
        if not user_id_to_check:
            return

        with rx.session() as session:
            links = session.exec(
                sqlmodel.select(EmpleadoVendedorLink)
                .options(sqlalchemy.orm.joinedload(EmpleadoVendedorLink.empleado).joinedload(UserInfo.user))
                .where(EmpleadoVendedorLink.vendedor_id == user_id_to_check)
            ).all()
            self.empleados = [link.empleado for link in links if link.empleado and link.empleado.user]

            self._solicitudes_de_empleo_enviadas = session.exec(
                sqlmodel.select(EmploymentRequest)
                .options(sqlalchemy.orm.joinedload(EmploymentRequest.candidate).joinedload(UserInfo.user))
                .where(EmploymentRequest.requester_id == user_id_to_check)
                .order_by(sqlmodel.desc(EmploymentRequest.created_at))
            ).all()

        # --- ✨ CORRECCIÓN CLAVE: Se llama al evento sin paréntesis ✨ ---
        yield AppState.load_employee_activity

    @rx.var
    def filtered_solicitudes_enviadas(self) -> list[SentRequestDTO]:
        """Filtra el historial por nombre y rango de fechas, y lo convierte a DTOs."""
        solicitudes = self._solicitudes_de_empleo_enviadas

        # Filtrar por nombre
        if self.search_query_sent_requests.strip():
            query = self.search_query_sent_requests.lower()
            solicitudes = [
                req for req in solicitudes
                if req.candidate and req.candidate.user and query in req.candidate.user.username.lower()
            ]

        # Filtrar por fecha de inicio
        if self.request_history_start_date:
            try:
                start_dt = datetime.fromisoformat(self.request_history_start_date).replace(tzinfo=pytz.UTC)
                solicitudes = [req for req in solicitudes if req.created_at.replace(tzinfo=pytz.UTC) >= start_dt]
            except ValueError:
                pass # Ignora fechas inválidas

        # Filtrar por fecha de fin
        if self.request_history_end_date:
            try:
                end_dt = datetime.fromisoformat(self.request_history_end_date).replace(tzinfo=pytz.UTC)
                # Añadimos un día para que el filtro incluya el día final completo
                end_dt_inclusive = end_dt + timedelta(days=1)
                solicitudes = [req for req in solicitudes if req.created_at.replace(tzinfo=pytz.UTC) < end_dt_inclusive]
            except ValueError:
                pass # Ignora fechas inválidas

        # Convertir los resultados filtrados a DTOs para la UI
        return [
            SentRequestDTO(
                id=req.id,
                status=req.status.value,
                candidate_name=req.candidate.user.username if req.candidate and req.candidate.user else "N/A",
                created_at_formatted=req.created_at_formatted,
                created_at=req.created_at
            ) for req in solicitudes
        ]

    @rx.event
    def search_users_for_employment(self):
        """
        [CORREGIDO] Busca usuarios que puedan ser contratados,
        incluyendo ahora tanto a Clientes como a otros Vendedores.
        """
        self.search_results_users = []
        query = self.search_query_users.strip()
        if not query:
            return rx.toast.info("Introduce un nombre de usuario o email para buscar.")

        with rx.session() as session:
            # Subconsulta para encontrar IDs de usuarios que ya son empleados de alguien
            subquery = sqlmodel.select(EmpleadoVendedorLink.empleado_id)
            
            results = session.exec(
                sqlmodel.select(UserInfo)
                .join(LocalUser)
                .where(
                    # --- ¡CORRECCIÓN CLAVE! ---
                    # Ahora busca usuarios cuyo rol sea CUSTOMER O VENDEDOR
                    UserInfo.role.in_([UserRole.CUSTOMER, UserRole.VENDEDOR]),
                    
                    # Excluye a los que ya son empleados
                    UserInfo.id.notin_(subquery),
                    
                    # Condición de búsqueda por nombre o email
                    (LocalUser.username.ilike(f"%{query}%")) | (UserInfo.email.ilike(f"%{query}%"))
                )
            ).all()
            self.search_results_users = results

    @rx.event
    def add_empleado(self, empleado_userinfo_id: int):
        """Vincula un usuario como empleado del vendedor en contexto."""
        if not self.context_user_id:
            return rx.toast.error("Error de contexto.")

        with rx.session() as session:
            # Doble verificación para asegurar que el usuario no sea ya un empleado
            existing_link = session.exec(
                sqlmodel.select(EmpleadoVendedorLink).where(EmpleadoVendedorLink.empleado_id == empleado_userinfo_id)
            ).first()
            if existing_link:
                return rx.toast.error("Este usuario ya es empleado de otro vendedor.")
            
            new_link = EmpleadoVendedorLink(
                vendedor_id=self.context_user_id,
                empleado_id=empleado_userinfo_id
            )
            session.add(new_link)
            session.commit()
            
            yield self.load_empleados()
            yield rx.toast.success("Empleado añadido correctamente.")

    @rx.event
    def remove_empleado(self, empleado_userinfo_id: int):
        """
        [CORREGIDO] Elimina la vinculación de un empleado. Ahora funciona tanto si la
        inicia el vendedor como si la inicia el propio empleado.
        """
        if not self.authenticated_user_info:
            return rx.toast.error("Debes iniciar sesión.")

        with rx.session() as session:
            # Buscamos el enlace donde el usuario a desvincular es el empleado.
            link_to_delete = session.exec(
                sqlmodel.select(EmpleadoVendedorLink).where(
                    EmpleadoVendedorLink.empleado_id == empleado_userinfo_id
                )
            ).one_or_none()

            if not link_to_delete:
                return rx.toast.error("No se encontró la relación de empleado.")

            # Verificamos los permisos: la acción la puede hacer el vendedor o el propio empleado.
            is_vendedor_del_empleado = self.authenticated_user_info.id == link_to_delete.vendedor_id
            is_el_propio_empleado = self.authenticated_user_info.id == empleado_userinfo_id

            if not is_vendedor_del_empleado and not is_el_propio_empleado:
                return rx.toast.error("No tienes permisos para realizar esta acción.")

            session.delete(link_to_delete)
            session.commit()
            
            # Si el que se desvincula es el propio empleado, recargamos su página
            if is_el_propio_empleado:
                yield rx.toast.info("Has dejado de ser empleado.")
                yield rx.call_script("window.location.reload()")
            else: # Si fue el vendedor, solo actualizamos su lista
                yield self.load_empleados()
                yield rx.toast.info("Empleado desvinculado correctamente.")
    
    # --- ✨ INICIO: AÑADE ESTA NUEVA FUNCIÓN ✨ ---
    @rx.event
    def leave_employment(self):
        """
        Permite que un empleado se desvincule de su empleador.
        Llama a la función `remove_empleado` pasándose a sí mismo como argumento.
        """
        if not self.is_empleado or not self.authenticated_user_info:
            return rx.toast.error("Esta acción no es válida.")
        
        # Llama a la lógica principal de desvinculación
        yield from self.remove_empleado(self.authenticated_user_info.id)
    # --- ✨ FIN: NUEVA FUNCIÓN ✨ ---


    @rx.event
    def start_vigilancia(self, vendedor_userinfo_id: int):
        """Inicia el modo de vigilancia para un administrador."""
        if not self.is_admin:
            return rx.toast.error("Acción no permitida.")
            
        self.original_admin_id = self.authenticated_user_info.id
        self.context_user_id = vendedor_userinfo_id
        self.is_vigilando = True
        
        yield rx.toast.info(f"Iniciando modo de vigilancia.")
        yield rx.redirect("/admin/finance")

    @rx.event
    def stop_vigilancia(self):
        """Detiene el modo de vigilancia y restaura el contexto del administrador."""
        if not self.is_admin or not self.original_admin_id:
            return
            
        self.context_user_id = self.original_admin_id
        self.is_vigilando = False
        self.original_admin_id = None
        
        yield rx.toast.info("Modo de vigilancia finalizado.")
        yield rx.redirect("/admin/users")

    search_query_all_users: str = ""

    def set_search_query_all_users(self, query: str):
        """Actualiza el término de búsqueda para la tabla de gestión de usuarios."""
        self.search_query_all_users = query

    # --- 2. PROPIEDAD COMPUTADA PARA FILTRAR USUARIOS ---
    # REEMPLAZA las propiedades computadas que causaban el error
    @rx.var
    def filtered_all_users(self) -> list[UserManagementDTO]:
        """Filtra la lista de DTOs de usuarios según la barra de búsqueda."""
        if not self.search_query_all_users.strip():
            return self.managed_users
        
        query = self.search_query_all_users.lower()
        return [
            u for u in self.managed_users
            if (query in u.username.lower() or query in u.email.lower())
        ]

    # --- 3. NUEVO MANEJADOR DE EVENTOS PARA CAMBIAR ROL DE VENDEDOR ---
    @rx.event
    def toggle_vendedor_role(self, userinfo_id: int):
        """[CORRECCIÓN DEFINITIVA] Cambia el rol de un usuario y actualiza la lista de DTOs."""
        if not self.is_admin:
            return rx.toast.error("No tienes permisos.")

        with rx.session() as session:
            user_info = session.get(UserInfo, userinfo_id)
            if user_info and user_info.user:
                if user_info.id == self.authenticated_user_info.id:
                    return rx.toast.warning("No puedes cambiar tu propio rol.")
                
                new_role = UserRole.CUSTOMER if user_info.role == UserRole.VENDEDOR else UserRole.VENDEDOR
                if user_info.role in [UserRole.CUSTOMER, UserRole.VENDEDOR]:
                    user_info.role = new_role
                    session.add(user_info)
                    session.commit()

                    # Actualiza el DTO en la lista del estado, en lugar de recargar todo
                    for i, u in enumerate(self.managed_users):
                        if u.id == userinfo_id:
                            self.managed_users[i].role = new_role
                            break
                    
                    toast_message = f"{user_info.user.username} ahora es un {new_role.value.capitalize()}."
                    return rx.toast.info(toast_message)
                else:
                    return rx.toast.error("Solo se puede alternar el rol entre Cliente y Vendedor.")



    # --- 4. NUEVO MANEJADOR PARA POLLING DE ROL (Redirección automática) ---
    @rx.event
    def poll_user_role(self):
        """
        Verifica periódicamente el rol del usuario actual en la base de datos.
        Si ha cambiado, fuerza una recarga de la página para actualizar la interfaz.
        """
        if not self.is_authenticated or not self.authenticated_user_info:
            return

        with rx.session() as session:
            # Obtiene el rol más reciente del usuario desde la base de datos
            db_user_role = session.exec(
                sqlmodel.select(UserInfo.role).where(UserInfo.id == self.authenticated_user_info.id)
            ).one_or_none()

            # Compara el rol de la BD con el rol que está en el estado actual de la app
            if db_user_role and db_user_role != self.authenticated_user_info.role:
                # Si son diferentes, significa que un admin cambió el rol.
                # Forzamos una recarga completa de la página.
                yield rx.toast.info("Tu rol ha sido actualizado. Redirigiendo...")
                yield rx.reload()

    # Variables de estado para el nuevo historial
    _activity_logs: list[ActivityLogDTO] = []
    activity_search_query: str = ""
    activity_start_date: str = ""
    activity_end_date: str = ""

    def set_activity_search_query(self, query: str):
        self.activity_search_query = query
    def set_activity_start_date(self, date: str):
        self.activity_start_date = date
    def set_activity_end_date(self, date: str):
        self.activity_end_date = date

    @rx.event
    def load_employee_activity(self):
        """Carga el historial de actividad para el vendedor en contexto."""
        user_id_to_check = self.context_user_id or (self.authenticated_user_info.id if self.authenticated_user_info else None)
        if not user_id_to_check:
            return

        with rx.session() as session:
            logs_db = session.exec(
                sqlmodel.select(ActivityLog)
                .options(sqlalchemy.orm.joinedload(ActivityLog.actor).joinedload(UserInfo.user))
                .where(ActivityLog.owner_id == user_id_to_check)
                .order_by(sqlmodel.desc(ActivityLog.created_at))
                .limit(100)
            ).all()

            self._activity_logs = [
                ActivityLogDTO(
                    id=log.id,
                    actor_name=log.actor.user.username if log.actor and log.actor.user else "N/A",
                    action_type=log.action_type,
                    description=log.description,
                    created_at_formatted=log.created_at_formatted,
                    # --- ✨ AÑADE ESTA LÍNEA PARA GUARDAR LA FECHA ORIGINAL ✨ ---
                    created_at=log.created_at
                ) for log in logs_db
            ]


    @rx.var
    def filtered_employee_activity(self) -> list[ActivityLogDTO]:
        """Filtra el historial de actividad por búsqueda de texto y rango de fechas."""
        logs = self._activity_logs
        
        # 1. Filtrado por texto de búsqueda (nombre, descripción o tipo de acción)
        if self.activity_search_query.strip():
            query = self.activity_search_query.lower()
            logs = [
                log for log in logs
                if query in log.actor_name.lower() 
                or query in log.description.lower() 
                or query in log.action_type.lower()
            ]

        # 2. Filtrado por fecha de inicio
        if self.activity_start_date:
            try:
                # Convertimos la fecha del filtro a un objeto datetime consciente de la zona horaria
                start_dt = datetime.fromisoformat(self.activity_start_date).replace(tzinfo=pytz.UTC)
                # Comparamos con la fecha original del registro
                logs = [log for log in logs if log.created_at.replace(tzinfo=pytz.UTC) >= start_dt]
            except ValueError:
                pass # Ignora fechas con formato incorrecto

        # 3. Filtrado por fecha de fin
        if self.activity_end_date:
            try:
                # Convertimos la fecha del filtro a un objeto datetime
                end_dt = datetime.fromisoformat(self.activity_end_date).replace(tzinfo=pytz.UTC)
                # Añadimos un día para que el filtro incluya el día final completo (hasta las 23:59:59)
                end_dt_inclusive = end_dt + timedelta(days=1)
                # Comparamos que la fecha del registro sea MENOR que el inicio del día siguiente
                logs = [log for log in logs if log.created_at.replace(tzinfo=pytz.UTC) < end_dt_inclusive]
            except ValueError:
                pass # Ignora fechas con formato incorrecto
        
        return logs

    @rx.event
    def submit_and_publish(self, form_data: dict):
        """
        [CORREGIDO] Manejador para crear y publicar un nuevo producto, con lógica de
        contexto robusta que funciona tanto para vendedores como para empleados.
        """
        owner_id = None
        creator_id_to_save = None

        # --- ✨ Lógica de contexto robusta ✨ ---
        if not self.authenticated_user_info:
            return rx.toast.error("Error de sesión. No se puede publicar.")

        if self.is_empleado:
            if not self.mi_vendedor_info:
                return rx.toast.error("Error de contexto: No se pudo encontrar al empleador.")
            owner_id = self.mi_vendedor_info.id
            creator_id_to_save = self.authenticated_user_info.id
        else: # Si es un Vendedor o Admin publicando para sí mismo
            owner_id = self.authenticated_user_info.id
        
        if not owner_id:
            return rx.toast.error("Error de sesión o contexto no válido. No se puede publicar.")
        # --- ✨ FIN DE LA CORRECCIÓN ✨ ---

        # 2. Extraer y validar los datos del formulario
        title = form_data.get("title", "").strip()
        price_str = form_data.get("price", "")
        category = form_data.get("category", "")
        content = form_data.get("content", "")
        profit_str = form_data.get("profit", "")
        shipping_cost_str = form_data.get("shipping_cost", "")
        limit_str = form_data.get("shipping_combination_limit", "3")

        if not all([title, price_str, category]):
            return rx.toast.error("El título, el precio y la categoría son campos obligatorios.")

        if not self.generated_variants_map:
            return rx.toast.error("Debes generar y configurar las variantes (stock, etc.) para al menos una imagen antes de publicar.")

        try:
            price_float = float(price_str)
            profit_float = float(profit_str) if profit_str else None
            shipping_cost = float(shipping_cost_str) if shipping_cost_str else None
            limit = int(limit_str) if self.combines_shipping and limit_str else None
            
            if self.combines_shipping and (limit is None or limit <= 0):
                return rx.toast.error("El límite para envío combinado debe ser un número mayor a 0.")
        except (ValueError, TypeError):
            return rx.toast.error("Precio, ganancia, costo de envío y límites deben ser números válidos.")

        # 3. Construir la lista final de variantes para la base de datos
        all_variants_for_db = []
        for index, generated_list in self.generated_variants_map.items():
            # La URL de la imagen principal del grupo
            main_image_url_for_group = self.new_variants[index].get("image_url", "")
            for variant_data in generated_list:
                variant_dict = {
                    "attributes": variant_data.attributes,
                    "stock": variant_data.stock,
                    # Usa la imagen asignada a la variante, o la del grupo como fallback
                    "image_url": variant_data.image_url or main_image_url_for_group,
                    "variant_uuid": str(uuid.uuid4()) # Asigna un ID único a cada variante
                }
                all_variants_for_db.append(variant_dict)

        if not all_variants_for_db:
            return rx.toast.error("No se encontraron variantes configuradas para guardar.")

        # 4. Crear y guardar el nuevo producto en la base de datos
        with rx.session() as session:
            new_post = BlogPostModel(
                userinfo_id=owner_id,          # ID del Vendedor (dueño)
                creator_id=creator_id_to_save, # ID del Empleado (si aplica) o None
                title=title,
                content=content,
                price=price_float,
                profit=profit_float,
                price_includes_iva=self.price_includes_iva,
                category=category,
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

            # --- ✨ AÑADIR REGISTRO DE ACTIVIDAD ✨ ---
            log_entry = ActivityLog(
                actor_id=self.authenticated_user_info.id,
                owner_id=owner_id,
                action_type="Creación de Publicación",
                description=f"Creó la publicación '{new_post.title}'"
            )
            session.add(log_entry)
            # --- ✨ FIN DEL REGISTRO ✨ ---

            session.commit()

        # 5. Limpiar el formulario y redirigir
        self._clear_add_form() # Asegúrate de tener esta función para limpiar el estado del form
        yield rx.toast.success("Producto publicado exitosamente.")
        yield rx.redirect("/blog")
    
    @rx.event
    def remove_add_image(self, index: int):
        """
        Elimina una imagen y sus datos asociados del formulario para AÑADIR productos.
        """
        if 0 <= index < len(self.new_variants):
            # Elimina la variante (que contiene la imagen) de la lista principal
            self.new_variants.pop(index)
            
            # Si había un mapa de variantes generado para esta imagen, lo eliminamos
            if index in self.generated_variants_map:
                del self.generated_variants_map[index]
            
            # Reajusta el índice de la imagen seleccionada si es necesario
            if self.selected_variant_index == index:
                # Si se eliminó la imagen seleccionada, deseleccionamos
                self.selected_variant_index = -1
            elif self.selected_variant_index > index:
                # Si se eliminó una imagen anterior a la seleccionada, ajustamos el índice
                self.selected_variant_index -= 1
            
            yield rx.toast.info("Imagen eliminada del formulario.")
    
    @rx.var
    def displayed_posts(self) -> list[ProductCardData]:
        """
        [VERSIÓN COMPLETA Y CORREGIDA]
        Variable computada que filtra y busca en tiempo real.
        Es la única fuente de verdad para la galería de productos.
        """
        # Se inicia con la lista completa de todos los posts
        source_posts = self.posts

        # 1. APLICA LA BÚSQUEDA EN TIEMPO REAL
        # Si hay algo escrito en la barra de búsqueda, se filtra la lista primero por el título.
        if self.search_term.strip():
            query = self.search_term.strip().lower()
            source_posts = [
                p for p in source_posts if query in p.title.lower()
            ]

        # 2. APLICA LOS FILTROS DEL PANEL LATERAL
        # El resto de la lógica de filtrado se aplica sobre la lista
        # que ya ha sido (o no) acotada por la búsqueda.
        posts_to_filter = source_posts
        
        # Filtro por Rango de Precios
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

        # Filtro por Colores
        if self.filter_colors:
            posts_to_filter = [
                p for p in posts_to_filter 
                if p.attributes.get("Color") in self.filter_colors
            ]

        # Filtro por Material o Tela
        if self.filter_materiales_tela:
            posts_to_filter = [
                p for p in posts_to_filter 
                if (p.attributes.get("Material") in self.filter_materiales_tela) or 
                   (p.attributes.get("Tela") in self.filter_materiales_tela)
            ]

        # Filtro por Tallas
        if self.filter_tallas:
            posts_to_filter = [
                p for p in posts_to_filter
                if any(
                    size in self.filter_tallas 
                    for size in p.attributes.get("Talla", [])
                )
            ]

        # Filtro por Tipo de Prenda/Calzado (General)
        if self.filter_tipos_general:
            posts_to_filter = [
                p for p in posts_to_filter
                if p.attributes.get("Tipo") in self.filter_tipos_general
            ]

        # Filtro de Envío Gratis
        if self.filter_free_shipping:
            posts_to_filter = [
                p for p in posts_to_filter 
                if p.shipping_cost == 0.0
            ]

        # Filtro de Moda Completa
        if self.filter_complete_fashion:
            posts_to_filter = [
                p for p in posts_to_filter 
                if p.is_moda_completa_eligible
            ]

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
    
    show_qr_scanner_modal: bool = False

    def toggle_qr_scanner_modal(self):
        self.show_qr_scanner_modal = not self.show_qr_scanner_modal

    def set_show_qr_scanner_modal(self, state: bool):
        self.show_qr_scanner_modal = state

    # --- INICIO: SECCIÓN PARA EL MODAL DE VISUALIZACIÓN DE QR ---

    # Variable para controlar la visibilidad del modal de visualización de QR
    show_qr_display_modal: bool = False

    # Variable para almacenar los datos del post cuyos QR se están mostrando
    post_for_qr_display: Optional[AdminPostRowData] = None

    @rx.event
    def open_qr_modal(self, post_id: int):
        """
        Busca un post por su ID y lo carga en el estado para mostrar sus QR en el modal.
        """
        # Buscamos el post en la lista que ya tenemos cargada en el estado
        post_data = next((p for p in self.my_admin_posts if p.id == post_id), None)
        
        if post_data:
            self.post_for_qr_display = post_data
            self.show_qr_display_modal = True
        else:
            return rx.toast.error("No se pudo encontrar la publicación.")

    def set_show_qr_display_modal(self, state: bool):
        """Controla la apertura y cierre del modal desde la UI."""
        self.show_qr_display_modal = state
        if not state:
            self.post_for_qr_display = None # Limpia el estado al cerrar

    # --- FIN DE LA SECCIÓN PARA EL MODAL DE VISUALIZACIÓN DE QR --

    @rx.event
    def handle_qr_scan_success(self, decoded_text: str):
        self.last_scanned_url = decoded_text  # Guardar para depuración
    
        if not decoded_text or "variant_uuid=" not in decoded_text:
            return rx.toast.error("El código QR no es válido para esta aplicación.")
        
        try:
            parsed_url = urlparse(decoded_text)
            query_params = parse_qs(parsed_url.query)
            variant_uuid = query_params.get("variant_uuid", [None])[0]
        except Exception:
            return rx.toast.error("URL malformada en el código QR.")

        if not variant_uuid:
            return rx.toast.error("No se encontró un identificador de producto en el QR.")
        
        # Reutilizar la lógica de búsqueda ya existente en AppState
        result = self.find_variant_by_uuid(variant_uuid)
        
        if not result:
            return rx.toast.error("Producto no encontrado para este código QR.")
        
        post, variant = result
        
        attributes = variant.get("attributes", {})
        selection_key_part = "-".join(sorted([f"{k}:{v}" for k, v in attributes.items()]))
        variant_index = next((i for i, v in enumerate(post.variants) if v.get("variant_uuid") == variant_uuid), -1)

        if variant_index == -1:
            return rx.toast.error("Error de consistencia de datos de la variante.")

        cart_key = f"{post.id}-{variant_index}-{selection_key_part}"
        
        available_stock = variant.get("stock", 0)
        quantity_in_cart = self.direct_sale_cart.get(cart_key, 0)
        
        if quantity_in_cart + 1 > available_stock:
            yield rx.toast.error(f"¡Sin stock para '{post.title}'!")
        else:
            self.direct_sale_cart[cart_key] = quantity_in_cart + 1
            yield rx.toast.success(f"'{post.title}' añadido a la Venta Directa.")
            self.show_qr_scanner_modal = False

    # --- Añade estas nuevas variables de estado ---
    show_public_qr_scanner_modal: bool = False

    def toggle_public_qr_scanner_modal(self):
        """Muestra u oculta el modal del escáner QR público."""
        self.show_public_qr_scanner_modal = not self.show_public_qr_scanner_modal

    def set_show_public_qr_scanner_modal(self, state: bool):
        self.show_public_qr_scanner_modal = state

    # --- Añade este nuevo manejador de eventos ---
    async def handle_public_qr_scan(self, files: list[rx.UploadFile]):
        """
        Manejador para el escáner público. Decodifica el QR y abre el modal del producto.
        """
        if not files:
            yield rx.toast.error("No se ha subido ningún archivo.")
            return

        self.show_public_qr_scanner_modal = False

        try:
            upload_data = await files[0].read()
            decoded_url = self._decode_qr_from_image(upload_data)

            if not decoded_url:
                yield rx.toast.error("No se pudo leer el código QR.", duration=6000)
                return

            if "variant_uuid=" not in decoded_url:
                yield rx.toast.error("El código QR no es válido.")
                return

            parsed_url = urlparse(decoded_url)
            query_params = parse_qs(parsed_url.query)
            variant_uuid = query_params.get("variant_uuid", [None])[0]

            if not variant_uuid:
                yield rx.toast.error("QR sin identificador de producto.")
                return

            result = self.find_variant_by_uuid(variant_uuid)

            if not result:
                yield rx.toast.error("Producto no encontrado para este código QR.")
                return

            post, _ = result
            # En lugar de añadir al carrito, llamamos al evento que abre el modal
            yield AppState.open_product_detail_modal(post.id)

        except Exception as e:
            logger.error(f"Error fatal al procesar el QR público: {e}")
            yield rx.toast.error("Ocurrió un error inesperado al procesar la imagen.")

    # --- Manejador para errores de la cámara ---
    @rx.event
    def handle_camera_error(self, error_message: str):
        """ Se ejecuta si la cámara no se puede iniciar o hay un error. """
        self.show_qr_scanner_modal = False   # Cierra el modal si hay un error
        return rx.toast.error(f"Error de cámara: {error_message}", duration=6000)

    @rx.event
    def open_qr_modal(self, post_id: int):
        """
        Busca un post por su ID y lo carga en el estado para mostrar sus QR en el modal.
        """
        # Buscamos el post en la lista que ya tenemos cargada en el estado
        post_data = next((p for p in self.my_admin_posts if p.id == post_id), None)
        
        if post_data:
            self.post_for_qr_display = post_data
            self.show_qr_display_modal = True
        else:
            return rx.toast.error("No se pudo encontrar la publicación.")

    def set_show_qr_display_modal(self, state: bool):
        """Controla la apertura y cierre del modal desde la UI."""
        self.show_qr_display_modal = state
        if not state:
            self.post_for_qr_display = None # Limpia el estado al cerrar

    # --- FIN DE LA SECCIÓN PARA EL MODAL DE QR ---

    # 1. La variable para el término de búsqueda de la tienda de administración.
    search_term: str = ""

    # 2. La función para actualizar la variable (setter).
    def set_search_term(self, term: str):
        self.search_term = term

    # --- FUNCIÓN DE BÚSQUEDA (DEBE ESTAR ASÍ) ---
    def find_variant_by_uuid(self, uuid_to_find: str) -> Optional[Tuple[BlogPostModel, dict]]:
        """
        Busca un producto y su variante específica usando un variant_uuid.
        Utiliza una consulta optimizada con el operador de contención (@>) de JSONB
        y un índice GIN para un rendimiento máximo.
        """
        with rx.session() as session:
            containment_payload = [{"variant_uuid": uuid_to_find}]

            # Se usa cast() para la conversión a JSONB, compatible con tu entorno
            post = session.exec(
                sqlmodel.select(BlogPostModel).where(
                    BlogPostModel.variants.op("@>")(cast(containment_payload, JSONB))
                )
            ).first()

            if not post:
                return None

            for variant in post.variants:
                if variant.get("variant_uuid") == uuid_to_find:
                    return post, variant

            return None

    # --- REEMPLAZA TU FUNCIÓN process_qr_url_on_load POR ESTA ---
    @rx.event
    def process_qr_url_on_load(self):
        """
        Se ejecuta al cargar /admin/store, procesa el variant_uuid de la URL,
        añade el item al carrito de venta directa y limpia la URL para evitar re-adiciones.
        """
        full_url = ""
        try:
            full_url = self.router.url
        except Exception:
            return

        if not full_url or "variant_uuid=" not in full_url:
            return

        try:
            parsed_url = urlparse(full_url)
            query_params = parse_qs(parsed_url.query)
            variant_uuid = query_params.get("variant_uuid", [None])[0]
        except Exception:
            return

        if not variant_uuid:
            return

        result = self.find_variant_by_uuid(variant_uuid)

        if not result:
            yield rx.toast.error("Código QR no válido o producto no encontrado.")
            return rx.redirect("/admin/store")

        post, variant = result
        attributes = variant.get("attributes", {})
        selection_key_part = "-".join(sorted([f"{k}:{v}" for k, v in attributes.items()]))
        variant_index = next((i for i, v in enumerate(post.variants) if v.get("variant_uuid") == variant_uuid), -1)

        if variant_index == -1:
            yield rx.toast.error("Error de consistencia de datos.")
            return rx.redirect("/admin/store")

        cart_key = f"{post.id}-{variant_index}-{selection_key_part}"
        available_stock = variant.get("stock", 0)
        quantity_in_cart = self.direct_sale_cart.get(cart_key, 0)

        if quantity_in_cart + 1 > available_stock:
            yield rx.toast.error(f"¡Sin stock! No quedan unidades de '{post.title}'.")
        else:
            self.direct_sale_cart[cart_key] = quantity_in_cart + 1
            yield rx.toast.success(f"'{post.title}' añadido a la Venta Directa.")

        return rx.redirect("/admin/store")
    

    
    # --- AÑADE ESTA PRIMERA NUEVA FUNCIÓN ---
    @rx.event
    def handle_public_qr_load(self, variant_uuid: str):
        """
        Manejador que recibe un UUID, busca el producto y RETORNA
        el evento para abrir el modal. No usa yield para evitar el error.
        """
        result = self.find_variant_by_uuid(variant_uuid)
        
        if result:
            post, variant = result
            # En lugar de usar 'yield', ahora simplemente retornamos el siguiente
            # evento que Reflex debe ejecutar.
            return AppState.open_product_detail_modal(post.id)
        else:
            # También retornamos el evento de notificación de error.
            return rx.toast.error("El producto del código QR no fue encontrado.")
        
    # --- 2. AÑADIR LA FUNCIÓN DE UTILIDAD PARA DECODIFICAR ---
    def _decode_qr_from_image(self, image_bytes: bytes) -> Optional[str]:
        """
        [VERSIÓN MEJORADA CON PIPELINE INTELIGENTE]
        Utiliza OpenCV para decodificar un QR, aplicando una secuencia de técnicas de
        mejora de imagen para aumentar la tasa de éxito en fotos imperfectas.
        """
        try:
            # 1. Cargar la imagen desde los bytes en memoria
            np_arr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if image is None:
                logger.error("No se pudo decodificar el buffer de la imagen con OpenCV.")
                return None

            detector = cv2.QRCodeDetector()

            # --- INICIO DE LA CASCADA DE PROCESAMIENTO ---

            # ETAPA 1: Intento con la imagen original (el más rápido)
            logger.info("Intento de decodificación QR - Etapa 1: Imagen Original")
            decoded_text, points, _ = detector.detectAndDecode(image)
            if points is not None and decoded_text:
                logger.info("ÉXITO en Etapa 1.")
                return decoded_text

            # ETAPA 2: Conversión a escala de grises
            logger.info("Intento de decodificación QR - Etapa 2: Escala de grises")
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            decoded_text, points, _ = detector.detectAndDecode(gray_image)
            if points is not None and decoded_text:
                logger.info("ÉXITO en Etapa 2.")
                return decoded_text

            # ETAPA 3: Umbral adaptativo (muy potente para sombras y brillos)
            logger.info("Intento de decodificación QR - Etapa 3: Umbral Adaptativo")
            thresh_image = cv2.adaptiveThreshold(
                gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            decoded_text, points, _ = detector.detectAndDecode(thresh_image)
            if points is not None and decoded_text:
                logger.info("ÉXITO en Etapa 3.")
                return decoded_text
            
            # ETAPA 4: Desenfoque ligero + Umbral (para eliminar ruido)
            logger.info("Intento de decodificación QR - Etapa 4: Desenfoque + Umbral")
            blur_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
            thresh_blur_image = cv2.adaptiveThreshold(
                blur_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            decoded_text, points, _ = detector.detectAndDecode(thresh_blur_image)
            if points is not None and decoded_text:
                logger.info("ÉXITO en Etapa 4.")
                return decoded_text

            logger.error("El QR no pudo ser detectado después de todas las etapas de pre-procesamiento.")
            return None

        except Exception as e:
            logger.error(f"Error fatal durante la decodificación del QR: {e}")
            return None
        
    # --- INICIA EL NUEVO BLOQUE DE CÓDIGO ---

    def _apply_clahe_color(self, image):
        """Aplica mejora de contraste a una imagen a color sin distorsionar los colores."""
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    def _unsharp_mask(self, image, sigma=1.0, strength=1.5):
        """Aplica un filtro de nitidez para corregir desenfoques leves."""
        blurred = cv2.GaussianBlur(image, (0, 0), sigma)
        return cv2.addWeighted(image, 1.0 + strength, blurred, -strength, 0)

    def _apply_morphological_cleanup(self, binary_image):
        """Elimina ruido y pequeños imperfectos de la imagen binarizada."""
        kernel = np.ones((3, 3), np.uint8)
        # Elimina ruido blanco (puntos pequeños)
        opened = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, kernel)
        # Rellena agujeros negros dentro del QR
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
        return closed

    def _decode_qr_from_image(self, image_bytes: bytes) -> Optional[str]:
        """
        [VERSIÓN 2.0 - MÁS INTELIGENTE]
        Utiliza OpenCV con un pipeline secuencial y robusto de técnicas de mejora de imagen.
        """
        try:
            np_arr = np.frombuffer(image_bytes, np.uint8)
            image_orig = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if image_orig is None:
                logger.error("No se pudo decodificar la imagen con OpenCV.")
                return None

            detector = cv2.QRCodeDetector()

            # --- Pipeline de Detección Secuencial ---

            # Intento 1: Imagen Original (para casos fáciles y rápidos)
            logger.info("Intento de decodificación QR - Etapa 1: Imagen Original")
            decoded_text, points, _ = detector.detectAndDecode(image_orig)
            if points is not None and decoded_text:
                logger.info("ÉXITO en Etapa 1.")
                return decoded_text

            # Intento 2: Con mejora de contraste (CLAHE)
            logger.info("Intento de decodificación QR - Etapa 2: Mejora de Contraste (CLAHE)")
            image_clahe = self._apply_clahe_color(image_orig)
            decoded_text, points, _ = detector.detectAndDecode(image_clahe)
            if points is not None and decoded_text:
                logger.info("ÉXITO en Etapa 2.")
                return decoded_text

            # Intento 3: Con mejora de nitidez sobre la imagen ya contrastada
            logger.info("Intento de decodificación QR - Etapa 3: Aumento de Nitidez")
            image_sharp = self._unsharp_mask(image_clahe, strength=1.2)
            decoded_text, points, _ = detector.detectAndDecode(image_sharp)
            if points is not None and decoded_text:
                logger.info("ÉXITO en Etapa 3.")
                return decoded_text

            # Intento 4: Con limpieza morfológica sobre una imagen binarizada
            logger.info("Intento de decodificación QR - Etapa 4: Limpieza Morfológica")
            gray_sharp = cv2.cvtColor(image_sharp, cv2.COLOR_BGR2GRAY)
            _, thresh_image = cv2.threshold(gray_sharp, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            image_morph = self._apply_morphological_cleanup(thresh_image)
            decoded_text, points, _ = detector.detectAndDecode(image_morph)
            if points is not None and decoded_text:
                logger.info("ÉXITO en Etapa 4.")
                return decoded_text

            logger.error("El QR no pudo ser detectado después de aplicar el pipeline de pre-procesamiento avanzado.")
            return None

        except Exception as e:
            logger.error(f"Error fatal durante la decodificación del QR: {e}")
            return None

    # --- FIN DEL NUEVO BLOQUE DE CÓDIGO ---

    # --- 3. AÑADIR EL NUEVO MANEJADOR DE EVENTOS COMPLETO ---
    async def handle_qr_image_upload(self, files: list[rx.UploadFile]):
        """
        [VERSIÓN CORREGIDA Y COMPLETA]
        Manejador para procesar la imagen de un QR subida por el administrador.
        Decodifica la imagen en el backend y añade el producto a la venta directa.
        """
        if not files:
            # Se notifica al usuario si no se subió ningún archivo
            yield rx.toast.error("No se ha subido ningún archivo.")
            return

        # Se cierra el modal inmediatamente para una mejor experiencia de usuario
        self.show_qr_scanner_modal = False
        
        try:
            # Se leen los datos binarios de la imagen subida
            upload_data = await files[0].read()
            
            # Se llama a la función de decodificación mejorada que aplica el pipeline de pre-procesamiento
            decoded_url = self._decode_qr_from_image(upload_data)
            
            if not decoded_url:
                # Si no se encuentra un QR, se notifica al usuario con un mensaje claro
                yield rx.toast.error("No se pudo encontrar un código QR en la imagen.", duration=6000)
                return

            # Se valida que la URL decodificada contenga el parámetro esperado
            if "variant_uuid=" not in decoded_url:
                yield rx.toast.error("El código QR no es válido para esta aplicación.")
                return
            
            try:
                # Se extrae el 'variant_uuid' de la URL
                parsed_url = urlparse(decoded_url)
                query_params = parse_qs(parsed_url.query)
                variant_uuid = query_params.get("variant_uuid", [None])[0]
            except Exception:
                yield rx.toast.error("URL malformada en el código QR.")
                return

            if not variant_uuid:
                yield rx.toast.error("No se encontró un identificador de producto en el QR.")
                return

            # Se busca el producto y la variante en la base de datos usando el UUID
            result = self.find_variant_by_uuid(variant_uuid)
            
            if not result:
                yield rx.toast.error("Producto no encontrado para este código QR.")
                return
                
            post, variant = result
            
            # Se reconstruye la clave del carrito y se verifica el stock
            attributes = variant.get("attributes", {})
            selection_key_part = "-".join(sorted([f"{k}:{v}" for k, v in attributes.items()]))
            variant_index = next((i for i, v in enumerate(post.variants) if v.get("variant_uuid") == variant_uuid), -1)
            
            if variant_index == -1:
                yield rx.toast.error("Error de consistencia de datos de la variante.")
                return

            cart_key = f"{post.id}-{variant_index}-{selection_key_part}"
            available_stock = variant.get("stock", 0)
            quantity_in_cart = self.direct_sale_cart.get(cart_key, 0)
            
            # Se añade el producto al carrito si hay stock disponible
            if quantity_in_cart + 1 > available_stock:
                yield rx.toast.error(f"¡Sin stock para '{post.title}'!")
            else:
                self.direct_sale_cart[cart_key] = quantity_in_cart + 1
                yield rx.toast.success(f"'{post.title}' añadido a la Venta Directa.")
                
        except Exception as e:
            logger.error(f"Error fatal al procesar la imagen del QR: {e}")
            yield rx.toast.error("Ocurrió un error inesperado al procesar la imagen.")


    @rx.event
    def load_gallery_and_shipping(self):
        """Manejador específico para la carga normal de la galería y el cálculo de envíos."""
        self.is_loading = True
        yield

        yield AppState.load_default_shipping_info

        with rx.session() as session:
            query = sqlmodel.select(BlogPostModel).where(BlogPostModel.publish_active == True)
            if self.current_category and self.current_category != "todos":
                query = query.where(BlogPostModel.category == self.current_category)

            results = session.exec(query.order_by(BlogPostModel.created_at.desc())).all()

            temp_posts = []
            for p in results:
                temp_posts.append(
                    ProductCardData.from_orm(p) # Usamos from_orm para simplificar
                )
            self._raw_posts = temp_posts

        yield AppState.recalculate_all_shipping_costs
        self.is_loading = False
    
    @rx.event
    def load_main_page_data(self):
        """
        Actúa como un 'router'. Lee la URL y decide qué manejador de eventos
        (para QR o para carga normal) debe ejecutarse a continuación.
        """
        full_url = ""
        try:
            full_url = self.router.url
        except Exception:
            pass

        if full_url and "variant_uuid=" in full_url:
            try:
                parsed_url = urlparse(full_url)
                query_params = parse_qs(parsed_url.query)
                variant_uuid_list = query_params.get("variant_uuid")
                if variant_uuid_list:
                    return AppState.handle_public_qr_load(variant_uuid_list[0])
            except Exception as e:
                logging.error(f"Error parseando URL de QR: {e}")

        try:
            parsed_url = urlparse(full_url)
            query_params = parse_qs(parsed_url.query)
            category_list = query_params.get("category")
            self.current_category = category_list[0] if category_list else "todos"
        except Exception:
            self.current_category = "todos"

        return AppState.load_gallery_and_shipping


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

    # --- ⚙️ INICIO: NUEVAS VARIABLES DE ESTADO PARA EL FORMULARIO DE EDICIÓN ⚙️ ---
    
    # Datos básicos del post en edición
    post_to_edit_id: Optional[int] = None
    edit_post_title: str = ""
    edit_post_content: str = ""
    edit_price_str: str = ""
    edit_category: str = ""
    
    # Imágenes
    edit_post_images_in_form: list[str] = []
    edit_selected_image_index: int = -1

    # Opciones de envío
    edit_shipping_cost_str: str = ""
    edit_is_moda_completa: bool = True
    edit_combines_shipping: bool = False
    edit_shipping_combination_limit_str: str = "3"
    edit_is_imported: bool = False
    edit_price_includes_iva: bool = True
    
    # Atributos y Variantes para el formulario de EDICIÓN
    edit_attr_colores: str = ""
    edit_attr_tallas_ropa: list[str] = []
    edit_attr_numeros_calzado: list[str] = []
    edit_attr_tamanos_mochila: list[str] = []
    edit_temp_talla: str = ""
    edit_temp_numero: str = ""
    edit_temp_tamano: str = ""
    edit_variants_map: dict[int, list[VariantFormData]] = {}



    @rx.event
    def start_editing_post(self, post_id: int):
        """
        [CORREGIDO] Inicia la edición de un post, con permisos unificados para Vendedor y Empleado.
        """
        if not self.authenticated_user_info:
            return rx.toast.error("Acción no permitida.")

        # --- ✨ INICIO: LÓGICA DE PERMISOS UNIFICADA ✨ ---
        # Determinamos cuál es el ID del "dueño" del contexto actual.
        owner_id = self.context_user_id or (self.authenticated_user_info.id if self.authenticated_user_info else None)
        if not owner_id:
            return rx.toast.error("No se pudo verificar la identidad del usuario.")
        # --- ✨ FIN: LÓGICA DE PERMISOS UNIFICADA ✨ ---

        with rx.session() as session:
            db_post = session.get(BlogPostModel, post_id)
            
            # Comparamos el dueño del post con el dueño del contexto.
            if not db_post or db_post.userinfo_id != owner_id:
                return rx.toast.error("No tienes permiso para editar esta publicación.")

            # El resto de la lógica para cargar los datos en el formulario se mantiene igual...
            self.post_to_edit_id = db_post.id
            self.edit_post_title = db_post.title
            self.edit_post_content = db_post.content
            self.edit_price_str = str(db_post.price or 0.0)
            self.edit_profit_str = str(db_post.profit or "")
            self.edit_category = db_post.category
            self.edit_shipping_cost_str = str(db_post.shipping_cost or "")
            self.edit_is_moda_completa = db_post.is_moda_completa_eligible
            self.edit_combines_shipping = db_post.combines_shipping
            self.edit_shipping_combination_limit_str = str(db_post.shipping_combination_limit or "3")
            self.edit_is_imported = db_post.is_imported
            self.edit_price_includes_iva = db_post.price_includes_iva
            self.edit_post_images_in_form = sorted(list(set(v.get("image_url", "") for v in (db_post.variants or []) if v.get("image_url"))))
            
            reconstructed_map = defaultdict(list)
            for variant_db in (db_post.variants or []):
                img_url = variant_db.get("image_url")
                if not img_url: continue
                try:
                    image_group_index = self.edit_post_images_in_form.index(img_url)
                    reconstructed_map[image_group_index].append(
                        VariantFormData(
                            attributes=variant_db.get("attributes", {}),
                            stock=variant_db.get("stock", 0),
                            image_url=img_url,
                        )
                    )
                except ValueError:
                    continue
            self.edit_variants_map = dict(reconstructed_map)
            
            if self.edit_post_images_in_form:
                yield self.select_edit_image_for_editing(0)
            self.is_editing_post = True

    
    # --- ⚙️ INICIO: LÓGICA FALTANTE PARA GESTIONAR VARIANTES EN EL FORMULARIO DE EDICIÓN ⚙️ ---

    @rx.event
    def generate_edit_variants(self):
        """
        Genera variantes para la imagen seleccionada en el formulario de EDICIÓN.
        """
        if self.edit_selected_image_index < 0:
            return rx.toast.error("Por favor, selecciona una imagen primero.")

        # Recopila los atributos del formulario de edición
        color = self.edit_attr_colores
        sizes, size_key = [], ""
        if self.edit_category == Category.ROPA.value:
            sizes, size_key = self.edit_attr_tallas_ropa, "Talla"
        elif self.edit_category == Category.CALZADO.value:
            sizes, size_key = self.edit_attr_numeros_calzado, "Número"
        elif self.edit_category == Category.MOCHILAS.value:
            sizes, size_key = self.edit_attr_tamanos_mochila, "Tamaño"

        if not color or not sizes:
            return rx.toast.error("Debes seleccionar un color y al menos una talla/tamaño/número.")

        # Genera las combinaciones
        generated_variants = []
        for size in sizes:
            generated_variants.append(
                VariantFormData(attributes={"Color": color, size_key: size})
            )
        
        self.edit_variants_map[self.edit_selected_image_index] = generated_variants
        return rx.toast.info(f"{len(generated_variants)} variantes generadas para la imagen seleccionada.")

    def _update_edit_variant_stock(self, group_index: int, item_index: int, new_stock: int):
        """Función auxiliar para actualizar el stock en el mapa de edición."""
        if group_index in self.edit_variants_map and 0 <= item_index < len(self.edit_variants_map[group_index]):
            self.edit_variants_map[group_index][item_index].stock = max(0, new_stock)

    def set_edit_variant_stock(self, group_index: int, item_index: int, stock_str: str):
        """Establece el stock para una variante en el formulario de edición."""
        try:
            self._update_edit_variant_stock(group_index, item_index, int(stock_str))
        except (ValueError, TypeError):
            pass

    def increment_edit_variant_stock(self, group_index: int, item_index: int):
        """Incrementa el stock de una variante en el formulario de edición."""
        if group_index in self.edit_variants_map and 0 <= item_index < len(self.edit_variants_map[group_index]):
            current_stock = self.edit_variants_map[group_index][item_index].stock
            self._update_edit_variant_stock(group_index, item_index, current_stock + 1)
            
    def decrement_edit_variant_stock(self, group_index: int, item_index: int):
        """Decrementa el stock de una variante en el formulario de edición."""
        if group_index in self.edit_variants_map and 0 <= item_index < len(self.edit_variants_map[group_index]):
            current_stock = self.edit_variants_map[group_index][item_index].stock
            self._update_edit_variant_stock(group_index, item_index, current_stock - 1)

    def assign_image_to_edit_variant(self, group_index: int, item_index: int, image_url: str):
        """Asigna una imagen a una variante específica en el formulario de edición."""
        if group_index in self.edit_variants_map and 0 <= item_index < len(self.edit_variants_map[group_index]):
            self.edit_variants_map[group_index][item_index].image_url = image_url

    # --- ⚙️ FIN: LÓGICA FALTANTE ⚙️ ---

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

    # ✨ --- REEMPLAZA POR COMPLETO LA FUNCIÓN `save_edited_post` --- ✨
    @rx.event
    def save_edited_post(self):
        """
        [CORREGIDO] Guarda una publicación editada, con permisos unificados y registrando al modificador.
        """
        if not self.authenticated_user_info or self.post_to_edit_id is None:
            return rx.toast.error("Error: No se pudo guardar la publicación.")
        
        # --- ✨ INICIO: LÓGICA DE PERMISOS UNIFICADA ✨ ---
        owner_id = self.context_user_id or (self.authenticated_user_info.id if self.authenticated_user_info else None)
        if not owner_id:
            return rx.toast.error("No se pudo verificar la identidad del usuario.")
        # --- ✨ FIN: LÓGICA DE PERMISOS UNIFICADA ✨ ---

        # ... (La lógica de validación de precios y construcción de variantes se mantiene igual)
        try:
            price = float(self.edit_price_str or 0.0)
            profit = float(self.edit_profit_str) if self.edit_profit_str else None
            shipping_cost = float(self.edit_shipping_cost_str) if self.edit_shipping_cost_str else None
            limit = int(self.edit_shipping_combination_limit_str) if self.edit_combines_shipping and self.edit_shipping_combination_limit_str else None
        except ValueError:
            return rx.toast.error("Precio, ganancia, costo de envío y límite deben ser números válidos.")
        all_variants_for_db = []
        for image_group_index, variant_list in self.edit_variants_map.items():
            main_image_for_group = self.unique_edit_form_images[image_group_index]
            for variant_form_data in variant_list:
                new_variant_dict = {
                    "attributes": variant_form_data.attributes, "stock": variant_form_data.stock,
                    "image_url": variant_form_data.image_url or main_image_for_group,
                    "variant_uuid": getattr(variant_form_data, 'variant_uuid', str(uuid.uuid4()))
                }
                all_variants_for_db.append(new_variant_dict)
        if not all_variants_for_db:
            return rx.toast.error("No se encontraron variantes configuradas para guardar.")

        with rx.session() as session:
            post_to_update = session.get(BlogPostModel, self.post_to_edit_id)
            
            if not post_to_update or post_to_update.userinfo_id != owner_id:
                return rx.toast.error("No tienes permiso para guardar esta publicación.")
                
            post_to_update.title = self.edit_post_title
            post_to_update.content = self.edit_post_content
            post_to_update.price = price
            post_to_update.profit = profit
            post_to_update.category = self.edit_category
            post_to_update.price_includes_iva = self.edit_price_includes_iva
            post_to_update.is_imported = self.edit_is_imported
            post_to_update.shipping_cost = shipping_cost
            post_to_update.is_moda_completa_eligible = self.edit_is_moda_completa
            post_to_update.combines_shipping = self.edit_combines_shipping
            post_to_update.shipping_combination_limit = limit
            post_to_update.variants = all_variants_for_db
            post_to_update.last_modified_by_id = self.authenticated_user_info.id
            
            session.add(post_to_update)
            
            log_entry = ActivityLog(
                actor_id=self.authenticated_user_info.id,
                owner_id=post_to_update.userinfo_id,
                action_type="Edición de Publicación",
                description=f"Modificó la publicación '{post_to_update.title}'"
            )
            session.add(log_entry)
            session.commit()

        yield self.cancel_editing_post(False)
        yield AppState.load_mis_publicaciones
        yield rx.toast.success("Publicación actualizada correctamente.")


    # --- ⚙️ INICIO: NUEVOS HELPERS Y PROPIEDADES PARA EL FORMULARIO DE EDICIÓN ⚙️ ---

    @rx.var
    def unique_edit_form_images(self) -> list[str]:
        """Devuelve una lista de URLs de imagen únicas para las miniaturas del modal de edición."""
        return self.edit_post_images_in_form

    def select_edit_image_for_editing(self, index: int):
        """Selecciona una imagen en el form de EDICIÓN y carga sus atributos."""
        self.edit_selected_image_index = index
        self.edit_attr_colores = ""
        self.edit_attr_tallas_ropa = []
        self.edit_attr_numeros_calzado = []
        self.edit_attr_tamanos_mochila = []

        # Cargar los atributos de la PRIMERA variante asociada a esta imagen para pre-llenar el form
        variants_in_group = self.edit_variants_map.get(index, [])
        if variants_in_group:
            first_variant_attrs = variants_in_group[0].attributes
            self.edit_attr_colores = first_variant_attrs.get("Color", "")
            
            all_tallas = sorted(list(set(v.attributes.get("Talla") for v in variants_in_group if v.attributes.get("Talla"))))
            all_numeros = sorted(list(set(v.attributes.get("Número") for v in variants_in_group if v.attributes.get("Número"))))
            all_tamanos = sorted(list(set(v.attributes.get("Tamaño") for v in variants_in_group if v.attributes.get("Tamaño"))))

            self.edit_attr_tallas_ropa = all_tallas
            self.edit_attr_numeros_calzado = all_numeros
            self.edit_attr_tamanos_mochila = all_tamanos
    
    # Setters para los campos del formulario de edición
    def set_edit_post_title(self, title: str): self.edit_post_title = title
    def set_edit_post_content(self, content: str): self.edit_post_content = content
    def set_edit_price_str(self, price: str): self.edit_price_str = price
    def set_edit_category(self, cat: str): self.edit_category = cat # Resto de la lógica de limpieza irá aquí si es necesaria
    def set_edit_shipping_cost_str(self, cost: str): self.edit_shipping_cost_str = cost
    def set_edit_is_moda_completa(self, val: bool): self.edit_is_moda_completa = val
    def set_edit_combines_shipping(self, val: bool): self.edit_combines_shipping = val
    def set_edit_shipping_combination_limit_str(self, val: str): self.edit_shipping_combination_limit_str = val
    def set_edit_is_imported(self, val: bool): self.edit_is_imported = val
    def set_edit_price_includes_iva(self, val: bool): self.edit_price_includes_iva = val
    def set_edit_attr_colores(self, val: str): self.edit_attr_colores = val
    def set_edit_temp_talla(self, val: str): self.edit_temp_talla = val
    def set_edit_temp_numero(self, val: str): self.edit_temp_numero = val
    def set_edit_temp_tamano(self, val: str): self.edit_temp_tamano = val

    # Lógica para añadir/quitar atributos en el formulario de EDICIÓN
    def add_edit_variant_attribute(self, key: str, value: str):
        target_list = getattr(self, f"edit_attr_{key.lower()}s_ropa" if key == "Talla" else (f"edit_attr_numeros_calzado" if key == "Número" else "edit_attr_tamanos_mochila"))
        if value not in target_list:
            target_list.append(value)
            target_list.sort()

    def remove_edit_variant_attribute(self, key: str, value: str):
        target_list = getattr(self, f"edit_attr_{key.lower()}s_ropa" if key == "Talla" else (f"edit_attr_numeros_calzado" if key == "Número" else "edit_attr_tamanos_mochila"))
        if value in target_list:
            target_list.remove(value)


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
    
    # AÑADE ESTA NUEVA FUNCIÓN DENTRO DE LA CLASE AppState
    def update_edit_form_state(self, form_data: dict):
        """
        [VERSIÓN CORREGIDA Y FINAL]
        Manejador centralizado que actualiza TODO el estado del formulario de edición.
        Se corrigen los nombres de las claves para que coincidan con los `name` del formulario.
        """
        # Actualiza los campos de texto y numéricos
        self.edit_post_title = form_data.get("title", "")
        self.edit_post_content = form_data.get("content", "")
        self.edit_price_str = form_data.get("price", "")
        self.edit_shipping_cost_str = form_data.get("edit_shipping_cost_str", "")
        self.edit_shipping_combination_limit_str = form_data.get("edit_shipping_combination_limit_str", "")
        
        # Actualiza los campos de selección (select)
        self.edit_category = form_data.get("category", "")
        
        # <-- INICIO DE LA CORRECCIÓN CLAVE -->
        # Se usan los nombres correctos que coinciden con la propiedad `name` en el formulario.
        self.edit_price_includes_iva = form_data.get("price_includes_iva", False)
        self.edit_is_imported = form_data.get("is_imported", False)
        self.edit_is_moda_completa = form_data.get("edit_is_moda_completa", False)
        self.edit_combines_shipping = form_data.get("combines_shipping", False)
        # <-- FIN DE LA CORRECCIÓN CLAVE -->

    @rx.event
    def remove_temp_image(self, filename: str):
        if filename in self.temp_images:
            self.temp_images.remove(filename)

    # ✨ --- FUNCIÓN NUEVA: Para eliminar una imagen del formulario de edición --- ✨
    @rx.event
    def remove_edit_image(self, img_url: str):
        """Elimina una imagen y sus variantes asociadas del formulario de edición."""
        if img_url in self.edit_post_images_in_form:
            try:
                # Encuentra el índice de la imagen a eliminar
                idx_to_remove = self.edit_post_images_in_form.index(img_url)
                
                # Elimina la imagen de la lista
                self.edit_post_images_in_form.pop(idx_to_remove)
                
                # Elimina el grupo de variantes asociado a esa imagen del mapa
                if idx_to_remove in self.edit_variants_map:
                    del self.edit_variants_map[idx_to_remove]
                
                # Reconstruye el mapa de variantes para reajustar los índices
                new_map = {}
                for i, key in enumerate(sorted(self.edit_variants_map.keys())):
                    if i != key:
                        new_map[i] = self.edit_variants_map[key]
                    else:
                        new_map[key] = self.edit_variants_map[key]
                self.edit_variants_map = new_map

                # Si la imagen eliminada era la que estaba seleccionada, deseleccionamos
                if self.edit_selected_image_index == idx_to_remove:
                    self.edit_selected_image_index = -1

            except ValueError:
                pass # La imagen no estaba en la lista

    # ✨ --- FUNCIÓN CORREGIDA: Para añadir nuevas imágenes --- ✨
    @rx.event
    async def handle_edit_upload(self, files: list[rx.UploadFile]):
        """Maneja la subida de NUEVAS imágenes en el modal de edición."""
        for file in files:
            upload_data = await file.read()
            unique_filename = f"{secrets.token_hex(8)}-{file.name}"
            outfile = rx.get_upload_dir() / unique_filename
            outfile.write_bytes(upload_data)
            # Añade la nueva imagen a la lista del formulario
            self.edit_post_images_in_form.append(unique_filename)

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
    
    # --- INICIO DE LA CORRECCIÓN CLAVE ---
    @rx.var
    def unique_modal_variants(self) -> list[UniqueVariantItem]:
        """
        Devuelve una lista de DTOs con URLs de imagen únicas para las
        miniaturas del modal, evitando duplicados.
        """
        if not self.product_in_modal or not self.product_in_modal.variants:
            return []
        
        unique_items = []
        seen_images = set()
        for i, variant in enumerate(self.product_in_modal.variants):
            image_url = variant.get("image_url")
            if image_url and image_url not in seen_images:
                seen_images.add(image_url)
                unique_items.append(UniqueVariantItem(variant=variant, index=i))
        return unique_items
    # --- FIN DE LA CORRECCIÓN CLAVE ---

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

    

    @rx.event
    def on_load_seller_profile(self):
        """Carga la ciudad y el barrio guardados del vendedor."""
        if self.is_admin and self.authenticated_user_info:
            with rx.session() as session:
                user_info = session.get(UserInfo, self.authenticated_user_info.id)
                if user_info:
                    # Carga ambos campos
                    self.seller_profile_city = user_info.seller_city or ""
                    self.seller_profile_barrio = user_info.seller_barrio or ""
                    self.seller_profile_address = user_info.seller_address or ""

    def set_seller_profile_barrio(self, barrio: str):
        """Actualiza el barrio seleccionado en el formulario de perfil."""
        self.seller_profile_barrio = barrio

    def set_seller_profile_address(self, address: str):
        self.seller_profile_address = address

    @rx.event
    def save_seller_profile(self, form_data: dict):
        """Guarda la ciudad, el barrio y la dirección del vendedor."""
        if not self.is_admin or not self.authenticated_user_info:
             return rx.toast.error("Acción no permitida.")

        address = form_data.get("seller_address", "")
        # Validar que tanto la ciudad como el barrio estén seleccionados
        if not self.seller_profile_city or not self.seller_profile_barrio or not address:
            return rx.toast.error("Debes seleccionar ciudad, barrio y escribir una dirección.")

        with rx.session() as session:
            user_info_to_update = session.get(UserInfo, self.authenticated_user_info.id)
            if user_info_to_update:
                user_info_to_update.seller_city = self.seller_profile_city # Guardar ciudad
                user_info_to_update.seller_barrio = self.seller_profile_barrio # Guardar barrio
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
        Calcula el resumen del carrito, ahora pasando la ciudad del vendedor y comprador
        para un cálculo de envío preciso.
        """
        if not self.cart:
            return {"subtotal": 0, "shipping_cost": 0, "grand_total": 0, "free_shipping_achieved": False, "iva": 0}

        with rx.session() as session:
            cart_items_details = self.cart_details
            if not cart_items_details:
                return {"subtotal": 0, "shipping_cost": 0, "grand_total": 0, "free_shipping_achieved": False, "iva": 0}

            post_ids = [item.product_id for item in cart_items_details]
            db_posts = session.exec(sqlmodel.select(BlogPostModel).where(BlogPostModel.id.in_(post_ids))).all()
            post_map = {p.id: p for p in db_posts}

            subtotal_base = sum(post_map.get(item.product_id).base_price * item.quantity for item in cart_items_details if post_map.get(item.product_id))
            iva = subtotal_base * 0.19
            subtotal_con_iva = subtotal_base + iva
            free_shipping_achieved = subtotal_con_iva >= 200000
            
            final_shipping_cost = 0.0
            if not free_shipping_achieved and self.default_shipping_address:
                # --- INICIO DE LA MODIFICACIÓN ---
                buyer_city = self.default_shipping_address.city
                buyer_barrio = self.default_shipping_address.neighborhood
                # --- FIN DE LA MODIFICACIÓN ---

                seller_groups = defaultdict(list)
                for item in cart_items_details:
                    db_post = post_map.get(item.product_id)
                    if db_post:
                        for _ in range(item.quantity):
                            seller_groups[db_post.userinfo_id].append(db_post)

                seller_ids = list(seller_groups.keys())
                sellers_info = session.exec(sqlmodel.select(UserInfo).where(UserInfo.id.in_(seller_ids))).all()
                # --- INICIO DE LA MODIFICACIÓN ---
                # Ahora obtenemos tanto la ciudad como el barrio del vendedor
                seller_data_map = {info.id: {"city": info.seller_city, "barrio": info.seller_barrio} for info in sellers_info}
                # --- FIN DE LA MODIFICACIÓN ---

                for seller_id, items_from_seller in seller_groups.items():
                    combinable_items = [p for p in items_from_seller if p.combines_shipping]
                    individual_items = [p for p in items_from_seller if not p.combines_shipping]
                    # --- INICIO DE LA MODIFICACIÓN ---
                    seller_data = seller_data_map.get(seller_id)
                    seller_city = seller_data.get("city") if seller_data else None
                    seller_barrio = seller_data.get("barrio") if seller_data else None
                    # --- FIN DE LA MODIFICACIÓN ---

                    for individual_item in individual_items:
                        cost = calculate_dynamic_shipping(
                            base_cost=individual_item.shipping_cost or 0.0,
                            seller_barrio=seller_barrio,
                            buyer_barrio=buyer_barrio,
                            # --- Pasamos los nuevos argumentos ---
                            seller_city=seller_city,
                            buyer_city=buyer_city
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
                            buyer_barrio=buyer_barrio,
                            # --- Pasamos los nuevos argumentos ---
                            seller_city=seller_city,
                            buyer_city=buyer_city
                        )
                        final_shipping_cost += (group_shipping_fee * num_fees)
            
            grand_total = subtotal_con_iva + final_shipping_cost
            
            return { "subtotal": subtotal_base, "shipping_cost": final_shipping_cost, "iva": iva, "grand_total": grand_total, "free_shipping_achieved": free_shipping_achieved }
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
        """Actualiza la selección de un atributo (ej: Talla) en el modal."""
        self.modal_selected_attributes[key] = value

    @rx.var
    def modal_attribute_selectors(self) -> list[ModalSelectorDTO]:
        """
        Genera dinámicamente la lista de selectores (ej: Tallas) necesarios
        basado en la imagen seleccionada y el stock disponible.
        """
        if not self.current_modal_variant or not self.product_in_modal: return []
        
        current_image_url = self.current_modal_image_filename
        
        # Filtra todas las variantes que pertenecen a la misma imagen
        variants_for_this_image = [
            v for v in self.product_in_modal.variants 
            if v.get("image_url") == current_image_url
        ]

        # Identifica qué atributos son seleccionables (Talla, Número, etc.)
        selectable_keys = list(set(
            key for v in variants_for_this_image 
            for key in v.get("attributes", {})
            if key in ["Talla", "Número", "Tamaño"]
        ))
        
        if not selectable_keys: return []

        key_to_select = selectable_keys[0] # Asumimos un solo tipo de selector por grupo de imagen
        
        # Encuentra las opciones disponibles Y con stock
        valid_options = sorted(list({
            v["attributes"][key_to_select]
            for v in variants_for_this_image
            if v.get("stock", 0) > 0 and key_to_select in v.get("attributes", {})
        }))
        
        if not valid_options: return []
        
        return [ModalSelectorDTO(
            key=key_to_select,
            options=valid_options,
            current_value=self.modal_selected_attributes.get(key_to_select, "")
        )]

    @rx.event
    def add_to_cart(self, product_id: int):
        """
        Lógica de añadir al carrito REESCRITA para encontrar la variante exacta
        basada en la selección del usuario y verificar su stock específico.
        """
        if not self.is_authenticated:
            return rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)
        if not self.product_in_modal or not self.current_modal_variant:
            return rx.toast.error("Error al identificar el producto.")

        # 1. Validar que se hayan seleccionado todos los atributos requeridos
        required_keys = {selector.key for selector in self.modal_attribute_selectors}
        if not all(key in self.modal_selected_attributes for key in required_keys):
            missing = required_keys - set(self.modal_selected_attributes.keys())
            return rx.toast.error(f"Por favor, selecciona: {', '.join(missing)}")

        # 2. Encontrar la variante exacta que coincide con la selección completa
        variant_to_add = None
        # Atributos de la imagen base (ej: Color)
        base_attributes = self.current_variant_display_attributes
        # Atributos seleccionados (ej: Talla)
        selected_attributes = self.modal_selected_attributes
        
        # Combinamos ambos para la búsqueda
        full_selection = {**base_attributes, **selected_attributes}
        
        for variant in self.product_in_modal.variants:
            if variant.get("attributes") == full_selection:
                variant_to_add = variant
                break
        
        if not variant_to_add:
            return rx.toast.error("La combinación seleccionada no está disponible.")

        # 3. Construir la clave única para el carrito
        # Usamos el índice de la variante visual para la imagen y los atributos para la unicidad
        selection_key_part = "-".join(sorted([f"{k}:{v}" for k, v in full_selection.items()]))
        cart_key = f"{product_id}-{self.modal_selected_variant_index}-{selection_key_part}"
        
        # 4. Verificar el stock de la variante encontrada
        stock_disponible = variant_to_add.get("stock", 0)
        cantidad_en_carrito = self.cart.get(cart_key, 0)
        
        if cantidad_en_carrito + 1 > stock_disponible:
            return rx.toast.error("¡Lo sentimos! No hay suficiente stock para esta combinación.")
        
        # 5. Si hay stock, añadir al carrito
        self.cart[cart_key] = cantidad_en_carrito + 1
        
        self.show_detail_modal = False
        return rx.toast.success("Producto añadido al carrito.")
    
    @rx.event
    def increase_cart_quantity(self, cart_key: str):
        """
        Aumenta la cantidad de un artículo en el carrito, verificando el stock disponible.
        """
        if cart_key not in self.cart:
            return

        # Extraer la información de la clave para encontrar el producto y la variante
        parts = cart_key.split('-')
        product_id = int(parts[0])
        selection_attrs = dict(part.split(':', 1) for part in parts[2:] if ':' in part)
        
        with rx.session() as session:
            post = session.get(BlogPostModel, product_id)
            if not post:
                return rx.toast.error("El producto ya no existe.")

            # Encontrar la variante específica para verificar su stock
            variant_to_check = None
            for variant in post.variants:
                if variant.get("attributes") == selection_attrs:
                    variant_to_check = variant
                    break
            
            if not variant_to_check:
                return rx.toast.error("La variante seleccionada ya no está disponible.")

            stock_disponible = variant_to_check.get("stock", 0)
            cantidad_actual = self.cart[cart_key]

            # La verificación clave: no permitir añadir más del stock
            if cantidad_actual + 1 > stock_disponible:
                return rx.toast.error("¡No hay más stock disponible para esta variante!")
            
            # Si hay stock, aumentar la cantidad
            self.cart[cart_key] += 1

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

    profit_str: str = ""

    def set_profit_str(self, profit: str):
        self.profit_str = profit

    edit_profit_str: str = ""
    def set_edit_profit_str(self, profit: str):
        self.edit_profit_str = profit

    # --- Variables para el Dashboard de Finanzas ---
    finance_stats: Optional[FinanceStatsDTO] = None
    product_finance_data: List[ProductFinanceDTO] = []
    profit_chart_data: List[Dict[str, Any]] = []
    search_product_finance: str = ""
    # Lista para almacenar los gastos cargados desde la BD
    all_gastos: List[GastoDataDTO] = []
    
    # Variables para el filtro de fechas de gastos
    gasto_start_date: str = ""
    gasto_end_date: str = ""

    # --- Nuevas variables para el detalle del producto/variante ---
    show_product_detail_modal: bool = False
    selected_product_detail: Optional[ProductDetailFinanceDTO] = None
    selected_variant_detail: Optional[VariantDetailFinanceDTO] = None # Detalle de la variante seleccionada
    selected_variant_index: int = -1 # Para seleccionar la variante en el modal
    product_detail_chart_data: List[Dict[str, Any]] = [] # Datos del gráfico de la variante seleccionada


    def set_search_product_finance(self, query: str):
        self.search_product_finance = query

    @rx.var
    def filtered_product_finance_data(self) -> List[ProductFinanceDTO]:
        """Filtra la tabla de finanzas por producto."""
        if not self.search_product_finance.strip():
            return self.product_finance_data
        
        query = self.search_product_finance.lower()
        return [
            p for p in self.product_finance_data 
            if query in p.title.lower()
        ]
    
    def _get_variant_key(self, variant_data: dict) -> str:
        """
        [VERSIÓN CORREGIDA Y ROBUSTA]
        Crea una clave única y estable para una variante basada en sus atributos.
        """
        if not isinstance(variant_data, dict):
            return str(uuid.uuid4())

        # Prioriza el UUID si existe, ya que es el identificador más fiable
        if variant_uuid := variant_data.get("variant_uuid"):
            return variant_uuid
        
        # Si no hay UUID, usa los atributos. Comprueba si el diccionario
        # ya es el de atributos o si los contiene.
        attrs = variant_data.get("attributes", variant_data)
        if not isinstance(attrs, dict) or not attrs:
            return variant_data.get("image_url", str(uuid.uuid4()))
        
        # Crea una clave ordenada y predecible a partir de los atributos
        sorted_attrs = sorted(attrs.items())
        return "-".join(f"{k}:{v}" for k, v in sorted_attrs)


    # --- Función para mostrar el detalle de un producto ---
    
    @rx.event
    async def show_product_detail(self, product_id: int):
        """
        [VERSIÓN CORREGIDA] Muestra el detalle financiero de un producto,
        permitiendo el acceso a Vendedores y Empleados.
        """
        # --- ✨ INICIO DE LA CORRECCIÓN CLAVE ✨ ---
        # Cambiamos 'if not self.is_admin:' por una condición que incluye todos los roles del panel.
        if not (self.is_admin or self.is_vendedor or self.is_empleado):
            yield rx.redirect("/")
            return
        # --- ✨ FIN DE LA CORRECCIÓN CLAVE ✨ ---

        self.selected_product_detail = None
        self.show_product_detail_modal = True
        yield

        with rx.session() as session:
            blog_post = session.get(BlogPostModel, product_id)
            if not blog_post:
                yield rx.toast.error("Producto no encontrado.")
                self.show_product_detail_modal = False
                return

            # ... (el resto de la lógica de la función para calcular finanzas se mantiene exactamente igual)
            variant_sales_aggregator = defaultdict(lambda: {
                "units": 0, "revenue": 0.0, "net_profit": 0.0, "cogs": 0.0, "daily_profit": defaultdict(float)
            })
            completed_purchases = session.exec(
                sqlmodel.select(PurchaseModel)
                .options(sqlalchemy.orm.selectinload(PurchaseModel.items).selectinload(PurchaseItemModel.blog_post))
                .where(
                    PurchaseModel.status.in_([PurchaseStatus.DELIVERED, PurchaseStatus.DIRECT_SALE]),
                    PurchaseItemModel.blog_post_id == product_id
                ).join(PurchaseItemModel)
            ).unique().all()
            
            product_total_units, product_total_revenue, product_total_net_profit, product_total_cogs = 0, 0.0, 0.0, 0.0
            product_shipping_collected, product_actual_shipping_cost = 0.0, 0.0

            for purchase in completed_purchases:
                product_shipping_collected += purchase.shipping_applied or 0.0
                product_actual_shipping_cost += purchase.actual_shipping_cost or purchase.shipping_applied or 0.0
                for item in purchase.items:
                    if item.blog_post_id == product_id and item.blog_post:
                        sold_variant_definition = next((v for v in item.blog_post.variants if v.get("attributes") == item.selected_variant), item.selected_variant)
                        variant_key = self._get_variant_key(sold_variant_definition)
                        item_revenue = item.price_at_purchase * item.quantity
                        profit_per_unit = item.blog_post.profit or 0.0
                        cost_per_unit = (item.blog_post.price or 0.0) - profit_per_unit
                        item_cogs = cost_per_unit * item.quantity
                        item_net_profit = profit_per_unit * item.quantity
                        aggregator = variant_sales_aggregator[variant_key]
                        aggregator["units"] += item.quantity
                        aggregator["revenue"] += item_revenue
                        aggregator["net_profit"] += item_net_profit
                        aggregator["cogs"] += item_cogs
                        aggregator["daily_profit"][purchase.purchase_date.strftime('%Y-%m-%d')] += item_net_profit
                        product_total_units += item.quantity
                        product_total_revenue += item_revenue
                        product_total_net_profit += item_net_profit
                        product_total_cogs += item_cogs

            product_shipping_profit_loss = product_shipping_collected - product_actual_shipping_cost
            grand_total_profit = product_total_net_profit + product_shipping_profit_loss

            product_variants_data = [
                VariantDetailFinanceDTO(
                    variant_key=self._get_variant_key(variant_db),
                    attributes_str=", ".join([f"{k}: {v}" for k, v in variant_db.get("attributes", {}).items()]),
                    image_url=variant_db.get("image_url"),
                    units_sold=variant_sales_aggregator.get(self._get_variant_key(variant_db), {}).get("units", 0),
                    total_revenue_cop=format_to_cop(variant_sales_aggregator.get(self._get_variant_key(variant_db), {}).get("revenue", 0.0)),
                    total_cogs_cop=format_to_cop(variant_sales_aggregator.get(self._get_variant_key(variant_db), {}).get("cogs", 0.0)),
                    total_net_profit_cop=format_to_cop(variant_sales_aggregator.get(self._get_variant_key(variant_db), {}).get("net_profit", 0.0)),
                    daily_profit_data=sorted([{"date": date, "Ganancia": profit} for date, profit in variant_sales_aggregator.get(self._get_variant_key(variant_db), {}).get("daily_profit", {}).items()], key=lambda x: x['date'])
                ) for variant_db in (blog_post.variants or [])
            ]

            self.selected_product_detail = ProductDetailFinanceDTO(
                product_id=blog_post.id,
                title=blog_post.title,
                image_url=blog_post.variants[0].get("image_url") if blog_post.variants else None,
                total_units_sold=product_total_units,
                total_revenue_cop=format_to_cop(product_total_revenue),
                total_cogs_cop=format_to_cop(product_total_cogs),
                product_profit_cop=format_to_cop(product_total_net_profit),
                shipping_collected_cop=format_to_cop(product_shipping_collected),
                shipping_profit_loss_cop=format_to_cop(product_shipping_profit_loss),
                total_profit_cop=format_to_cop(grand_total_profit),
                variants=product_variants_data
            )
            
            if product_variants_data:
                first_sold_variant_index = next((i for i, v in enumerate(product_variants_data) if v.units_sold > 0), 0)
                self.select_variant_for_detail(first_sold_variant_index)
    
    # --- Función para seleccionar una variante específica en el detalle del producto ---
    @rx.event
    def select_variant_for_detail(self, index: int):
        if self.selected_product_detail and 0 <= index < len(self.selected_product_detail.variants):
            self.selected_variant_index = index
            self.selected_variant_detail = self.selected_product_detail.variants[index]
            self.product_detail_chart_data = self.selected_variant_detail.daily_profit_data
        else:
            self.selected_variant_index = -1
            self.selected_variant_detail = None
            self.product_detail_chart_data = []


    @rx.event
    def close_product_detail_modal(self):
        """Cierra el modal de detalle del producto y resetea su estado."""
        self.show_detail_modal = False
        self.product_in_modal = None
        # Añadimos también el reseteo de las otras variables para asegurar la limpieza completa
        self.selected_product_detail = None
        self.selected_variant_detail = None
        self.selected_variant_index = -1
        self.product_detail_chart_data = []

    @rx.event
    def set_show_product_detail_modal(self, open: bool):
        """Controla la visibilidad del modal de finanzas y limpia el estado al cerrar."""
        self.show_product_detail_modal = open
        # Si el modal se está cerrando, limpiamos los datos para la próxima vez
        if not open:
            self.selected_product_detail = None
            self.selected_variant_detail = None
            self.selected_variant_index = -1
            self.product_detail_chart_data = []

    # --- ✨ INICIO DE NUEVAS VARIABLES Y SETTERS ✨ ---
    admin_final_shipping_cost: Dict[int, str] = {}

    def set_admin_final_shipping_cost(self, purchase_id: int, value: str):
        """Guarda el costo de envío final ingresado por el admin."""
        self.admin_final_shipping_cost[purchase_id] = value
    # --- ✨ FIN DE NUEVAS VARIABLES Y SETTERS ✨ ---

    # --- INICIO: NUEVOS EVENT HANDLERS Y VARS PARA GASTOS ---

    def set_gasto_start_date(self, date: str):
        """Actualiza la fecha de inicio para el filtro de gastos."""
        self.gasto_start_date = date

    def set_gasto_end_date(self, date: str):
        """Actualiza la fecha de fin para el filtro de gastos."""
        self.gasto_end_date = date

    @rx.var
    def gasto_categories(self) -> list[str]:
        """Devuelve la lista de categorías de gastos para el formulario."""
        return [c.value for c in GastoCategoria]

    @rx.var
    def filtered_gastos(self) -> List[GastoDataDTO]:
        """Filtra la lista de gastos por el rango de fechas seleccionado."""
        if not self.gasto_start_date and not self.gasto_end_date:
            return self.all_gastos

        try:
            start_dt = datetime.strptime(self.gasto_start_date, '%Y-%m-%d') if self.gasto_start_date else None
            end_dt = datetime.strptime(self.gasto_end_date, '%Y-%m-%d') if self.gasto_end_date else None
        except ValueError:
            return self.all_gastos

        def parse_fecha(fecha_str: str) -> datetime:
            return datetime.strptime(fecha_str.split(' ')[0], '%d-%m-%Y')

        filtered = self.all_gastos
        if start_dt:
            filtered = [g for g in filtered if parse_fecha(g.fecha_formateada) >= start_dt]
        if end_dt:
            filtered = [g for g in filtered if parse_fecha(g.fecha_formateada) <= end_dt]
            
        return filtered

    @rx.event
    def load_gastos(self):
        """Carga todos los gastos registrados, incluyendo el nombre del creador."""
        if not (self.is_admin or self.is_vendedor or self.is_empleado):
            return

        owner_id = self.context_user_info.id if self.context_user_info else (self.authenticated_user_info.id if self.authenticated_user_info else None)
        if not owner_id:
            return

        with rx.session() as session:
            gastos_db = session.exec(
                sqlmodel.select(Gasto)
                .options(sqlalchemy.orm.joinedload(Gasto.creator).joinedload(UserInfo.user))
                .where(Gasto.userinfo_id == owner_id)
                .order_by(Gasto.fecha.desc())
            ).all()

            self.all_gastos = [
                GastoDataDTO(
                    id=g.id,
                    fecha_formateada=g.fecha_formateada,
                    descripcion=g.descripcion,
                    categoria=g.categoria.value,
                    valor_cop=g.valor_cop,
                    # --- ✨ INICIO: AÑADIMOS EL NOMBRE DEL CREADOR AL DTO ✨ ---
                    creator_name=g.creator.user.username if g.creator and g.creator.user else "N/A"
                    # --- ✨ FIN: AÑADIMOS EL NOMBRE DEL CREADOR AL DTO ✨ ---
                ) for g in gastos_db
            ]

    @rx.event
    def handle_add_gasto(self, form_data: dict):
        """Manejador para crear un nuevo registro de gasto, ahora con atribución."""
        if not (self.is_admin or self.is_vendedor or self.is_empleado) or not self.authenticated_user_info:
            return rx.toast.error("Acción no permitida.")

        owner_id = self.context_user_info.id if self.context_user_info else self.authenticated_user_info.id
        creator_id = self.authenticated_user_info.id

        descripcion = form_data.get("descripcion")
        categoria = form_data.get("categoria")
        valor_str = form_data.get("valor")

        if not all([descripcion, categoria, valor_str]):
            return rx.toast.error("Todos los campos son obligatorios.")

        try:
            valor_float = float(valor_str)
            if valor_float <= 0: raise ValueError()
        except (ValueError, TypeError):
            return rx.toast.error("El valor debe ser un número positivo.")
        
        with rx.session() as session:
            new_gasto = Gasto(
                userinfo_id=owner_id,       # El gasto pertenece al vendedor
                creator_id=creator_id,      # Fue creado por el usuario logueado
                descripcion=descripcion,
                categoria=categoria,
                valor=valor_float
            )
            session.add(new_gasto)

            # --- ✨ AÑADIR REGISTRO DE ACTIVIDAD ✨ ---
            log_entry = ActivityLog(
                actor_id=creator_id,
                owner_id=owner_id,
                action_type="Registro de Gasto",
                description=f"Registró un gasto de {format_to_cop(valor_float)}: '{descripcion}'"
            )
            session.add(log_entry)

            session.commit()

        yield AppState.load_gastos
        yield rx.toast.success("Gasto registrado exitosamente.")

    # --- FIN: NUEVOS EVENT HANDLERS Y VARS PARA GASTOS ---

    # MODIFY THIS EXISTING EVENT HANDLER
    @rx.event
    def on_load_finance_data(self):
        """
        [CORREGIDO] Se ejecuta al cargar la página de finanzas.
        Ahora permite el acceso a Vendedores y Empleados.
        """
        # --- ✨ INICIO DE LA CORRECCIÓN CLAVE ✨ ---
        if not (self.is_admin or self.is_vendedor or self.is_empleado):
            return rx.redirect("/")
        # --- ✨ FIN DE LA CORRECCIÓN CLAVE ✨ ---

        today = datetime.now(timezone.utc)
        thirty_days_ago = today - timedelta(days=30)
        
        self.finance_end_date = today.strftime('%Y-%m-%d')
        self.finance_start_date = thirty_days_ago.strftime('%Y-%m-%d')
        
        self.gasto_end_date = today.strftime('%Y-%m-%d')
        self.gasto_start_date = thirty_days_ago.strftime('%Y-%m-%d')
        
        yield AppState.filter_finance_data
        yield AppState.load_gastos

    @rx.event
    def filter_finance_data(self):
        """
        Evento que se dispara al hacer clic en el botón 'Filtrar'.
        Llama a la función de cálculo con las fechas seleccionadas.
        """
        yield from self._calculate_finance_data()

    def _calculate_finance_data(self):
        """
        [VERSIÓN 5.1 - Corregida] Lógica central que calcula todas las métricas financieras
        basándose en el rango de fechas del estado.
        """
        self.is_loading = True
        yield

        with rx.session() as session:
            # Construye la consulta base
            query = (
                sqlmodel.select(PurchaseModel)
                .options(
                    sqlalchemy.orm.selectinload(PurchaseModel.items)
                    .selectinload(PurchaseItemModel.blog_post)
                )
                .where(PurchaseModel.status.in_([PurchaseStatus.DELIVERED, PurchaseStatus.DIRECT_SALE]))
            )

            # Aplica los filtros de fecha si existen
            try:
                if self.finance_start_date:
                    start_date = datetime.strptime(self.finance_start_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
                    query = query.where(PurchaseModel.purchase_date >= start_date)
                if self.finance_end_date:
                    end_date = datetime.strptime(self.finance_end_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
                    end_date_inclusive = end_date + timedelta(days=1)
                    query = query.where(PurchaseModel.purchase_date < end_date_inclusive)
            except ValueError:
                pass

            completed_purchases = session.exec(query.order_by(PurchaseModel.purchase_date.desc())).unique().all()

            total_revenue = 0.0
            total_cogs = 0.0
            total_net_profit = 0.0
            total_shipping_collected = sum(p.shipping_applied or 0.0 for p in completed_purchases)
            total_actual_shipping_cost = sum(p.actual_shipping_cost or p.shipping_applied or 0.0 for p in completed_purchases)
            total_sales_count = len(completed_purchases)
            
            product_aggregator = defaultdict(lambda: {"title": "", "units": 0, "revenue": 0.0, "net_profit": 0.0, "cogs": 0.0})
            daily_profit = defaultdict(float)

            for purchase in completed_purchases:
                purchase_date_str = purchase.purchase_date.strftime('%Y-%m-%d')
                for item in purchase.items:
                    if item.blog_post:
                        item_revenue = item.price_at_purchase * item.quantity
                        profit_per_unit = item.blog_post.profit or 0.0
                        cost_per_unit = (item.blog_post.price or 0.0) - profit_per_unit
                        item_cogs = cost_per_unit * item.quantity
                        item_net_profit = profit_per_unit * item.quantity

                        total_revenue += item_revenue
                        total_cogs += item_cogs
                        total_net_profit += item_net_profit
                        daily_profit[purchase_date_str] += item_net_profit

                        aggregator = product_aggregator[item.blog_post_id]
                        aggregator["title"] = item.blog_post.title
                        aggregator["units"] += item.quantity
                        aggregator["revenue"] += item_revenue
                        aggregator["net_profit"] += item_net_profit
                        aggregator["cogs"] += item_cogs
            
            shipping_profit_loss = total_shipping_collected - total_actual_shipping_cost
            grand_total_net_profit = total_net_profit + shipping_profit_loss
            avg_order_value = total_revenue / total_sales_count if total_sales_count > 0 else 0
            profit_margin = (grand_total_net_profit / total_revenue) * 100 if total_revenue > 0 else 0

            self.finance_stats = FinanceStatsDTO(
                total_revenue_cop=format_to_cop(total_revenue),
                total_cogs_cop=format_to_cop(total_cogs),
                total_profit_cop=format_to_cop(grand_total_net_profit),
                total_shipping_cop=format_to_cop(total_shipping_collected),
                shipping_profit_loss_cop=format_to_cop(shipping_profit_loss),
                total_sales_count=total_sales_count,
                average_order_value_cop=format_to_cop(avg_order_value),
                profit_margin_percentage=f"{profit_margin:.2f}%"
            )

            self.product_finance_data = sorted([
                ProductFinanceDTO(
                    product_id=pid,
                    title=data["title"],
                    units_sold=data["units"],
                    total_revenue_cop=format_to_cop(data["revenue"]),
                    total_cogs_cop=format_to_cop(data["cogs"]),
                    total_net_profit_cop=format_to_cop(data["net_profit"]),
                    profit_margin_str=f"{(data['net_profit'] / data['revenue'] * 100):.2f}%" if data.get('revenue', 0) > 0 else "0.00%"
                ) for pid, data in product_aggregator.items()
            ], key=lambda x: x.units_sold, reverse=True)

            if daily_profit:
                sorted_dates = sorted(daily_profit.keys())
                self.profit_chart_data = [{"date": date, "Ganancia": daily_profit[date]} for date in sorted_dates]
            else:
                self.profit_chart_data = []

        self.is_loading = False

    @rx.event
    def export_product_finance_csv(self):
        """
        Genera un archivo CSV a partir de los datos filtrados de rendimiento
        por producto y lo descarga en el navegador del usuario.
        """
        if not self.filtered_product_finance_data:
            return rx.toast.info("No hay datos para exportar.")

        output = io.StringIO()
        writer = csv.writer(output)

        # Escribir la fila de encabezado
        headers = [
            "Producto", "Unidades Vendidas", "Ingresos", 
            "Costo Total", "Ganancia Neta", "Margen de Ganancia (%)"
        ]
        writer.writerow(headers)

        # Escribir los datos de cada producto
        for p_data in self.filtered_product_finance_data:
            writer.writerow([
                p_data.title,
                p_data.units_sold,
                p_data.total_revenue_cop,
                p_data.total_cogs_cop,
                p_data.total_net_profit_cop,
                p_data.profit_margin_str
            ])
        
        output.seek(0)
        return rx.download(data=output.getvalue(), filename="rendimiento_productos.csv")

    # --- Funciones de formulario de publicación ---

    def _clear_add_form(self):
        self.title = ""
        self.content = ""
        self.price_str = ""
        self.profit_str = ""
        self.category = ""
        self.temp_images = []
        self.new_variants = []
        self.selected_variant_index = -1
        self.attr_colores = ""
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
        self.variant_form_data = []
        self.generated_variants_map = {}

    # --- 👇 AÑADE ESTAS VARIABLES PARA EL FORMULARIO 👇 ---
    shipping_cost_str: str = ""
    #free_shipping_threshold_str: str = ""
    # --- 👇 AÑADE ESTA LÍNEA 👇 ---
    is_moda_completa: bool = True # Activo por defecto

    # --- 👇 AÑADE ESTE NUEVO MÉTODO 👇 ---
    def set_is_moda_completa(self, value: bool):
        self.is_moda_completa = value

    @rx.var
    def current_path(self) -> str:
        """Devuelve la ruta de la página actual."""
        # --- CORRECCIÓN ---
        return self.router.url

    # --- 👇 AÑADE ESTAS VARIABLES PARA LOS FILTROS 👇 ---
    filter_free_shipping: bool = False
    filter_complete_fashion: bool = False
        
    # --- ✨ INICIO: AÑADE ESTA NUEVA VARIABLE ✨ ---
    mis_publicaciones_list: list[AdminPostRowData] = []
    # --- ✨ FIN: AÑADE ESTA NUEVA VARIABLE ✨ ---

    @rx.event
    def load_mis_publicaciones(self):
        """
        Carga explícitamente las publicaciones para la página 'Mis Publicaciones'
        basándose en el contexto del usuario.
        """
        owner_id = self.context_user_id or (self.authenticated_user_info.id if self.authenticated_user_info else None)

        if not owner_id:
            self.mis_publicaciones_list = []
            return

        base_url = get_config().deploy_url

        with rx.session() as session:
            posts_from_db = session.exec(
                sqlmodel.select(BlogPostModel)
                .options(
                    sqlalchemy.orm.joinedload(BlogPostModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(BlogPostModel.creator).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(BlogPostModel.last_modified_by).joinedload(UserInfo.user)
                )
                .where(BlogPostModel.userinfo_id == owner_id)
                .order_by(BlogPostModel.created_at.desc())
            ).all()

            admin_posts = []
            for p in posts_from_db:
                # ... (La lógica para construir el DTO AdminPostRowData se mantiene igual)
                main_image = p.variants[0].get("image_url", "") if p.variants else ""
                creator_username = p.creator.user.username if p.creator and p.creator.user else None
                owner_username = p.userinfo.user.username if p.userinfo and p.userinfo.user else "Vendedor"
                modifier_username = p.last_modified_by.user.username if p.last_modified_by and p.last_modified_by.user else None
                variants_dto_list = [] # Lógica para llenar variants_dto_list

                admin_posts.append(
                    AdminPostRowData(
                        id=p.id,
                        title=p.title,
                        price_cop=p.price_cop,
                        publish_active=p.publish_active,
                        main_image_url=main_image,
                        variants=variants_dto_list,
                        creator_name=creator_username,
                        owner_name=owner_username,
                        last_modified_by_name=modifier_username
                    )
                )

            # Guardamos el resultado en la nueva variable de estado
            self.mis_publicaciones_list = admin_posts

    @rx.event
    def delete_post(self, post_id: int):
        """
        [CORREGIDO] Elimina una publicación, con permisos para empleados
        y eliminando la restricción de si tiene compras asociadas.
        """
        if not self.authenticated_user_info:
            return rx.toast.error("Acción no permitida.")

        with rx.session() as session:
            post_to_delete = session.get(BlogPostModel, post_id)

            # --- ✨ CORRECCIÓN DE PERMISOS CLAVE ✨ ---
            if not post_to_delete or post_to_delete.userinfo_id != self.context_user_id:
                yield rx.toast.error("No tienes permiso para eliminar esta publicación.")
                return
            # --- ✨ FIN DE LA CORRECCIÓN ✨ ---
            
            # --- Eliminamos la restricción de compras existentes ---
            
            session.delete(post_to_delete)
            session.commit()
            
            yield rx.toast.success("Publicación eliminada correctamente.")
            yield AppState.on_load_admin_store

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

    # Variables de estado para el proceso de pago
    checkout_url: str = ""
    is_payment_processing: bool = False

    # --- ✨ AÑADE ESTA NUEVA VARIABLE DE ESTADO ---
    sistecredito_polling_purchase_id: Optional[int] = None

    @rx.event
    async def handle_checkout(self):
        """
        [VERSIÓN FINAL CORREGIDA] Procesa la compra, enrutando a Sistecredito, 
        Wompi (Online) o Contra Entrega según la selección del usuario.
        """
        if not self.is_authenticated or not self.default_shipping_address:
            yield rx.toast.error("Por favor, inicia sesión y selecciona una dirección predeterminada.")
            return
        if not self.authenticated_user_info:
            yield rx.toast.error("Error de sesión. Vuelve a iniciar sesión.")
            return
        if not self.cart:
            yield rx.toast.info("Tu carrito está vacío.")
            return

        summary = self.cart_summary
        
        # --- ✨ CORRECCIÓN CLAVE: Inicializamos la lista aquí al principio ✨ ---
        items_to_create = []

        if self.payment_method == "Sistecredito":
            with rx.session() as session:
                product_ids = list(set([int(key.split('-')[0]) for key in self.cart.keys()]))
                posts_to_check = session.exec(
                    sqlmodel.select(BlogPostModel).where(BlogPostModel.id.in_(product_ids)).with_for_update()
                ).all()
                post_map = {p.id: p for p in posts_to_check}

                for cart_key, quantity_in_cart in self.cart.items():
                    parts = cart_key.split('-')
                    prod_id = int(parts[0])
                    selection_attrs = dict(part.split(':', 1) for part in parts[2:] if ':' in part)
                    post = post_map.get(prod_id)
                    if not post:
                        yield rx.toast.error("Uno de los productos ya no está disponible. Compra cancelada.")
                        return
                    
                    variant_found = False
                    for variant in post.variants:
                        if variant.get("attributes") == selection_attrs:
                            if variant.get("stock", 0) < quantity_in_cart:
                                attr_str = ', '.join(selection_attrs.values())
                                yield rx.toast.error(f"Stock insuficiente para '{post.title} ({attr_str})'. Compra cancelada.")
                                return
                            variant_found = True
                            break
                    if not variant_found:
                        yield rx.toast.error(f"La variante para '{post.title}' ya no existe. Compra cancelada.")
                        return

                new_purchase = PurchaseModel(
                    userinfo_id=self.authenticated_user_info.id,
                    total_price=summary["grand_total"],
                    status=PurchaseStatus.PENDING_SISTECREDITO_URL,
                    payment_method=self.payment_method,
                    shipping_applied=summary["shipping_cost"],
                    shipping_name=self.default_shipping_address.name,
                    shipping_city=self.default_shipping_address.city,
                    shipping_neighborhood=self.default_shipping_address.neighborhood,
                    shipping_address=self.default_shipping_address.address,
                    shipping_phone=self.default_shipping_address.phone,
                )
                session.add(new_purchase)
                session.commit()
                session.refresh(new_purchase)

                for cart_key, quantity_in_cart in self.cart.items():
                    parts = cart_key.split('-')
                    prod_id = int(parts[0])
                    selection_attrs = dict(part.split(':', 1) for part in parts[2:] if ':' in part)
                    post_to_update = post_map.get(prod_id)
                    if post_to_update:
                        for variant in post_to_update.variants:
                            if variant.get("attributes") == selection_attrs:
                                variant["stock"] -= quantity_in_cart
                                break
                        session.add(post_to_update)
                        session.add(PurchaseItemModel(
                            purchase_id=new_purchase.id,
                            blog_post_id=post_to_update.id,
                            quantity=quantity_in_cart,
                            price_at_purchase=post_to_update.price,
                            selected_variant=selection_attrs,
                        ))
                session.commit()

                purchase_data_for_api = {
                    "purchase_id": new_purchase.id,
                    "total_price": new_purchase.total_price * 100,
                    "tax": summary.get("iva", 0) * 100,
                    "tax_base": summary.get("subtotal", 0) * 100,
                    "client_document": "1061796101",
                    "client_name": self.default_shipping_address.name.split(' ')[0],
                    "client_lastname": ' '.join(self.default_shipping_address.name.split(' ')[1:]),
                    "client_email": self.authenticated_user_info.email,
                    "client_phone": self.default_shipping_address.phone,
                    "shipping_city": self.default_shipping_address.city,
                    "shipping_address": self.default_shipping_address.address,
                    "url_response": f"{self.base_app_url}/my-purchases",
                    "url_confirmation": f"{get_config().api_url}/webhooks/sistecredito",
                }

                sistecredito_id = await sistecredito_service.create_sistecredito_transaction(purchase_data_for_api)

                if sistecredito_id:
                    new_purchase.sistecredito_transaction_id = sistecredito_id
                    session.add(new_purchase)
                    session.commit()
                    self.sistecredito_polling_purchase_id = new_purchase.id
                    self.cart.clear()
                    yield rx.redirect("/processing-payment")
                    return
                else:
                    new_purchase.status = PurchaseStatus.FAILED
                    session.add(new_purchase)
                    session.commit()
                    yield rx.toast.error("No se pudo iniciar el pago con Sistecredito. Inténtalo de nuevo.")
                    return
        
        else: # Lógica para Wompi (Online) y Contra Entrega
            purchase_id_for_payment = None
            total_price_for_payment = None

            with rx.session() as session:
                product_ids = list(set([int(key.split('-')[0]) for key in self.cart.keys()]))
                posts_to_check = session.exec(
                    sqlmodel.select(BlogPostModel).where(BlogPostModel.id.in_(product_ids)).with_for_update()
                ).all()
                post_map = {p.id: p for p in posts_to_check}

                for cart_key, quantity_in_cart in self.cart.items():
                    parts = cart_key.split('-')
                    prod_id = int(parts[0])
                    selection_attrs = dict(part.split(':', 1) for part in parts[2:] if ':' in part)
                    post = post_map.get(prod_id)
                    if not post:
                        yield rx.toast.error("Uno de los productos ya no está disponible. Compra cancelada.")
                        return
                    
                    variant_found = False
                    for variant in post.variants:
                        if variant.get("attributes") == selection_attrs:
                            if variant.get("stock", 0) < quantity_in_cart:
                                attr_str = ', '.join(selection_attrs.values())
                                yield rx.toast.error(f"Stock insuficiente para '{post.title} ({attr_str})'. Compra cancelada.")
                                return
                            variant_found = True
                            break
                    if not variant_found:
                        yield rx.toast.error(f"La variante para '{post.title}' ya no existe. Compra cancelada.")
                        return

                initial_status = PurchaseStatus.PENDING_PAYMENT if self.payment_method == "Online" else PurchaseStatus.PENDING_CONFIRMATION
                
                new_purchase = PurchaseModel(
                    userinfo_id=self.authenticated_user_info.id,
                    total_price=summary["grand_total"],
                    shipping_applied=summary["shipping_cost"],
                    status=initial_status,
                    payment_method=self.payment_method,
                    shipping_name=self.default_shipping_address.name,
                    shipping_city=self.default_shipping_address.city,
                    shipping_neighborhood=self.default_shipping_address.neighborhood,
                    shipping_address=self.default_shipping_address.address,
                    shipping_phone=self.default_shipping_address.phone,
                )
                session.add(new_purchase)
                session.commit()
                session.refresh(new_purchase)

                purchase_id_for_payment = new_purchase.id
                total_price_for_payment = new_purchase.total_price

                for cart_key, quantity_in_cart in self.cart.items():
                    parts = cart_key.split('-')
                    prod_id = int(parts[0])
                    selection_attrs = dict(part.split(':', 1) for part in parts[2:] if ':' in part)
                    post_to_update = post_map.get(prod_id)
                    if post_to_update:
                        for variant in post_to_update.variants:
                            if variant.get("attributes") == selection_attrs:
                                variant["stock"] -= quantity_in_cart
                                break
                        session.add(post_to_update)
                        item = PurchaseItemModel(
                            purchase_id=new_purchase.id,
                            blog_post_id=post_to_update.id,
                            quantity=quantity_in_cart,
                            price_at_purchase=post_to_update.price,
                            selected_variant=selection_attrs,
                        )
                        session.add(item)
                        items_to_create.append(item)
                session.commit()

            if self.payment_method == "Online":
                if purchase_id_for_payment is None:
                    yield rx.toast.error("Error crítico: No se pudo obtener el ID de la compra.")
                    return

                payment_info = await wompi_service.create_wompi_payment_link(
                    purchase_id=purchase_id_for_payment,
                    total_price=total_price_for_payment
                )

                if payment_info:
                    payment_url, payment_link_id = payment_info
                    with rx.session() as session:
                        purchase_to_update = session.get(PurchaseModel, purchase_id_for_payment)
                        if purchase_to_update:
                            purchase_to_update.wompi_payment_link_id = payment_link_id
                            session.add(purchase_to_update)
                            session.commit()
                    self.cart.clear()
                    self.default_shipping_address = None
                    yield rx.call_script(f"window.location.href = '{payment_url}'")
                    return
                else:
                    yield rx.toast.error("No se pudo generar el enlace de pago. Intenta de nuevo desde tu historial de compras.")
                    return

            else:  # Pago Contra Entrega
                self.cart.clear()
                self.default_shipping_address = None
                
                with rx.session() as session:
                    seller_groups = defaultdict(list)
                    for item in items_to_create:
                        post_owner_id = post_map[item.blog_post_id].userinfo_id
                        seller_groups[post_owner_id].append(item.blog_post_id)

                    for seller_id, product_ids in seller_groups.items():
                        notification = NotificationModel(
                            userinfo_id=seller_id,
                            message=f"¡Nueva orden (#{new_purchase.id}) recibida! Tienes productos pendientes de confirmar.",
                            url="/admin/confirm-payments"
                        )
                        session.add(notification)
                    session.commit()

                yield rx.toast.success("¡Gracias por tu compra! Tu orden está pendiente de confirmación.")
                yield rx.redirect("/my-purchases")
                return
            
        
    # 🟡 REEMPLAZA esta función en tu archivo 🟡
    @rx.event
    async def start_sistecredito_polling(self):
        """
        [CORREGIDO] Inicia el proceso de sondeo al cargar la página de procesamiento.
        """
        if not self.sistecredito_polling_purchase_id:
            yield rx.toast.error("Error: No se encontró una compra para procesar.")
            yield rx.redirect("/cart")
            return

        with rx.session() as session:
            purchase = session.get(PurchaseModel, self.sistecredito_polling_purchase_id)
            if not purchase or not purchase.sistecredito_transaction_id:
                yield rx.toast.error("Error de consistencia de datos.")
                yield rx.redirect("/cart")
                return
            
            transaction_id = purchase.sistecredito_transaction_id

        self.sistecredito_polling_purchase_id = None
        redirect_url = await sistecredito_service.poll_for_redirect_url(transaction_id)

        if redirect_url:
            # Éxito: redirigir al usuario a Sistecredito
            # --- ✨ INICIO DE LA CORRECCIÓN ✨ ---
            # Usamos rx.call_script para la redirección externa.
            yield rx.call_script(f"window.location.href = '{redirect_url}'")
            # --- ✨ FIN DE LA CORRECCIÓN ✨ ---
        else:
            # Falla: notificar y redirigir de vuelta al carrito
            yield rx.toast.error("Sistecredito no pudo procesar tu solicitud. Por favor, intenta de nuevo.") # [cite: 1822]
            yield rx.redirect("/cart")


    # --- ✨ AÑADE ESTE NUEVO EVENT HANDLER COMPLETO ---
    @rx.event
    async def confirm_sistecredito_on_redirect(self, transaction_id: str):
        """Verifica el estado de una transacción de Sistecredito cuando el usuario regresa al sitio."""
        yield rx.toast.info("Verificando estado del pago con Sistecredito...")
        verified_data = await sistecredito_service.verify_transaction_status(transaction_id)
        
        if verified_data and verified_data.get("transactionStatus") == "Approved":
            with rx.session() as session:
                purchase = session.exec(
                    sqlmodel.select(PurchaseModel).where(PurchaseModel.sistecredito_transaction_id == transaction_id)
                ).one_or_none()
                if purchase and purchase.status != PurchaseStatus.CONFIRMED:
                    purchase.status = PurchaseStatus.CONFIRMED
                    purchase.confirmed_at = datetime.now(timezone.utc)
                    purchase.sistecredito_authorization_code = verified_data.get("paymentMethodResponse", {}).get("authorizationCode")
                    purchase.sistecredito_invoice = verified_data.get("invoice")
                    session.add(purchase)
                    session.commit()
                    yield self.load_purchases # Recarga la vista
                    yield rx.toast.success("¡Tu pago con Sistecredito ha sido confirmado!")
        else:
            yield rx.toast.warning("El pago aún no ha sido aprobado. El estado se actualizará automáticamente.")
    
    async def process_wompi_confirmation(self, event_data: dict):
        """
        Este EventHandler recibe los datos del webhook y actualiza la BD de forma segura.
        """
        async with self.session() as session:
            try:
                transaction_data = event_data.get("data", {}).get("transaction", {})
                status = transaction_data.get("status")
                payment_link_id = transaction_data.get("payment_link_id")

                if status != "APPROVED" or not payment_link_id:
                    print(f"EventHandler ignorado: status={status}")
                    return

                purchase_query = sqlmodel.select(PurchaseModel).where(
                    PurchaseModel.wompi_payment_link_id == payment_link_id
                )
                purchase = (await session.exec(purchase_query)).one_or_none()

                if not purchase:
                    print(f"EventHandler: Compra con link_id '{payment_link_id}' no encontrada.")
                    return

                if purchase.status != PurchaseStatus.CONFIRMED:
                    purchase.status = PurchaseStatus.CONFIRMED
                    purchase.confirmed_at = datetime.now(timezone.utc)
                    purchase.wompi_transaction_id = transaction_data.get("id")
                    session.add(purchase)
                    await session.commit()
                    print(f"¡ÉXITO! EventHandler actualizó la compra #{purchase.id} a CONFIRMED.")
                else:
                    print(f"EventHandler: Compra #{purchase.id} ya estaba confirmada.")

            except Exception as e:
                print(f"ERROR en EventHandler process_wompi_confirmation: {e}")

    @rx.event
    async def confirm_payment_on_redirect(self, wompi_tx_id: str):
        """
        [VERSIÓN FINAL] Verifica una transacción y la actualiza buscando por el
        payment_link_id, que es el método más fiable.
        """
        yield rx.toast.info("Verificando estado del pago...")
        
        transaction_details = await wompi_service.get_wompi_transaction_details(wompi_tx_id)
        
        if transaction_details and transaction_details.get("status") == "APPROVED":
            # Extraemos el payment_link_id, nuestro identificador fiable
            payment_link_id = transaction_details.get("payment_link_id")
            
            if not payment_link_id:
                yield rx.toast.error("La transacción de Wompi no tiene un ID de enlace de pago asociado.")
                return

            with rx.session() as session:
                # Buscamos la compra en NUESTRA base de datos usando el payment_link_id
                purchase_to_update = session.exec(
                    sqlmodel.select(PurchaseModel).where(PurchaseModel.wompi_payment_link_id == payment_link_id)
                ).one_or_none()

                if purchase_to_update and purchase_to_update.status == PurchaseStatus.PENDING_PAYMENT:
                    # Si la encontramos y está pendiente, la confirmamos
                    purchase_to_update.status = PurchaseStatus.CONFIRMED
                    purchase_to_update.confirmed_at = datetime.now(timezone.utc)
                    purchase_to_update.wompi_transaction_id = wompi_tx_id # Guardamos el ID de la transacción final
                    session.add(purchase_to_update)
                    session.commit()
                    
                    yield rx.toast.success("¡Tu pago ha sido confirmado!")
                    yield AppState.load_purchases
                elif purchase_to_update:
                    yield rx.toast.info("Este pago ya había sido confirmado.")
                else:
                    yield rx.toast.error(f"No se encontró una compra correspondiente al enlace de pago.")
        else:
            yield rx.toast.warning("El pago aún no ha sido aprobado. El estado se actualizará con la tarea automática.")

    @rx.event
    async def on_load_purchases_page(self):
        """
        Se ejecuta al cargar la página de compras. Carga el historial
        y verifica si viene de una redirección de Wompi.
        """
        # Primero, intenta verificar un pago si la URL contiene el ID
        try:
            # --- CORRECCIÓN ---
            full_url = self.router.url
            if full_url and "?" in full_url:
                query_params = parse_qs(full_url.split("?")[1])
                wompi_id = query_params.get("id", [None])[0]
                if wompi_id:
                    yield AppState.confirm_payment_on_redirect(wompi_id)

                sistecredito_id = query_params.get("paymentRef", [None])[0]
                if sistecredito_id:
                    yield AppState.confirm_sistecredito_on_redirect(sistecredito_id)
        except Exception as e:
            print(f"Error al parsear la URL de redirección: {e}")

        yield AppState.load_purchases
        yield AppState.check_for_auto_confirmations

    def toggle_form(self):
        self.show_form = not self.show_form
    def set_city(self, city: str): self.city = city; self.neighborhood = ""
    def set_neighborhood(self, hood: str): self.neighborhood = hood
    def set_search_city(self, query: str): self.search_city = query
    def set_search_neighborhood(self, query: str): self.search_neighborhood = query
    
    @rx.var
    def cities(self) -> List[str]:
        """
        CORREGIDO: Ahora usa la lista completa de TODAS las ciudades.
        """
        if not self.search_city.strip():
            return ALL_CITIES # Usa la lista completa
        
        query = self.search_city.lower()
        return [c for c in ALL_CITIES if query in c.lower()]

    @rx.var
    def neighborhoods(self) -> List[str]:
        """
        CORREGIDO: Ahora usa el diccionario maestro para obtener los barrios
        de CUALQUIER ciudad seleccionada.
        """
        if not self.city:
            return []  # Si no hay ciudad, no hay barrios
        
        # Busca en nuestro gran diccionario la lista de barrios para la ciudad actual
        all_hoods = COLOMBIA_LOCATIONS.get(self.city, [])
        
        if not self.search_neighborhood.strip():
            return sorted(all_hoods)
        
        query = self.search_neighborhood.lower()
        return sorted([n for n in all_hoods if query in n.lower()])

    # --- FIN DE LA CORRECIÓN ---

    @rx.event
    def recalculate_all_shipping_costs(self):
        """
        Recalcula el costo de envío para cada producto basado en la dirección
        del comprador y la ciudad/barrio del vendedor.
        """
        if not self._raw_posts:
            self.posts = []
            return

        # Si no hay dirección, los costos vuelven a ser los base
        if not self.default_shipping_address:
            self.posts = self._raw_posts
            return

        # --- INICIO DE LA MODIFICACIÓN ---
        buyer_city = self.default_shipping_address.city
        buyer_barrio = self.default_shipping_address.neighborhood
        # --- FIN DE LA MODIFICACIÓN ---
        
        with rx.session() as session:
            seller_ids = {p.userinfo_id for p in self._raw_posts}
            sellers_info = session.exec(
                sqlmodel.select(UserInfo).where(UserInfo.id.in_(list(seller_ids)))
            ).all()
            # --- INICIO DE LA MODIFICACIÓN ---
            # Obtenemos un mapa con la ciudad y el barrio de cada vendedor
            seller_data_map = {info.id: {"city": info.seller_city, "barrio": info.seller_barrio} for info in sellers_info}
            # --- FIN DE LA MODIFICACIÓN ---

            recalculated_posts = []
            for post in self._raw_posts:
                # --- INICIO DE LA MODIFICACIÓN ---
                seller_data = seller_data_map.get(post.userinfo_id)
                seller_city = seller_data.get("city") if seller_data else None
                seller_barrio = seller_data.get("barrio") if seller_data else None
                
                final_shipping_cost = calculate_dynamic_shipping(
                    base_cost=post.shipping_cost or 0.0,
                    seller_barrio=seller_barrio,
                    buyer_barrio=buyer_barrio,
                    # Pasamos los nuevos argumentos a la llamada
                    seller_city=seller_city,
                    buyer_city=buyer_city
                )
                # --- FIN DE LA MODIFICACIÓN ---

                updated_post = post.copy()
                updated_post.shipping_display_text = f"Envío: {format_to_cop(final_shipping_cost)}" if final_shipping_cost > 0 else "Envío a convenir"
                
                recalculated_posts.append(updated_post)

        self.posts = recalculated_posts


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
        """
        Permite al usuario confirmar que ha recibido un pedido.
        Cambia el estado de SHIPPED a DELIVERED.
        """
        if not self.authenticated_user_info:
            return rx.toast.error("Debes iniciar sesión.")

        with rx.session() as session:
            purchase = session.get(PurchaseModel, purchase_id)
            
            # Doble chequeo de seguridad: el usuario debe ser el dueño y la compra debe estar en estado "Enviado"
            if purchase and purchase.userinfo_id == self.authenticated_user_info.id and purchase.status == PurchaseStatus.SHIPPED:
                purchase.status = PurchaseStatus.DELIVERED
                purchase.user_confirmed_delivery_at = datetime.now(timezone.utc)
                session.add(purchase)
                
                # Opcional: Notificar al usuario que ya puede calificar el producto
                notification = NotificationModel(
                    userinfo_id=purchase.userinfo_id,
                    message=f"¡Gracias por confirmar! Ya puedes calificar los productos de tu compra #{purchase.id}.",
                    url="/my-purchases"
                )
                session.add(notification)
                session.commit()

                # Recargamos la lista de compras para que la UI se actualice al instante
                yield AppState.load_purchases
                yield rx.toast.success("¡Entrega confirmada! Gracias por tu compra.")
            else:
                yield rx.toast.error("No se pudo confirmar la entrega para esta compra.")

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

    # 1. La variable para el término de búsqueda de la tienda de administración.
    search_term: str = ""

    # 2. La función para actualizar la variable (setter).
    def set_search_term(self, term: str):
        self.search_term = term

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
    managed_users: list[UserManagementDTO] = []
    admin_store_posts: list[ProductCardData] = []
    show_admin_sidebar: bool = False

    def set_new_purchase_notification(self, value: bool):
        self.new_purchase_notification = value

    @rx.event
    def notify_admin_of_new_purchase(self):
        self.new_purchase_notification = True

    # --- ✨ MÉTODO MODIFICADO: `load_purchase_history` (para Admin) ✨ ---
    @rx.event
    def load_purchase_history(self):
        """
        [CORREGIDO] Carga el historial de compras finalizadas, incluyendo el nombre
        del usuario que realizó la última acción.
        """
        if not (self.is_admin or self.is_vendedor or self.is_empleado):
            self.purchase_history = []
            return

        with rx.session() as session:
            user_id_to_check = self.context_user_info.id if self.context_user_info else (self.authenticated_user_info.id if self.authenticated_user_info else 0)

            results = session.exec(
                sqlmodel.select(PurchaseModel)
                .options(
                    sqlalchemy.orm.joinedload(PurchaseModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post),
                    # --- ✨ INICIO: AÑADIMOS LA CARGA DEL USUARIO DE LA ACCIÓN ✨ ---
                    sqlalchemy.orm.joinedload(PurchaseModel.action_by).joinedload(UserInfo.user)
                    # --- ✨ FIN: AÑADIMOS LA CARGA DEL USUARIO DE LA ACCIÓN ✨ ---
                )
                .where(
                    PurchaseModel.status.in_([PurchaseStatus.DELIVERED, PurchaseStatus.DIRECT_SALE]),
                    PurchaseItemModel.blog_post.has(BlogPostModel.userinfo_id == user_id_to_check)
                )
                .join(PurchaseItemModel)
                .order_by(PurchaseModel.purchase_date.desc())
            ).unique().all()
            
            temp_history = []
            for p in results:
                # ... (la lógica para `detailed_items` se mantiene igual)
                detailed_items = [] # Tu lógica para llenar detailed_items va aquí

                # --- ✨ INICIO: OBTENEMOS EL NOMBRE DEL USUARIO DE LA ACCIÓN ✨ ---
                actor_name = p.action_by.user.username if p.action_by and p.action_by.user else None
                # --- ✨ FIN: OBTENEMOS EL NOMBRE DEL USUARIO DE LA ACCIÓN ✨ ---

                temp_history.append(
                    AdminPurchaseCardData(
                        id=p.id,
                        customer_name=p.userinfo.user.username,
                        customer_email=p.userinfo.email,
                        purchase_date_formatted=p.purchase_date_formatted,
                        status=p.status.value,
                        total_price=p.total_price,
                        shipping_applied=p.shipping_applied,
                        shipping_name=p.shipping_name,
                        shipping_full_address=f"{p.shipping_address}, {p.shipping_neighborhood}, {p.shipping_city}",
                        shipping_phone=p.shipping_phone, 
                        payment_method=p.payment_method,
                        confirmed_at=p.confirmed_at,
                        items=detailed_items,
                        # --- ✨ INICIO: PASAMOS EL DATO AL DTO ✨ ---
                        action_by_name=actor_name
                        # --- ✨ FIN: PASAMOS EL DATO AL DTO ✨ ---
                    )
                )
            self.purchase_history = temp_history

    @rx.var
    def active_purchase_items_map(self) -> dict[int, list[PurchaseItemCardData]]:
        """
        Crea un diccionario que mapea el ID de una compra ACTIVA a su lista de artículos.
        Esto evita el acceso anidado (purchase.items) que causa el error de compilación.
        """
        return {p.id: p.items for p in self.active_purchases}
    
    # --- ✨ INICIO DE LA SOLUCIÓN DEFINITIVA PARA EL HISTORIAL ✨ ---
    @rx.var
    def purchase_history_items_map(self) -> dict[int, list[PurchaseItemCardData]]:
        """
        Crea un diccionario que mapea el ID de una compra del HISTORIAL a su lista de artículos.
        Esto evita el acceso anidado (purchase.items) que causa el error de compilación.
        """
        return {p.id: p.items for p in self.purchase_history}
    # --- ✨ FIN DE LA SOLUCIÓN DEFINITIVA ✨ ---

    @rx.event
    def load_active_purchases(self):
        """
        [CORREGIDO] Carga las compras activas, incluyendo el nombre del usuario
        que realizó la última acción sobre ellas.
        """
        if not (self.is_admin or self.is_vendedor or self.is_empleado): 
            return

        self.new_purchase_notification = False
        
        with rx.session() as session:
            user_id_to_check = self.context_user_info.id if self.context_user_info else (self.authenticated_user_info.id if self.authenticated_user_info else 0)
            
            purchases = session.exec(
                sqlmodel.select(PurchaseModel)
                .options(
                    sqlalchemy.orm.joinedload(PurchaseModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post),
                    # --- ✨ INICIO: AÑADIMOS LA CARGA DEL USUARIO DE LA ACCIÓN ✨ ---
                    sqlalchemy.orm.joinedload(PurchaseModel.action_by).joinedload(UserInfo.user)
                    # --- ✨ FIN: AÑADIMOS LA CARGA DEL USUARIO DE LA ACCIÓN ✨ ---
                )
                .where(
                    PurchaseModel.status.in_([
                        PurchaseStatus.PENDING_CONFIRMATION,
                        PurchaseStatus.CONFIRMED,
                        PurchaseStatus.SHIPPED,
                    ]),
                    # Aseguramos que solo cargue los pedidos del vendedor correcto
                    PurchaseItemModel.blog_post.has(BlogPostModel.userinfo_id == user_id_to_check)
                )
                .join(PurchaseItemModel)
                .order_by(PurchaseModel.purchase_date.asc())
            ).unique().all()
            
            active_purchases_list = []
            for p in purchases:
                # ... (la lógica para `detailed_items` se mantiene igual)
                detailed_items = [] # Tu lógica para llenar detailed_items va aquí
                
                # --- ✨ INICIO: OBTENEMOS EL NOMBRE DEL USUARIO DE LA ACCIÓN ✨ ---
                actor_name = p.action_by.user.username if p.action_by and p.action_by.user else None
                # --- ✨ FIN: OBTENEMOS EL NOMBRE DEL USUARIO DE LA ACCIÓN ✨ ---

                active_purchases_list.append(
                    AdminPurchaseCardData(
                        id=p.id,
                        customer_name=p.userinfo.user.username if p.userinfo and p.userinfo.user else "N/A", 
                        customer_email=p.userinfo.email if p.userinfo else "N/A",
                        purchase_date_formatted=p.purchase_date_formatted,
                        status=p.status.value, 
                        total_price=p.total_price,
                        payment_method=p.payment_method,
                        confirmed_at=p.confirmed_at,
                        shipping_applied=p.shipping_applied,
                        shipping_name=p.shipping_name, 
                        shipping_full_address=f"{p.shipping_address}, {p.shipping_neighborhood}, {p.shipping_city}",
                        shipping_phone=p.shipping_phone,
                        items=detailed_items,
                        # --- ✨ INICIO: PASAMOS EL DATO AL DTO ✨ ---
                        action_by_name=actor_name
                        # --- ✨ FIN: PASAMOS EL DATO AL DTO ✨ ---
                    )
                )
            self.active_purchases = active_purchases_list

    # --- AÑADE ESTA NUEVA FUNCIÓN COMPLETA ---
    @rx.event
    def poll_for_new_orders(self):
        """
        Verifica periódicamente si hay nuevas órdenes que requieran acción
        y activa la notificación sin recargar toda la data.
        """
        if not self.is_admin:
            return

        with rx.session() as session:
            # Busca órdenes que requieran la primera acción del admin
            new_order_to_confirm = session.exec(
                sqlmodel.select(PurchaseModel.id).where(
                    PurchaseModel.status.in_([
                        PurchaseStatus.PENDING_CONFIRMATION,
                        PurchaseStatus.CONFIRMED
                    ])
                )
            ).first()

            # Si encuentra al menos una, activa la notificación
            if new_order_to_confirm:
                self.new_purchase_notification = True

    def _update_shipping_and_notify(self, session, purchase, total_delta):
        """
        Función auxiliar que centraliza la lógica para actualizar el envío, 
        guardar el costo final y notificar al cliente.
        """
        # 1. Guarda el costo de envío final ingresado por el admin
        try:
            final_shipping_cost_str = self.admin_final_shipping_cost.get(purchase.id)
            # Si el admin ingresó un valor, lo usamos. Si no, usamos el costo inicial cargado a la compra.
            purchase.actual_shipping_cost = float(final_shipping_cost_str) if final_shipping_cost_str else purchase.shipping_applied
        except (ValueError, TypeError):
            # Si el valor ingresado no es un número válido, usamos el costo inicial como respaldo.
            purchase.actual_shipping_cost = purchase.shipping_applied
        
        # 2. Actualiza el estado y las fechas del pedido
        purchase.status = PurchaseStatus.SHIPPED
        purchase.estimated_delivery_date = datetime.now(timezone.utc) + total_delta
        purchase.delivery_confirmation_sent_at = datetime.now(timezone.utc)
        # --- ✨ CORRECCIÓN CLAVE: Guardamos el ID del usuario que actúa ✨ ---
        purchase.action_by_id = self.authenticated_user_info.id
        session.add(purchase)

        # 3. Construye el mensaje de notificación para el cliente
        days = total_delta.days
        hours, remainder = divmod(total_delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        time_parts = []
        if days > 0: time_parts.append(f"{days} día(s)")
        if hours > 0: time_parts.append(f"{hours} hora(s)")
        if minutes > 0: time_parts.append(f"{minutes} minuto(s)")
        
        time_str = ", ".join(time_parts) if time_parts else "pronto"
        mensaje = f"¡Tu compra #{purchase.id} está en camino! 🚚 Llegará en aprox. {time_str}."

        # 4. Crea y guarda la notificación
        notification = NotificationModel(
            userinfo_id=purchase.userinfo_id,
            message=mensaje,
            url="/my-purchases"
        )
        session.add(notification)
        
        # 5. Limpia el valor temporal del formulario para esta orden
        if purchase.id in self.admin_final_shipping_cost:
            del self.admin_final_shipping_cost[purchase.id]

    @rx.event
    def ship_confirmed_online_order(self, purchase_id: int):
        """
        Notifica el envío de un pedido online ya confirmado, utilizando la lógica unificada.
        """
        if not self.is_admin: 
            return rx.toast.error("Acción no permitida.")
        
        # Valida que se haya ingresado un tiempo de entrega
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
                # Llama a la función auxiliar con la lógica compartida
                self._update_shipping_and_notify(session, purchase, total_delta)
                session.commit()
                yield rx.toast.success("Notificación de envío enviada.")
                yield AppState.load_active_purchases
            else:
                yield rx.toast.error("La compra debe estar 'confirmada' para poder notificar el envío.")

    @rx.event
    def ship_pending_cod_order(self, purchase_id: int):
        """
        Envía un pedido Contra Entrega, utilizando la lógica unificada.
        """
        if not self.is_admin: 
            return rx.toast.error("Acción no permitida.")
        
        # La validación del tiempo es idéntica
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
                # Llama a la misma función auxiliar
                self._update_shipping_and_notify(session, purchase, total_delta)
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
            if purchase and purchase.status == PurchaseStatus.PENDING_CONFIRMATION and purchase.payment_method == "Online":
                purchase.status = PurchaseStatus.CONFIRMED
                purchase.confirmed_at = datetime.now(timezone.utc)
                session.add(purchase)

                # --- ✨ INICIO DE LA CORRECCIÓN ✨ ---
                # Notificar al cliente que su pago fue confirmado
                notification = NotificationModel(
                    userinfo_id=purchase.userinfo_id,
                    message=f"¡Tu pago para la compra #{purchase.id} ha sido confirmado! Pronto prepararemos tu envío.",
                    url="/my-purchases"
                )
                session.add(notification)
                # --- ✨ FIN DE LA CORRECCIÓN ✨ ---
                
                session.commit()
                yield rx.toast.success(f"Pago de la compra #{purchase.id} confirmado.")
                yield AppState.load_active_purchases
            else:
                yield rx.toast.error("Esta acción no es válida para este tipo de compra o estado.")
    
    @rx.event
    def confirm_cod_payment_received(self, purchase_id: int):
        """Confirma el pago de un pedido Contra Entrega, registrando al actor."""
        if not self.authenticated_user_info:
            return rx.toast.error("Acción no permitida.")
        
        with rx.session() as session:
            purchase = session.get(PurchaseModel, purchase_id)
            if purchase and purchase.payment_method == "Contra Entrega" and purchase.status in [PurchaseStatus.SHIPPED, PurchaseStatus.DELIVERED]:
                purchase.confirmed_at = datetime.now(timezone.utc)
                
                # --- ✨ CORRECCIÓN CLAVE: Guardamos el ID del usuario que confirma ✨ ---
                purchase.action_by_id = self.authenticated_user_info.id

                session.add(purchase)
                session.commit()
                
                yield rx.toast.success(f"Pago de la compra #{purchase.id} registrado.")
                yield AppState.load_active_purchases
            else:
                yield rx.toast.error("Esta acción no es válida para este pedido.")

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

    # --- ✨ MÉTODO MODIFICADO: `load_purchases` (para User) ✨ ---
    @rx.event
    def load_purchases(self):
        if not self.authenticated_user_info:
            self.user_purchases = []
            return
        with rx.session() as session:
            # ... (la consulta a la base de datos se mantiene igual) ...
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
                            variant_image_url = ""
                            for variant in item.blog_post.variants:
                                if variant.get("attributes") == item.selected_variant:
                                    variant_image_url = variant.get("image_url", "")
                                    break
                            if not variant_image_url and item.blog_post.variants:
                                variant_image_url = item.blog_post.variants[0].get("image_url", "")
                            
                            # --- ✨ CAMBIO 3: Se crea la cadena de texto aquí también ---
                            variant_str = ", ".join([f"{k}: {v}" for k, v in item.selected_variant.items()])

                            purchase_items_data.append(
                                PurchaseItemCardData(
                                    id=item.blog_post.id,
                                    title=item.blog_post.title,
                                    image_url=variant_image_url,
                                    price_at_purchase=item.price_at_purchase,
                                    price_at_purchase_cop=format_to_cop(item.price_at_purchase),
                                    quantity=item.quantity,
                                    variant_details_str=variant_str, # Se asigna la cadena pre-formateada
                                )
                            )
                
                temp_purchases.append(
                    UserPurchaseHistoryCardData(
                        # ... (otros campos del DTO se asignan igual) ...
                        id=p.id, userinfo_id=p.userinfo_id, purchase_date_formatted=p.purchase_date_formatted,
                        status=p.status.value, total_price_cop=p.total_price_cop,
                        shipping_applied_cop=format_to_cop(p.shipping_applied),
                        shipping_name=p.shipping_name, shipping_address=p.shipping_address,
                        shipping_neighborhood=p.shipping_neighborhood, shipping_city=p.shipping_city,
                        shipping_phone=p.shipping_phone, items=purchase_items_data,
                        estimated_delivery_date_formatted=format_utc_to_local(p.estimated_delivery_date)
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
        # --- ✅ USAMOS EL NUEVO NOMBRE ---
        return sum(1 for n in self.user_notifications if not n.is_read)

    def _load_notifications_logic(self):
        """
        [VERSIÓN CON FILTRADO DE URL]
        Carga notificaciones para el comprador, excluyendo explícitamente
        aquellas que pertenecen al panel de administración.
        """
        if self.is_admin or self.is_vendedor or self.is_empleado:
            self.user_notifications = []
            return
        if not self.authenticated_user_info:
            self.user_notifications = []
            return

        with rx.session() as session:
            # --- CORRECCIÓN CLAVE: Añadimos el filtro por URL ---
            notifications_db = session.exec(
                sqlmodel.select(NotificationModel)
                .where(
                    NotificationModel.userinfo_id == self.authenticated_user_info.id,
                    ~NotificationModel.url.startswith("/admin") # El '~' significa 'NO'
                )
                .order_by(sqlmodel.col(NotificationModel.created_at).desc())
                .limit(20)
            ).all()
            self.user_notifications = [NotificationDTO.from_orm(n) for n in notifications_db]


    # Los métodos load_notifications y poll_notifications no cambian,
    # ya que simplemente llaman a _load_notifications_logic.
    @rx.event
    def load_notifications(self):
        self._load_notifications_logic()

    @rx.event
    def poll_notifications(self):
        if self.is_authenticated:
            self._load_notifications_logic()

    @rx.event
    def mark_all_as_read(self):
        if not self.authenticated_user_info:
            return
            
        # --- ✅ USAMOS EL NUEVO NOMBRE ---
        unread_ids = [n.id for n in self.user_notifications if not n.is_read]
        if not unread_ids:
            return
            
        with rx.session() as session:
            stmt = sqlmodel.update(NotificationModel).where(NotificationModel.id.in_(unread_ids)).values(is_read=True)
            session.exec(stmt)
            session.commit()
        
        yield self.load_notifications()

    @rx.event
    def clear_all_notifications(self):
        """
        Elimina permanentemente todas las notificaciones para el usuario actual.
        """
        if not self.authenticated_user_info:
            return

        with rx.session() as session:
            # Crea una declaración de borrado para todas las notificaciones del usuario
            statement = sqlmodel.delete(NotificationModel).where(
                NotificationModel.userinfo_id == self.authenticated_user_info.id
            )
            session.exec(statement)
            session.commit()

        # Vacía la lista en el estado para que la UI se actualice al instante
        self.user_notifications = []
        yield rx.toast.success("Notificaciones eliminadas.")
    
    # --- ✨ INICIO: MÉTODO OPCIONAL PARA on_click SIN ACCIÓN ✨ ---
    @rx.event
    def do_nothing(self):
        """Un evento que no hace nada, útil para condicionales."""
        pass
    # --- ✨ FIN: MÉTODO OPCIONAL ✨ ---

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
        
        # --- INICIO DE LA MODIFICACIÓN ---
        email = form_data.get("email", "").strip().lower()
        if not email.endswith("@gmail.com"):
            # Usamos un toast para mostrar el error en este formulario
            yield rx.toast.error("Correo inválido. Solo se permiten direcciones @gmail.com.")
            return
        # --- FIN DE LA MODIFICACIÓN ---

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
    

    # REEMPLAZA la variable all_users
    managed_users: list[UserManagementDTO] = []

    # REEMPLAZA el manejador de eventos load_all_users
    @rx.event
    def load_all_users(self):
        """
        [CORRECCIÓN DEFINITIVA] Carga todos los usuarios y los convierte en DTOs seguros para el estado.
        """
        if not self.is_admin:
            self.managed_users = []
            return rx.redirect("/")
        
        with rx.session() as session:
            users_from_db = session.exec(
                sqlmodel.select(UserInfo).options(sqlalchemy.orm.joinedload(UserInfo.user))
            ).all()
            
            # Convierte los objetos complejos de la BD en DTOs simples y seguros
            self.managed_users = [
                UserManagementDTO(
                    id=u.id,
                    username=u.user.username if u.user else "Usuario no válido",
                    email=u.email,
                    role=u.role,
                    is_banned=u.is_banned,
                    is_verified=u.is_verified,
                )
                for u in users_from_db
            ]


    @rx.event
    def toggle_admin_role(self, userinfo_id: int):
        """[CORRECCIÓN DEFINITIVA] Cambia el rol de un usuario a/desde Admin y actualiza el DTO."""
        if not self.is_admin:
            return rx.toast.error("No tienes permisos.")
            
        with rx.session() as session:
            user_info = session.get(UserInfo, userinfo_id)
            if user_info:
                if user_info.id == self.authenticated_user_info.id:
                    return rx.toast.warning("No puedes cambiar tu propio rol.")
                
                new_role = UserRole.CUSTOMER if user_info.role == UserRole.ADMIN else UserRole.ADMIN
                user_info.role = new_role
                session.add(user_info)
                session.commit()

                # Actualiza el DTO en la lista del estado
                for i, u in enumerate(self.managed_users):
                    if u.id == userinfo_id:
                        self.managed_users[i].role = new_role
                        break


    @rx.event
    def ban_user(self, userinfo_id: int, days: int = 7):
        """[CORRECCIÓN DEFINITIVA] Veta a un usuario y actualiza el DTO."""
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

                # Actualiza el DTO en la lista del estado
                for i, u in enumerate(self.managed_users):
                    if u.id == userinfo_id:
                        self.managed_users[i].is_banned = True
                        break

    @rx.event
    def unban_user(self, userinfo_id: int):
        """[CORRECCIÓN DEFINITIVA] Quita el veto a un usuario y actualiza el DTO."""
        if not self.is_admin:
            return rx.toast.error("No tienes permisos.")

        with rx.session() as session:
            user_info = session.get(UserInfo, userinfo_id)
            if user_info:
                user_info.is_banned = False
                user_info.ban_expires_at = None
                session.add(user_info)
                session.commit()
                
                # Actualiza el DTO en la lista del estado
                for i, u in enumerate(self.managed_users):
                    if u.id == userinfo_id:
                        self.managed_users[i].is_banned = False
                        break
    
    # --- 👇 AÑADE ESTA NUEVA PROPIEDAD COMPUTADA AQUÍ 👇 ---
    @rx.var
    def filtered_admin_store_posts(self) -> list[ProductCardData]:
        """Filtra los productos de la tienda de admin según el término de búsqueda."""
        if not self.search_term.strip():
            return self.admin_store_posts  # Devuelve todos si no hay búsqueda
        
        query = self.search_term.strip().lower()
        return [
            p for p in self.admin_store_posts if query in p.title.lower()
        ]

    @rx.event
    def on_load_admin_store(self):
        """
        [CORREGIDO] Carga las publicaciones para la "Tienda (Punto de Venta)"
        usando la identidad correcta del vendedor.
        """
        if not (self.is_admin or self.is_vendedor or self.is_empleado):
            return rx.redirect("/")

        yield AppState.load_all_users

        owner_id = None
        # --- ✨ Lógica de contexto robusta ✨ ---
        if self.is_empleado and self.mi_vendedor_info:
            owner_id = self.mi_vendedor_info.id
        elif self.authenticated_user_info:
            owner_id = self.authenticated_user_info.id

        if not owner_id:
            self.admin_store_posts = []
            return

        with rx.session() as session:
            # La consulta ahora usa el `owner_id` correcto
            results = session.exec(
                sqlmodel.select(BlogPostModel)
                .where(BlogPostModel.userinfo_id == owner_id) # <-- CORRECCIÓN CLAVE
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

    # 1. Nueva variable de estado para el campo de búsqueda del vendedor
    search_seller_barrio: str = ""

    # 2. Nuevo manejador de eventos para actualizar esa variable
    def set_search_seller_barrio(self, query: str):
        self.search_seller_barrio = query

    # Nuevas variables de estado
    seller_profile_city: str = ""
    search_seller_city: str = ""

    # Setter para la ciudad
    def set_seller_profile_city(self, city: str):
        self.seller_profile_city = city
        self.seller_profile_barrio = "" # Limpiar el barrio al cambiar de ciudad

    # Setter para la búsqueda de ciudad
    def set_search_seller_city(self, query: str):
        self.search_seller_city = query

    @rx.var
    def filtered_seller_cities(self) -> list[str]:
        """Filtra la lista de todas las ciudades para el selector de búsqueda."""
        if not self.search_seller_city.strip():
            return ALL_CITIES
        query = self.search_seller_city.lower()
        return [city for city in ALL_CITIES if query in city.lower()]

    @rx.var
    def filtered_seller_barrios(self) -> list[str]:
        """
        Devuelve dinámicamente los barrios de la ciudad seleccionada por el vendedor.
        """
        if not self.seller_profile_city:
            return [] # No mostrar barrios si no se ha seleccionado una ciudad
        
        # Obtiene la lista de barrios del diccionario maestro
        all_hoods = COLOMBIA_LOCATIONS.get(self.seller_profile_city, [])
        
        # Aplica el filtro de búsqueda (lógica que ya tenías para barrios)
        if not self.search_seller_barrio.strip():
            return sorted(all_hoods)
        query = self.search_seller_barrio.lower()
        return sorted([n for n in all_hoods if query in n.lower()])

    
    
     # --- ✨ INICIO: SECCIÓN DE PERFIL DE USUARIO CORREGIDA ✨ ---
    
    # DTO para mostrar datos en el formulario de forma segura
    profile_info: UserProfileData = UserProfileData()
    
    # Variables para los campos controlados del formulario
    profile_username: str = ""
    profile_phone: str = ""

    def set_profile_username(self, name: str):
        self.profile_username = name

    def set_profile_phone(self, phone: str):
        self.profile_phone = phone

    # --- ✨ INICIO: NUEVAS VARIABLES DE ESTADO PARA NOTIFICACIONES DEL VENDEDOR ✨ ---
    admin_notifications: List[NotificationDTO] = []
    # --- ✨ INICIO: AÑADE ESTA VARIABLE DE ESTADO DE VUELTA ✨ ---
    pending_request_notification: Optional[PendingRequestDTO] = None
    # --- ✨ FIN: AÑADE ESTA VARIABLE DE ESTADO DE VUELTA ✨ ---

    @rx.var
    def admin_unread_count(self) -> int:
        """Calcula el número de notificaciones no leídas para el vendedor."""
        return sum(1 for n in self.admin_notifications if not n.is_read)
    # --- ✨ FIN: NUEVAS VARIABLES DE ESTADO ✨ ---

    # ... (resto de tus funciones)

    def _load_admin_notifications_logic(self):
        """
        [VERSIÓN CON FILTRADO DE URL]
        Carga únicamente las notificaciones cuyo URL empieza con '/admin',
        asegurando que solo se muestren alertas relevantes para el vendedor.
        """
        user_id_to_check = self.context_user_id if self.is_vigilando else (self.authenticated_user_info.id if self.authenticated_user_info else None)
        if not user_id_to_check:
            self.admin_notifications = []
            return

        with rx.session() as session:
            # --- CORRECCIÓN CLAVE: Añadimos el filtro por URL ---
            notifications_db = session.exec(
                sqlmodel.select(NotificationModel)
                .where(
                    NotificationModel.userinfo_id == user_id_to_check,
                    NotificationModel.url.startswith("/admin")
                )
                .order_by(sqlmodel.col(NotificationModel.created_at).desc())
                .limit(20)
            ).all()
            self.admin_notifications = [NotificationDTO.from_orm(n) for n in notifications_db]

            # La lógica del banner de empleo se mantiene igual
            if not self.pending_request_notification and (self.is_vendedor or self.is_admin):
                first_pending_request = session.exec(
                    sqlmodel.select(EmploymentRequest).where(
                        EmploymentRequest.candidate_id == user_id_to_check,
                        EmploymentRequest.status == RequestStatus.PENDING
                    )
                ).first()
                if first_pending_request:
                    self.pending_request_notification = PendingRequestDTO(
                        id=first_pending_request.id,
                        requester_username=first_pending_request.requester_username
                    )

    
    @rx.event
    def poll_admin_notifications(self):
        """
        [VERSIÓN FINAL] Evento de sondeo para el panel.
        1. Carga las notificaciones para la campana.
        2. Sincroniza el contexto del empleado para asegurar que siempre tenga
        el ID de su vendedor, incluso después de aceptar una invitación.
        """
        # --- ✨ INICIO: LÓGICA DE SINCRONIZACIÓN DE CONTEXTO ✨ ---
        if self.is_authenticated and self.authenticated_user_info:
            # Si el usuario es un empleado pero su contexto no está definido (p.ej. tras aceptar invitación)
            if self.is_empleado and self.context_user_id != self.mi_vendedor_info.id:
                # Forzamos la actualización del contexto con el ID de su vendedor
                self.context_user_id = self.mi_vendedor_info.id
                # Forzamos la recarga de las publicaciones con el nuevo contexto
                yield AppState.load_mis_publicaciones
        # --- ✨ FIN: LÓGICA DE SINCRONIZACIÓN DE CONTEXTO ✨ ---
        
        # La lógica existente para cargar las notificaciones se mantiene
        self._load_admin_notifications_logic()

    @rx.event
    def mark_all_admin_as_read(self):
        """Marca todas las notificaciones del vendedor como leídas."""
        if not self.admin_notifications:
            return
            
        unread_ids = [n.id for n in self.admin_notifications if not n.is_read]
        if not unread_ids:
            return
            
        with rx.session() as session:
            stmt = sqlmodel.update(NotificationModel).where(NotificationModel.id.in_(unread_ids)).values(is_read=True)
            session.exec(stmt)
            session.commit()
        
        # Actualiza la UI al instante
        for i in range(len(self.admin_notifications)):
            if self.admin_notifications[i].id in unread_ids:
                self.admin_notifications[i].is_read = True
    # --- ✨ FIN: NUEVA LÓGICA DE CARGA ✨ ---

    # --- AÑADE ESTA LÍNEA DENTRO DE TU CLASE AppState ---
    solicitudes_de_empleo_recibidas: list[EmploymentRequest] = []

    search_query_sent_requests: str = ""

    # En likemodas/state.py, dentro de AppState
    def set_search_query_sent_requests(self, query: str):
        self.search_query_sent_requests = query

    @rx.event
    def on_load_profile_page(self):
        """
        [CORREGIDO Y COMPLETO] Carga los datos del perfil del usuario actual
        y también busca las solicitudes de empleo pendientes que ha recibido.
        """
        if not self.authenticated_user_info:
            # Si no está autenticado, no hay nada que cargar.
            return

        with rx.session() as session:
            # 1. Cargar la información básica del perfil
            user_info = session.get(UserInfo, self.authenticated_user_info.id)
            if user_info and user_info.user:
                self.profile_info = UserProfileData(
                    username=user_info.user.username,
                    email=user_info.email,
                    phone=user_info.phone or "",
                    avatar_url=user_info.avatar_url or "",
                    tfa_enabled=user_info.tfa_enabled
                )
                self.profile_username = user_info.user.username
                self.profile_phone = user_info.phone or ""
            
            # 2. Cargar las solicitudes de empleo pendientes para este usuario
            self.solicitudes_de_empleo_recibidas = session.exec(
                sqlmodel.select(EmploymentRequest)
                .options(sqlalchemy.orm.joinedload(EmploymentRequest.requester).joinedload(UserInfo.user))
                .where(
                    EmploymentRequest.candidate_id == self.authenticated_user_info.id,
                    EmploymentRequest.status == RequestStatus.PENDING
                )
            ).all()

    # --- REEMPLAZA LA FUNCIÓN `enviar_solicitud_empleo` ---
    @rx.event
    def enviar_solicitud_empleo(self, candidate_userinfo_id: int):
        """[CORREGIDO] El Vendedor envía una solicitud de empleo, notificando con la URL correcta."""
        if not (self.is_vendedor or self.is_admin) or not self.authenticated_user_info:
            return rx.toast.error("No tienes permisos para enviar solicitudes.")

        requester_id = self.authenticated_user_info.id

        with rx.session() as session:
            if requester_id == candidate_userinfo_id:
                return rx.toast.error("No puedes enviarte una solicitud a ti mismo.")

            existing_request = session.exec(
                sqlmodel.select(EmploymentRequest).where(
                    EmploymentRequest.requester_id == requester_id,
                    EmploymentRequest.candidate_id == candidate_userinfo_id,
                    EmploymentRequest.status == RequestStatus.PENDING
                )
            ).first()
            if existing_request:
                return rx.toast.info("Ya has enviado una solicitud pendiente a este usuario.")

            requester_info = session.get(UserInfo, requester_id)
            if not requester_info or not requester_info.user:
                return rx.toast.error("Error al identificar al solicitante.")
            
            new_request = EmploymentRequest(
                requester_id=requester_id,
                candidate_id=candidate_userinfo_id,
                requester_username=requester_info.user.username
            )
            session.add(new_request)

            notification = NotificationModel(
                userinfo_id=candidate_userinfo_id,
                message=f"¡{requester_info.user.username} quiere contratarte como empleado!",
                url="/admin/profile"
            )
            session.add(notification)
            session.commit()
        
        self.search_results_users = []
        yield rx.toast.success("Solicitud de empleo enviada.")
        
        # --- ✨ CORRECCIÓN CLAVE: Usamos 'yield from' para encadenar eventos que también usan 'yield' ✨ ---
        yield from self.load_empleados()

    # --- AÑADE ESTA NUEVA FUNCIÓN ---
    @rx.event
    def descartar_solicitud_empleo(self, request_id: int):
        """Permite al vendedor 'descartar' (rechazar) una solicitud pendiente que envió."""
        if not (self.is_vendedor or self.is_admin) or not self.authenticated_user_info:
            return rx.toast.error("No tienes permisos.")

        with rx.session() as session:
            request = session.get(EmploymentRequest, request_id)
            if not request or request.requester_id != self.authenticated_user_info.id:
                return rx.toast.error("Solicitud no válida o no te pertenece.")
            
            if request.status == RequestStatus.PENDING:
                request.status = RequestStatus.REJECTED
                session.add(request)
                session.commit()
                yield self.load_empleados()
                return rx.toast.info("Has descartado la solicitud.")

    # 2. --- Nueva función para buscar solicitudes ---
    @rx.event
    def poll_employment_requests(self):
        """
        [VERSIÓN ROBUSTA] Busca periódicamente la primera solicitud de empleo pendiente
        y guarda un DTO limpio en el estado para evitar errores de sesión.
        """
        if not self.authenticated_user_info or self.pending_request_notification:
            return

        with rx.session() as session:
            # La consulta a la base de datos sigue siendo simple
            first_pending = session.exec(
                sqlmodel.select(EmploymentRequest).where(
                    EmploymentRequest.candidate_id == self.authenticated_user_info.id,
                    EmploymentRequest.status == RequestStatus.PENDING
                )
            ).first()

            # --- ✨ INICIO DE LA CORRECCIÓN CLAVE ✨ ---
            # Si encontramos una solicitud, creamos nuestro DTO simple
            if first_pending:
                self.pending_request_notification = PendingRequestDTO(
                    id=first_pending.id,
                    requester_username=first_pending.requester_username
                )
            # --- ✨ FIN DE LA CORRECCIÓN CLAVE ✨ ---

    # 3. --- Función 'responder_solicitud_empleo' (reemplazar la existente) ---
    @rx.event
    def responder_solicitud_empleo(self, request_id: int, aceptada: bool):
        """
        [VERSIÓN FINAL] El candidato acepta o rechaza una solicitud. Si acepta,
        el contexto se actualiza y los datos se cargan inmediatamente.
        """
        if not self.authenticated_user_info:
            return rx.toast.error("Debes iniciar sesión.")

        with rx.session() as session:
            request = session.get(EmploymentRequest, request_id)

            if not request or request.candidate_id != self.authenticated_user_info.id:
                return rx.toast.error("Solicitud no válida.")

            self.pending_request_notification = None

            if aceptada:
                existing_link = session.exec(
                    sqlmodel.select(EmpleadoVendedorLink).where(EmpleadoVendedorLink.empleado_id == request.candidate_id)
                ).first()
                if existing_link:
                    request.status = RequestStatus.REJECTED
                    session.add(request)
                    session.commit()
                    yield self.on_load_profile_page()
                    return rx.toast.error("Ya eres empleado de otro vendedor. Solicitud rechazada.")

                new_link = EmpleadoVendedorLink(vendedor_id=request.requester_id, empleado_id=request.candidate_id)
                session.add(new_link)
                request.status = RequestStatus.ACCEPTED
                session.add(request)
                
                candidate_user = session.get(UserInfo, request.candidate_id)
                if candidate_user and candidate_user.user:
                    notification = NotificationModel(
                        userinfo_id=request.requester_id,
                        message=f"¡{candidate_user.user.username} ha aceptado tu solicitud de empleo!",
                        url="/admin/employees"
                    )
                    session.add(notification)
                
                session.commit()
                
                yield rx.toast.success("¡Bienvenido! Cargando las publicaciones de tu empleador...")

                # --- ✨ INICIO DE LA CORRECCIÓN CLAVE: SECUENCIA DE EVENTOS INSTANTÁNEA ✨ ---
                
                # 1. Forzamos la actualización del contexto del empleado.
                self.context_user_id = request.requester_id
                
                # 2. Llamamos al evento que carga las publicaciones.
                yield AppState.load_mis_publicaciones
                
                # 3. Redirigimos al empleado a la página donde ya estarán los datos.
                yield rx.redirect("/blog")
                
                # --- ✨ FIN DE LA CORRECCIÓN CLAVE ✨ ---
            
            else: # Si la solicitud es rechazada
                request.status = RequestStatus.REJECTED
                session.add(request)
                # ... (Lógica de notificación de rechazo se mantiene)
                session.commit()
                yield self.on_load_profile_page()
                yield rx.toast.info("Has rechazado la oferta de empleo.")

    @rx.event
    async def handle_avatar_upload(self, files: list[rx.UploadFile]):
        """Maneja la subida de una nueva imagen de perfil."""
        if not self.authenticated_user_info:
            # --- CORRECCIÓN ---
            yield rx.toast.error("Debes iniciar sesión.")
            return

        if not files:
            return
            
        upload_data = await files[0].read()
        unique_filename = f"avatar-{self.authenticated_user_info.id}-{secrets.token_hex(4)}.webp"
        outfile = rx.get_upload_dir() / unique_filename
        outfile.write_bytes(upload_data)
        
        with rx.session() as session:
            user_info = session.get(UserInfo, self.authenticated_user_info.id)
            if user_info:
                user_info.avatar_url = unique_filename
                session.add(user_info)
                session.commit()
        
        yield self.on_load_profile_page()
        yield rx.toast.success("Imagen de perfil actualizada.")

    @rx.event
    def handle_profile_update(self, form_data: dict):
        """Actualiza el nombre de usuario y el teléfono."""
        if not self.authenticated_user_info:
            # --- CORRECCIÓN ---
            yield rx.toast.error("Debes iniciar sesión.")
            return
            
        new_username = form_data.get("username", "").strip()
        new_phone = form_data.get("phone", "").strip()

        if not new_username:
            # --- CORRECCIÓN ---
            yield rx.toast.error("El nombre de usuario no puede estar vacío.")
            return

        with rx.session() as session:
            existing_user = session.exec(
                sqlmodel.select(LocalUser).where(LocalUser.username == new_username)
            ).one_or_none()
            if existing_user and existing_user.id != self.authenticated_user.id:
                # --- CORRECCIÓN ---
                yield rx.toast.error("Ese nombre de usuario ya está en uso.")
                return

            user_info = session.get(UserInfo, self.authenticated_user_info.id)
            local_user = session.get(LocalUser, self.authenticated_user.id)
            
            if user_info and local_user:
                if local_user.username != new_username:
                    stmt = (
                        sqlmodel.update(CommentModel)
                        .where(CommentModel.userinfo_id == user_info.id)
                        .values(author_username=new_username, author_initial=new_username[0].upper())
                    )
                    session.exec(stmt)
                
                local_user.username = new_username
                user_info.phone = new_phone
                session.add(local_user)
                session.add(user_info)
                session.commit()

        yield self.on_load_profile_page()
        yield rx.toast.success("Perfil actualizado correctamente.")

    @rx.event
    def handle_password_change(self, form_data: dict):
        """Cambia la contraseña del usuario tras verificar la actual."""
        if not self.authenticated_user:
            yield rx.toast.error("Debes iniciar sesión.") # [cite: 1732]
            return
            
        current_password = form_data.get("current_password")
        new_password = form_data.get("new_password")
        confirm_password = form_data.get("confirm_password")

        # Validar que todos los campos estén completos
        if not all([current_password, new_password, confirm_password]): # [cite: 1733]
            yield rx.toast.error("Todos los campos son obligatorios.")
            return
        
        # Validar que las nuevas contraseñas coincidan
        if new_password != confirm_password: # [cite: 1734]
            yield rx.toast.error("Las nuevas contraseñas no coinciden.")
            return
        
        # Validar la fortaleza de la nueva contraseña
        password_errors = validate_password(new_password)
        if password_errors:
            yield rx.toast.error("\n".join(password_errors))
            return
            
        with rx.session() as session:
            local_user = session.get(LocalUser, self.authenticated_user.id) # [cite: 1735]
            
            # Verificar que la contraseña actual sea correcta
            if not bcrypt.checkpw(current_password.encode("utf-8"), local_user.password_hash):
                yield rx.toast.error("La contraseña actual es incorrecta.")
                return
                
            # Hashear y guardar la nueva contraseña
            local_user.password_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()) # [cite: 1736]
            session.add(local_user)
            session.commit()
            
        yield rx.toast.success("Contraseña actualizada con éxito.")

    @rx.event
    def handle_account_deletion(self, form_data: dict):
        """Elimina permanentemente la cuenta del usuario."""
        if not self.authenticated_user:
            # --- CORRECCIÓN ---
            yield rx.toast.error("Debes iniciar sesión.")
            return
            
        password = form_data.get("password")
        if not password:
            # --- CORRECCIÓN ---
            yield rx.toast.error("Debes ingresar tu contraseña para eliminar la cuenta.")
            return

        with rx.session() as session:
            local_user = session.get(LocalUser, self.authenticated_user.id)
            if not bcrypt.checkpw(password.encode("utf-8"), local_user.password_hash):
                # --- CORRECCIÓN ---
                yield rx.toast.error("La contraseña es incorrecta.")
                return
                
            session.delete(local_user)
            session.commit()
            
        yield rx.toast.success("Tu cuenta ha sido eliminada permanentemente.")
        yield AppState.do_logout
        # --- CORRECCIÓN ---
        yield rx.redirect("/")

    # --- ✨ FIN: SECCIÓN DE PERFIL DE USUARIO CORREGIDA ✨ ---



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

    @rx.event
    def vote_on_comment(self, comment_id: int, vote_type: str):
        """Maneja el voto de un usuario en un comentario, con validaciones."""
        if not self.is_authenticated or not self.authenticated_user_info:
            return rx.toast.error("Debes iniciar sesión para votar.")

        with rx.session() as session:
            comment = session.get(CommentModel, comment_id)
            if not comment:
                return rx.toast.error("El comentario ya no existe.")

            # --- CORRECCIÓN AQUÍ: Evitar que los usuarios voten en sus propios comentarios ---
            if comment.userinfo_id == self.authenticated_user_info.id:
                return rx.toast.info("No puedes votar en tu propio comentario.")

            first_purchase = session.exec(
                sqlmodel.select(PurchaseModel).where(
                    PurchaseModel.userinfo_id == self.authenticated_user_info.id
                )
            ).first()

            if not first_purchase:
                return rx.toast.error("Debes realizar al menos una compra para poder votar.")

            existing_vote = session.exec(
                sqlmodel.select(CommentVoteModel).where(
                    CommentVoteModel.userinfo_id == self.authenticated_user_info.id,
                    CommentVoteModel.comment_id == comment_id,
                )
            ).one_or_none()

            if existing_vote:
                if existing_vote.vote_type == vote_type:
                    session.delete(existing_vote)
                else:
                    existing_vote.vote_type = vote_type
                    session.add(existing_vote)
            else:
                new_vote = CommentVoteModel(
                    userinfo_id=self.authenticated_user_info.id,
                    comment_id=comment_id,
                    vote_type=vote_type,
                )
                session.add(new_vote)

            session.commit()

        if self.product_in_modal:
            yield AppState.open_product_detail_modal(self.product_in_modal.id)
            
    # --- ✨ FIN DEL BLOQUE DE CÓDIGO CORREGIDO PARA VOTACIONES ✨ ---


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

    # --- ✨ INICIO DEL BLOQUE DE CÓDIGO CORREGIDO PARA VOTACIONES ✨ ---

    def _convert_comment_to_dto(self, comment_model: CommentModel) -> CommentData:
        """
        Convierte un CommentModel de la BD a un CommentData DTO,
        incluyendo los datos de votación, reputación y avatar.
        """
        user_vote = ""
        if self.authenticated_user_info:
            vote = next(
                (v for v in comment_model.votes if v.userinfo_id == self.authenticated_user_info.id), 
                None
            )
            if vote:
                user_vote = vote.vote_type

        # --- ✨ CORRECCIÓN AQUÍ: Guardamos solo el nombre del archivo (string) ✨ ---
        avatar_filename = ""
        if comment_model.userinfo and comment_model.userinfo.avatar_url:
            avatar_filename = comment_model.userinfo.avatar_url

        return CommentData(
            id=comment_model.id,
            content=comment_model.content,
            rating=comment_model.rating,
            author_username=comment_model.author_username,
            author_initial=comment_model.author_initial,
            created_at_formatted=comment_model.created_at_formatted,
            updates=[self._convert_comment_to_dto(update) for update in sorted(comment_model.updates, key=lambda u: u.created_at)],
            likes=comment_model.likes,
            dislikes=comment_model.dislikes,
            user_vote=user_vote,
            author_reputation=comment_model.userinfo.reputation.value if comment_model.userinfo else UserReputation.NONE.value,
            
            # Pasamos el nombre del archivo (string) al DTO
            author_avatar_url=avatar_filename,
        )

    # --- NUEVOS MANEJADORES PARA EL MODAL ---
    def set_modal_variant_index(self, index: int):
        """
        Llamado al hacer clic en una miniatura. Selecciona la variante visual
        y reinicia las selecciones de atributos.
        """
        self.modal_selected_variant_index = index
        self.modal_selected_attributes = {} # Limpia la selección de talla anterior

    @rx.event
    def open_product_detail_modal(self, post_id: int):
        # Reiniciar el estado inicial para el modal
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
        self.expanded_comments = {}

        with rx.session() as session:
            db_post = session.exec(
                sqlmodel.select(BlogPostModel).options(
                    sqlalchemy.orm.joinedload(BlogPostModel.comments).joinedload(CommentModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(BlogPostModel.comments).joinedload(CommentModel.votes),
                    sqlalchemy.orm.joinedload(BlogPostModel.comments).joinedload(CommentModel.updates),
                    sqlalchemy.orm.joinedload(BlogPostModel.userinfo).joinedload(UserInfo.user)
                ).where(BlogPostModel.id == post_id)
            ).unique().one_or_none()

            if not db_post or not db_post.publish_active:
                self.show_detail_modal = False
                return rx.toast.error("Producto no encontrado.")

            # --- INICIO DE LA CORRECCIÓN ---

            # 1. Obtenemos los datos del comprador y vendedor, incluyendo la CIUDAD
            buyer_barrio = self.default_shipping_address.neighborhood if self.default_shipping_address else None
            buyer_city = self.default_shipping_address.city if self.default_shipping_address else None
            
            seller_barrio = db_post.userinfo.seller_barrio if db_post.userinfo else None
            seller_city = db_post.userinfo.seller_city if db_post.userinfo else None

            # 2. Llamamos a la función con TODOS los argumentos requeridos
            final_shipping_cost = calculate_dynamic_shipping(
                base_cost=db_post.shipping_cost or 0.0,
                seller_barrio=seller_barrio,
                buyer_barrio=buyer_barrio,
                seller_city=seller_city,
                buyer_city=buyer_city
            )
            
            shipping_text = f"Envío: {format_to_cop(final_shipping_cost)}" if final_shipping_cost > 0 else "Envío a convenir"
            
            # --- FIN DE LA CORRECCIÓN ---
            
            seller_name = db_post.userinfo.user.username if db_post.userinfo and db_post.userinfo.user else "N/A"
            seller_id = db_post.userinfo.id if db_post.userinfo else 0
            
            # El resto de la función para construir el DTO y cargar comentarios no cambia...
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
                shipping_display_text=shipping_text, # Usamos el costo calculado
                seller_name=seller_name,
                seller_id=seller_id,
                seller_score=db_post.seller_score,
            )
            
            if self.product_in_modal.variants:
                self._set_default_attributes_from_variant(self.product_in_modal.variants[0])

            # Lógica de comentarios usando el nuevo método
            all_comment_dtos = [self._convert_comment_to_dto(c) for c in db_post.comments] # <-- Llamada corregida
            original_comment_dtos = [dto for dto in all_comment_dtos if dto.id not in {update.id for parent in all_comment_dtos for update in parent.updates}]
            self.product_comments = sorted(original_comment_dtos, key=lambda c: c.id, reverse=True)

            # Lógica para mostrar/ocultar el formulario de opinión (sin cambios)
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
                            self.my_review_for_product = self._convert_comment_to_dto(latest_entry) # <-- Llamada corregida
                            self.review_rating = latest_entry.rating
                            self.review_content = latest_entry.content
                        else:
                            self.review_limit_reached = True

        yield AppState.load_saved_post_ids

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
            # --- CORRECCIÓN ---
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
                    sqlmodel.select(UserInfo).options(
                        sqlalchemy.orm.joinedload(UserInfo.user),
                        # --- ✨ LÍNEA AÑADIDA: Carga previa de los posts para el cálculo ---
                        sqlalchemy.orm.selectinload(UserInfo.posts).selectinload(BlogPostModel.comments).selectinload(CommentModel.votes)
                    )
                    .where(UserInfo.id == seller_id_int)
                ).one_or_none()
                
                if seller_info_db and seller_info_db.user:
                    self.seller_page_info = SellerInfoData(
                        id=seller_info_db.id,
                        username=seller_info_db.user.username,
                        # --- ✨ LÍNEA AÑADIDA: Se pasa la puntuación calculada al DTO ---
                        overall_seller_score=seller_info_db.overall_seller_score
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
                    
                    temp_posts = []
                    for p in posts:
                        temp_posts.append(
                            ProductCardData(
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
        yield rx.redirect(f"/returns?purchase_id={purchase_id}")

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
            # --- CORRECCIÓN ---
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
                items=purchase_items_data,
                # --- AÑADE ESTA LÍNEA FALTANTE ---
                estimated_delivery_date_formatted=format_utc_to_local(purchase_db.estimated_delivery_date)
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
        """
        [CORREGIDO] Carga todos los tickets de soporte donde el usuario actual
        es el vendedor, permitiendo el acceso a Vendedores y Administradores.
        """
        # --- ¡ESTA ES LA CORRECCIÓN CLAVE! ---
        # Ahora comprobamos si el usuario NO es admin Y TAMPOCO es vendedor.
        if not (self.is_admin or self.is_vendedor):
            return rx.redirect("/")

        # El resto de la función se mantiene igual.
        with rx.session() as session:
            # La consulta busca tickets donde el usuario actual sea el vendedor.
            # Un admin sin tickets no verá nada, lo cual es correcto.
            # Si un admin está en modo vigilancia, el context_user_id será el del vendedor.
            user_id_to_check = self.context_user_id if self.context_user_id else self.authenticated_user_info.id

            tickets = session.exec(
                sqlmodel.select(SupportTicketModel)
                .options(sqlalchemy.orm.joinedload(SupportTicketModel.buyer).joinedload(UserInfo.user))
                .where(SupportTicketModel.seller_id == user_id_to_check)
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
