# full_stack_python/models.py (CORREGIDO Y AMPLIADO)

from typing import Optional, List
from . import utils
from sqlmodel import Field, Relationship, Column, JSON
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
    # --- ✨ NUEVO: Campo de Rol ---
    role: UserRole = Field(default=UserRole.CUSTOMER, nullable=False)
    
    user: Optional[LocalUser] = Relationship()
    posts: List["BlogPostModel"] = Relationship(back_populates="userinfo")
    contact_entries: List["ContactEntryModel"] = Relationship(back_populates="userinfo")
    # --- ✨ NUEVO: Relación con Compras ---
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

# --- ✨ NUEVO: Modelo para el estado de la compra ---
class PurchaseStatus(str, enum.Enum):
    PENDING = "pending_confirmation"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"

# --- ✨ NUEVO: Modelo para la Orden de Compra ---
class PurchaseModel(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id")
    userinfo: "UserInfo" = Relationship(back_populates="purchases")
    
    purchase_date: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    total_price: float
    status: PurchaseStatus = Field(default=PurchaseStatus.PENDING, nullable=False)
    
    items: List["PurchaseItemModel"] = Relationship(back_populates="purchase")

# --- ✨ NUEVO: Modelo para los Items de la Compra ---
class PurchaseItemModel(rx.Model, table=True):
    purchase_id: int = Field(foreign_key="purchasemodel.id")
    purchase: "PurchaseModel" = Relationship(back_populates="items")
    
    blog_post_id: int = Field(foreign_key="blogpostmodel.id")
    blog_post: "BlogPostModel" = Relationship()
    
    quantity: int
    price_at_purchase: float # Guardamos el precio al momento de la compra


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

# ... (Clase ContactEntryModel sin cambios) ...
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
        """Devuelve la fecha de creación como string formateado."""
        return self.created_at.strftime("%Y-%m-%d %H:%M")

    def dict(self, **kwargs):
        return super().dict(**kwargs) | {"created_at_formatted": self.created_at_formatted}