# likemodas/state.py (VERSIÓN FINAL Y CORRECTA)

import reflex as rx
import reflex_local_auth
from typing import List, Dict, Optional
from sqlmodel import select
from .models import UserInfo, UserRole, Product, Purchase, PurchaseItem, PurchaseStatus

class AppState(reflex_local_auth.LocalAuthState):
    """Estado central de la aplicación."""

    error_message: str = ""
    success_message: str = ""
    
    def handle_login(self, form_data: dict):
        """Manejador de login explícito que llama a la lógica de la librería."""
        return super().handle_login(form_data)

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
        self.error_message = ""
        self.success_message = ""
        super().handle_registration(form_data)

        if self.new_user_id is not None and self.new_user_id >= 0:
            with rx.session() as session:
                role = UserRole.ADMIN if form_data["username"] == "admin" else UserRole.CUSTOMER
                user_info = UserInfo(email=form_data["email"], role=role, user_id=self.new_user_id)
                session.add(user_info)
                session.commit()
            self.success_message = "¡Cuenta creada con éxito! Ya puedes iniciar sesión."
        else:
            self.error_message = super().error_message

    #--- Gestión de Productos (Público y Admin) ---
    products: List[Product] = []

    def load_products(self):
        with rx.session() as session:
            self.products = session.exec(select(Product).where(Product.is_published == True)).all()

    # --- Carrito ---
    cart: Dict[int, int] = {} 

    def add_to_cart(self, product_id: int):
        self.cart[product_id] = self.cart.get(product_id, 0) + 1

    @rx.var
    def cart_items_count(self) -> int:
        return sum(self.cart.values())

    @rx.var
    def cart_items(self) -> list[tuple[Product, int]]:
        if not self.cart:
            return []
        with rx.session() as session:
            items = []
            for pid, qty in self.cart.items():
                product = session.get(Product, pid)
                if product:
                    items.append((product, qty))
            return items

    @rx.var
    def cart_total(self) -> float:
        total = 0.0
        for product, qty in self.cart_items:
            total += product.price * qty
        return total

    @rx.var
    def cart_total_cop(self) -> str:
        return f"${self.cart_total:,.0f}"

    #--- Checkout ---
    my_purchases: List[Purchase] = []

    def load_my_purchases(self):
        if self.authenticated_user_info:
            with rx.session() as session:
                self.my_purchases = session.exec(select(Purchase).where(Purchase.buyer_id == self.authenticated_user_info.id)).all()

    def handle_checkout(self):
        if not self.is_authenticated or not self.cart: return
        with rx.session() as session:
            purchase_items_data = [
                PurchaseItem(quantity=qty, product_title=product.title, price_at_purchase=product.price)
                for product, qty in self.cart_items
            ]
            purchase = Purchase(
                total_price=self.cart_total,
                buyer_id=self.authenticated_user_info.id,
                items=purchase_items_data
            )
            session.add(purchase)
            session.commit()
        self.cart = {}
        return rx.redirect("/my-account")