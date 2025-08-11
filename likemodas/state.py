# likemodas/state.py

import reflex as rx
import reflex_local_auth
from typing import List, Dict, Optional
from sqlmodel import select
from .models import UserInfo, UserRole, Product, Purchase, PurchaseItem, PurchaseStatus

class AppState(reflex_local_auth.LocalAuthState):
    """Estado central de la aplicación."""

    #--- Propiedades de Usuario ---
    @rx.var
    def authenticated_user_info(self) -> Optional[UserInfo]:
        if self.is_authenticated:
            with rx.session() as session:
                return session.exec(select(UserInfo).where(UserInfo.user_id == self.authenticated_user.id)).one_or_none()
        return None

    @rx.var
    def is_admin(self) -> bool:
        return self.authenticated_user_info and self.authenticated_user_info.role == UserRole.ADMIN

    #--- Registro Personalizado ---
    def handle_registration_custom(self, form_data: dict):
        super().handle_registration(form_data)
        if self.new_user_id is not None and self.new_user_id >= 0:
            with rx.session() as session:
                role = UserRole.ADMIN if form_data["username"] == "admin" else UserRole.CUSTOMER
                user_info = UserInfo(email=form_data["email"], role=role, user_id=self.new_user_id)
                session.add(user_info)
                session.commit()

    #--- Gestión de Productos (Público y Admin) ---
    products: List[Product] = []

    def load_products(self):
        with rx.session() as session:
            self.products = session.exec(select(Product).where(Product.is_published == True)).all()

    def handle_product_create(self, form_data: dict):
        if not self.is_admin: return
        with rx.session() as session:
            product = Product(
                title=form_data["title"],
                content=form_data["content"],
                price=float(form_data["price"]),
                seller_id=self.authenticated_user_info.id
            )
            session.add(product)
            session.commit()
        self.load_products()
        return rx.redirect("/admin/products")

    def delete_product(self, product_id: int):
        if not self.is_admin: return
        with rx.session() as session:
            product = session.get(Product, product_id)
            if product:
                session.delete(product)
                session.commit()
        self.load_products()

    #--- Carrito ---
    cart: Dict[int, int] = {} # product_id: quantity

    def add_to_cart(self, product_id: int):
        self.cart[product_id] = self.cart.get(product_id, 0) + 1

    @rx.var
    def cart_items_count(self) -> int:
        return sum(self.cart.values())

    #--- Checkout ---
    my_purchases: List[Purchase] = []

    def load_my_purchases(self):
        if self.authenticated_user_info:
            with rx.session() as session:
                self.my_purchases = session.exec(select(Purchase).where(Purchase.buyer_id == self.authenticated_user_info.id)).all()

    def handle_checkout(self):
        if not self.is_authenticated or not self.cart: return
        with rx.session() as session:
            total = 0
            purchase_items_data = []
            for pid, qty in self.cart.items():
                product = session.get(Product, pid)
                if product:
                    total += product.price * qty
                    purchase_items_data.append(
                        PurchaseItem(quantity=qty, product_title=product.title, price_at_purchase=product.price)
                    )
            
            purchase = Purchase(
                total_price=total,
                buyer_id=self.authenticated_user_info.id,
                items=purchase_items_data
            )
            session.add(purchase)
            session.commit()

        self.cart = {}
        return rx.redirect("/my-account")

    #--- Admin: Gestión de Usuarios y Órdenes ---
    all_users: List[UserInfo] = []
    all_purchases: List[Purchase] = []

    def load_all_users(self):
        if not self.is_admin: return
        with rx.session() as session:
            self.all_users = session.exec(select(UserInfo).options(rx.select.load(UserInfo.user))).all()

    def load_all_purchases(self):
        if not self.is_admin: return
        with rx.session() as session:
            self.all_purchases = session.exec(select(Purchase).options(rx.select.load(Purchase.buyer).load(UserInfo.user))).all()

    def toggle_ban_user(self, user_id: int):
        if not self.is_admin: return
        with rx.session() as session:
            user_info = session.get(UserInfo, user_id)
            if user_info:
                user_info.is_banned = not user_info.is_banned
                session.add(user_info)
                session.commit()
        self.load_all_users()