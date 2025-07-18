# full_stack_python/models.py (CORREGIDO Y COMPLETO)

from typing import Optional, List
from . import utils
from sqlmodel import Field, Relationship, Column, JSON
# --- ✨ AÑADIDO: Importar String ---
from sqlalchemy import String
from datetime import datetime
import reflex as rx
from reflex_local_auth.user import LocalUser
import sqlalchemy
import enum

class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"

class UserInfo(rx.Model, table=True):
    email: str
    user_id: int = Field(foreign_key="localuser.id")
    
    # --- ✨ CORRECCIÓN: Se define explícitamente la columna como String ---
    role: UserRole = Field(
        default=UserRole.CUSTOMER,
        sa_column=Column(String, server_default=UserRole.CUSTOMER.value, nullable=False)
    )
    # --- FIN DE CAMBIOS ---
    
    user: Optional[LocalUser] = Relationship()
    posts: List["BlogPostModel"] = Relationship(back_populates="userinfo")
    contact_entries: List["ContactEntryModel"] = Relationship(back_populates="userinfo")
    purchases: List["PurchaseModel"] = Relationship(back_populates="userinfo")
    
    created_at: datetime = Field(
        default_factory=utils.timing.get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={"server_default": sqlalchemy.func.now()},
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=utils.timing.get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={"onupdate": sqlalchemy.func.now(), "server_default": sqlalchemy.func.now()},
        nullable=False,
    )

class PurchaseStatus(str, enum.Enum):
    PENDING = "pending_confirmation"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"

class PurchaseModel(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id")
    userinfo: "UserInfo" = Relationship(back_populates="purchases")
    
    purchase_date: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    confirmed_at: Optional[datetime] = Field(default=None)
    total_price: float
    status: PurchaseStatus = Field(default=PurchaseStatus.PENDING, nullable=False)
    
    items: List["PurchaseItemModel"] = Relationship(back_populates="purchase")

    @property
    def purchase_date_formatted(self) -> str:
        return self.purchase_date.strftime('%d-%m-%Y %H:%M')

    @property
    def items_formatted(self) -> list[str]:
        if not self.items:
            return []
        return [
            f"{item.quantity}x {item.blog_post.title} (@ ${item.price_at_purchase:.2f} c/u)"
            for item in self.items
        ]

    # --- ✨ CORRECCIÓN: AÑADE ESTE MÉTODO ---
    def dict(self, **kwargs):
        """
        Sobrescribe el método dict para incluir las propiedades computadas
        y hacerlas accesibles en el frontend.
        """
        d = super().dict(**kwargs)
        d["purchase_date_formatted"] = self.purchase_date_formatted
        d["items_formatted"] = self.items_formatted
        return d

class PurchaseItemModel(rx.Model, table=True):
    purchase_id: int = Field(foreign_key="purchasemodel.id")
    purchase: "PurchaseModel" = Relationship(back_populates="items")
    
    blog_post_id: int = Field(foreign_key="blogpostmodel.id")
    blog_post: "BlogPostModel" = Relationship()
    
    quantity: int
    price_at_purchase: float

class BlogPostModel(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id")
    userinfo: "UserInfo" = Relationship(back_populates="posts")
    title: str
    content: str
    price: float = 0.0
    images: list[str] = Field(default=[], sa_column=Column(JSON))
    publish_active: bool = False
    publish_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    @property
    def created_at_formatted(self) -> str:
        return self.created_at.strftime("%Y-%m-%d")
    @property
    def publish_date_formatted(self) -> str:
        if not self.publish_date:
            return ""
        return self.publish_date.strftime("%d-%m-%Y")

class ContactEntryModel(rx.Model, table=True):
    userinfo_id: Optional[int] = Field(default=None, foreign_key="userinfo.id")
    userinfo: Optional["UserInfo"] = Relationship(back_populates="contact_entries")
    first_name: str
    last_name: Optional[str] = None
    email: Optional[str] = None
    message: str
    created_at: datetime = Field(
        default_factory=utils.timing.get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={"server_default": sqlalchemy.func.now()},
        nullable=False,
    )
    @property
    def created_at_formatted(self) -> str:
        return self.created_at.strftime("%Y-%m-%d %H:%M")
    def dict(self, **kwargs):
        return super().dict(**kwargs) | {"created_at_formatted": self.created_at_formatted}