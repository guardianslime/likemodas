# likemodas/cart/state.py

import reflex as rx
from typing import Dict, List, Tuple, Optional
from sqlmodel import select, or_, cast
from sqlalchemy import String
from datetime import datetime
import reflex_local_auth
import sqlalchemy

from ..auth.state import SessionState
from ..models import Category, PurchaseModel, PurchaseStatus, UserInfo, PurchaseItemModel, BlogPostModel, NotificationModel, ShippingAddressModel
from ..utils.formatting import format_to_cop 

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

class CartState(SessionState):
    cart: Dict[int, int] = rx.Field(default_factory=dict)
    posts: list[ProductCardData] = rx.Field(default_factory=list)
    default_shipping_address: Optional[ShippingAddressModel] = None
    is_loading: bool = True
    
    @rx.var
    def cart_total(self) -> float:
        return sum(p.price * q for p, q in self.cart_details if p and p.price)
    
    @rx.var
    def cart_details(self) -> List[Tuple[ProductCardData, int]]:
        if not self.cart: return []
        post_map = {p.id: p for p in self.posts}
        return [(post_map[pid], self.cart[pid]) for pid in self.cart if pid in post_map]

    @rx.event
    def on_load(self):
        self.is_loading = True
        yield
        with rx.session() as session:
            results = session.exec(
                select(BlogPostModel)
                .options(sqlalchemy.orm.joinedload(BlogPostModel.comments))
                .where(BlogPostModel.publish_active == True, BlogPostModel.publish_date < datetime.now())
                .order_by(BlogPostModel.created_at.desc())
            ).unique().all()
            
            self.posts = [
                ProductCardData(
                    id=p.id or 0,
                    title=p.title or "Producto sin nombre",
                    price=p.price or 0.0,
                    price_formatted=format_to_cop(p.price or 0.0),
                    image_urls=p.image_urls or [],
                    average_rating=p.average_rating or 0.0,
                    rating_count=p.rating_count or 0
                ) for p in results
            ]
        self.is_loading = False

    @rx.event
    def handle_checkout(self):
        if not self.is_authenticated or not self.default_shipping_address:
            return rx.toast.error("Por favor, selecciona una dirección predeterminada.")
        
        user_info = self.authenticated_user_info
        if not user_info or user_info.id is None:
            return rx.toast.error("Error de usuario. Vuelve a iniciar sesión.")

        with rx.session() as session:
            post_ids = list(self.cart.keys())
            db_posts_map = {p.id: p for p in session.exec(select(BlogPostModel).where(BlogPostModel.id.in_(post_ids))).all()}
            
            new_purchase = PurchaseModel(
                userinfo_id=int(user_info.id),
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
            
            for post_id, quantity in self.cart.items():
                if post_id in db_posts_map:
                    post = db_posts_map[post_id]
                    session.add(PurchaseItemModel(
                        purchase_id=new_purchase.id, 
                        blog_post_id=post.id, 
                        quantity=quantity, 
                        price_at_purchase=post.price
                    ))
            session.commit()

        self.cart.clear()
        self.default_shipping_address = None
        
        yield type(self).notify_admin_of_new_purchase
        
        yield rx.toast.success("¡Gracias por tu compra! Tu orden está pendiente de confirmación.")
        return rx.redirect("/my-purchases")