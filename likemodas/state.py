# likemodas/state.py

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

from . import navigation
from .models import (
    UserInfo, UserRole, VerificationToken, BlogPostModel, ShippingAddressModel,
    PurchaseModel, PurchaseStatus, PurchaseItemModel, NotificationModel, Category,
    CommentModel, PasswordResetToken, LocalUser, ContactEntryModel
)
from .services.email_service import send_verification_email, send_password_reset_email
from .utils.formatting import format_to_cop
from .utils.validators import validate_password
from .data.colombia_locations import load_colombia_data
from .data.product_options import (
    LISTA_TIPOS_ROPA, LISTA_TIPOS_ZAPATOS, LISTA_TIPOS_MOCHILAS, LISTA_TIPOS_GENERAL,
    LISTA_COLORES, LISTA_TALLAS_ROPA, LISTA_NUMEROS_CALZADO, LISTA_MATERIALES, LISTA_MEDIDAS_GENERAL
)

# --- MODELOS DE DATOS SEGUROS PARA LA UI (DTOs) ---
class ProductCardData(rx.Base):
    id: int
    title: str
    price: float = 0.0
    image_urls: list[str] = []
    average_rating: float = 0.0
    rating_count: int = 0
    
    @classmethod
    def from_orm(cls, orm_obj: BlogPostModel) -> "ProductCardData":
        return cls(
            id=orm_obj.id,
            title=orm_obj.title,
            price=orm_obj.price or 0.0,
            image_urls=orm_obj.image_urls or [],
            average_rating=orm_obj.average_rating,
            rating_count=orm_obj.rating_count,
        )
    
    @property
    def price_cop(self) -> str:
        return format_to_cop(self.price)

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

# --- ESTADO PRINCIPAL DE LA APLICACIÓN ---
class AppState(reflex_local_auth.LocalAuthState):
    """El estado único y monolítico de la aplicación."""

    success: bool = False
    error_message: str = ""
    
    # --- AUTH / SESSION ---
    @rx.var(cache=True)
    def authenticated_user_info(self) -> UserInfo | None:
        if not self.is_authenticated or self.authenticated_user.id < 0:
            return None
        with rx.session() as session:
            return session.exec(sqlmodel.select(UserInfo).where(UserInfo.user_id == self.authenticated_user.id)).one_or_none()

    @rx.var
    def is_admin(self) -> bool:
        return self.authenticated_user_info is not None and self.authenticated_user_info.role == UserRole.ADMIN

    # --- REGISTRO Y VERIFICACIÓN ---
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

    # --- MANEJO DE CONTRASEÑA ---
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

    # --- FILTROS DE BÚSQUEDA ---
    min_price: str = ""
    max_price: str = ""
    show_filters: bool = False
    current_category: str = ""
    open_filter_name: str = ""
    filter_color: str = ""
    filter_talla: str = ""
    filter_tipo_prenda: str = ""
    filter_tipo_zapato: str = ""
    filter_numero_calzado: str = ""
    filter_tipo_mochila: str = ""
    filter_tipo_general: str = ""
    filter_material_tela: str = ""
    filter_medida_talla: str = ""

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

    # --- PRODUCTOS Y GALERÍA PÚBLICA ---
    posts: list[ProductCardData] = []
    is_loading: bool = True

    @rx.event
    def on_load(self):
        self.is_loading = True
        yield
        with rx.session() as session:
            results = session.exec(sqlmodel.select(BlogPostModel).options(sqlalchemy.orm.joinedload(BlogPostModel.comments)).where(BlogPostModel.publish_active == True).order_by(BlogPostModel.created_at.desc())).unique().all()
            self.posts = [ProductCardData.from_orm(p) for p in results]
        self.is_loading = False
    
    # --- LÓGICA PARA MODALES ---
    # --- Modal de Detalle de Producto (Vista Pública) ---
    show_detail_modal: bool = False
    product_in_modal: Optional[BlogPostModel] = None
    current_image_index: int = 0

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

    @rx.event
    def open_product_detail_modal(self, post_id: int):
        self.product_in_modal = None
        self.show_detail_modal = True
        self.current_image_index = 0
        yield
        with rx.session() as session:
            db_post = session.exec(
                sqlmodel.select(BlogPostModel)
                .options(sqlalchemy.orm.joinedload(BlogPostModel.comments))
                .where(BlogPostModel.id == post_id, BlogPostModel.publish_active == True)
            ).one_or_none()
            if db_post:
                self.product_in_modal = db_post
            else:
                self.show_detail_modal = False
                yield rx.toast.error("Producto no encontrado o no disponible.")

    @rx.event
    def close_product_detail_modal(self, open_state: bool):
        if not open_state:
            self.show_detail_modal = False
            self.product_in_modal = None

    # --- Modal de Edición de Producto (Vista Admin) ---
    is_editing_post: bool = False
    post_to_edit: Optional[BlogPostModel] = None
    post_title: str = ""
    post_content: str = ""
    price_str: str = ""

    def set_post_title(self, title: str): self.post_title = title
    def set_post_content(self, content: str): self.post_content = content
    def set_price(self, price: str): self.price_str = price
    
    @rx.event
    def start_editing_post(self, post_id: int):
        if not self.is_admin:
            return rx.toast.error("Acción no permitida.")
        with rx.session() as session:
            db_post = session.get(BlogPostModel, post_id)
            if db_post and db_post.userinfo_id == self.authenticated_user_info.id:
                self.post_to_edit = db_post
                self.post_title = db_post.title
                self.post_content = db_post.content
                self.price_str = str(db_post.price or 0.0)
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
                session.add(post_to_update)
                session.commit()
                yield self.cancel_editing_post(False)
                yield rx.toast.success("Publicación actualizada correctamente.")

    # --- CARRITO DE COMPRAS ---
    cart: Dict[int, int] = {}
    @rx.var
    def cart_items_count(self) -> int: return sum(self.cart.values())

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

    # --- GESTIÓN DE FORMULARIO DE AÑADIR PRODUCTO (ADMIN) ---
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
        if not self.is_admin: return rx.toast.error("Acción no permitida.")
        if not all([form_data.get("title"), form_data.get("price"), form_data.get("category")]):
            return rx.toast.error("Título, precio y categoría son obligatorios.")
        
        with rx.session() as session:
            new_post = BlogPostModel(
                userinfo_id=self.authenticated_user_info.id,
                title=form_data["title"],
                content=form_data.get("content", ""),
                price=float(form_data.get("price", 0.0)),
                category=form_data["category"],
                image_urls=self.temp_images,
                publish_active=True,
                publish_date=datetime.now(timezone.utc),
            )
            session.add(new_post)
            session.commit()
            session.refresh(new_post)
        self._clear_add_form()
        yield rx.toast.success("Producto publicado.")
        return rx.redirect("/blog")
        
    # --- GESTIÓN DE BLOG (ADMIN) ---
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
                
    # --- CHECKOUT Y DIRECCIONES ---
    addresses: List[ShippingAddressModel] = []
    show_form: bool = False
    city: str = ""
    neighborhood: str = ""
    search_city: str = ""
    search_neighborhood: str = ""
    default_shipping_address: Optional[ShippingAddressModel] = None

    def toggle_form(self): self.show_form = ~self.show_form
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
            # Desmarcar el default actual
            current_default = session.exec(sqlmodel.select(ShippingAddressModel).where(ShippingAddressModel.userinfo_id == self.authenticated_user_info.id, ShippingAddressModel.is_default == True)).one_or_none()
            if current_default:
                current_default.is_default = False
                session.add(current_default)
            # Marcar el nuevo default
            new_default = session.get(ShippingAddressModel, address_id)
            if new_default and new_default.userinfo_id == self.authenticated_user_info.id:
                new_default.is_default = True
                session.add(new_default)
                session.commit()
                yield self.load_addresses()

    # --- BÚSQUEDA ---
    search_term: str = ""
    search_results: List[ProductCardData] = []
    def set_search_term(self, term: str): self.search_term = term

    @rx.event
    def perform_search(self):
        if not self.search_term.strip(): return
        with rx.session() as session:
            results = session.exec(sqlmodel.select(BlogPostModel).options(sqlalchemy.orm.joinedload(BlogPostModel.comments)).where(BlogPostModel.title.ilike(f"%{self.search_term.strip()}%"), BlogPostModel.publish_active == True)).all()
            self.search_results = [ProductCardData.from_orm(p) for p in results]
        return rx.redirect("/search-results")
    
    # --- GESTIÓN DE USUARIOS (ADMIN) ---
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
        """
        Carga todos los productos (publicados o no) en la variable de estado
        de la tienda de admin para que el admin pueda ver todo.
        """
        if not self.is_admin:
            return rx.redirect("/")

        with rx.session() as session:
            # Consulta para traer TODOS los posts, no solo los activos.
            results = session.exec(
                sqlmodel.select(BlogPostModel)
                .options(sqlalchemy.orm.joinedload(BlogPostModel.comments))
                .order_by(BlogPostModel.created_at.desc())
            ).unique().all()
            
            # Poblamos la nueva variable de estado.
            self.admin_store_posts = [
                ProductCardData(
                    id=p.id, 
                    title=p.title, 
                    price=p.price or 0.0, 
                    image_urls=p.image_urls or [], 
                    average_rating=p.average_rating, 
                    rating_count=p.rating_count
                ) for p in results
            ]


    show_admin_sidebar: bool = False

    def toggle_admin_sidebar(self):
        """Muestra u oculta la barra lateral de administración."""
        self.show_admin_sidebar = not self.show_admin_sidebar