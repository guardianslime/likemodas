# likemodas/cart/state.py (VERSIÓN FINAL CON IMPORTACIÓN CORREGIDA)

import reflex as rx
from typing import Dict, List, Tuple
from ..auth.state import SessionState
from ..models import PurchaseModel, PurchaseStatus, UserInfo, PurchaseItemModel, BlogPostModel, NotificationModel
from sqlmodel import select
from datetime import datetime
import reflex_local_auth
import sqlalchemy
# --- CAMBIO 1: Se elimina la importación de aquí para romper el ciclo ---
# from ..admin.state import AdminConfirmState 
from ..data.colombia_locations import load_colombia_data

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

    # (El resto de la clase hasta handle_checkout no cambia)
    # ... on_load, cart_items_count, cart_details, etc. ...
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
                
    @rx.event
    def handle_checkout(self, form_data: dict):
        """Maneja el envío del formulario de pago."""
        # --- CAMBIO 2: Se importa AdminConfirmState aquí adentro ---
        from ..admin.state import AdminConfirmState

        name = form_data.get("shipping_name", "").strip()
        address = form_data.get("shipping_address", "").strip()
        phone = form_data.get("shipping_phone", "").strip()
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
    

class AdminConfirmState(SessionState):
    """Estado para manejar las confirmaciones de compras pendientes."""
    pending_purchases: List[PurchaseModel] = []

    @rx.event
    def load_pending_purchases(self):
        """Carga las compras pendientes para que el admin las revise."""
        if not self.is_admin:
            self.pending_purchases = []
            return
        with rx.session() as session:
            statement = (
                select(PurchaseModel)
                .options(
                    sqlalchemy.orm.joinedload(PurchaseModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post)
                )
                .where(PurchaseModel.status == PurchaseStatus.PENDING)
                .order_by(PurchaseModel.purchase_date.asc())
            )
            self.pending_purchases = session.exec(statement).unique().all()
            self.new_purchase_notification = len(self.pending_purchases) > 0

    # ✅ NUEVO EVENTO PARA CONFIRMAR UN PAGO
    @rx.event
    def confirm_payment(self, purchase_id: int):
        """Confirma un pago, actualiza el estado y notifica al usuario."""
        if not self.is_admin:
            return rx.toast.error("No tienes permisos de administrador.")
        
        with rx.session() as session:
            purchase = session.get(PurchaseModel, purchase_id)
            if not purchase:
                return rx.toast.error("Compra no encontrada.")

            purchase.status = PurchaseStatus.CONFIRMED
            purchase.confirmed_at = datetime.utcnow()
            
            # Crea una notificación para el usuario
            notification = NotificationModel(
                userinfo_id=purchase.userinfo_id,
                message=f"¡Tu compra #{purchase.id} ha sido confirmada!",
                url="/my-purchases"
            )
            session.add(purchase)
            session.add(notification)
            session.commit()
        
        yield rx.toast.success(f"Compra #{purchase_id} confirmada.")
        # Vuelve a cargar la lista de pendientes para que se actualice la UI
        yield self.load_pending_purchases()

    @classmethod
    def notify_admin_of_new_purchase(cls):
        return SessionState.set_new_purchase_notification(True)


class PaymentHistoryState(SessionState):
    """Estado para ver el historial de compras confirmadas y enviadas."""
    purchases: List[PurchaseModel] = []

    @rx.event
    def load_confirmed_purchases(self):
        if not self.is_admin:
            self.purchases = []
            return
        with rx.session() as session:
            statement = (
                select(PurchaseModel)
                .options(
                    sqlalchemy.orm.joinedload(PurchaseModel.userinfo).joinedload(UserInfo.user),
                    sqlalchemy.orm.joinedload(PurchaseModel.items).joinedload(PurchaseItemModel.blog_post)
                )
                .where(PurchaseModel.status != PurchaseStatus.PENDING)
                .order_by(PurchaseModel.purchase_date.desc())
            )
            self.purchases = session.exec(statement).unique().all()
