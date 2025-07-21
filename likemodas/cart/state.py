# likemodas/cart/state.py (VERSIÓN FINAL Y CORREGIDA)

import reflex as rx
from typing import Dict, List, Tuple
from ..auth.state import SessionState  # <--- ¡ESTA ES LA LÍNEA CORREGIDA!
from ..models import BlogPostModel, PurchaseModel, PurchaseItemModel, PurchaseStatus
from sqlmodel import select
from datetime import datetime
import reflex_local_auth
import sqlalchemy
from ..admin.state import AdminConfirmState

class ProductCardData(rx.Base):
    id: int
    title: str
    price: float = 0.0
    images: list[str] = []
    average_rating: float = 0.0
    rating_count: int = 0

class CartState(SessionState):
    """
    Estado que maneja el carrito de compras Y la carga de productos públicos.
    """
    cart: Dict[int, int] = {}
    purchase_successful: bool = False
    posts: list[ProductCardData] = []

    @rx.event
    def on_load(self):
        """Carga los posts, calcula las calificaciones y los transforma para la vista."""
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
                    id=post.id,
                    title=post.title,
                    price=post.price,
                    images=post.images,
                    average_rating=post.average_rating,
                    rating_count=post.rating_count
                )
                for post in results
            ]

    @rx.var
    def cart_items_count(self) -> int:
        return sum(self.cart.values())

    # --- 👇 ESTE MÉTODO ES EL ÚNICO CAMBIO IMPORTANTE 👇 ---
    @rx.var
    def cart_details(self) -> List[Tuple[ProductCardData, int]]:
        """Devuelve los detalles del carrito usando el modelo de vista ProductCardData."""
        if not self.cart:
            return []
        
        # Filtra los posts ya cargados en memoria para encontrar los que están en el carrito
        posts_in_cart = [
            post for post in self.posts if post.id in self.cart
        ]
        
        # Crea un mapa para un acceso rápido
        post_map = {post.id: post for post in posts_in_cart}

        # Devuelve una lista de tuplas (ProductCardData, cantidad)
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

    @rx.event
    def handle_checkout(self):
        if not self.is_authenticated or self.cart_total <= 0:
            return rx.window_alert("No se puede procesar la compra.")
        with rx.session() as session:
            user_info = self.authenticated_user_info
            if not user_info:
                 return rx.window_alert("Usuario no encontrado.")
            
            # Para crear la compra, sí necesitamos los objetos reales de la BD
            post_ids_in_cart = list(self.cart.keys())
            db_posts_query = select(BlogPostModel).where(BlogPostModel.id.in_(post_ids_in_cart))
            db_posts = session.exec(db_posts_query).all()
            db_post_map = {post.id: post for post in db_posts}

            new_purchase = PurchaseModel(
                userinfo_id=user_info.id,
                total_price=self.cart_total,
                status=PurchaseStatus.PENDING 
            )
            session.add(new_purchase)
            session.commit()
            session.refresh(new_purchase)

            for post_id, quantity in self.cart.items():
                if post_id in db_post_map:
                    post = db_post_map[post_id]
                    purchase_item = PurchaseItemModel(
                        purchase_id=new_purchase.id,
                        blog_post_id=post.id,
                        quantity=quantity,
                        price_at_purchase=post.price
                    )
                    session.add(purchase_item)

            session.commit()
        self.cart = {}
        self.purchase_successful = True
        yield AdminConfirmState.notify_admin_of_new_purchase()
        yield rx.toast.success("¡Gracias por tu compra!\nTu orden está pendiente de confirmación.")
        return rx.redirect("/my-purchases")