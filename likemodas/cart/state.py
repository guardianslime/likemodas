# likemodas/cart/state.py

import reflex as rx
from typing import Dict, List, Tuple
from ..auth.state import SessionState
from ..models import BlogPostModel, PurchaseModel, PurchaseItemModel, PurchaseStatus
from sqlmodel import select
from datetime import datetime
import reflex_local_auth
import sqlalchemy
from ..admin.state import AdminConfirmState
from ..data.colombia_locations import load_colombia_data # Importamos los datos

class ProductCardData(rx.Base):
    id: int
    title: str
    price: float = 0.0
    images: list[str] = []
    average_rating: float = 0.0
    rating_count: int = 0

class CartState(SessionState):
    cart: Dict[int, int] = {}
    
    # --- ESTADO PARA EL FORMULARIO DE ENVÍO ---
    colombia_data: Dict[str, List[str]] = load_colombia_data()
    shipping_name: str = ""
    shipping_city: str = ""
    shipping_neighborhood: str = ""
    shipping_address: str = ""
    shipping_phone: str = ""
    
    @rx.var
    def cities(self) -> List[str]:
        """Devuelve una lista de todas las ciudades para el menú desplegable."""
        return list(self.colombia_data.keys())

    @rx.var
    def neighborhoods(self) -> List[str]:
        """Devuelve los barrios de la ciudad seleccionada."""
        return self.colombia_data.get(self.shipping_city, [])

    @rx.event
    def set_shipping_city_and_reset_neighborhood(self, city: str):
        """Actualiza la ciudad y reinicia el barrio seleccionado."""
        self.shipping_city = city
        self.shipping_neighborhood = ""

    # (on_load, cart_items_count, cart_details, etc. no cambian)
    # ...
    
    @rx.event
    def handle_checkout(self, form_data: dict):
        """Maneja el envío del formulario de pago."""
        # Se extraen los datos del formulario que envía el componente rx.form
        name = form_data.get("shipping_name", "").strip()
        address = form_data.get("shipping_address", "").strip()
        phone = form_data.get("shipping_phone", "").strip()
        
        # Los datos de los menús desplegables se toman del estado
        city = self.shipping_city
        neighborhood = self.shipping_neighborhood

        if not all([name, city, address, phone]):
            return rx.toast.error("Por favor, completa todos los campos requeridos (*).")
        
        # ... (resto de la lógica de handle_checkout no cambia)
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