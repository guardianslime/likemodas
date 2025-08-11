# likemodas/models.py

from typing import Optional, List
from datetime import datetime, timezone
import reflex as rx
from reflex_local_auth.user import LocalUser
import enum
from sqlmodel import Field, Relationship, Column, JSON

def get_utc_now() -> datetime:
    """Devuelve la hora actual en UTC."""
    return datetime.now(timezone.utc)

class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"

class PurchaseStatus(str, enum.Enum):
    PENDING = "pendiente"
    CONFIRMED = "confirmado"

class UserInfo(rx.Model, table=True):
    """Información extendida del usuario."""
    email: str = Field(unique=True, index=True)
    role: UserRole = Field(default=UserRole.CUSTOMER)
    created_at: datetime = Field(default_factory=get_utc_now)
    is_banned: bool = Field(default=False) # Para la funcionalidad de amonestaciones

    user_id: int = Field(foreign_key="localuser.id", unique=True)
    user: Optional[LocalUser] = Relationship()

    products: List["Product"] = Relationship(back_populates="seller")
    purchases: List["Purchase"] = Relationship(back_populates="buyer")

class Product(rx.Model, table=True):
    """Modelo de productos/publicaciones."""
    title: str
    content: str
    price: float = Field(default=0.0)
    image_url: Optional[str] = None # Simplificado a una sola imagen principal
    is_published: bool = Field(default=True)
    created_at: datetime = Field(default_factory=get_utc_now)

    seller_id: int = Field(foreign_key="userinfo.id")
    seller: UserInfo = Relationship(back_populates="products")

    @rx.var
    def price_cop(self) -> str:
        return f"${self.price:,.0f}"

class Purchase(rx.Model, table=True):
    """Una compra realizada por un usuario."""
    total_price: float
    status: PurchaseStatus = Field(default=PurchaseStatus.PENDING)
    created_at: datetime = Field(default_factory=get_utc_now)
    shipping_details: dict = Field(default={}, sa_column=Column(JSON))

    buyer_id: int = Field(foreign_key="userinfo.id")
    buyer: UserInfo = Relationship(back_populates="purchases")

    items: List["PurchaseItem"] = Relationship(back_populates="purchase")

class PurchaseItem(rx.Model, table=True):
    """Un ítem dentro de una compra."""
    quantity: int
    product_title: str
    price_at_purchase: float

    purchase_id: int = Field(foreign_key="purchase.id")
    purchase: Purchase = Relationship(back_populates="items")