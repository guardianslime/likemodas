# likemodas/models/cart.py

from sqlmodel import Field, Relationship
from typing import Optional, List
from datetime import datetime
import reflex as rx

from .blog import BlogPostModel
# Corrección para evitar dependencias circulares
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user import UserInfo

from .base import format_utc_to_local
from ..utils.formatting import format_to_cop
from .enums import PurchaseStatus

class PurchaseModel(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    userinfo_id: int = Field(foreign_key="userinfo.id")
    total_price: float
    status: PurchaseStatus = Field(default=PurchaseStatus.PENDING)
    purchase_date: datetime = Field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = None

    shipping_name: Optional[str]
    shipping_city: Optional[str]
    shipping_neighborhood: Optional[str]
    shipping_address: Optional[str]
    shipping_phone: Optional[str]

    items: List["PurchaseItemModel"] = Relationship(back_populates="purchase")
    # Se usa un string ("UserInfo") para la referencia
    userinfo: "UserInfo" = Relationship(back_populates="purchases")

    @property
    def purchase_date_formatted(self) -> str:
        return format_utc_to_local(self.purchase_date)
        
    @property
    def confirmed_at_formatted(self) -> str:
        return format_utc_to_local(self.confirmed_at)

    @property
    def total_price_cop(self) -> str:
        return format_to_cop(self.total_price)
    
    @property
    def items_formatted(self) -> list[str]:
        """Devuelve una lista formateada de los artículos de la compra."""
        if not self.items:
            return []
        return [item.display_name for item in self.items]


class PurchaseItemModel(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    purchase_id: int = Field(foreign_key="purchasemodel.id")
    blog_post_id: int = Field(foreign_key="blogpostmodel.id")
    quantity: int
    price_at_purchase: float

    purchase: "PurchaseModel" = Relationship(back_populates="items")
    blog_post: "BlogPostModel" = Relationship()

    @property
    def display_name(self) -> str:
        """Genera un nombre legible para el artículo en la compra."""
        title = self.blog_post.title if self.blog_post else "Producto no encontrado"
        return f"{self.quantity} x {title}"