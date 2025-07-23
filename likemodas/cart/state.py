import reflex as rx
from typing import Dict, List, Tuple
from ..auth.state import SessionState
from ..models import BlogPostModel, PurchaseModel, PurchaseItemModel, ShippingAddressModel, PurchaseStatus
from sqlmodel import select
from datetime import datetime
import reflex_local_auth
import sqlalchemy
from ..data.colombia_locations import load_colombia_data
# Se importa AdminConfirmState desde su ubicación correcta para las notificaciones
from ..admin.state import AdminConfirmState
from ..ui.filter_state import FilterState # <-- AÑADE ESTA IMPORTACIÓN

class ProductCardData(rx.Base):
    id: int
    title: str
    price: float = 0.0
    images: list[str] = []
    average_rating: float = 0.0
    rating_count: int = 0

class CartState(SessionState):
    cart: Dict[int, int] = {}
    posts: list[ProductCardData] = []
    
    colombia_data: Dict[str, List[str]] = load_colombia_data()
    shipping_name: str = ""
    shipping_city: str = ""
    shipping_neighborhood: str = ""
    shipping_address: str = ""
    shipping_phone: str = ""
    
    @rx.var
    def cities(self) -> List[str]:
        return list(self.colombia_data.keys())

    @rx.var
    def neighborhoods(self) -> List[str]:
        return self.colombia_data.get(self.shipping_city, [])
    
    @rx.var
    def filtered_posts(self) -> list[ProductCardData]:
        """Filtra la lista de posts principal según los filtros de precio."""
        # Obtiene una instancia del estado de los filtros
        filter_state = self.get_state(FilterState)
        
        posts_to_filter = self.posts
        
        try:
            # Accede a los valores como atributos normales de Python
            min_p = float(filter_state.min_price) if filter_state.min_price else 0
        except ValueError:
            min_p = 0
            
        try:
            # Accede a los valores como atributos normales de Python
            max_p = float(filter_state.max_price) if filter_state.max_price else float('inf')
        except ValueError:
            max_p = float('inf')

        if min_p > 0 or max_p != float('inf'):
            return [
                p for p in posts_to_filter
                if (p.price >= min_p and p.price <= max_p)
            ]
        
        return posts_to_filter
    
    @rx.event
    def set_shipping_city_and_reset_neighborhood(self, city: str):
        self.shipping_city = city
        self.shipping_neighborhood = ""

    @rx.event
    def on_load(self):
        with rx.session() as session:
            statement = (
                select(BlogPostModel)
                .options(sqlalchemy.orm.joinedload(BlogPostModel.comments))
                .where(BlogPostModel.publish_active == True, BlogPostModel.publish_date < datetime.now())
                .order_by(BlogPostModel.created_at.desc())
            )
            results = session.exec(statement).unique().all()
            self.posts = [
                ProductCardData(
                    id=post.id, title=post.title, price=post.price, images=post.images,
                    average_rating=post.average_rating, rating_count=post.rating_count
                ) for post in results
            ]
            
    @rx.var
    def cart_items_count(self) -> int:
        return sum(self.cart.values())

    @rx.var
    def cart_details(self) -> List[Tuple[ProductCardData, int]]:
        if not self.cart:
            return []
        posts_in_cart = [post for post in self.posts if post.id in self.cart]
        post_map = {post.id: post for post in posts_in_cart}
        return [(post_map[pid], self.cart[pid]) for pid in self.cart.keys() if pid in post_map]

    @rx.var
    def cart_total(self) -> float:
        total = 0.0
        for post, quantity in self.cart_details:
            if post and post.price:
                total += post.price * quantity
        return total

    @rx.event
    def add_to_cart(self, post_id: int):
        if not self.is_authenticated:
            return rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)
        current_quantity = self.cart.get(post_id, 0)
        self.cart[post_id] = current_quantity + 1

    @rx.event
    def remove_from_cart(self, post_id: int):
        if post_id in self.cart:
            if self.cart[post_id] > 1:
                self.cart[post_id] -= 1
            else:
                self.cart.pop(post_id, None)
                self.cart = self.cart
    
    @rx.var
    def dashboard_posts(self) -> list[ProductCardData]:
        limit = min(20, len(self.posts))
        return self.posts[:limit]

    @rx.var
    def landing_page_posts(self) -> list[ProductCardData]:
        if not self.posts:
            return []
        return self.posts[:1]
        

    @rx.event
    def load_default_shipping_info(self):
        """Carga la dirección predeterminada del usuario si existe."""
        if not self.authenticated_user_info:
            return

        with rx.session() as session:
            default_address = session.exec(
                select(ShippingAddressModel).where(
                    ShippingAddressModel.userinfo_id == self.authenticated_user_info.id,
                    ShippingAddressModel.is_default == True
                )
            ).one_or_none()

            if default_address:
                # Pre-popula los campos del estado del carrito
                self.shipping_name = default_address.name
                self.shipping_phone = default_address.phone
                self.shipping_city = default_address.city
                self.shipping_neighborhood = default_address.neighborhood
                self.shipping_address = default_address.address
                # ¡Dispara el evento para cargar los barrios correspondientes!
                yield self.set_shipping_city_and_reset_neighborhood(default_address.city)


    @rx.event
    def handle_checkout(self, form_data: dict):
        """
        Maneja la compra final usando la información de envío del formulario.
        """
        # Validación usando la información del formulario
        name = form_data.get("shipping_name", "").strip()
        phone = form_data.get("shipping_phone", "").strip()
        address = form_data.get("shipping_address", "").strip()
        city = self.shipping_city
        neighborhood = self.shipping_neighborhood

        if not all([name, city, address, phone]):
            return rx.toast.error("Por favor, completa todos los campos requeridos (*).")
        
        if not self.is_authenticated or self.cart_total <= 0:
            return rx.window_alert("No se puede procesar la compra.")
        
        with rx.session() as session:
            user_info = self.authenticated_user_info
            if not user_info:
                 return rx.window_alert("Usuario no encontrado.")
            
            post_ids_in_cart = list(self.cart.keys())
            db_posts_query = select(BlogPostModel).where(BlogPostModel.id.in_(post_ids_in_cart))
            db_posts = session.exec(db_posts_query).all()
            db_post_map = {post.id: post for post in db_posts}

            new_purchase = PurchaseModel(
                userinfo_id=user_info.id,
                total_price=self.cart_total,
                status=PurchaseStatus.PENDING,
                # Usa las variables del formulario y del estado
                shipping_name=name,
                shipping_city=city,
                shipping_neighborhood=neighborhood,
                shipping_address=address,
                shipping_phone=phone
            )
            session.add(new_purchase)
            session.commit()
            session.refresh(new_purchase)

            for post_id, quantity in self.cart.items():
                if post_id in db_post_map:
                    post = db_post_map[post_id]
                    purchase_item = PurchaseItemModel(
                        purchase_id=new_purchase.id, blog_post_id=post.id,
                        quantity=quantity, price_at_purchase=post.price
                    )
                    session.add(purchase_item)
            session.commit()

        self.cart = {}
        yield AdminConfirmState.notify_admin_of_new_purchase()
        yield rx.toast.success("¡Gracias por tu compra! Tu orden está pendiente de confirmación.")
        return rx.redirect("/my-purchases")

