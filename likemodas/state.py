# likemodas/state.py (CORREGIDO)

from __future__ import annotations
import reflex as rx
import reflex_local_auth
from urllib.parse import urlparse, parse_qs
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
    CommentModel, PasswordResetToken, LocalUser, ContactEntryModel,
    CommentVoteModel, VoteType
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
class CommentData(rx.Base):
    id: int; content: str; rating: int; created_at_formatted: str
    author_username: str; likes: int; dislikes: int

class PostDetailData(rx.Base):
    id: int; title: str; content: str; price: float; price_cop: str
    image_urls: list[str]; created_at_formatted: str; publish_active: bool
    comments: list[CommentData] = []

    @classmethod
    def from_orm(cls, post: BlogPostModel) -> "PostDetailData":
        return cls(
            id=post.id, title=post.title, content=post.content, price=post.price,
            price_cop=post.price_cop, image_urls=post.image_urls,
            created_at_formatted=post.created_at_formatted, publish_active=post.publish_active,
            comments=[
                CommentData(
                    id=c.id, content=c.content, rating=c.rating, created_at_formatted=c.created_at_formatted,
                    author_username=c.userinfo.user.username if c.userinfo and c.userinfo.user else "Anónimo",
                    likes=c.likes, dislikes=c.dislikes
                )
                for c in sorted(post.comments, key=lambda c: c.created_at, reverse=True)
            ]
        )

class ProductCardData(rx.Base):
    id: int; title: str; price: float = 0.0; image_urls: list[str] = []
    average_rating: float = 0.0; rating_count: int = 0; price_cop: str

    @classmethod
    def from_orm(cls, post: BlogPostModel) -> "ProductCardData":
        return cls(
            id=post.id, title=post.title, price=post.price or 0.0,
            image_urls=post.image_urls or [], average_rating=post.average_rating,
            rating_count=post.rating_count, price_cop=format_to_cop(post.price or 0.0)
        )

class AdminPurchaseCardData(rx.Base):
    id: int; customer_name: str; customer_email: str; purchase_date_formatted: str
    status: str; total_price: float; shipping_name: str; shipping_full_address: str
    shipping_phone: str; items_formatted: list[str]
    @property
    def total_price_cop(self) -> str: return format_to_cop(self.total_price)

class UserPurchaseHistoryCardData(rx.Base):
    id: int; purchase_date_formatted: str; status: str; total_price_cop: str
    shipping_name: str; shipping_address: str; shipping_neighborhood: str
    shipping_city: str; shipping_phone: str; items_formatted: list[str]

# --- ESTADO PRINCIPAL DE LA APLICACIÓN ---
class AppState(reflex_local_auth.LocalAuthState):
    """El estado único y monolítico de la aplicación."""

    # --- AUTH / SESSION ---
    error_message: str = ""
    success: bool = False

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
    @rx.event
    def handle_registration_email(self, form_data: dict):
        username, password = form_data.get("username"), form_data.get("password")
        password_errors = validate_password(password)
        if password_errors:
           self.error_message = "\n".join(password_errors)
           return

        with rx.session() as session:
            if session.exec(sqlmodel.select(LocalUser).where(LocalUser.username == username)).one_or_none():
                self.error_message = f"El usuario '{username}' ya existe."
                return

            password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            new_user = LocalUser(username=username, password_hash=password_hash)
            session.add(new_user); session.commit(); session.refresh(new_user)
            
            user_role = UserRole.ADMIN if username == "guardiantlemor01" else UserRole.CUSTOMER
            new_user_info = UserInfo(email=form_data["email"], user_id=new_user.id, role=user_role)
            session.add(new_user_info); session.commit(); session.refresh(new_user_info)

            token_str = secrets.token_urlsafe(32)
            expires = datetime.now(timezone.utc) + timedelta(hours=24)
            verification_token = VerificationToken(token=token_str, userinfo_id=new_user_info.id, expires_at=expires)
            session.add(verification_token); session.commit()
            
            send_verification_email(recipient_email=new_user_info.email, token=token_str)
        self.success = True

    info_message: str = ""

    @rx.event
    def verify_token(self):
        if not self.router.url: return
        token = parse_qs(urlparse(self.router.url).query).get("token", [""])[0]
        if not token:
            self.info_message = "Error: No se proporcionó un token de verificación."
            return

        with rx.session() as session:
            db_token = session.exec(sqlmodel.select(VerificationToken).where(VerificationToken.token == token)).one_or_none()
            if not db_token or datetime.now(timezone.utc) > db_token.expires_at:
                self.info_message = "El token de verificación es inválido o ha expirado."
                if db_token: session.delete(db_token); session.commit()
                return
            
            user_info = session.get(UserInfo, db_token.userinfo_id)
            if user_info:
                user_info.is_verified = True
                session.add(user_info); session.delete(db_token); session.commit()
                yield rx.toast.success("¡Cuenta verificada! Por favor, inicia sesión.")
                return rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)
            
            self.info_message = "Error: No se encontró el usuario asociado a este token."

    # --- MANEJO DE CONTRASEÑA OLVIDADA ---
    is_success: bool = False
    token: str = ""
    is_token_valid: bool = False

    def handle_forgot_password(self, form_data: dict):
        email = form_data.get("email", "")
        if not email:
            self.info_message, self.is_success = "Por favor, introduce tu correo electrónico.", False
            return
        with rx.session() as session:
            user_info = session.exec(sqlmodel.select(UserInfo).where(UserInfo.email == email)).one_or_none()
            if user_info:
                token_str = secrets.token_urlsafe(32)
                expires = datetime.now(timezone.utc) + timedelta(hours=1)
                reset_token = PasswordResetToken(token=token_str, user_id=user_info.user_id, expires_at=expires)
                session.add(reset_token); session.commit()
                send_password_reset_email(recipient_email=email, token=token_str)
        self.info_message, self.is_success = "Si una cuenta con ese correo existe, hemos enviado un enlace para restablecer la contraseña.", True

    def on_load_check_token(self):
        self.token = self.router.page.query_params.get("token", "")
        if not self.token:
            self.info_message, self.is_token_valid = "Enlace no válido. Falta el token.", False
            return
        with rx.session() as session:
            db_token = session.exec(sqlmodel.select(PasswordResetToken).where(PasswordResetToken.token == self.token)).one_or_none()
            if not db_token or datetime.now(timezone.utc) > db_token.expires_at:
                self.info_message, self.is_token_valid = "El enlace de reseteo es inválido o ha expirado.", False
                if db_token: session.delete(db_token); session.commit()
                return
            self.is_token_valid = True

    def handle_reset_password(self, form_data: dict):
        password, confirm_password = form_data.get("password", ""), form_data.get("confirm_password", "")
        if not self.is_token_valid: self.info_message = "Token no válido."; return
        if password != confirm_password: self.info_message = "Las contraseñas no coinciden."; return
        password_errors = validate_password(password)
        if password_errors: self.info_message = "\n".join(password_errors); return
        with rx.session() as session:
            db_token = session.exec(sqlmodel.select(PasswordResetToken).where(PasswordResetToken.token == self.token)).one_or_none()
            if not db_token: self.info_message = "Token inválido."; return
            user = session.get(LocalUser, db_token.user_id)
            if user:
                user.password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
                session.add(user); session.delete(db_token); session.commit()
                yield rx.toast.success("¡Contraseña actualizada con éxito!")
                return rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)

    # --- FILTROS DE BÚSQUEDA ---
    min_price: str = ""; max_price: str = ""; show_filters: bool = False; current_category: str = ""
    open_filter_name: str = ""; filter_color: str = ""; filter_talla: str = ""
    filter_tipo_prenda: str = ""; filter_tipo_zapato: str = ""; filter_numero_calzado: str = ""
    filter_tipo_mochila: str = ""; filter_tipo_general: str = ""; filter_material_tela: str = ""
    filter_medida_talla: str = ""

    def toggle_filters(self): self.show_filters = not self.show_filters
    def clear_all_filters(self):
        self.min_price, self.max_price, self.filter_color, self.filter_talla = "", "", "", ""
        self.filter_tipo_prenda, self.filter_tipo_zapato, self.filter_tipo_mochila = "", "", ""
        self.filter_tipo_general, self.filter_material_tela, self.filter_medida_talla = "", "", ""
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

    search_tipo_prenda: str = ""; search_tipo_zapato: str = ""; search_tipo_mochila: str = ""
    search_tipo_general: str = ""; search_color: str = ""; search_talla: str = ""
    search_numero_calzado: str = ""; search_material_tela: str = ""; search_medida_talla: str = ""
    
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

    # --- PRODUCTOS Y GALERÍA ---
    posts: list[ProductCardData] = []
    post: Optional[PostDetailData] = None
    is_loading: bool = True

    @rx.event
    def on_load(self):
        self.is_loading = True
        yield
        with rx.session() as session:
            results = session.exec(sqlmodel.select(BlogPostModel).options(sqlalchemy.orm.joinedload(BlogPostModel.comments)).where(BlogPostModel.publish_active == True, BlogPostModel.publish_date < datetime.now(timezone.utc)).order_by(BlogPostModel.created_at.desc())).unique().all()
            self.posts = [ProductCardData.from_orm(p) for p in results]
        self.is_loading = False
    
    @rx.event
    def on_load_public_detail(self):
        self.post = None; self.is_loading = True
        yield
        try:
            pid = int(self.router.page.query_params.get("id", "0"))
        except (ValueError, TypeError):
            self.is_loading = False
            return
        
        with rx.session() as session:
            db_post = session.exec(sqlmodel.select(BlogPostModel).options(sqlalchemy.orm.joinedload(BlogPostModel.comments).joinedload(CommentModel.userinfo).joinedload(UserInfo.user), sqlalchemy.orm.joinedload(BlogPostModel.comments).joinedload(CommentModel.votes)).where(BlogPostModel.id == pid, BlogPostModel.publish_active == True)).unique().one_or_none()
            if db_post:
                self.post = PostDetailData.from_orm(db_post)
        self.is_loading = False

    # --- CARRITO DE COMPRAS ---
    cart: Dict[int, int] = rx.Field(default_factory=dict)
    @rx.var
    def cart_items_count(self) -> int: return sum(self.cart.values())
    @rx.var
    def cart_total(self) -> float: return sum(p.price * q for p, q in self.cart_details if p and p.price)
    @rx.var
    def cart_total_cop(self) -> str: return format_to_cop(self.cart_total)
    
    @rx.var
    def cart_details(self) -> List[Tuple[Optional[ProductCardData], int]]:
        if not self.cart: return []
        with rx.session() as session:
            post_ids = list(self.cart.keys())
            if not post_ids: return []
            results = session.exec(sqlmodel.select(BlogPostModel).where(BlogPostModel.id.in_(post_ids))).all()
            post_map = {p.id: ProductCardData.from_orm(p) for p in results}
            return [(post_map.get(pid), self.cart[pid]) for pid in post_ids]

    @rx.event
    def add_to_cart(self, post_id: int):
        if not self.is_authenticated: return rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)
        self.cart[post_id] = self.cart.get(post_id, 0) + 1
        return rx.toast.success("Producto añadido al carrito.")
        
    @rx.event
    def remove_from_cart(self, post_id: int):
        if post_id in self.cart:
            self.cart[post_id] -= 1
            if self.cart[post_id] <= 0: del self.cart[post_id]

    # --- GESTIÓN DE FORMULARIO DE AÑADIR PRODUCTO (ADMIN) ---
    title: str = ""; content: str = ""; price: str = ""; category: str = ""
    temp_images: list[str] = rx.Field(default_factory=list)
    tipo_prenda: str = ""; search_add_tipo_prenda: str = ""

    @rx.var
    def categories(self) -> list[str]: return [c.value for c in Category]
    def set_title(self, value: str): self.title = value
    def set_content(self, value: str): self.content = value
    def set_price_from_input(self, value: str): self.price = value
    def set_category(self, value: str): self.category = value; self.tipo_prenda = ""
    def set_tipo_prenda(self, value: str): self.tipo_prenda = value
    def set_search_add_tipo_prenda(self, value: str): self.search_add_tipo_prenda = value

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        uploaded_filenames = []
        for file in files:
            upload_data = await file.read()
            outfile = rx.get_upload_dir() / file.name
            outfile.write_bytes(upload_data)
            uploaded_filenames.append(file.name)
        async with self: self.temp_images.extend(uploaded_filenames)

    @rx.event
    def remove_image(self, filename: str): self.temp_images.remove(filename)
    
    def _clear_add_form(self):
        self.title, self.content, self.price, self.category, self.tipo_prenda, self.temp_images = "", "", "", "", "", []
    
    def _create_post_from_state(self, is_published: bool) -> BlogPostModel:
        price_float = float(self.price) if self.price else 0.0
        attributes = {'tipo_prenda': self.tipo_prenda} if self.category == Category.ROPA.value else {}
        return BlogPostModel(
            userinfo_id=self.authenticated_user_info.id, title=self.title, content=self.content, price=price_float,
            image_urls=self.temp_images, category=self.category, attributes=attributes,
            publish_active=is_published, publish_date=datetime.now(timezone.utc) if is_published else None
        )
        
    @rx.event
    def submit_draft(self):
        if not self.is_admin or not self.title: return rx.toast.error("El título es obligatorio.")
        with rx.session() as session: session.add(self._create_post_from_state(is_published=False)); session.commit()
        self._clear_add_form()
        yield rx.toast.success("Borrador guardado.")
        return rx.redirect(navigation.routes.BLOG_POSTS_ROUTE)

    @rx.event
    def submit_and_publish(self):
        if not self.is_admin or not self.title or not self.price or not self.category:
            return rx.toast.error("Título, precio y categoría son obligatorios.")
        with rx.session() as session:
            new_post = self._create_post_from_state(is_published=True)
            session.add(new_post); session.commit(); session.refresh(new_post)
            new_id = new_post.id
        self._clear_add_form()
        yield rx.toast.success("Producto publicado.")
        return rx.redirect(f"{navigation.routes.BLOG_PUBLIC_DETAIL_ROUTE}/{new_id}")

    # --- DIRECCIONES DE ENVÍO Y CHECKOUT ---
    addresses: List[ShippingAddressModel] = rx.Field(default_factory=list)
    show_form: bool = False
    city: str = ""; neighborhood: str = ""; search_city: str = ""; search_neighborhood: str = ""
    default_shipping_address: Optional[ShippingAddressModel] = None
    
    @rx.event
    def handle_checkout(self):
        if not self.is_authenticated or not self.default_shipping_address: return rx.toast.error("Por favor, selecciona una dirección predeterminada.")
        if not self.authenticated_user_info: return rx.toast.error("Error de usuario. Vuelve a iniciar sesión.")
        with rx.session() as session:
            new_purchase = PurchaseModel(
                userinfo_id=self.authenticated_user_info.id, total_price=self.cart_total, status=PurchaseStatus.PENDING,
                shipping_name=self.default_shipping_address.name, shipping_city=self.default_shipping_address.city,
                shipping_neighborhood=self.default_shipping_address.neighborhood, shipping_address=self.default_shipping_address.address,
                shipping_phone=self.default_shipping_address.phone
            )
            session.add(new_purchase); session.commit(); session.refresh(new_purchase)
            post_map = {p.id: p for p in session.exec(sqlmodel.select(BlogPostModel).where(BlogPostModel.id.in_(list(self.cart.keys())))).all()}
            for post_id, quantity in self.cart.items():
                if post_id in post_map: session.add(PurchaseItemModel(purchase_id=new_purchase.id, blog_post_id=post_map[post_id].id, quantity=quantity, price_at_purchase=post_map[post_id].price))
            session.commit()
        self.cart.clear(); self.default_shipping_address = None
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
                self.addresses = session.exec(sqlmodel.select(ShippingAddressModel).where(ShippingAddressModel.userinfo_id == self.authenticated_user_info.id).order_by(ShippingAddressModel.is_default.desc(), ShippingAddressModel.created_at.desc())).all()

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
            session.add(new_addr); session.commit()
        self.show_form = False
        yield self.load_addresses()
        return rx.toast.success("Nueva dirección guardada.")

    @rx.event
    def load_default_shipping_info(self):
        if self.authenticated_user_info:
            with rx.session() as session:
                self.default_shipping_address = session.exec(sqlmodel.select(ShippingAddressModel).where(ShippingAddressModel.userinfo_id == self.authenticated_user_info.id, ShippingAddressModel.is_default == True)).one_or_none()

    @rx.event
    def delete_address(self, address_id: int):
        if not self.authenticated_user_info: return
        with rx.session() as session:
            address_to_delete = session.get(ShippingAddressModel, address_id)
            if address_to_delete and address_to_delete.userinfo_id == self.authenticated_user_info.id:
                session.delete(address_to_delete); session.commit()
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
                session.add(new_default); session.commit()
                yield self.load_addresses()
    
    # --- BÚSQUEDA ---
    search_term: str = ""; search_results: List[ProductCardData] = []
    def set_search_term(self, term: str): self.search_term = term

    @rx.event
    def perform_search(self):
        if not self.search_term.strip(): return
        with rx.session() as session:
            results = session.exec(sqlmodel.select(BlogPostModel).options(sqlalchemy.orm.joinedload(BlogPostModel.comments)).where(BlogPostModel.title.ilike(f"%{self.search_term.strip()}%"), BlogPostModel.publish_active == True)).unique().all()
            self.search_results = [ProductCardData.from_orm(p) for p in results]
        return rx.redirect("/search-results")
        
    # --- PANEL DE ADMINISTRACIÓN ---
    pending_purchases: List[AdminPurchaseCardData] = []
    confirmed_purchases: List[AdminPurchaseCardData] = []
    new_purchase_notification: bool = False
    admin_posts: list[ProductCardData] = []
    search_query_admin_posts: str = ""
    search_query_admin_history: str = ""
    post_title: str = ""; post_content: str = ""; price_str: str = ""

    def set_new_purchase_notification(self, value: bool): self.new_purchase_notification = value
    def set_search_query_admin_posts(self, query: str): self.search_query_admin_posts = query
    def set_search_query_admin_history(self, query: str): self.search_query_admin_history = query
    def set_post_title(self, title: str): self.post_title = title
    def set_post_content(self, content: str): self.post_content = content
    def set_price(self, price: str): self.price_str = price
    
    @rx.var
    def blog_post_edit_url(self) -> str:
        return f"/blog/{self.post.id}/edit" if self.post else ""

    @rx.var
    def filtered_admin_posts(self) -> list[ProductCardData]:
        if not self.search_query_admin_posts.strip(): return self.admin_posts
        q = self.search_query_admin_posts.lower()
        return [p for p in self.admin_posts if q in p.title.lower()]

    @rx.var
    def filtered_admin_purchases(self) -> list[AdminPurchaseCardData]:
        if not self.search_query_admin_history.strip(): return self.confirmed_purchases
        q = self.search_query_admin_history.lower()
        return [p for p in self.confirmed_purchases if q in f"#{p.id}" or q in p.customer_name.lower() or q in p.customer_email.lower()]

    @rx.event
    def notify_admin_of_new_purchase(self): self.new_purchase_notification = True

    @rx.event
    def load_pending_purchases(self):
        if not self.is_admin: return
        with rx.session() as session:
            purchases = session.exec(sqlmodel.select(PurchaseModel).options(sqlalchemy.orm.joinedload(PurchaseModel.userinfo).joinedload(UserInfo.user), sqlalchemy.orm.joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post)).where(PurchaseModel.status == PurchaseStatus.PENDING).order_by(PurchaseModel.purchase_date.asc())).unique().all()
            self.pending_purchases = [AdminPurchaseCardData(id=p.id, customer_name=p.userinfo.user.username, customer_email=p.userinfo.email, purchase_date_formatted=p.purchase_date_formatted, status=p.status.value, total_price=p.total_price, shipping_name=p.shipping_name, shipping_full_address=f"{p.shipping_address}, {p.shipping_neighborhood}, {p.shipping_city}", shipping_phone=p.shipping_phone, items_formatted=p.items_formatted) for p in purchases]
            yield self.set_new_purchase_notification(len(self.pending_purchases) > 0)

    @rx.event
    def confirm_payment(self, purchase_id: int):
        if not self.is_admin: return
        with rx.session() as session:
            purchase = session.get(PurchaseModel, purchase_id)
            if purchase and purchase.status == PurchaseStatus.PENDING:
                purchase.status = PurchaseStatus.CONFIRMED; purchase.confirmed_at = datetime.now(timezone.utc)
                notification = NotificationModel(userinfo_id=purchase.userinfo_id, message=f"¡Tu compra #{purchase.id} ha sido confirmada!", url="/my-purchases")
                session.add(purchase); session.add(notification); session.commit()
                yield rx.toast.success(f"Compra #{purchase_id} confirmada.")
                yield self.load_pending_purchases()

    @rx.event
    def load_confirmed_purchases(self):
        if not self.is_admin: return
        with rx.session() as session:
            results = session.exec(sqlmodel.select(PurchaseModel).options(sqlalchemy.orm.joinedload(PurchaseModel.userinfo).joinedload(UserInfo.user), sqlalchemy.orm.joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post)).where(PurchaseModel.status != PurchaseStatus.PENDING).order_by(PurchaseModel.purchase_date.desc())).unique().all()
            self.confirmed_purchases = [AdminPurchaseCardData(id=p.id, customer_name=p.userinfo.user.username, customer_email=p.userinfo.email, purchase_date_formatted=p.purchase_date_formatted, status=p.status.value, total_price=p.total_price, shipping_name=p.shipping_name, shipping_full_address=f"{p.shipping_address}, {p.shipping_neighborhood}, {p.shipping_city}", shipping_phone=p.shipping_phone, items_formatted=p.items_formatted) for p in results]

    @rx.event
    def load_admin_posts(self):
        if not self.is_admin: return
        with rx.session() as session:
            results = session.exec(sqlmodel.select(BlogPostModel).options(sqlalchemy.orm.joinedload(BlogPostModel.comments)).order_by(BlogPostModel.created_at.desc())).unique().all()
            self.admin_posts = [ProductCardData.from_orm(p) for p in results]

    @rx.event
    def on_load_edit(self):
        try:
            pid = int(self.router.page.query_params.get("blog_id", "0"))
        except (ValueError, TypeError):
            self.post = None; return
        with rx.session() as session:
            db_post = session.get(BlogPostModel, pid)
            if db_post:
                self.post = PostDetailData.from_orm(db_post)
                self.post_title = db_post.title
                self.post_content = db_post.content
                self.price_str = str(db_post.price)

    @rx.event
    def handle_edit_submit(self, form_data: dict):
        if not self.is_admin or not self.post: return rx.toast.error("No se pudo guardar.")
        with rx.session() as session:
            post_to_update = session.get(BlogPostModel, self.post.id)
            if post_to_update:
                post_to_update.title = form_data.get("title", post_to_update.title)
                post_to_update.content = form_data.get("content", post_to_update.content)
                try: post_to_update.price = float(form_data.get("price", post_to_update.price))
                except (ValueError, TypeError): return rx.toast.error("El precio debe ser un número.")
                session.add(post_to_update); session.commit()
                yield rx.toast.success("Post actualizado.")
                return rx.redirect(f"/blog-public/{self.post.id}")

    @rx.event
    def delete_post(self, post_id: int):
        if not self.is_admin: return rx.toast.error("Acción no permitida.")
        with rx.session() as session:
            post_to_delete = session.get(BlogPostModel, post_id)
            if post_to_delete:
                session.delete(post_to_delete); session.commit()
                yield rx.toast.success("Publicación eliminada.")
                return rx.redirect(navigation.routes.BLOG_POSTS_ROUTE)

    @rx.event
    def toggle_publish_status(self, post_id: int):
        if not self.is_admin: return rx.toast.error("Acción no permitida.")
        with rx.session() as session:
            post_to_update = session.get(BlogPostModel, post_id)
            if post_to_update:
                post_to_update.publish_active = not post_to_update.publish_active
                session.add(post_to_update); session.commit(); session.refresh(post_to_update)
                self.post = PostDetailData.from_orm(post_to_update)
                return rx.toast.info(f"Estado de publicación: {post_to_update.publish_active}")
                 
    # --- HISTORIAL DE COMPRAS (USUARIO) ---
    user_purchases: List[UserPurchaseHistoryCardData] = []
    search_query_user_history: str = ""
    def set_search_query_user_history(self, query: str): self.search_query_user_history = query
    @rx.var
    def filtered_user_purchases(self) -> list[UserPurchaseHistoryCardData]:
        if not self.search_query_user_history.strip(): return self.user_purchases
        q = self.search_query_user_history.lower()
        return [p for p in self.user_purchases if q in f"#{p.id}" or any(q in item.lower() for item in p.items_formatted)]

    @rx.event
    def load_purchases(self):
        if not self.authenticated_user_info: return
        with rx.session() as session:
            results = session.exec(sqlmodel.select(PurchaseModel).options(sqlalchemy.orm.joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post)).where(PurchaseModel.userinfo_id == self.authenticated_user_info.id).order_by(PurchaseModel.purchase_date.desc())).unique().all()
            self.user_purchases = [UserPurchaseHistoryCardData(id=p.id, purchase_date_formatted=p.purchase_date_formatted, status=p.status.value, total_price_cop=p.total_price_cop, shipping_name=p.shipping_name, shipping_address=p.shipping_address, shipping_neighborhood=p.shipping_neighborhood, shipping_city=p.shipping_city, shipping_phone=p.shipping_phone, items_formatted=p.items_formatted) for p in results]

    # --- NOTIFICACIONES ---
    notifications: List[NotificationModel] = []
    @rx.var
    def unread_count(self) -> int: return sum(1 for n in self.notifications if not n.is_read)
    @rx.event
    def load_notifications(self):
        if not self.authenticated_user_info: return
        with rx.session() as session: self.notifications = session.exec(sqlmodel.select(NotificationModel).where(NotificationModel.userinfo_id == self.authenticated_user_info.id).order_by(sqlmodel.col(NotificationModel.created_at).desc())).all()
    @rx.event
    def mark_all_as_read(self):
        if not self.authenticated_user_info: return
        unread_ids = [n.id for n in self.notifications if not n.is_read]
        if not unread_ids: return
        with rx.session() as session:
            stmt = sqlmodel.update(NotificationModel).where(NotificationModel.id.in_(unread_ids)).values(is_read=True)
            session.exec(stmt); session.commit()
        yield self.load_notifications()

    # --- CONTACTO ---
    form_data: dict = {}; did_submit_contact: bool = False
    contact_entries: list[ContactEntryModel] = []; search_query_contact: str = ""
    def set_search_query_contact(self, query: str): self.search_query_contact = query
    @rx.var
    def thank_you_message(self) -> str:
        first_name = self.form_data.get("first_name", "")
        return f"¡Gracias, {first_name}!" if first_name else "¡Gracias por tu mensaje!"
    @rx.var
    def filtered_entries(self) -> list[ContactEntryModel]:
        if not self.search_query_contact.strip(): return self.contact_entries
        q = self.search_query_contact.lower()
        return [e for e in self.contact_entries if q in f"{e.first_name} {e.last_name} {e.email} {e.message}".lower()]
    async def handle_contact_submit(self, form_data: dict):
        self.form_data = form_data
        with rx.session() as session:
            user_info = self.authenticated_user_info
            entry = ContactEntryModel(first_name=form_data.get("first_name"), last_name=form_data.get("last_name"), email=form_data.get("email"), message=form_data.get("message"), userinfo_id=user_info.id if user_info else None)
            session.add(entry); session.commit()
        self.did_submit_contact = True; yield
        await asyncio.sleep(4)
        self.did_submit_contact = False; yield
    def load_entries(self):
        with rx.session() as session: self.contact_entries = session.exec(sqlmodel.select(ContactEntryModel).order_by(ContactEntryModel.id.desc())).all()
    
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

    # --- NUEVO EVENTO ON_LOAD PARA LA PÁGINA PRINCIPAL ---
    @rx.event
    def on_load_main_page(self):
        """Carga todos los productos y revisa la URL para abrir un modal si es necesario."""
        # Primero, ejecuta la lógica original para cargar la galería
        yield AppState.on_load

        # Luego, revisa si la URL tiene un ID de producto
        # Reflex lo poblará automáticamente en self.router.page.params
        product_id = self.router.page.params.get("product_id", None)
        if product_id is not None:
            # Si hay un ID, llama al evento para abrir el modal
            yield AppState.open_product_detail_modal(int(product_id), redirect=False)

    # --- FUNCIÓN DE ABRIR MODAL (ACTUALIZADA) ---
    @rx.event
    def open_product_detail_modal(self, post_id: int, redirect: bool = True):
        # ... (la lógica para buscar el producto en la BD se mantiene igual) ...
        self.product_in_modal = None
        self.show_detail_modal = True
        self.current_image_index = 0
        yield
        with rx.session() as session:
            db_post = session.exec(
                sqlmodel.select(BlogPostModel)
                .options(sqlalchemy.orm.joinedload(BlogPostModel.comments))
                .where(BlogPostModel.id == post_id, BlogPostModel.publish_active == True)
            ).unique().one_or_none()
            if db_post:
                self.product_in_modal = db_post
                # Si se necesita, actualiza la URL del navegador sin recargar la página
                if redirect:
                    yield rx.redirect(f"/product/{post_id}")
            else:
                self.show_detail_modal = False
                yield rx.toast.error("Producto no encontrado o no disponible.")

    # --- FUNCIÓN DE CERRAR MODAL (ACTUALIZADA) ---
    @rx.event
    def close_product_detail_modal(self, open_state: bool):
        if not open_state:
            self.show_detail_modal = False
            self.product_in_modal = None
            # Al cerrar, devolvemos la URL a la página principal
            yield rx.redirect("/")