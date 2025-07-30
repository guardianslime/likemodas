# likemodas/cart/state.py

import reflex as rx
from typing import Dict, List, Tuple, Optional
from ..auth.state import SessionState
from ..models import Category, PurchaseModel, PurchaseStatus, UserInfo, PurchaseItemModel, BlogPostModel, NotificationModel, ShippingAddressModel
from sqlmodel import select
from datetime import datetime
import reflex_local_auth
import sqlalchemy
from sqlalchemy import or_, cast, String
from ..data.colombia_locations import load_colombia_data
from ..admin.state import AdminConfirmState
from ..utils.formatting import format_to_cop 

class ProductCardData(rx.Base):
    id: int
    title: str
    price: float = 0.0
    price_formatted: str = ""  # <-- ✅ CAMBIO CLAVE: Añadimos este campo
    image_urls: list[str] = ""
    average_rating: float = 0.0
    rating_count: int = 0

    @property
    def price_cop(self) -> str:
        """Propiedad para el precio ya formateado."""
        return format_to_cop(self.price)



class CartState(SessionState):
    cart: Dict[int, int] = {}
    posts: list[ProductCardData] = []
    default_shipping_address: Optional[ShippingAddressModel] = None

    # --- ✅ NUEVA BANDERA DE CARGA ---
    is_loading: bool = True

    @rx.var
    def dashboard_posts(self) -> list[ProductCardData]:
        return self.posts[:20]

    @rx.var
    def landing_page_posts(self) -> list[ProductCardData]:
        return self.posts[:1] if self.posts else []

    @rx.var
    def filtered_posts(self) -> list[ProductCardData]:
        posts_to_filter = self.posts
        if self.current_category and self.current_category != "todos":
            with rx.session() as session:
                try:
                    category_enum = Category(self.current_category)
                    post_ids_in_category = set(session.exec(select(BlogPostModel.id).where(BlogPostModel.category == category_enum)).all())
                    posts_to_filter = [p for p in self.posts if p.id in post_ids_in_category]
                except ValueError:
                    return []
        try:
            min_p = float(self.min_price) if self.min_price else 0
            max_p = float(self.max_price) if self.max_price else float('inf')
        except (ValueError, TypeError):
            min_p, max_p = 0, float('inf')
        if min_p > 0 or max_p != float('inf'):
            posts_to_filter = [p for p in posts_to_filter if min_p <= p.price <= max_p]
        active_filters = any([self.filter_color, self.filter_talla, self.filter_tipo_prenda, self.filter_numero_calzado, self.filter_tipo_zapato, self.filter_tipo_mochila, self.filter_tipo_general, self.filter_material_tela, self.filter_medida_talla])
        if not active_filters:
            return posts_to_filter
        with rx.session() as session:
            post_ids = [p.id for p in posts_to_filter]
            if not post_ids: return []
            query = select(BlogPostModel).where(BlogPostModel.id.in_(post_ids))
            if self.current_category == Category.ROPA.value:
                if self.filter_color: query = query.where(cast(BlogPostModel.attributes['color'], String).ilike(f"%{self.filter_color}%"))
                if self.filter_talla: query = query.where(cast(BlogPostModel.attributes['talla'], String).ilike(f"%{self.filter_talla}%"))
                if self.filter_tipo_prenda: query = query.where(cast(BlogPostModel.attributes['tipo_prenda'], String) == self.filter_tipo_prenda)
            elif self.current_category == Category.CALZADO.value:
                if self.filter_color: query = query.where(cast(BlogPostModel.attributes['color'], String).ilike(f"%{self.filter_color}%"))
                if self.filter_numero_calzado: query = query.where(cast(BlogPostModel.attributes['numero_calzado'], String) == self.filter_numero_calzado)
                if self.filter_tipo_zapato: query = query.where(cast(BlogPostModel.attributes['tipo_zapato'], String) == self.filter_tipo_zapato)
            elif self.current_category == Category.MOCHILAS.value:
                if self.filter_tipo_mochila: query = query.where(cast(BlogPostModel.attributes['tipo_mochila'], String) == self.filter_tipo_mochila)
            else:
                if self.filter_tipo_general: query = query.where(or_(cast(BlogPostModel.attributes['tipo_prenda'], String) == self.filter_tipo_general, cast(BlogPostModel.attributes['tipo_zapato'], String) == self.filter_tipo_general, cast(BlogPostModel.attributes['tipo_mochila'], String) == self.filter_tipo_mochila))
                if self.filter_material_tela: mat = f"%{self.filter_material_tela}%"; query = query.where(or_(cast(BlogPostModel.attributes['tipo_tela'], String).ilike(mat), cast(BlogPostModel.attributes['material'], String).ilike(mat)))
                if self.filter_medida_talla: med = f"%{self.filter_medida_talla}%"; query = query.where(or_(cast(BlogPostModel.attributes['talla'], String).ilike(med), cast(BlogPostModel.attributes['numero_calzado'], String).ilike(med), cast(BlogPostModel.attributes['medidas'], String).ilike(med)))
                if self.filter_color: query = query.where(cast(BlogPostModel.attributes['color'], String).ilike(f"%{self.filter_color}%"))
            filtered_db_posts = session.exec(query).all()
            filtered_ids = {p.id for p in filtered_db_posts}
            return [p for p in posts_to_filter if p.id in filtered_ids]

    @rx.var
    def cart_total_cop(self) -> str:
        return format_to_cop(self.cart_total)

    @rx.event
    def load_posts_and_set_category(self):
        self.is_loading = True
        yield
        
        self.current_category = self.router.page.params.get("cat_name", "")
        # Llama al on_load original para recargar los posts, que ya gestiona la bandera
        yield self.on_load

    @rx.event
    def on_load(self):
        """Carga los posts y les añade el precio ya formateado."""
        self.is_loading = True
        yield
        with rx.session() as session:
            results = session.exec(
                select(BlogPostModel)
                .options(sqlalchemy.orm.joinedload(BlogPostModel.comments))
                .where(BlogPostModel.publish_active == True, BlogPostModel.publish_date < datetime.now())
                .order_by(BlogPostModel.created_at.desc())
            ).unique().all()
            
            # --- ✅ CAMBIO CLAVE AQUÍ ---
            # Creamos la lista de posts y llenamos 'price_formatted' al instante.
            self.posts = [
                ProductCardData(
                    id=p.id,
                    title=p.title,
                    price=p.price,
                    price_formatted=format_to_cop(p.price),
                    image_urls=p.image_urls or [], # <-- LÍNEA CORREGIDA
                    average_rating=p.average_rating,
                    rating_count=p.rating_count
                ) for p in results
            ]
        self.is_loading = False
             
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
        if not self.is_authenticated: return rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)
        self.cart[post_id] = self.cart.get(post_id, 0) + 1

    @rx.event
    def remove_from_cart(self, post_id: int):
        if post_id in self.cart:
            if self.cart[post_id] > 1: self.cart[post_id] -= 1
            else: self.cart.pop(post_id, None); self.cart = self.cart

    @rx.event
    def load_default_shipping_info(self):
        if self.authenticated_user_info:
            with rx.session() as session:
                self.default_shipping_address = session.exec(select(ShippingAddressModel).where(ShippingAddressModel.userinfo_id == self.authenticated_user_info.id, ShippingAddressModel.is_default == True)).one_or_none()

    @rx.event
    def handle_checkout(self):
        if not self.is_authenticated or not self.default_shipping_address:
            return rx.toast.error("Por favor, selecciona una dirección predeterminada.")
        with rx.session() as session:
            user_info = self.authenticated_user_info
            if not user_info: return rx.window_alert("Usuario no encontrado.")
            post_ids = list(self.cart.keys())
            db_posts_map = {p.id: p for p in session.exec(select(BlogPostModel).where(BlogPostModel.id.in_(post_ids))).all()}
            new_purchase = PurchaseModel(
                userinfo_id=user_info.id, total_price=self.cart_total, status=PurchaseStatus.PENDING,
                shipping_name=self.default_shipping_address.name, shipping_city=self.default_shipping_address.city,
                shipping_neighborhood=self.default_shipping_address.neighborhood, shipping_address=self.default_shipping_address.address,
                shipping_phone=self.default_shipping_address.phone
            )
            session.add(new_purchase); session.commit(); session.refresh(new_purchase)
            for post_id, quantity in self.cart.items():
                if post_id in db_posts_map:
                    post = db_posts_map[post_id]
                    session.add(PurchaseItemModel(purchase_id=new_purchase.id, blog_post_id=post.id, quantity=quantity, price_at_purchase=post.price))
            session.commit()
        self.cart.clear(); self.default_shipping_address = None
        yield AdminConfirmState.notify_admin_of_new_purchase()
        yield rx.toast.success("¡Gracias por tu compra! Tu orden está pendiente de confirmación.")
        return rx.redirect("/my-purchases")