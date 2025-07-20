# likemodas/cart/state.py (VERSIÓN CORREGIDA FINAL)

import reflex as rx
from typing import Dict, List, Tuple
from ..auth.state import SessionState
# ✨ CAMBIO: Se importan todos los modelos necesarios para la consulta
from ..models import BlogPostModel, PurchaseModel, PurchaseItemModel, PurchaseStatus, CommentModel, UserInfo
from sqlmodel import select
from datetime import datetime
import reflex_local_auth
import sqlalchemy # Importa sqlalchemy completo

from ..admin.state import AdminConfirmState

class CartState(SessionState):
    """
    Estado para manejar el carrito de compras y el proceso de checkout.
    """
    cart: Dict[int, int] = {}
    purchase_successful: bool = False
    posts: list[BlogPostModel] = []

    def on_load(self):
        """Carga todos los posts públicos y activos para la galería."""
        with rx.session() as session:
            # --- ✨ CONSULTA CORREGIDA Y MÁS ROBUSTA ---
            # Esta consulta ahora carga de forma anidada las publicaciones,
            # sus comentarios y la información de usuario de cada comentario.
            statement = (
                select(BlogPostModel)
                .options(
                    sqlalchemy.orm.joinedload(BlogPostModel.comments)
                    .joinedload(CommentModel.userinfo)
                    .joinedload(UserInfo.user)
                )
                .where(BlogPostModel.publish_active == True, BlogPostModel.publish_date < datetime.now())
                .order_by(BlogPostModel.created_at.desc())
            )
            self.posts = session.exec(statement).unique().all()


    @rx.var
    def cart_items_count(self) -> int:
        """Devuelve el número total de items en el carrito."""
        return sum(self.cart.values())

    @rx.var
    def cart_details(self) -> List[Tuple[BlogPostModel, int]]:
        """
        Devuelve una lista de tuplas con el objeto BlogPostModel y la cantidad.
        """
        if not self.cart:
            return []
        with rx.session() as session:
            post_ids = list(self.cart.keys())
            posts = session.exec(
                select(BlogPostModel)
                .options(sqlalchemy.orm.joinedload(BlogPostModel.comments))
                .where(BlogPostModel.id.in_(post_ids))
            ).unique().all()
            post_map = {post.id: post for post in posts}
            return [(post_map[pid], self.cart[pid]) for pid in post_ids if pid in post_map]

    @rx.var
    def cart_total(self) -> float:
        """Calcula el precio total del carrito."""
        total = 0.0
        for post, quantity in self.cart_details:
            if post and post.price:
                total += post.price * quantity
        return total

    @rx.event
    def add_to_cart(self, post_id: int):
        """Añade un producto al carrito o incrementa su cantidad."""
        if not self.is_authenticated:
            return rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)
        
        current_quantity = self.cart.get(post_id, 0)
        self.cart[post_id] = current_quantity + 1

    @rx.event
    def remove_from_cart(self, post_id: int):
        """Reduce la cantidad de un producto o lo elimina si es el último."""
        if post_id in self.cart:
            if self.cart[post_id] > 1:
                self.cart[post_id] -= 1
            else:
                self.cart.pop(post_id, None)
                self.cart = self.cart

    @rx.event
    def handle_checkout(self):
        """
        Procesa el pago: crea los registros de compra en la BD y limpia el carrito.
        """
        if not self.is_authenticated or self.cart_total <= 0:
            return rx.window_alert("No se puede procesar la compra.")

        with rx.session() as session:
            user_info = self.authenticated_user_info
            if not user_info:
                 return rx.window_alert("Usuario no encontrado.")

            new_purchase = PurchaseModel(
                userinfo_id=user_info.id,
                total_price=self.cart_total,
                status=PurchaseStatus.PENDING 
            )
            session.add(new_purchase)
            session.commit()
            session.refresh(new_purchase)

            for post, quantity in self.cart_details:
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