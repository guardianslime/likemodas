# likemodas/models.py (Versión Final Corregida)

from typing import Optional, List, ClassVar # <--- 1. IMPORTA ClassVar
from datetime import datetime
import enum
import pytz
import reflex as rx
import sqlalchemy
from sqlmodel import Field, Relationship, Column, JSON
from sqlalchemy import String
from reflex_local_auth.user import LocalUser
from .utils.timing import get_utc_now
from .utils.formatting import format_to_cop


# --- Adelanta la declaración de CommentModel ---
if "CommentModel" not in locals():
    CommentModel = "CommentModel"

# --- Funciones de Utilidad ---
def format_utc_to_local(utc_dt: Optional[datetime]) -> str:
    if not utc_dt:
        return "N/A"
    try:
        colombia_tz = pytz.timezone("America/Bogota")
        aware_utc_dt = utc_dt.replace(tzinfo=pytz.utc)
        local_dt = aware_utc_dt.astimezone(colombia_tz)
        return local_dt.strftime('%d-%m-%Y %I:%M %p')
    except Exception:
        return utc_dt.strftime('%Y-%m-%d %H:%M')

# --- Tabla de Asociación para Publicaciones Guardadas ---
class SavedPostLink(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id", primary_key=True)
    blogpostmodel_id: int = Field(foreign_key="blogpostmodel.id", primary_key=True)

# --- Enumeraciones ---
class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"

class PurchaseStatus(str, enum.Enum):
    PENDING = "pending_confirmation"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"

class VoteType(str, enum.Enum):
    LIKE = "like"
    DISLIKE = "dislike"

class Category(str, enum.Enum):
    ROPA = "ropa"
    CALZADO = "calzado"
    MOCHILAS = "mochilas"
    OTROS = "otros"

# --- Modelos de Base de Datos ---

# Forward declaration para resolver dependencias circulares en type hints
if "PurchaseItemModel" not in locals():
    PurchaseItemModel = "PurchaseItemModel"
if "CommentModel" not in locals():
    CommentModel = "CommentModel"

class UserInfo(rx.Model, table=True):
    __tablename__ = "userinfo"
    email: str
    user_id: int = Field(foreign_key="localuser.id", unique=True)
    role: UserRole = Field(default=UserRole.CUSTOMER, sa_column=Column(String, server_default=UserRole.CUSTOMER.value, nullable=False))
    is_verified: bool = Field(default=False, nullable=False)
    is_banned: bool = Field(default=False, nullable=False)
    ban_expires_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=get_utc_now, sa_type=sqlalchemy.DateTime(timezone=True), sa_column_kwargs={"server_default": sqlalchemy.func.now()}, nullable=False)
    updated_at: datetime = Field(default_factory=get_utc_now, sa_type=sqlalchemy.DateTime(timezone=True), sa_column_kwargs={"onupdate": sqlalchemy.func.now(), "server_default": sqlalchemy.func.now()}, nullable=False)

    # 2. ANOTA EL DICCIONARIO CON ClassVar[dict]
    relationship_attributes: ClassVar[dict] = {
        "user": Relationship(),
        "posts": Relationship(back_populates="userinfo"),
        "verification_tokens": Relationship(back_populates="userinfo"),
        "shipping_addresses": Relationship(back_populates="userinfo"),
        "contact_entries": Relationship(back_populates="userinfo"),
        "purchases": Relationship(back_populates="userinfo"),
        "notifications": Relationship(back_populates="userinfo"),
        "comments": Relationship(back_populates="userinfo"),
        "comment_votes": Relationship(back_populates="userinfo"),
        "saved_posts": Relationship(back_populates="saved_by_users", link_model=SavedPostLink),
    }

class VerificationToken(rx.Model, table=True):
    token: str = Field(unique=True, index=True)
    userinfo_id: int = Field(foreign_key="userinfo.id")
    expires_at: datetime
    created_at: datetime = Field(default_factory=get_utc_now, sa_column_kwargs={"server_default": sqlalchemy.func.now()}, nullable=False)
    
    relationship_attributes: ClassVar[dict] = {
        "userinfo": Relationship(back_populates="verification_tokens")
    }
    
    class Config:
        exclude = {"userinfo"}

class PasswordResetToken(rx.Model, table=True):
    token: str = Field(unique=True, index=True)
    user_id: int = Field(foreign_key="localuser.id")
    expires_at: datetime
    created_at: datetime = Field(default_factory=get_utc_now, sa_column_kwargs={"server_default": sqlalchemy.func.now()}, nullable=False)

class BlogPostModel(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id")
    title: str; content: str
    price: float = 0.0
    attributes: dict = Field(default={}, sa_column=Column(JSON))
    image_urls: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    publish_active: bool = False
    publish_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=get_utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=get_utc_now, sa_column_kwargs={"onupdate": sqlalchemy.func.now()}, nullable=False)
    category: Category = Field(default=Category.OTROS, sa_column=Column(String, nullable=False, server_default=Category.OTROS.value))
    
    relationship_attributes: ClassVar[dict] = {
        "userinfo": Relationship(back_populates="posts"),
        "comments": Relationship(back_populates="blog_post"),
        "saved_by_users": Relationship(back_populates="saved_posts", link_model=SavedPostLink),
    }
    
    class Config:
        exclude = {"userinfo"}
    
    @property
    def rating_count(self) -> int:
        # Tuve que añadir una comprobación para evitar un error si comments es None
        return len(self.comments) if self.comments is not None else 0

    @property
    def average_rating(self) -> float:
        # Tuve que añadir una comprobación para evitar un error si comments es None
        if not self.comments:
            return 0.0
        return sum(c.rating for c in self.comments) / len(self.comments)
    
    @property
    def created_at_formatted(self) -> str: return format_utc_to_local(self.created_at)

    @property
    def publish_date_formatted(self) -> str: return format_utc_to_local(self.publish_date)

    @property
    def price_cop(self) -> str: return format_to_cop(self.price)

class ShippingAddressModel(rx.Model, table=True):
    __tablename__ = "shippingaddress"
    userinfo_id: int = Field(foreign_key="userinfo.id")
    name: str; phone: str; city: str; neighborhood: str; address: str
    is_default: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=get_utc_now, nullable=False)

    relationship_attributes: ClassVar[dict] = {
        "userinfo": Relationship(back_populates="shipping_addresses")
    }

    class Config:
        exclude = {"userinfo"}

class PurchaseModel(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id")
    purchase_date: datetime = Field(default_factory=get_utc_now, nullable=False)
    confirmed_at: Optional[datetime] = Field(default=None)
    total_price: float
    status: PurchaseStatus = Field(default=PurchaseStatus.PENDING, nullable=False)
    shipping_name: Optional[str] = None; shipping_city: Optional[str] = None
    shipping_neighborhood: Optional[str] = None; shipping_address: Optional[str] = None
    shipping_phone: Optional[str] = None
    
    relationship_attributes: ClassVar[dict] = {
        "userinfo": Relationship(back_populates="purchases"),
        "items": Relationship(back_populates="purchase"),
    }

    class Config:
        exclude = {"userinfo"}

    @property
    def purchase_date_formatted(self) -> str: return format_utc_to_local(self.purchase_date)
    @property
    def confirmed_at_formatted(self) -> str: return format_utc_to_local(self.confirmed_at)
    @property
    def total_price_cop(self) -> str: return format_to_cop(self.total_price)
    @property
    def items_formatted(self) -> list[str]:
        if not self.items: return []
        return [f"{item.quantity}x {item.blog_post.title} (a {format_to_cop(item.price_at_purchase)} c/u)" for item in self.items if item.blog_post]

class PurchaseItemModel(rx.Model, table=True):
    purchase_id: int = Field(foreign_key="purchasemodel.id")
    blog_post_id: int = Field(foreign_key="blogpostmodel.id")
    quantity: int
    price_at_purchase: float
    
    relationship_attributes: ClassVar[dict] = {
        "purchase": Relationship(back_populates="items"),
        "blog_post": Relationship(),
    }

    class Config:
        exclude = {"purchase"}

class NotificationModel(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id")
    message: str
    is_read: bool = Field(default=False)
    url: Optional[str] = None
    created_at: datetime = Field(default_factory=get_utc_now, sa_type=sqlalchemy.DateTime(timezone=True), nullable=False)
    
    relationship_attributes: ClassVar[dict] = {
        "userinfo": Relationship(back_populates="notifications")
    }
    
    class Config:
        exclude = {"userinfo"}
    
    @property
    def created_at_formatted(self) -> str: return format_utc_to_local(self.created_at)

class ContactEntryModel(rx.Model, table=True):
    userinfo_id: Optional[int] = Field(default=None, foreign_key="userinfo.id")
    first_name: str
    last_name: Optional[str] = None
    email: Optional[str] = None
    message: str
    created_at: datetime = Field(default_factory=get_utc_now, sa_type=sqlalchemy.DateTime(timezone=True), nullable=False)

    relationship_attributes: ClassVar[dict] = {
        "userinfo": Relationship(back_populates="contact_entries")
    }

    class Config:
        exclude = {"userinfo"}

    @property
    def created_at_formatted(self) -> str: return format_utc_to_local(self.created_at)

class CommentModel(rx.Model, table=True):
    content: str; rating: int
    created_at: datetime = Field(default_factory=get_utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=get_utc_now, sa_column_kwargs={"onupdate": sqlalchemy.func.now()}, nullable=False)
    userinfo_id: int = Field(foreign_key="userinfo.id")
    blog_post_id: int = Field(foreign_key="blogpostmodel.id")
    
    relationship_attributes: ClassVar[dict] = {
        "userinfo": Relationship(back_populates="comments"),
        "blog_post": Relationship(back_populates="comments"),
        "votes": Relationship(back_populates="comment"),
    }

    class Config:
        exclude = {"blog_post", "userinfo"}

    @property
    def created_at_formatted(self) -> str: return format_utc_to_local(self.created_at)

    @property
    def updated_at_formatted(self) -> str:
        return format_utc_to_local(self.updated_at)
    
    @property
    def was_updated(self) -> bool:
        return (self.updated_at - self.created_at).total_seconds() > 5

    @property
    def likes(self) -> int: 
        # Tuve que añadir una comprobación para evitar un error si votes es None
        return sum(1 for vote in self.votes if vote.vote_type == VoteType.LIKE) if self.votes is not None else 0

    @property
    def dislikes(self) -> int: 
        # Tuve que añadir una comprobación para evitar un error si votes es None
        return sum(1 for vote in self.votes if vote.vote_type == VoteType.DISLIKE) if self.votes is not None else 0

class CommentVoteModel(rx.Model, table=True):
    vote_type: VoteType = Field(sa_column=Column(String))
    userinfo_id: int = Field(foreign_key="userinfo.id")
    comment_id: int = Field(foreign_key="commentmodel.id")
    
    relationship_attributes: ClassVar[dict] = {
        "userinfo": Relationship(back_populates="comment_votes"),
        "comment": Relationship(back_populates="votes"),
    }

    class Config:
        exclude = {"userinfo", "comment"}