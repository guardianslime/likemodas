# ============================================================================
# likemodas/models.py (Corregido)
# ============================================================================
from __future__ import annotations
from typing import Optional, List
from sqlmodel import Field, Relationship, Column, JSON
import sqlalchemy
from datetime import datetime
import reflex as rx
from reflex_local_auth.user import LocalUser as reflex_LocalUser
import enum
import pytz
# ✅ SOLUCIÓN: Se cambia la importación de '..' a '.' para que sea relativa al paquete actual.
from .utils.formatting import format_to_cop

# --- Helper Functions ---
def format_utc_to_local(utc_dt: Optional[datetime]) -> str:
    if not utc_dt:
        return "N/A"
    colombia_tz = pytz.timezone("America/Bogota")
    if utc_dt.tzinfo is None:
        aware_utc_dt = pytz.utc.localize(utc_dt)
    else:
        aware_utc_dt = utc_dt
    local_dt = aware_utc_dt.astimezone(colombia_tz)
    return local_dt.strftime('%d-%m-%Y %I:%M %p')

# --- Enums ---
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

# --- Models ---
class LocalUser(reflex_LocalUser, table=True):
    __table_args__ = {"extend_existing": True}
    userinfo: Optional["UserInfo"] = Relationship(back_populates="user")

class UserInfo(rx.Model, table=True):
    __table_args__ = {"extend_existing": True}
    email: str
    user_id: int = Field(foreign_key="localuser.id")
    role: UserRole = Field(default=UserRole.CUSTOMER)
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": sqlalchemy.func.now()}, nullable=False)

    user: Optional["LocalUser"] = Relationship(back_populates="userinfo")
    posts: List["BlogPostModel"] = Relationship(back_populates="userinfo")
    verification_tokens: List["VerificationToken"] = Relationship(back_populates="userinfo")
    shipping_addresses: List["ShippingAddressModel"] = Relationship(back_populates="userinfo")
    purchases: List["PurchaseModel"] = Relationship(back_populates="userinfo")
    notifications: List["NotificationModel"] = Relationship(back_populates="userinfo")
    comments: List["CommentModel"] = Relationship(back_populates="userinfo")
    contact_entries: List["ContactEntryModel"] = Relationship(back_populates="userinfo")
    comment_votes: List["CommentVoteModel"] = Relationship(back_populates="userinfo")

class VerificationToken(rx.Model, table=True):
    __table_args__ = {"extend_existing": True}
    token: str = Field(unique=True, index=True)
    userinfo_id: int = Field(foreign_key="userinfo.id")
    expires_at: datetime
    userinfo: "UserInfo" = Relationship(back_populates="verification_tokens")

class PasswordResetToken(rx.Model, table=True):
    __table_args__ = {"extend_existing": True}
    token: str = Field(unique=True, index=True)
    user_id: int = Field(foreign_key="localuser.id")
    expires_at: datetime

class BlogPostModel(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id")
    title: str
    content: str
    price: float = 0.0
    attributes: dict = Field(default={}, sa_column=Column(JSON))
    image_urls: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    publish_active: bool = False
    publish_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": sqlalchemy.func.now()})
    category: Category = Field(default=Category.OTROS)

    userinfo: "UserInfo" = Relationship(back_populates="posts")
    comments: list["CommentModel"] = Relationship(back_populates="blog_post")

    @property
    def rating_count(self) -> int: return len(self.comments)
    @property
    def average_rating(self) -> float:
        if not self.comments: return 0.0
        return sum(c.rating for c in self.comments) / len(self.comments)
    @property
    def created_at_formatted(self) -> str: return format_utc_to_local(self.created_at)
    @property
    def publish_date_formatted(self) -> str: return format_utc_to_local(self.publish_date)
    @property
    def price_cop(self) -> str: return format_to_cop(self.price)

class ShippingAddressModel(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id")
    name: str
    phone: str
    city: str
    neighborhood: str
    address: str
    is_default: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    userinfo: "UserInfo" = Relationship(back_populates="shipping_addresses")

class PurchaseModel(rx.Model, table=True):
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

    items: list["PurchaseItemModel"] = Relationship(back_populates="purchase")
    userinfo: "UserInfo" = Relationship(back_populates="purchases")

    @property
    def purchase_date_formatted(self) -> str: return format_utc_to_local(self.purchase_date)
    @property
    def confirmed_at_formatted(self) -> str: return format_utc_to_local(self.confirmed_at)
    @property
    def total_price_cop(self) -> str: return format_to_cop(self.total_price)
    @property
    def items_formatted(self) -> list[str]:
        if not self.items: return []
        return [item.display_name for item in self.items]

class PurchaseItemModel(rx.Model, table=True):
    purchase_id: int = Field(foreign_key="purchasemodel.id")
    blog_post_id: int = Field(foreign_key="blogpostmodel.id")
    quantity: int
    price_at_purchase: float

    purchase: "PurchaseModel" = Relationship(back_populates="items")
    blog_post: "BlogPostModel" = Relationship()

    @property
    def display_name(self) -> str:
        title = self.blog_post.title if self.blog_post else "Producto no encontrado"
        return f"{self.quantity} x {title}"

class NotificationModel(rx.Model, table=True):
    userinfo_id: int = Field(foreign_key="userinfo.id")
    message: str
    is_read: bool = Field(default=False)
    url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    userinfo: "UserInfo" = Relationship(back_populates="notifications")
    @property
    def created_at_formatted(self) -> str: return format_utc_to_local(self.created_at)

class ContactEntryModel(rx.Model, table=True):
    userinfo_id: Optional[int] = Field(default=None, foreign_key="userinfo.id")
    first_name: str
    last_name: Optional[str] = None
    email: Optional[str] = None
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    userinfo: Optional["UserInfo"] = Relationship(back_populates="contact_entries")
    @property
    def created_at_formatted(self) -> str: return format_utc_to_local(self.created_at)

class CommentModel(rx.Model, table=True):
    content: str
    rating: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": sqlalchemy.func.now()})
    userinfo_id: int = Field(foreign_key="userinfo.id")
    blog_post_id: int = Field(foreign_key="blogpostmodel.id")
    userinfo: "UserInfo" = Relationship(back_populates="comments")
    blog_post: "BlogPostModel" = Relationship(back_populates="comments")
    votes: list["CommentVoteModel"] = Relationship(back_populates="comment")

class CommentVoteModel(rx.Model, table=True):
    vote_type: VoteType
    userinfo_id: int = Field(foreign_key="userinfo.id")
    comment_id: int = Field(foreign_key="commentmodel.id")
    userinfo: "UserInfo" = Relationship(back_populates="comment_votes")
    comment: "CommentModel" = Relationship(back_populates="votes")

class ProductCardData(rx.Base):
    id: int
    title: str
    price: float = 0.0
    image_urls: list[str] = []
    average_rating: float = 0.0
    rating_count: int = 0
    @property
    def price_cop(self) -> str: return format_to_cop(self.price)
