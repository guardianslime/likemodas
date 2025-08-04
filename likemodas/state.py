# likemodas/state.py

import reflex as rx
import reflex_local_auth
import sqlmodel
import sqlalchemy
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import secrets
import re

from . import navigation
from .models import (
    UserInfo, UserRole, VerificationToken, BlogPostModel, ShippingAddressModel,
    PurchaseModel, PurchaseStatus, PurchaseItemModel, NotificationModel, Category,
    CommentModel, CommentVoteModel, VoteType, ContactEntryModel
)
from .services.email_service import send_verification_email
from .utils.formatting import format_to_cop
from .data.colombia_locations import load_colombia_data
from .data.product_options import (
    LISTA_TIPOS_ROPA, LISTA_TIPOS_ZAPATOS, LISTA_TIPOS_MOCHILAS, LISTA_TIPOS_GENERAL,
    LISTA_COLORES, LISTA_TALLAS_ROPA, LISTA_NUMEROS_CALZADO, LISTA_MATERIALES, LISTA_MEDIDAS_GENERAL
)

# Modelo de datos que se puede usar en varios lugares
class ProductCardData(rx.Base):
    id: int
    title: str
    price: float = 0.0
    price_formatted: str = ""
    image_urls: list[str] = []
    average_rating: float = 0.0
    rating_count: int = 0
    @property
    def price_cop(self) -> str:
        return format_to_cop(self.price)

class AppState(reflex_local_auth.LocalAuthState):
    """
    El estado único y monolítico de la aplicación.
    Contiene todas las variables y métodos de los estados modulares.
    """
    
    # --- Variables de SessionState (Auth) ---
    new_purchase_notification: bool = False
    min_price: str = ""
    max_price: str = ""
    show_filters: bool = False
    current_category: str = ""
    filter_color: str = ""
    # ... (y todas las demás variables de filtro)

    # --- Variables de NavState ---
    # (No tiene variables, solo métodos)

    # --- Variables de CartState ---
    cart: Dict[int, int] = rx.Field(default_factory=dict)
    posts: list[ProductCardData] = rx.Field(default_factory=list)
    default_shipping_address: Optional[ShippingAddressModel] = None
    is_loading: bool = True

    # --- Variables de BlogPostState ---
    admin_posts: list[BlogPostModel] = rx.Field(default_factory=list) # Renombrado para evitar colisión
    post: Optional[BlogPostModel] = None
    
    # --- Variables de CommentState ---
    comments: list[CommentModel] = rx.Field(default_factory=list)
    new_comment_text: str = ""
    new_comment_rating: int = 0

    # --- Variables de SearchState ---
    search_term: str = ""
    search_results: List[ProductCardData] = []
    
    # --- Y así sucesivamente para las variables de los demás estados... ---
    
    # --- MÉTODOS DE TODOS LOS ESTADOS FUSIONADOS ---

    # Métodos de SessionState / Auth
    @rx.var(cache=True)
    def authenticated_user_info(self) -> UserInfo | None: 
        if not self.authenticated_user or self.authenticated_user.id < 0:
            return None
        with rx.session() as session:
            return session.exec(
                sqlmodel.select(UserInfo).where(UserInfo.user_id == self.authenticated_user.id)
            ).one_or_none()

    @rx.var
    def is_admin(self) -> bool:
        return self.authenticated_user_info is not None and self.authenticated_user_info.role == UserRole.ADMIN

    # Métodos de NavState
    def to_home(self): return rx.redirect(navigation.routes.HOME_ROUTE)
    def to_login(self): return rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)
    def to_register(self): return rx.redirect(reflex_local_auth.routes.REGISTER_ROUTE)
    def to_logout(self): return rx.redirect(navigation.routes.LOGOUT_ROUTE)
    def to_my_account(self): return rx.redirect(navigation.routes.MY_ACCOUNT_ROUTE)
    def to_contact(self): return rx.redirect(navigation.routes.CONTACT_US_ROUTE)

    # Métodos de CartState
    @rx.var
    def cart_items_count(self) -> int: return sum(self.cart.values())
    
    @rx.var
    def cart_details(self) -> List[Tuple[ProductCardData, int]]:
        if not self.cart: return []
        post_map = {p.id: p for p in self.posts}
        return [(post_map[pid], self.cart[pid]) for pid in self.cart if pid in post_map]

    @rx.var
    def cart_total(self) -> float:
        return sum(p.price * q for p, q in self.cart_details if p and p.price)
        
    @rx.event
    def add_to_cart(self, post_id: int):
        if not self.is_authenticated:
            return rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)
        self.cart[post_id] = self.cart.get(post_id, 0) + 1

    # ... y así sucesivamente para TODOS los demás métodos de TODOS tus archivos de estado.
    # Debes copiarlos y pegarlos aquí dentro del cuerpo de la clase AppState.