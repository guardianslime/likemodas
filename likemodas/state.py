from __future__ import annotations
import reflex as rx
import reflex_local_auth
import sqlmodel
from sqlmodel import select
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

from .base_state import State
from .models import Product, ProductImage


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

class AdminStoreState(State):
    """Estado para la página de administración de la tienda."""
    products: List[Product] = []
    show_add_modal: bool = False
    show_edit_modal: bool = False
    new_product_name: str = ""
    new_product_description: str = ""
    new_product_price: float = 0.0
    
    # Variable para almacenar el producto que se está editando
    product_to_edit: Optional[Product] = None
    
    # Manejador de subida de archivos
    img_upload_ref = "upload_images"

    @rx.cached_var
    def get_image_upload_url(self) -> str:
        """Devuelve la URL para la subida de imágenes."""
        return "http://localhost:8000/upload"

    def load_products(self):
        """Carga todos los productos de la base de datos."""
        with rx.session() as session:
            self.products = session.exec(
                select(Product).options(
                    # Carga las imágenes relacionadas para evitar consultas N+1
                    selectinload(Product.images) 
                )
            ).all()

    # --- Lógica para el Modal de Edición ---

    def set_product_to_edit(self, product: Product):
        """Prepara el producto para ser editado y muestra el modal."""
        self.product_to_edit = product
        self.show_edit_modal = True

    def close_edit_modal(self):
        """Cierra el modal de edición y limpia la selección."""
        self.show_edit_modal = False
        self.product_to_edit = None

    async def handle_image_replace(self):
        """Maneja la subida y reemplazo de imágenes para un producto existente."""
        if not self.product_to_edit:
            return

        with rx.session() as session:
            # 1. Obtenemos el producto de la sesión actual para poder modificarlo
            product_in_db = session.get(Product, self.product_to_edit.id)
            if not product_in_db:
                return  # Producto no encontrado

            # 2. Eliminamos las imágenes antiguas de la base de datos
            for image in product_in_db.images:
                session.delete(image)
            
            # 3. Subimos los nuevos archivos
            upload_files = await self.get_upload_files(ref=self.img_upload_ref)
            
            # 4. Creamos los nuevos registros de imágenes y los asociamos
            for file in upload_files:
                new_image = ProductImage(
                    product_id=product_in_db.id, 
                    img=f"/{file['key']}" # Guardamos la ruta relativa
                )
                product_in_db.images.append(new_image)
            
            session.add(product_in_db)
            session.commit()

        # 5. Cerramos el modal y recargamos la lista de productos para ver los cambios
        self.close_edit_modal()
        self.load_products()

    def update_product(self):
        """Actualiza los datos del producto en la base de datos."""
        if not self.product_to_edit:
            return
        
        with rx.session() as session:
            product_in_db = session.get(Product, self.product_to_edit.id)
            if product_in_db:
                product_in_db.name = self.product_to_edit.name
                product_in_db.description = self.product_to_edit.description
                product_in_db.price = self.product_to_edit.price
                session.add(product_in_db)
                session.commit()
        
        self.close_edit_modal()
        self.load_products()

# --- DTOs (Data Transfer Objects) para la UI ---
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

# ✨ NUEVO DTO para el Modal de Detalles del Producto
class ProductDetailData(rx.Base):
    id: int
    title: str
    content: str
    price_cop: str
    image_urls: list[str] = []
    created_at_formatted: str

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
    
    @rx.var(cache=True)
    def authenticated_user_info(self) -> UserInfo | None:
        if not self.is_authenticated or self.authenticated_user.id < 0:
            return None
        with rx.session() as session:
            return session.exec(sqlmodel.select(UserInfo).where(UserInfo.user_id == self.authenticated_user.id)).one_or_none()

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

    search_tipo_prenda: str = ""
    search_tipo_zapato: str = ""
    search_tipo_mochila: str = ""
    search_tipo_general: str = ""
    search_color: str = ""
    search_talla: str = ""
    search_numero_calzado: str = ""
    search_material_tela: str = ""
    search_medida_talla: str = ""

    def set_search_tipo_prenda(self, query: str): self.search_tipo_prenda = query
    def set_search_tipo_zapato(self, query: str): self.search_tipo_zapato = query
    def set_search_tipo_mochila(self, query: str): self.search_tipo_mochila = query
    def set_search_tipo_general(self, query: str): self.search_tipo_general = query
    def set_search_color(self, query: str): self.search_color = query
    def set_search_talla(self, query: str): self.search_talla = query
    def set_search_numero_calzado(self, query: str): self.search_numero_calzado = query
    def set_search_material_tela(self, query: str): self.search_material_tela = query
    def set_search_medida_talla(self, query: str): self.search_medida_talla = query

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

    posts: list[ProductCardData] = []
    is_loading: bool = True

    @rx.event
    def on_load(self):
        self.is_loading = True
        yield
        with rx.session() as session:
            results = session.exec(sqlmodel.select(BlogPostModel).where(BlogPostModel.publish_active == True).order_by(BlogPostModel.created_at.desc())).all()
            self.posts = [ProductCardData.from_orm(p) for p in results]
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
                yield self.load_pending_purchases()
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
        abre el modal correspondiente usando el método moderno.
        """
        if self.is_admin:
            return rx.redirect("/admin/store")

        yield AppState.on_load

        # Obtener la URL completa desde el router
        full_url = self.router.url
        product_id = None

        if full_url and "?" in full_url:
            # Descomponer la URL para analizar sus partes
            parsed_url = urlparse(full_url)
            # Extraer los parámetros de la consulta en un diccionario
            query_params = parse_qs(parsed_url.query)

            # 'parse_qs' devuelve valores como listas, ej: {'product': ['1']}
            product_id_list = query_params.get("product")
            if product_id_list:
                product_id = product_id_list[0]

        if product_id is not None:
            yield AppState.open_product_detail_modal(int(product_id))

    @rx.event
    def open_product_detail_modal(self, post_id: int):
        self.product_in_modal = None
        self.show_detail_modal = True
        self.current_image_index = 0
        yield
        with rx.session() as session:
            db_post = session.get(BlogPostModel, post_id)
            if db_post and db_post.publish_active:
                self.product_in_modal = ProductDetailData(
                    id=db_post.id,
                    title=db_post.title,
                    content=db_post.content,
                    price_cop=db_post.price_cop,
                    image_urls=db_post.image_urls,
                    created_at_formatted=db_post.created_at_formatted
                )
                # ✨ ELIMINADO: Ya no necesitamos redirigir la URL
            else:
                self.show_detail_modal = False
                yield rx.toast.error("Producto no encontrado o no disponible.")


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
    
