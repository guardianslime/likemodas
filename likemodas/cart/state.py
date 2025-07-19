# likemodas/cart/state.py (CORREGIDO Y COMPLETO)

import reflex as rx
from typing import Dict, List, Tuple
from ..auth.state import SessionState
from ..models import BlogPostModel, PurchaseModel, PurchaseItemModel, PurchaseStatus
from sqlmodel import select
from datetime import datetime
import reflex_local_auth

# Asegúrate de que esta importación (del paso anterior) esté presente
from ..admin.state import AdminConfirmState

class CartState(SessionState):
    """
    Estado para manejar el carrito de compras y el proceso de checkout.
    """
    # El carrito será un diccionario: {post_id: quantity}
    cart: Dict[int, int] = {}
    
    # Para mostrar un mensaje de éxito después de la compra
    purchase_successful: bool = False

    # Variable y método para cargar los posts públicos
    posts: list[BlogPostModel] = []

    def on_load(self):
        """Carga todos los posts públicos y activos para la galería."""
        with rx.session() as session:
            self.posts = session.exec(
                select(BlogPostModel)
                .where(BlogPostModel.publish_active == True, BlogPostModel.publish_date < datetime.now())
                .order_by(BlogPostModel.created_at.desc())
            ).all()

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
            posts = session.exec(select(BlogPostModel).where(BlogPostModel.id.in_(post_ids))).all()
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
                # Usamos pop para asegurar que se elimine la clave
                self.cart.pop(post_id, None)
                # Forzamos la actualización para que la UI reaccione
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

            # 1. Crear la orden de compra principal
            new_purchase = PurchaseModel(
                userinfo_id=user_info.id,
                total_price=self.cart_total,
                status=PurchaseStatus.PENDING 
            )
            session.add(new_purchase)
            session.commit()
            session.refresh(new_purchase)

            # 2. Crear los items de la compra
            for post, quantity in self.cart_details:
                purchase_item = PurchaseItemModel(
                    purchase_id=new_purchase.id,
                    blog_post_id=post.id,
                    quantity=quantity,
                    price_at_purchase=post.price
                )
                session.add(purchase_item)
            
            session.commit()

        # 3. Limpiar el carrito y redirigir
        self.cart = {}
        self.purchase_successful = True
        
        # 4. Enviar notificaciones y redirigir
        yield AdminConfirmState.notify_admin_of_new_purchase()
        yield rx.toast.success("¡Gracias por tu compra! Tu orden está pendiente de confirmación.")
        
        return rx.redirect("/my-purchases")